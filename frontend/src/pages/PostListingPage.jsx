import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { Button } from '../components/ui/Button';
import { Upload, X } from 'lucide-react';
import { categories } from '../data/mockData';
import { useTheme } from '../contexts/ThemeContext';

const PostListingPage = () => {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: '',
    condition: '',
    location: ''
  });
  const [images, setImages] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Submit to Firebase
    console.log('Submitting:', formData, images);
    navigate('/seller');
  };

  const field = (key) => ({
    value: formData[key],
    onChange: (e) => setFormData({ ...formData, [key]: e.target.value })
  });

  return (
    <div className={`min-h-[100dvh] pb-20 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header hideSearch />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className={`font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-2 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`} data-testid="post-listing-title">
            Post New Listing
          </h1>
          <p className={`text-base mb-8 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Fill in the details to list your item</p>

          <form onSubmit={handleSubmit} className={`rounded-2xl border p-8 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            {/* Images */}
            <div className="mb-6">
              <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Product Images</label>
              <div className={`border-2 border-dashed rounded-xl p-8 text-center hover:border-blue-500 transition-colors cursor-pointer ${darkMode ? 'border-slate-600' : 'border-slate-200'}`}>
                <Upload className={`h-12 w-12 mx-auto mb-3 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Click to upload or drag and drop</p>
                <p className={`text-xs mt-1 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>PNG, JPG up to 10MB</p>
              </div>
            </div>

            {/* Title */}
            <div className="mb-6">
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Title</label>
              <input
                type="text"
                placeholder="e.g., MacBook Pro 14-inch M1"
                className={`w-full rounded-xl border px-4 py-3 outline-none transition-all ${
                  darkMode 
                    ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-blue-500'
                    : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                }`}
                required
                {...field('title')}
              />
            </div>

            {/* Description */}
            <div className="mb-6">
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Description</label>
              <textarea
                rows={4}
                placeholder="Describe your item..."
                className={`w-full rounded-xl border px-4 py-3 outline-none transition-all resize-none ${
                  darkMode 
                    ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-blue-500'
                    : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                }`}
                required
                {...field('description')}
              />
            </div>

            {/* Price & Category */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Price (₹)</label>
                <input
                  type="number"
                  placeholder="25000"
                  className={`w-full rounded-xl border px-4 py-3 outline-none transition-all ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-blue-500'
                      : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                  }`}
                  required
                  {...field('price')}
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Category</label>
                <select
                  className={`w-full rounded-xl border px-4 py-3 outline-none transition-all ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-slate-200 focus:border-blue-500'
                      : 'bg-white border-slate-200 text-slate-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                  }`}
                  required
                  {...field('category')}
                >
                  <option value="">Select category</option>
                  {categories.filter(c => c !== 'All').map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Condition & Location */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Condition</label>
                <select
                  className={`w-full rounded-xl border px-4 py-3 outline-none transition-all ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-slate-200 focus:border-blue-500'
                      : 'bg-white border-slate-200 text-slate-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                  }`}
                  required
                  {...field('condition')}
                >
                  <option value="">Select condition</option>
                  <option value="Like New">Like New</option>
                  <option value="Excellent">Excellent</option>
                  <option value="Good">Good</option>
                  <option value="Fair">Fair</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Location</label>
                <input
                  type="text"
                  placeholder="e.g., IIT Delhi"
                  className={`w-full rounded-xl border px-4 py-3 outline-none transition-all ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-blue-500'
                      : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                  }`}
                  required
                  {...field('location')}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/seller')}
                className={`flex-1 rounded-xl ${darkMode ? 'border-slate-600 hover:border-slate-500 hover:bg-slate-700' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
              >
                Post Listing
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PostListingPage;

