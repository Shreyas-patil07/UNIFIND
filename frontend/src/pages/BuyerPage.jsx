import React, { useState, useMemo, useEffect } from 'react';
import Header from '../components/Header';
import ProductCard from '../components/ProductCard';
import { ProductCardSkeleton } from '../components/SkeletonLoader';
import { categories } from '../data/categories';
import { getProducts } from '../services/api';
import { SlidersHorizontal, X, ChevronDown, Search, ArrowUpDown, Clock, Trash2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { getRecentlyViewed, addToRecentlyViewed, clearRecentlyViewed } from '../utils/recentlyViewed';

const BuyerPage = () => {
  const { darkMode } = useTheme();
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedMathsLevel, setSelectedMathsLevel] = useState('all');
  const [selectedMaterial, setSelectedMaterial] = useState('all');
  const [selectedGraphicsItem, setSelectedGraphicsItem] = useState('all');
  const [condition, setCondition] = useState('all');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [subjectDropdownOpen, setSubjectDropdownOpen] = useState(false);
  const [mathsDropdownOpen, setMathsDropdownOpen] = useState(false);
  const [materialDropdownOpen, setMaterialDropdownOpen] = useState(false);
  const [graphicsDropdownOpen, setGraphicsDropdownOpen] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  const [sortDropdownOpen, setSortDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  const subjects = [
    'All Subjects',
    'Maths',
    'Mechanics',
    'BEEE',
    'Physics',
    'Chemistry',
    'DBMS',
    'AOA',
    'DSA',
    'OS',
    'CT',
    'DSGT'
  ];

  const mathsLevels = [
    'All Maths',
    'Maths-1',
    'Maths-2',
    'Maths-3',
    'Maths-4'
  ];

  const materials = [
    'All Materials',
    'Laptop',
    'Lab Coat',
    'Scientific Calculator',
    'Graphics Kit'
  ];

  const graphicsKitItems = [
    'All Graphics Items',
    'Graphics Drawing Kit',
    'Drawing Board',
    'T-square or Mini Drafter',
    'Set Squares',
    'Instrument Box',
    'Pencils and Leads',
    'Scales',
    'Protractors',
    'French Curves',
    'Stencils',
    'Ruling Pens'
  ];

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'price-low', label: 'Price: Low to High' },
    { value: 'price-high', label: 'Price: High to Low' },
    { value: 'condition-best', label: 'Condition: Best First' },
    { value: 'most-viewed', label: 'Most Viewed' }
  ];

  // Load recently viewed and search history on mount
  useEffect(() => {
    const viewed = getRecentlyViewed();
    setRecentlyViewed(Array.isArray(viewed) ? viewed : []);
    try {
      const history = JSON.parse(localStorage.getItem('unifind_search_history') || '[]');
      setSearchHistory(Array.isArray(history) ? history : []);
    } catch (e) {
      setSearchHistory([]);
    }
  }, []);

  // Close sort dropdown when filter drawer opens
  useEffect(() => {
    if (filterDrawerOpen) {
      setSortDropdownOpen(false);
    }
  }, [filterDrawerOpen]);

  // Close filter drawer when sort dropdown opens
  useEffect(() => {
    if (sortDropdownOpen) {
      setFilterDrawerOpen(false);
    }
  }, [sortDropdownOpen]);

  // Load products from API
  useEffect(() => {
    const loadProducts = async () => {
      try {
        setLoading(true);
        const fetchedProducts = await getProducts({
          category: selectedCategory !== 'All' ? selectedCategory : undefined
        });
        setProducts(Array.isArray(fetchedProducts) ? fetchedProducts : []);
        console.log('Products loaded:', Array.isArray(fetchedProducts) ? fetchedProducts.length : 0);
      } catch (error) {
        console.error('Failed to load products:', error);
        console.error('Error details:', error.response?.data || error.message);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [selectedCategory]);

  // Debug: Log condition changes
  useEffect(() => {
    console.log('Condition filter changed to:', condition);
  }, [condition]);

  // Handle product view
  const handleProductView = (product) => {
    addToRecentlyViewed(product);
    setRecentlyViewed(getRecentlyViewed());
  };

  // Handle search submission
  const handleSearch = (query) => {
    const historyArray = Array.isArray(searchHistory) ? searchHistory : [];
    if (query.trim() && !historyArray.includes(query.trim())) {
      const updated = [query.trim(), ...historyArray].slice(0, 10);
      setSearchHistory(updated);
      localStorage.setItem('unifind_search_history', JSON.stringify(updated));
    }
  };

  // Clear search history
  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('unifind_search_history');
  };

  // Clear recently viewed
  const handleClearRecentlyViewed = () => {
    clearRecentlyViewed();
    setRecentlyViewed([]);
  };

  // Memoize filtered and sorted products for better performance
  const sortedProducts = useMemo(() => {
    const filtered = (Array.isArray(products) ? products : []).filter(product => {
      // Search filter
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          product.title.toLowerCase().includes(query) ||
          product.description.toLowerCase().includes(query) ||
          product.location.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }

      if (selectedCategory !== 'All' && product.category !== selectedCategory) return false;
      
      // Printed Notes filtering
      if (selectedCategory === 'Printed Notes') {
        if (selectedSubject !== 'all' && selectedSubject !== 'Maths' && product.subject !== selectedSubject) return false;
        if (selectedSubject === 'Maths' && selectedMathsLevel !== 'all' && product.subject !== selectedMathsLevel) return false;
        if (selectedSubject === 'Maths' && selectedMathsLevel === 'all' && !['Maths-1', 'Maths-2', 'Maths-3', 'Maths-4'].includes(product.subject)) return false;
      }
      
      // Materials filtering
      if (selectedCategory === 'Materials') {
        if (selectedMaterial !== 'all' && selectedMaterial !== 'Graphics Kit' && product.materialType !== selectedMaterial) return false;
        if (selectedMaterial === 'Graphics Kit' && selectedGraphicsItem !== 'all' && product.materialType !== selectedGraphicsItem) return false;
        if (selectedMaterial === 'Graphics Kit' && selectedGraphicsItem === 'all') {
          const graphicsItems = ['Graphics Drawing Kit', 'Drawing Board', 'T-square or Mini Drafter', 'Set Squares', 'Instrument Box', 'Pencils and Leads', 'Scales', 'Protractors', 'French Curves', 'Stencils', 'Ruling Pens'];
          if (!graphicsItems.includes(product.materialType)) return false;
        }
      }
      
      if (condition !== 'all' && product.condition !== condition) {
        console.log(`Filtering out product: ${product.title}, condition: ${product.condition}, filter: ${condition}`);
        return false;
      }
      return true;
    });

    // Sort filtered products
    return [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.postedDate) - new Date(a.postedDate);
        case 'oldest':
          return new Date(a.postedDate) - new Date(b.postedDate);
        case 'price-low':
          return a.price - b.price;
        case 'price-high':
          return b.price - a.price;
        case 'condition-best':
          return b.conditionScore - a.conditionScore;
        case 'most-viewed':
          return b.views - a.views;
        default:
          return 0;
      }
    });
  }, [products, searchQuery, selectedCategory, selectedSubject, selectedMathsLevel, selectedMaterial, selectedGraphicsItem, condition, sortBy]);

  const activeFiltersCount = [
    selectedCategory !== 'All',
    selectedSubject !== 'all',
    selectedMathsLevel !== 'all',
    selectedMaterial !== 'all',
    selectedGraphicsItem !== 'all',
    condition !== 'all'
  ].filter(Boolean).length;

  const resetFilters = () => {
    setSelectedCategory('All');
    setSelectedSubject('all');
    setSelectedMathsLevel('all');
    setSelectedMaterial('all');
    setSelectedGraphicsItem('all');
    setCondition('all');
    setSortBy('newest');
  };

  const FilterChip = ({ label, active, onClick, testId }) => (
    <button
      onClick={onClick}
      className={`flex-shrink-0 px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
        active
          ? 'bg-indigo-600 text-white shadow-glow-indigo'
          : darkMode 
            ? 'bg-slate-800 text-slate-300 border border-slate-700 hover:border-indigo-500 hover:text-indigo-400'
            : 'bg-white text-slate-700 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600'
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  );

  return (
    <div className={`min-h-[100dvh] pb-[calc(64px+env(safe-area-inset-bottom))] ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header />

      {/* Sticky Search Bar */}
      <div className={`sticky top-16 sm:top-[72px] z-40 ${
        darkMode ? 'bg-slate-900' : 'bg-slate-50'
      }`}>
        <div className="px-3 sm:px-6 md:px-10 lg:px-20 pt-3 pb-3">
          <div className="relative">
            <Search className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 ${darkMode ? 'text-indigo-400' : 'text-indigo-500'}`} />
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch(searchQuery);
                }
              }}
              className={`w-full pl-10 sm:pl-12 pr-10 sm:pr-12 py-2.5 sm:py-3 rounded-lg sm:rounded-xl text-sm font-medium border transition-all duration-200 ${
                darkMode 
                  ? 'bg-slate-800 border-slate-700 text-slate-200 placeholder-slate-400 focus:border-indigo-500'
                  : 'bg-white border-slate-200 text-slate-700 placeholder-slate-400 focus:border-indigo-400'
              } focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className={`absolute right-3 top-1/2 -translate-y-1/2 p-1 sm:p-1.5 rounded-lg transition-all active:scale-95 ${
                  darkMode ? 'hover:bg-slate-700 text-slate-400 hover:text-slate-200' : 'hover:bg-slate-100 text-slate-500 hover:text-slate-700'
                }`}
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="px-3 sm:px-6 md:px-10 lg:px-20 with-bottom-nav">

        {/* ===== RECENTLY VIEWED ===== */}
        {Array.isArray(recentlyViewed) && recentlyViewed.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className={`text-sm font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
                Recently Viewed
              </h2>
              <button
                onClick={handleClearRecentlyViewed}
                className={`flex items-center gap-1 text-xs font-medium ${darkMode ? 'text-slate-400 hover:text-red-400' : 'text-slate-500 hover:text-red-600'} transition-colors`}
              >
                <Trash2 className="h-3.5 w-3.5" />
                Clear
              </button>
            </div>
            <div className="overflow-x-auto pb-2">
              <div className="flex gap-3" style={{ minWidth: 'min-content' }}>
                {recentlyViewed.slice(0, 6).map((product) => (
                  <div key={product.id} className="w-40 flex-shrink-0">
                    <ProductCard product={product} onView={handleProductView} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== FILTERS BAR (Filters & Sort) ===== */}
        <div className="mb-6">
          <div className="flex items-center gap-3 pb-2 relative">
            <div className="flex items-center gap-3 overflow-x-auto flex-1">
              {/* Combined Filters Button */}
              <div className="relative flex-shrink-0">
                <button
                  onClick={() => {
                    console.log('Filters button clicked');
                    setFilterDrawerOpen(true);
                  }}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors shadow-sm ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700 text-slate-300 hover:border-indigo-500'
                      : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                  } ${activeFiltersCount > 0 ? 'ring-2 ring-indigo-500/50 border-indigo-500' : ''}`}
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  <span>Filters</span>
                  {activeFiltersCount > 0 && (
                    <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                      {activeFiltersCount}
                    </span>
                  )}
                </button>
              </div>

              {/* Reset Button */}
              {activeFiltersCount > 0 && (
                <button
                  onClick={resetFilters}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors shadow-sm flex-shrink-0 ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700 text-slate-300 hover:border-red-500 hover:text-red-400'
                      : 'bg-white border-slate-200 text-slate-700 hover:border-red-300 hover:text-red-600'
                  }`}
                >
                  <X className="h-4 w-4" />
                  <span className="hidden sm:inline">Reset</span>
                </button>
              )}
            </div>

            {/* Sort Dropdown - Outside overflow container */}
            <div className="relative flex-shrink-0 ml-auto">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Sort button clicked, current state:', sortDropdownOpen);
                  setSortDropdownOpen(!sortDropdownOpen);
                }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors shadow-sm ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 text-slate-300 hover:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                }`}
              >
                <ArrowUpDown className="h-4 w-4" />
                <span className="hidden sm:inline">{sortOptions.find(opt => opt.value === sortBy)?.label || 'Sort'}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${sortDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Sort Popup */}
              {sortDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-[60]" 
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log('Sort backdrop clicked');
                      setSortDropdownOpen(false);
                    }}
                  />
                  <div className={`absolute top-full right-0 mt-2 rounded-xl border shadow-xl z-[61] min-w-[200px] ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700' 
                      : 'bg-white border-slate-200'
                  }`}>
                    {sortOptions.map((option, index) => (
                      <button
                        key={option.value}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSortBy(option.value);
                          setSortDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                          sortBy === option.value
                            ? darkMode
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-600'
                            : darkMode
                              ? 'text-slate-300 hover:bg-slate-700'
                              : 'text-slate-700 hover:bg-slate-50'
                        } ${index === 0 ? 'rounded-t-xl' : ''} ${index === sortOptions.length - 1 ? 'rounded-b-xl' : ''}`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4">
            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} data-testid="results-count">
              <span className={`font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{sortedProducts.length}</span> results
              {selectedCategory !== 'All' && (
                <span className="ml-1">in <span className="font-semibold text-indigo-600">{selectedCategory}</span></span>
              )}
            </p>
          </div>
        </div>

        {/* ===== UNIFIED FILTER DRAWER ===== */}
        {filterDrawerOpen && (
          <>
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] animate-fade-in"
              onClick={() => setFilterDrawerOpen(false)}
            />
            <div className={`fixed bottom-0 left-0 right-0 z-[61] rounded-t-3xl p-6 shadow-2xl animate-slide-in-up max-h-[80vh] overflow-y-auto ${darkMode ? 'bg-slate-800 border-t-2 border-slate-700' : 'bg-white border-t-2 border-slate-200'}`}>
              <div className="flex items-center justify-between mb-6">
                <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>Filters</h3>
                <button 
                  onClick={() => setFilterDrawerOpen(false)} 
                  className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-700 text-slate-300' : 'hover:bg-slate-100 text-slate-600'}`}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Category Section */}
              <div className="mb-6">
                <h4 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Category</h4>
                <div className="flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <FilterChip
                      key={cat}
                      label={cat}
                      active={selectedCategory === cat}
                      onClick={() => {
                        console.log('Category selected:', cat);
                        setSelectedCategory(cat);
                      }}
                      testId={`category-filter-${cat.toLowerCase()}`}
                    />
                  ))}
                </div>
              </div>

              {/* Condition Section */}
              <div className="mb-6">
                <h4 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Condition</h4>
                <div className="flex flex-wrap gap-2">
                  {[
                    { label: 'All Conditions', val: 'all', testId: 'condition-filter-all' },
                    { label: 'Like New', val: 'Like New', testId: 'condition-filter-like-new' },
                    { label: 'Excellent', val: 'Excellent', testId: 'condition-filter-excellent' },
                    { label: 'Good', val: 'Good', testId: 'condition-filter-good' },
                    { label: 'Fair', val: 'Fair', testId: 'condition-filter-fair' },
                  ].map(({ label, val, testId }) => (
                    <FilterChip
                      key={val}
                      label={label}
                      active={condition === val}
                      onClick={() => { 
                        console.log('Condition selected:', val);
                        setCondition(val); 
                      }}
                      testId={testId}
                    />
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                <button
                  onClick={() => {
                    resetFilters();
                    setFilterDrawerOpen(false);
                  }}
                  className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-colors ${
                    darkMode 
                      ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' 
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  Reset
                </button>
                <button
                  onClick={() => setFilterDrawerOpen(false)}
                  className="flex-1 bg-indigo-600 text-white px-4 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </>
        )}

        {/* ===== PRODUCTS GRID ===== */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-5">
          {loading ? (
            Array.from({ length: 8 }).map((_, i) => <ProductCardSkeleton key={i} />)
          ) : (
            sortedProducts.map((product) => (
              <ProductCard key={product.id} product={product} onView={handleProductView} />
            ))
          )}
        </div>

        {/* Empty state */}
        {sortedProducts.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <p className={`text-lg font-semibold mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`} data-testid="no-results-message">
              No products found
            </p>
            <p className={`text-sm mb-6 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Try adjusting your filters</p>
            <button onClick={resetFilters} className="btn-gradient px-6 py-2.5 text-sm">
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuyerPage;
