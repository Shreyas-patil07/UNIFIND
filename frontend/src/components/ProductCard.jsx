import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Eye, MessageCircle } from 'lucide-react';
import { Button } from './ui/Button';
import { users } from '../data/mockData';

const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const seller = users.find(u => u.id === product.sellerId);

  const getConditionColor = (condition) => {
    switch (condition) {
      case 'Like New':
        return 'bg-green-500';
      case 'Excellent':
        return 'bg-emerald-500';
      case 'Good':
        return 'bg-yellow-500';
      case 'Fair':
        return 'bg-orange-500';
      default:
        return 'bg-slate-500';
    }
  };

  return (
    <div 
      className="group flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10"
      onClick={() => navigate(`/listing/${product.id}`)}
      data-testid={`product-card-${product.id}`}
    >
      {/* Image */}
      <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
        <img
          src={product.images[0]}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          data-testid="product-card-image"
        />
        {/* Condition Badge */}
        <div className="absolute top-3 left-3">
          <span 
            className={`${getConditionColor(product.condition)} px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider text-white shadow-lg`}
            data-testid="product-condition-badge"
          >
            {product.condition}
          </span>
        </div>
        {/* Views */}
        <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center gap-1">
          <Eye className="h-3 w-3 text-white" />
          <span className="text-xs text-white font-medium">{product.views}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col">
        {/* Title & Price */}
        <h3 className="text-lg font-semibold text-slate-900 mb-1 line-clamp-2" data-testid="product-title">
          {product.title}
        </h3>
        <div className="text-2xl font-bold text-blue-600 mb-3" data-testid="product-price">
          ₹{product.price.toLocaleString()}
        </div>

        {/* Location */}
        <div className="flex items-center gap-1 text-sm text-slate-500 mb-4">
          <MapPin className="h-4 w-4" />
          <span data-testid="product-location">{product.location}</span>
        </div>

        {/* Seller Info */}
        <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100">
          <img
            src={seller?.avatar}
            alt={seller?.name}
            className="h-8 w-8 rounded-full object-cover"
            data-testid="seller-avatar"
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate" data-testid="seller-name">
              {seller?.name}
            </p>
            <p className="text-xs text-slate-500">{seller?.college}</p>
          </div>
          <div className="bg-green-50 px-2 py-1 rounded-lg">
            <span className="text-xs font-bold text-green-700" data-testid="seller-trust-score">
              {seller?.trustScore}%
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-auto">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 rounded-xl border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/listing/${product.id}`);
            }}
            data-testid="product-view-btn"
          >
            View
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-200 active:scale-95"
            onClick={(e) => {
              e.stopPropagation();
              navigate('/chat');
            }}
            data-testid="product-chat-btn"
          >
            <MessageCircle className="h-4 w-4 mr-2" />
            Chat
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
