import React, { useState, useMemo, useEffect } from 'react';
import Header from '../components/Header';
import ProductCard from '../components/ProductCard';
import { ProductCardSkeleton } from '../components/SkeletonLoader';
import { products, categories } from '../data/mockData';
import { SlidersHorizontal, X, ChevronDown, Search, ArrowUpDown, Clock, Trash2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { getRecentlyViewed, addToRecentlyViewed, clearRecentlyViewed } from '../utils/recentlyViewed';

const BuyerPage = () => {
  const { darkMode } = useTheme();
  const [loading, setLoading] = useState(false);
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
    setRecentlyViewed(getRecentlyViewed());
    const history = JSON.parse(localStorage.getItem('unifind_search_history') || '[]');
    setSearchHistory(history);
  }, []);

  // Handle product view
  const handleProductView = (product) => {
    addToRecentlyViewed(product);
    setRecentlyViewed(getRecentlyViewed());
  };

  // Handle search submission
  const handleSearch = (query) => {
    if (query.trim() && !searchHistory.includes(query.trim())) {
      const updated = [query.trim(), ...searchHistory].slice(0, 10);
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
    const filtered = products.filter(product => {
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
      
      if (condition !== 'all' && product.condition !== condition) return false;
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
    condition !== 'all',
    searchQuery.trim() !== ''
  ].filter(Boolean).length;

  const resetFilters = () => {
    setSelectedCategory('All');
    setSelectedSubject('all');
    setSelectedMathsLevel('all');
    setSelectedMaterial('all');
    setSelectedGraphicsItem('all');
    setCondition('all');
    setSearchQuery('');
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
    <div className={`min-h-[100dvh] pb-20 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header />

      <div className="px-4 sm:px-6 md:px-10 lg:px-20 py-6 with-bottom-nav">

        {/* ===== HERO BANNER ===== */}
        <div className="relative bg-gradient-hero rounded-2xl sm:rounded-3xl overflow-hidden mb-8 p-6 sm:p-10">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-1/3 w-48 h-48 bg-violet-500/15 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10">
            <span className="inline-flex items-center gap-1.5 bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-3">
              🛍️ Marketplace
            </span>
            <h1
              className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-black text-white mb-2"
              data-testid="buyer-page-title"
            >
              Discover Amazing Deals
            </h1>
            <p className="text-slate-400 text-sm sm:text-base max-w-md">
              Browse verified listings from SIGCE students. Safe, trusted campus commerce.
            </p>
          </div>
        </div>

        {/* ===== SEARCH BAR ===== */}
        <div className="mb-6">
          <div className="relative">
            <Search className={`absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} />
            <input
              type="text"
              placeholder="Search by title, description, or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch(searchQuery);
                }
              }}
              className={`w-full pl-12 pr-4 py-3.5 rounded-xl text-sm font-medium border transition-all duration-200 ${
                darkMode 
                  ? 'bg-slate-800 border-slate-700 text-slate-200 placeholder-slate-500 focus:border-indigo-500'
                  : 'bg-white border-slate-200 text-slate-700 placeholder-slate-400 focus:border-indigo-300'
              } focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className={`absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-lg transition-colors ${
                  darkMode ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-500'
                }`}
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Search History */}
          {searchHistory.length > 0 && !searchQuery && (
            <div className={`mt-3 p-3 rounded-xl border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock className={`h-4 w-4 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} />
                  <span className={`text-xs font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Recent Searches</span>
                </div>
                <button
                  onClick={clearSearchHistory}
                  className={`text-xs font-medium ${darkMode ? 'text-slate-400 hover:text-red-400' : 'text-slate-500 hover:text-red-600'} transition-colors`}
                >
                  Clear
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {searchHistory.slice(0, 5).map((term, index) => (
                  <button
                    key={index}
                    onClick={() => setSearchQuery(term)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      darkMode 
                        ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
                    }`}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ===== RECENTLY VIEWED ===== */}
        {recentlyViewed.length > 0 && (
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

        {/* ===== CATEGORY CHIPS (horizontal scroll on mobile) ===== */}
        <div className="mb-5">
          <div className={`text-xs font-bold uppercase tracking-wider mb-2.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Category</div>
          <div className="chips-row">
            {categories.map((cat) => (
              <FilterChip
                key={cat}
                label={cat}
                active={selectedCategory === cat}
                onClick={() => {
                  setSelectedCategory(cat);
                  if (cat !== 'Printed Notes') {
                    setSelectedSubject('all');
                    setSelectedMathsLevel('all');
                  }
                  if (cat !== 'Materials') {
                    setSelectedMaterial('all');
                    setSelectedGraphicsItem('all');
                  }
                }}
                testId={`category-filter-${cat.toLowerCase()}`}
              />
            ))}
          </div>
        </div>

        {/* ===== SUBJECT DROPDOWN (only visible when Printed Notes is selected) ===== */}
        {selectedCategory === 'Printed Notes' && (
          <div className="mb-5">
            <div className={`text-xs font-bold uppercase tracking-wider mb-2.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Subject</div>
            <div className="relative inline-block w-full sm:w-64">
              <button
                onClick={() => setSubjectDropdownOpen(!subjectDropdownOpen)}
                className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium border transition-all duration-200 ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 text-slate-200 hover:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                } ${selectedSubject !== 'all' ? 'ring-2 ring-indigo-500/50' : ''}`}
              >
                <span>{selectedSubject === 'all' ? 'All Subjects' : selectedSubject}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${subjectDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {subjectDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setSubjectDropdownOpen(false)}
                  />
                  <div className={`absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-xl z-20 max-h-80 overflow-y-auto ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700' 
                      : 'bg-white border-slate-200'
                  }`}>
                    {subjects.map((subject) => (
                      <button
                        key={subject}
                        onClick={() => {
                          setSelectedSubject(subject === 'All Subjects' ? 'all' : subject);
                          if (subject !== 'Maths') {
                            setSelectedMathsLevel('all');
                          }
                          setSubjectDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                          (selectedSubject === 'all' && subject === 'All Subjects') || selectedSubject === subject
                            ? darkMode
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-600'
                            : darkMode
                              ? 'text-slate-300 hover:bg-slate-700'
                              : 'text-slate-700 hover:bg-slate-50'
                        } ${subject === subjects[0] ? 'rounded-t-xl' : ''} ${subject === subjects[subjects.length - 1] ? 'rounded-b-xl' : ''}`}
                      >
                        {subject}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ===== MATHS LEVEL DROPDOWN (only visible when Maths is selected) ===== */}
        {selectedCategory === 'Printed Notes' && selectedSubject === 'Maths' && (
          <div className="mb-5">
            <div className={`text-xs font-bold uppercase tracking-wider mb-2.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Maths Level</div>
            <div className="relative inline-block w-full sm:w-64">
              <button
                onClick={() => setMathsDropdownOpen(!mathsDropdownOpen)}
                className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium border transition-all duration-200 ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 text-slate-200 hover:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                } ${selectedMathsLevel !== 'all' ? 'ring-2 ring-indigo-500/50' : ''}`}
              >
                <span>{selectedMathsLevel === 'all' ? 'All Maths' : selectedMathsLevel}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${mathsDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {mathsDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setMathsDropdownOpen(false)}
                  />
                  <div className={`absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-xl z-20 max-h-80 overflow-y-auto ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700' 
                      : 'bg-white border-slate-200'
                  }`}>
                    {mathsLevels.map((level) => (
                      <button
                        key={level}
                        onClick={() => {
                          setSelectedMathsLevel(level === 'All Maths' ? 'all' : level);
                          setMathsDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                          (selectedMathsLevel === 'all' && level === 'All Maths') || selectedMathsLevel === level
                            ? darkMode
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-600'
                            : darkMode
                              ? 'text-slate-300 hover:bg-slate-700'
                              : 'text-slate-700 hover:bg-slate-50'
                        } ${level === mathsLevels[0] ? 'rounded-t-xl' : ''} ${level === mathsLevels[mathsLevels.length - 1] ? 'rounded-b-xl' : ''}`}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ===== MATERIAL TYPE DROPDOWN (only visible when Materials is selected) ===== */}
        {selectedCategory === 'Materials' && (
          <div className="mb-5">
            <div className={`text-xs font-bold uppercase tracking-wider mb-2.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Material Type</div>
            <div className="relative inline-block w-full sm:w-64">
              <button
                onClick={() => setMaterialDropdownOpen(!materialDropdownOpen)}
                className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium border transition-all duration-200 ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 text-slate-200 hover:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                } ${selectedMaterial !== 'all' ? 'ring-2 ring-indigo-500/50' : ''}`}
              >
                <span>{selectedMaterial === 'all' ? 'All Materials' : selectedMaterial}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${materialDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {materialDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setMaterialDropdownOpen(false)}
                  />
                  <div className={`absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-xl z-20 max-h-80 overflow-y-auto ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700' 
                      : 'bg-white border-slate-200'
                  }`}>
                    {materials.map((material) => (
                      <button
                        key={material}
                        onClick={() => {
                          setSelectedMaterial(material === 'All Materials' ? 'all' : material);
                          if (material !== 'Graphics Kit') {
                            setSelectedGraphicsItem('all');
                          }
                          setMaterialDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                          (selectedMaterial === 'all' && material === 'All Materials') || selectedMaterial === material
                            ? darkMode
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-600'
                            : darkMode
                              ? 'text-slate-300 hover:bg-slate-700'
                              : 'text-slate-700 hover:bg-slate-50'
                        } ${material === materials[0] ? 'rounded-t-xl' : ''} ${material === materials[materials.length - 1] ? 'rounded-b-xl' : ''}`}
                      >
                        {material}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ===== GRAPHICS KIT ITEMS DROPDOWN (only visible when Graphics Kit is selected) ===== */}
        {selectedCategory === 'Materials' && selectedMaterial === 'Graphics Kit' && (
          <div className="mb-5">
            <div className={`text-xs font-bold uppercase tracking-wider mb-2.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Graphics Kit Items</div>
            <div className="relative inline-block w-full sm:w-64">
              <button
                onClick={() => setGraphicsDropdownOpen(!graphicsDropdownOpen)}
                className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium border transition-all duration-200 ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 text-slate-200 hover:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                } ${selectedGraphicsItem !== 'all' ? 'ring-2 ring-indigo-500/50' : ''}`}
              >
                <span>{selectedGraphicsItem === 'all' ? 'All Graphics Items' : selectedGraphicsItem}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${graphicsDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {graphicsDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setGraphicsDropdownOpen(false)}
                  />
                  <div className={`absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-xl z-20 max-h-80 overflow-y-auto ${
                    darkMode 
                      ? 'bg-slate-800 border-slate-700' 
                      : 'bg-white border-slate-200'
                  }`}>
                    {graphicsKitItems.map((item) => (
                      <button
                        key={item}
                        onClick={() => {
                          setSelectedGraphicsItem(item === 'All Graphics Items' ? 'all' : item);
                          setGraphicsDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                          (selectedGraphicsItem === 'all' && item === 'All Graphics Items') || selectedGraphicsItem === item
                            ? darkMode
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-600'
                            : darkMode
                              ? 'text-slate-300 hover:bg-slate-700'
                              : 'text-slate-700 hover:bg-slate-50'
                        } ${item === graphicsKitItems[0] ? 'rounded-t-xl' : ''} ${item === graphicsKitItems[graphicsKitItems.length - 1] ? 'rounded-b-xl' : ''}`}
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ===== FILTER BAR ===== */}
        <div className="flex items-center justify-end gap-3 mb-6">
          {/* Filter button (mobile) + Reset */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {activeFiltersCount > 0 && (
              <button
                onClick={resetFilters}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-red-600 bg-red-50 border border-red-200 hover:bg-red-100 transition-colors"
              >
                <X className="h-3 w-3" />
                Reset
              </button>
            )}
            <button
              onClick={() => setFilterDrawerOpen(true)}
              className={`relative flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-semibold border transition-colors shadow-sm ${
                darkMode 
                  ? 'bg-slate-800 border-slate-700 text-slate-300 hover:border-indigo-500'
                  : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
              }`}
            >
              <SlidersHorizontal className="h-4 w-4" />
              <span className="hidden sm:inline">Condition</span>
              {condition !== 'all' && (
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-indigo-600 text-white text-[9px] font-bold rounded-full flex items-center justify-center">1</span>
              )}
            </button>
          </div>
        </div>

        {/* ===== CONDITION FILTER DRAWER ===== */}
        {filterDrawerOpen && (
          <>
            <div
              className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 animate-fade-in"
              onClick={() => setFilterDrawerOpen(false)}
            />
            <div className={`fixed bottom-0 left-0 right-0 z-50 rounded-t-3xl p-6 shadow-2xl animate-slide-in-up md:static md:rounded-2xl md:bg-transparent md:shadow-none md:p-0 md:animate-none ${darkMode ? 'bg-slate-800' : 'bg-white'}`}>
              <div className="flex items-center justify-between mb-5">
                <h3 className={`text-base font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>Condition</h3>
                <button onClick={() => setFilterDrawerOpen(false)} className={`p-1.5 rounded-lg ${darkMode ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2 mb-6">
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
                    onClick={() => { setCondition(val); setFilterDrawerOpen(false); }}
                    testId={testId}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {/* ===== RESULTS COUNT & SORT ===== */}
        <div className="flex items-center justify-between mb-5 gap-3">
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} data-testid="results-count">
            <span className={`font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{sortedProducts.length}</span> results
            {selectedCategory !== 'All' && (
              <span className="ml-1">in <span className="font-semibold text-indigo-600">{selectedCategory}</span></span>
            )}
          </p>
          
          {/* Sort Dropdown */}
          <div className="relative">
            <button
              onClick={() => setSortDropdownOpen(!sortDropdownOpen)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium border transition-all duration-200 ${
                darkMode 
                  ? 'bg-slate-800 border-slate-700 text-slate-200 hover:border-indigo-500'
                  : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
              }`}
            >
              <ArrowUpDown className="h-4 w-4" />
              <span className="hidden sm:inline">Sort</span>
              <ChevronDown className={`h-3.5 w-3.5 transition-transform duration-200 ${sortDropdownOpen ? 'rotate-180' : ''}`} />
            </button>
            
            {sortDropdownOpen && (
              <>
                <div 
                  className="fixed inset-0 z-10" 
                  onClick={() => setSortDropdownOpen(false)}
                />
                <div className={`absolute top-full right-0 mt-2 w-56 rounded-xl border shadow-xl z-20 ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700' 
                    : 'bg-white border-slate-200'
                }`}>
                  {sortOptions.map((option, index) => (
                    <button
                      key={option.value}
                      onClick={() => {
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

