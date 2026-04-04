import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { products } from '../data/mockData';
import { Edit2, Trash2, CheckCircle2, Plus, Eye } from 'lucide-react';
import { Button } from '../components/ui/Button';

const SellerPage = () => {
  const navigate = useNavigate();
  // Mock - show first 3 products as user's listings
  const myListings = products.slice(0, 3);

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <div>
            <h1 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 mb-2" data-testid="seller-page-title">
              My Listings
            </h1>
            <p className="text-base text-slate-600">Manage your products</p>
          </div>
          <Button
            onClick={() => navigate('/post-listing')}
            className="bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
            data-testid="post-new-listing-btn"
          >
            <Plus className="h-5 w-5 mr-2" />
            Post New Listing
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="seller-stat-active">
            <div className="text-sm text-slate-600 mb-1">Active Listings</div>
            <div className="text-3xl font-black text-slate-900">{myListings.length}</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="seller-stat-sold">
            <div className="text-sm text-slate-600 mb-1">Sold This Month</div>
            <div className="text-3xl font-black text-slate-900">5</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="seller-stat-revenue">
            <div className="text-sm text-slate-600 mb-1">Total Revenue</div>
            <div className="text-3xl font-black text-slate-900">₹124k</div>
          </div>
        </div>

        {/* Listings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {myListings.map((product) => (
            <div
              key={product.id}
              className="group bg-white rounded-2xl border border-slate-200 overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10"
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
                <h3 className="text-lg font-bold text-slate-900 mb-2 line-clamp-1" data-testid="seller-listing-title">
                  {product.title}
                </h3>
                <div className="text-2xl font-black text-blue-600 mb-4" data-testid="seller-listing-price">
                  ₹{product.price.toLocaleString()}
                </div>

                {/* Condition & Location */}
                <div className="flex items-center gap-2 mb-5 pb-5 border-b border-slate-100">
                  <span className="bg-green-100 text-green-700 px-2 py-1 rounded-lg text-xs font-semibold">
                    {product.condition}
                  </span>
                  <span className="text-sm text-slate-500">{product.location}</span>
                </div>

                {/* Actions */}
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all"
                    data-testid="seller-listing-edit-btn"
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl border-slate-200 hover:border-red-500 hover:bg-red-50 hover:text-red-600 transition-all"
                    data-testid="seller-listing-delete-btn"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl border-slate-200 hover:border-green-500 hover:bg-green-50 hover:text-green-600 transition-all col-span-1"
                    data-testid="seller-listing-sold-btn"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {myListings.length === 0 && (
          <div className="text-center py-20">
            <p className="text-lg text-slate-500 mb-6">You haven't posted any listings yet</p>
            <Button
              onClick={() => navigate('/post-listing')}
              className="bg-blue-600 text-white"
              data-testid="empty-post-listing-btn"
            >
              <Plus className="h-5 w-5 mr-2" />
              Post Your First Listing
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerPage;
