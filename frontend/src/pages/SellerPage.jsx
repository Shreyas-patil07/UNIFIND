import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { categories } from '../data/categories';
import { getProducts } from '../services/api';
import { Edit2, Trash2, CheckCircle2, Plus, Eye, Search, X, Clock, Trash2 as TrashIcon, ChevronDown, ArrowUpDown, SlidersHorizontal } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const SellerPage = () => {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const { currentUser } = useAuth();
  
  // State management
  const [myListings, setMyListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Load user's products
  useEffect(() => {
    const loadMyListings = async () => {
      if (!currentUser) return;

      try {
        const userProducts = await getProducts({ seller_id: currentUser.uid });
        setMyListings(Array.isArray(userProducts) ? userProducts : []);
        console.log('Seller products loaded:', Array.isArray(userProducts) ? userProducts.length : 0);
      } catch (error) {
        console.error('Failed to load listings:', error);
        console.error('Error details:', error.response?.data || error.message);
        setMyListings([]);
      } finally {
        setLoading(false);
      }
    };

    loadMyListings();
  }, [currentUser]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [condition, setCondition] = useState('all');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedMathsLevel, setSelectedMathsLevel] = useState('all');
  const [selectedMaterial, setSelectedMaterial] = useState('all');
  const [selectedGraphicsItem, setSelectedGraphicsItem] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [sortDropdownOpen, setSortDropdownOpen] = useState(false);
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteProductId, setDeleteProductId] = useState(null);

  const statusOptions = ['all', 'active', 'sold'];
  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'price-high', label: 'Price: High to Low' },
    { value: 'price-low', label: 'Price: Low to High' },
    { value: 'most-viewed', label: 'Most Viewed' }
  ];

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

  // Load search history on mount
  useEffect(() => {
    try {
      const history = JSON.parse(localStorage.getItem('unifind_seller_search_history') || '[]');
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

  // Handle search
  const handleSearch = (query) => {
    const historyArray = Array.isArray(searchHistory) ? searchHistory : [];
    if (query.trim() && !historyArray.includes(query.trim())) {
      const updated = [query.trim(), ...historyArray].slice(0, 10);
      setSearchHistory(updated);
      localStorage.setItem('unifind_seller_search_history', JSON.stringify(updated));
    }
  };

  // Clear search history
  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('unifind_seller_search_history');
  };

  // Handle edit
  const handleEdit = (productId) => {
    navigate(`/edit-listing/${productId}`);
  };

  // Handle delete
  const handleDelete = (productId) => {
    setDeleteProductId(productId);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    setMyListings((Array.isArray(myListings) ? myListings : []).filter(p => p.id !== deleteProductId));
    setShowDeleteModal(false);
    setDeleteProductId(null);
  };

  // Handle mark as sold
  const handleMarkAsSold = (productId) => {
    setMyListings((Array.isArray(myListings) ? myListings : []).map(p => 
      p.id === productId ? { ...p, status: p.status === 'sold' ? 'active' : 'sold' } : p
    ));
  };

  // Filter and sort listings
  const filteredAndSortedListings = useMemo(() => {
    let filtered = (Array.isArray(myListings) ? myListings : []).filter(product => {
      // Search filter
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          product.title.toLowerCase().includes(query) ||
          product.description.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }

      // Category filter
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

      // Condition filter
      if (condition !== 'all' && product.condition !== condition) return false;

      // Status filter
      if (selectedStatus !== 'all') {
        const productStatus = product.status || 'active';
        if (productStatus !== selectedStatus) return false;
      }

      return true;
    });

    // Sort
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
        case 'most-viewed':
          return b.views - a.views;
        default:
          return 0;
      }
    });
  }, [myListings, searchQuery, selectedCategory, selectedSubject, selectedMathsLevel, selectedMaterial, selectedGraphicsItem, condition, selectedStatus, sortBy]);

  const activeCount = (Array.isArray(myListings) ? myListings : []).filter(p => (p.status || 'active') === 'active').length;
  const soldCount = (Array.isArray(myListings) ? myListings : []).filter(p => p.status === 'sold').length;
  const totalRevenue = (Array.isArray(myListings) ? myListings : []).filter(p => p.status === 'sold').reduce((sum, p) => sum + p.price, 0);

  const activeFiltersCount = [
    selectedCategory !== 'All',
    selectedSubject !== 'all',
    selectedMathsLevel !== 'all',
    selectedMaterial !== 'all',
    selectedGraphicsItem !== 'all',
    condition !== 'all',
    selectedStatus !== 'all'
  ].filter(Boolean).length;

  const resetFilters = () => {
    setSelectedCategory('All');
    setSelectedSubject('all');
    setSelectedMathsLevel('all');
    setSelectedMaterial('all');
    setSelectedGraphicsItem('all');
    setCondition('all');
    setSelectedStatus('all');
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
      <Header hideSearch />
      
      <div className="px-4 sm:px-6 md:px-10 lg:px-20 py-8 with-bottom-nav">
        {/* Header */}
        <div className="flex items-center justify-between mb-7">
          <div>
            <h1 className={`font-['Outfit'] text-2xl sm:text-3xl font-black mb-1 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`} data-testid="seller-page-title">
              My Listings
            </h1>
            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Manage your campus products</p>
          </div>
          <button
            onClick={() => navigate('/post-listing')}
            className="btn-gradient flex items-center gap-2 px-5 py-2.5 text-sm"
            data-testid="post-new-listing-btn"
          >
            <Plus className="h-4 w-4" />
            New Listing
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-7">
          <div className={`rounded-2xl border p-4 text-center ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`} data-testid="seller-stat-active">
            <div className="text-xl sm:text-2xl font-black text-indigo-600 mb-0.5">{activeCount}</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Active</div>
          </div>
          <div className={`rounded-2xl border p-4 text-center ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`} data-testid="seller-stat-sold">
            <div className="text-xl sm:text-2xl font-black text-emerald-600 mb-0.5">{soldCount}</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Sold</div>
          </div>
          <div className={`rounded-2xl border p-4 text-center ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`} data-testid="seller-stat-revenue">
            <div className="text-xl sm:text-2xl font-black text-amber-600 mb-0.5">₹{(totalRevenue / 1000).toFixed(0)}k</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Revenue</div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className={`absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} />
            <input
              type="text"
              placeholder="Search your listings..."
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
          {Array.isArray(searchHistory) && searchHistory.length > 0 && !searchQuery && (
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

        {/* Filters */}
        <div className="mb-6">
          <div className="flex items-center gap-3 pb-2 relative">
            <div className="flex items-center gap-3 overflow-x-auto flex-1">
              {/* Combined Filters Button */}
              <div className="relative flex-shrink-0">
                <button
                  onClick={() => setFilterDrawerOpen(true)}
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
            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              <span className={`font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{filteredAndSortedListings.length}</span> listings
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
                      onClick={() => setSelectedCategory(cat)}
                      testId={`category-filter-${cat.toLowerCase()}`}
                    />
                  ))}
                </div>
              </div>

              {/* Status Section */}
              <div className="mb-6">
                <h4 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Status</h4>
                <div className="flex flex-wrap gap-2">
                  {statusOptions.map((status) => (
                    <FilterChip
                      key={status}
                      label={status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                      active={selectedStatus === status}
                      onClick={() => setSelectedStatus(status)}
                      testId={`status-filter-${status}`}
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
                      onClick={() => setCondition(val)}
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

        {/* Listings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {filteredAndSortedListings.map((product) => {
            const isSold = product.status === 'sold';
            return (
              <div
                key={product.id}
                className={`group rounded-2xl border overflow-hidden transition-all duration-300 hover:-translate-y-1 ${
                  isSold ? 'opacity-60' : ''
                } ${
                  darkMode 
                    ? 'bg-slate-800 border-slate-700 hover:border-indigo-500 hover:shadow-lg'
                    : 'bg-white border-slate-200 hover:border-indigo-400/40 hover:shadow-card-hover'
                }`}
                data-testid={`seller-listing-${product.id}`}
              >
                {/* Image */}
                <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
                  <img
                    src={product.images[0]}
                    alt={product.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  {/* Sold Badge */}
                  {isSold && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <span className="bg-emerald-500 text-white px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider">
                        Sold
                      </span>
                    </div>
                  )}
                  {/* Views Badge */}
                  <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center gap-1">
                    <Eye className="h-3 w-3 text-white" />
                    <span className="text-xs text-white font-medium">{product.views}</span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className={`text-lg font-bold mb-2 line-clamp-1 ${darkMode ? 'text-slate-200' : 'text-slate-900'}`} data-testid="seller-listing-title">
                    {product.title}
                  </h3>
                  <div className="text-2xl font-black text-indigo-600 mb-3" data-testid="seller-listing-price">
                    ₹{product.price.toLocaleString()}
                  </div>

                  {/* Condition & Location */}
                  <div className={`flex items-center gap-2 mb-5 pb-5 border-b ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
                    <span className="bg-green-100 text-green-700 px-2 py-1 rounded-lg text-xs font-semibold">
                      {product.condition}
                    </span>
                    <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{product.location}</span>
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => handleEdit(product.id)}
                      className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                        darkMode 
                          ? 'border-slate-700 hover:border-indigo-500 hover:bg-indigo-900/30 hover:text-indigo-400 text-slate-400'
                          : 'border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600'
                      }`}
                      data-testid="seller-listing-edit-btn"
                      title="Edit Listing"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(product.id)}
                      className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                        darkMode 
                          ? 'border-slate-700 hover:border-red-500 hover:bg-red-900/30 hover:text-red-400 text-slate-400'
                          : 'border-slate-200 hover:border-red-400 hover:bg-red-50 hover:text-red-600 text-slate-600'
                      }`}
                      data-testid="seller-listing-delete-btn"
                      title="Delete Listing"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleMarkAsSold(product.id)}
                      className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                        isSold
                          ? darkMode
                            ? 'border-emerald-500 bg-emerald-900/30 text-emerald-400'
                            : 'border-emerald-400 bg-emerald-50 text-emerald-700'
                          : darkMode 
                            ? 'border-slate-700 hover:border-emerald-500 hover:bg-emerald-900/30 hover:text-emerald-400 text-slate-400'
                            : 'border-slate-200 hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600'
                      }`}
                      data-testid="seller-listing-sold-btn"
                      title={isSold ? "Mark as Active" : "Mark as Sold"}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <>
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 animate-fade-in" onClick={() => setShowDeleteModal(false)} />
            <div className={`fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md p-6 rounded-2xl shadow-2xl animate-scale-in ${
              darkMode ? 'bg-slate-800' : 'bg-white'
            }`}>
              <div className="text-center">
                <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
                  <TrashIcon className="h-6 w-6 text-red-600" />
                </div>
                <h3 className={`text-lg font-bold mb-2 ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
                  Delete Listing?
                </h3>
                <p className={`text-sm mb-6 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  This action cannot be undone. The listing will be permanently removed.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowDeleteModal(false)}
                    className={`flex-1 py-2.5 rounded-xl font-semibold text-sm transition-colors ${
                      darkMode 
                        ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmDelete}
                    className="flex-1 py-2.5 rounded-xl font-semibold text-sm bg-red-600 text-white hover:bg-red-700 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

        {filteredAndSortedListings.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📦</div>
            <p className={`text-lg font-semibold mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>No listings found</p>
            <p className={`text-sm mb-6 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
              {myListings.length === 0 ? 'Post your first item to start selling' : 'Try adjusting your filters'}
            </p>
            {myListings.length === 0 ? (
              <button
                onClick={() => navigate('/post-listing')}
                className="btn-gradient px-6 py-2.5 text-sm inline-flex items-center gap-2"
                data-testid="empty-post-listing-btn"
              >
                <Plus className="h-4 w-4" />
                Post First Listing
              </button>
            ) : (
              <button onClick={resetFilters} className="btn-gradient px-6 py-2.5 text-sm">
                Reset Filters
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerPage;
