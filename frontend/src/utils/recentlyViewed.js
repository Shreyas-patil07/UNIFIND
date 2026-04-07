// Utility functions for managing recently viewed products

const RECENTLY_VIEWED_KEY = 'unifind_recently_viewed';
const MAX_RECENT_ITEMS = 10;

export const addToRecentlyViewed = (product) => {
  try {
    const existing = getRecentlyViewed();
    
    // Remove if already exists to avoid duplicates
    const filtered = existing.filter(item => item.id !== product.id);
    
    // Add to beginning
    const updated = [product, ...filtered].slice(0, MAX_RECENT_ITEMS);
    
    localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Error saving to recently viewed:', error);
  }
};

export const getRecentlyViewed = () => {
  try {
    const stored = localStorage.getItem(RECENTLY_VIEWED_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error reading recently viewed:', error);
    return [];
  }
};

export const clearRecentlyViewed = () => {
  try {
    localStorage.removeItem(RECENTLY_VIEWED_KEY);
  } catch (error) {
    console.error('Error clearing recently viewed:', error);
  }
};
