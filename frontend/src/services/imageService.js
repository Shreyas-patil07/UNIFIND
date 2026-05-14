/**
 * Image Service - Abstracted image upload with compression
 * Supports: Supabase Storage (profiles) + Cloudinary (products)
 * 
 * Usage Examples:
 * 
 * Single upload:
 *   const url = await imageService.upload(file, 'product');
 * 
 * Multiple uploads (parallel):
 *   const urls = await imageService.uploadMultiple([file1, file2, file3], 'product');
 *   // Returns array of successful URLs, handles individual failures gracefully
 */

class ImageService {
  constructor() {
    this.MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
    this.TARGET_SIZE = 500 * 1024; // 500KB target
    this.MAX_DIMENSION = 1920;
    this.QUALITY = 0.8;
  }

  /**
   * Main upload method - routes to correct provider
   * @param {File} file - Image file to upload
   * @param {string} type - 'profile' or 'product'
   * @returns {Promise<string>} - Image URL
   */
  async upload(file, type = 'product') {
    // Validate file
    this.validateFile(file);

    // Compress image
    const compressed = await this.compressImage(file);

    // Route to correct provider
    if (type === 'profile') {
      // SECURE: Use backend endpoint for profile photos
      return this.uploadProfileToBackend(compressed);
    } else {
      return this.uploadToCloudinary(compressed);
    }
  }

  /**
   * Validate image file
   */
  validateFile(file) {
    // Validate file type - only JPEG, PNG, WebP allowed
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type.toLowerCase())) {
      throw new Error('Only JPEG, PNG, and WebP images are supported');
    }
    
    // Validate file size - max 5MB before compression
    if (file.size > this.MAX_FILE_SIZE) {
      throw new Error('Image must be less than 5MB');
    }
  }

  /**
   * Compress image to target size (~500KB)
   * @param {File} file - Original image file
   * @returns {Promise<File>} - Compressed image file
   */
  async compressImage(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onerror = () => reject(new Error('Failed to read file'));
      
      reader.onload = (event) => {
        const img = new Image();
        
        img.onerror = () => reject(new Error('Failed to load image'));
        
        img.onload = () => {
          try {
            const canvas = document.createElement('canvas');
            let { width, height } = img;

            // Calculate new dimensions
            if (width > this.MAX_DIMENSION || height > this.MAX_DIMENSION) {
              if (width > height) {
                height = Math.round((height / width) * this.MAX_DIMENSION);
                width = this.MAX_DIMENSION;
              } else {
                width = Math.round((width / height) * this.MAX_DIMENSION);
                height = this.MAX_DIMENSION;
              }
            }

            canvas.width = width;
            canvas.height = height;

            // Draw and compress
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            // Convert to blob
            canvas.toBlob(
              (blob) => {
                if (!blob) {
                  reject(new Error('Failed to compress image'));
                  return;
                }
                
                const compressedFile = new File([blob], file.name, {
                  type: 'image/jpeg',
                  lastModified: Date.now(),
                });
                
                console.log(`Compressed: ${(file.size / 1024).toFixed(0)}KB → ${(blob.size / 1024).toFixed(0)}KB`);
                resolve(compressedFile);
              },
              'image/jpeg',
              this.QUALITY
            );
          } catch (error) {
            reject(error);
          }
        };

        img.src = event.target.result;
      };

      reader.readAsDataURL(file);
    });
  }

  /**
   * Upload to backend API (for profile photos)
   * This is the SECURE way - backend handles upload and deletion
   */
  async uploadProfileToBackend(file) {
    try {
      console.log('🔵 Starting backend profile upload...');
      
      // Get Firebase auth token
      const { auth } = await import('./firebase');
      if (!auth.currentUser) {
        throw new Error('User must be authenticated');
      }

      const token = await auth.currentUser.getIdToken();
      
      // Create form data
      const formData = new FormData();
      formData.append('file', file);

      // Get backend URL from environment
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      const backendUrl = apiUrl.replace('/api', ''); // Remove /api suffix if present
      
      console.log('🔵 Uploading to backend:', `${backendUrl}/upload/profile-image`);

      // Upload to backend
      const response = await fetch(`${backendUrl}/upload/profile-image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Backend upload error:', errorData);
        throw new Error(errorData.detail || 'Backend upload failed');
      }

      const data = await response.json();
      console.log('✅ Backend upload successful:', data);
      
      return data.url;
    } catch (error) {
      console.error('❌ Backend upload failed:', error);
      throw new Error('Failed to upload profile image: ' + error.message);
    }
  }

  /**
   * Upload to Cloudinary (for product images)
   */
  async uploadToCloudinary(file) {
    try {
      const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
      
      console.log('Cloudinary cloud name:', cloudName);
      
      if (!cloudName) {
        throw new Error('Cloudinary cloud name not configured');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('upload_preset', 'unifind_products');
      formData.append('folder', 'unifind/products');

      console.log('Uploading to Cloudinary...', file.name, file.size);

      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`,
        {
          method: 'POST',
          body: formData,
        }
      );

      console.log('Cloudinary response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Cloudinary error:', errorData);
        throw new Error(errorData.error?.message || 'Cloudinary upload failed');
      }

      const data = await response.json();
      console.log('Cloudinary upload successful:', data.secure_url);
      return data.secure_url;
    } catch (error) {
      console.error('Cloudinary upload failed:', error);
      throw new Error('Failed to upload to Cloudinary: ' + error.message);
    }
  }

  /**
   * Upload multiple images in parallel
   * @param {File[]} files - Array of image files to upload
   * @param {string} type - 'profile' or 'product' (default: 'product')
   * @returns {Promise<string[]>} - Array of successful Image_URLs
   */
  async uploadMultiple(files, type = 'product') {
    if (!Array.isArray(files) || files.length === 0) {
      throw new Error('Files must be a non-empty array');
    }

    // Upload all files concurrently
    const uploadPromises = files.map(async (file, index) => {
      try {
        const url = await this.upload(file, type);
        return { success: true, url, index };
      } catch (error) {
        console.error(`Failed to upload file ${index + 1}:`, error.message);
        return { success: false, error: error.message, index };
      }
    });

    // Wait for all uploads to complete
    const results = await Promise.all(uploadPromises);

    // Extract successful URLs
    const successfulUrls = results
      .filter(result => result.success)
      .map(result => result.url);

    // Log failures for debugging
    const failures = results.filter(result => !result.success);
    if (failures.length > 0) {
      console.warn(`${failures.length} upload(s) failed:`, failures);
    }

    return successfulUrls;
  }

  /**
   * Optimize Cloudinary URL for display
   * @param {string} url - Original Cloudinary URL
   * @param {number} width - Target width
   * @returns {string} - Optimized URL
   */
  optimizeUrl(url, width = 800) {
    if (!url || !url.includes('cloudinary.com')) {
      return url;
    }

    // Add optimization transformations
    return url.replace(
      '/upload/',
      `/upload/f_auto,q_auto:good,w_${width},c_limit/`
    );
  }

  /**
   * Get thumbnail URL (Cloudinary only)
   */
  getThumbnailUrl(url) {
    return this.optimizeUrl(url, 200);
  }

  /**
   * Get medium URL (Cloudinary only)
   */
  getMediumUrl(url) {
    return this.optimizeUrl(url, 800);
  }
}

export default new ImageService();
