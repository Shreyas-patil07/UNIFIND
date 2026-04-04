import React, { useState } from 'react';
import Header from '../components/Header';
import ProductCard from '../components/ProductCard';
import { ProductCardSkeleton } from '../components/SkeletonLoader';
import { products, categories } from '../data/mockData';
import { SlidersHorizontal } from 'lucide-react';

const BuyerPage = () => {
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [priceRange, setPriceRange] = useState('all');
  const [condition, setCondition] = useState('all');

  // Filter products
  const filteredProducts = products.filter(product => {
    if (selectedCategory !== 'All' && product.category !== selectedCategory) return false;
    
    if (priceRange === 'under-20k' && product.price >= 20000) return false;
    if (priceRange === '20k-50k' && (product.price < 20000 || product.price >= 50000)) return false;
    if (priceRange === 'above-50k' && product.price < 50000) return false;
    
    if (condition !== 'all' && product.condition !== condition) return false;
    
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        {/* Hero Banner */}
        <div className="relative bg-gradient-to-br from-blue-600 to-blue-700 rounded-3xl overflow-hidden mb-12 p-8 md:p-12">
          <div className="relative z-10">
            <h1 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-white mb-3" data-testid="buyer-page-title">
              Discover Amazing Deals
            </h1>
            <p className="text-lg text-blue-100 max-w-2xl">
              Browse thousands of verified listings from students across campus
            </p>
          </div>
          <div className="absolute top-0 right-0 w-1/2 h-full opacity-10">
            <img
              src="https://images.unsplash.com/photo-1759863639101-d1ad4923d655?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        {/* Filters Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <SlidersHorizontal className="h-5 w-5" />
              Filters
            </h2>
          </div>

          {/* Category Chips */}
          <div className="mb-6">
            <div className="text-sm font-medium text-slate-700 mb-3">Category</div>
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    selectedCategory === cat
                      ? 'bg-blue-600 text-white shadow-[0_0_0_1px_rgba(37,99,235,1)_inset]'
                      : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-500'
                  }`}
                  data-testid={`category-filter-${cat.toLowerCase()}`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Price & Condition Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Price Range */}
            <div>
              <div className="text-sm font-medium text-slate-700 mb-3">Price Range</div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setPriceRange('all')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    priceRange === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="price-filter-all"
                >
                  All
                </button>
                <button
                  onClick={() => setPriceRange('under-20k')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    priceRange === 'under-20k' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="price-filter-under-20k"
                >
                  Under ₹20k
                </button>
                <button
                  onClick={() => setPriceRange('20k-50k')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    priceRange === '20k-50k' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="price-filter-20k-50k"
                >
                  ₹20k - ₹50k
                </button>
                <button
                  onClick={() => setPriceRange('above-50k')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    priceRange === 'above-50k' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="price-filter-above-50k"
                >
                  Above ₹50k
                </button>
              </div>
            </div>

            {/* Condition */}
            <div>
              <div className="text-sm font-medium text-slate-700 mb-3">Condition</div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setCondition('all')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    condition === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="condition-filter-all"
                >
                  All
                </button>
                <button
                  onClick={() => setCondition('Like New')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    condition === 'Like New' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="condition-filter-like-new"
                >
                  Like New
                </button>
                <button
                  onClick={() => setCondition('Excellent')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    condition === 'Excellent' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="condition-filter-excellent"
                >
                  Excellent
                </button>
                <button
                  onClick={() => setCondition('Good')}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    condition === 'Good' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
                  }`}
                  data-testid="condition-filter-good"
                >
                  Good
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-sm text-slate-600" data-testid="results-count">
            Showing <span className="font-bold text-slate-900">{filteredProducts.length}</span> results
          </p>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            Array.from({ length: 6 }).map((_, i) => <ProductCardSkeleton key={i} />)
          ) : (
            filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))
          )}
        </div>

        {filteredProducts.length === 0 && !loading && (
          <div className="text-center py-20">
            <p className="text-lg text-slate-500" data-testid="no-results-message">No products found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuyerPage;
