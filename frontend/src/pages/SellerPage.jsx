import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { products } from '../data/mockData';
import { Edit2, Trash2, CheckCircle2, Plus, Eye } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useTheme } from '../contexts/ThemeContext';

const SellerPage = () => {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  // Mock - show first 3 products as user's listings
  const myListings = products.slice(0, 3);

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
            <div className="text-xl sm:text-2xl font-black text-indigo-600 mb-0.5">{myListings.length}</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Active</div>
          </div>
          <div className={`rounded-2xl border p-4 text-center ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`} data-testid="seller-stat-sold">
            <div className="text-xl sm:text-2xl font-black text-emerald-600 mb-0.5">5</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Sold</div>
          </div>
          <div className={`rounded-2xl border p-4 text-center ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`} data-testid="seller-stat-revenue">
            <div className="text-xl sm:text-2xl font-black text-amber-600 mb-0.5">₹124k</div>
            <div className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Revenue</div>
          </div>
        </div>

        {/* Listings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {myListings.map((product) => (
            <div
              key={product.id}
              className={`group rounded-2xl border overflow-hidden transition-all duration-300 hover:-translate-y-1 ${
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
                    className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                      darkMode 
                        ? 'border-slate-700 hover:border-indigo-500 hover:bg-indigo-900/30 hover:text-indigo-400 text-slate-400'
                        : 'border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600'
                    }`}
                    data-testid="seller-listing-edit-btn"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button
                    className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                      darkMode 
                        ? 'border-slate-700 hover:border-red-500 hover:bg-red-900/30 hover:text-red-400 text-slate-400'
                        : 'border-slate-200 hover:border-red-400 hover:bg-red-50 hover:text-red-600 text-slate-600'
                    }`}
                    data-testid="seller-listing-delete-btn"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                  <button
                    className={`flex items-center justify-center py-2 rounded-xl border transition-all text-xs font-medium ${
                      darkMode 
                        ? 'border-slate-700 hover:border-emerald-500 hover:bg-emerald-900/30 hover:text-emerald-400 text-slate-400'
                        : 'border-slate-200 hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600'
                    }`}
                    data-testid="seller-listing-sold-btn"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {myListings.length === 0 && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📦</div>
            <p className={`text-lg font-semibold mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>No listings yet</p>
            <p className={`text-sm mb-6 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Post your first item to start selling</p>
            <button
              onClick={() => navigate('/post-listing')}
              className="btn-gradient px-6 py-2.5 text-sm inline-flex items-center gap-2"
              data-testid="empty-post-listing-btn"
            >
              <Plus className="h-4 w-4" />
              Post First Listing
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerPage;

