import React, { useState } from 'react';
import Header from '../components/Header';
import ProductCard from '../components/ProductCard';
import { ProductCardSkeleton } from '../components/SkeletonLoader';
import { products, categories } from '../data/mockData';
import { SlidersHorizontal, X } from 'lucide-react';

const BuyerPage = () => {
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [priceRange, setPriceRange] = useState('all');
  const [condition, setCondition] = useState('all');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);

  const filteredProducts = products.filter(product => {
    if (selectedCategory !== 'All' && product.category !== selectedCategory) return false;
    if (priceRange === 'under-20k' && product.price >= 20000) return false;
    if (priceRange === '20k-50k' && (product.price < 20000 || product.price >= 50000)) return false;
    if (priceRange === 'above-50k' && product.price < 50000) return false;
    if (condition !== 'all' && product.condition !== condition) return false;
    return true;
  });

  const activeFiltersCount = [
    selectedCategory !== 'All',
    priceRange !== 'all',
    condition !== 'all',
  ].filter(Boolean).length;

  const resetFilters = () => {
    setSelectedCategory('All');
    setPriceRange('all');
    setCondition('all');
  };

  const FilterChip = ({ label, active, onClick, testId }) => (
    <button
      onClick={onClick}
      className={`flex-shrink-0 px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
        active
          ? 'bg-indigo-600 text-white shadow-glow-indigo'
          : 'bg-white text-slate-700 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600'
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-slate-50">
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

        {/* ===== CATEGORY CHIPS (horizontal scroll on mobile) ===== */}
        <div className="mb-5">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2.5">Category</div>
          <div className="chips-row">
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

        {/* ===== FILTER BAR ===== */}
        <div className="flex items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-2 overflow-x-auto chips-row flex-1">
            {/* Price filter inline */}
            {[
              { label: 'All Prices', val: 'all', testId: 'price-filter-all' },
              { label: 'Under ₹20k', val: 'under-20k', testId: 'price-filter-under-20k' },
              { label: '₹20k–₹50k', val: '20k-50k', testId: 'price-filter-20k-50k' },
              { label: 'Above ₹50k', val: 'above-50k', testId: 'price-filter-above-50k' },
            ].map(({ label, val, testId }) => (
              <FilterChip
                key={val}
                label={label}
                active={priceRange === val}
                onClick={() => setPriceRange(val)}
                testId={testId}
              />
            ))}
          </div>

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
              className="relative flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-semibold bg-white border border-slate-200 text-slate-700 hover:border-indigo-300 transition-colors shadow-sm"
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
            <div className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl p-6 shadow-2xl animate-slide-in-up md:static md:rounded-2xl md:bg-transparent md:shadow-none md:p-0 md:animate-none">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-base font-bold text-slate-900">Condition</h3>
                <button onClick={() => setFilterDrawerOpen(false)} className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500">
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

        {/* ===== RESULTS COUNT ===== */}
        <div className="flex items-center justify-between mb-5">
          <p className="text-sm text-slate-500" data-testid="results-count">
            <span className="font-bold text-slate-900">{filteredProducts.length}</span> results
            {selectedCategory !== 'All' && (
              <span className="ml-1">in <span className="font-semibold text-indigo-600">{selectedCategory}</span></span>
            )}
          </p>
        </div>

        {/* ===== PRODUCTS GRID ===== */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-5">
          {loading ? (
            Array.from({ length: 8 }).map((_, i) => <ProductCardSkeleton key={i} />)
          ) : (
            filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))
          )}
        </div>

        {/* Empty state */}
        {filteredProducts.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-lg font-semibold text-slate-700 mb-2" data-testid="no-results-message">
              No products found
            </p>
            <p className="text-slate-400 text-sm mb-6">Try adjusting your filters</p>
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
