import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Eye, MessageCircle, Heart } from 'lucide-react';
import { users } from '../data/mockData';

const conditionConfig = {
  'Like New': { color: 'bg-emerald-500', label: 'Like New' },
  'Excellent': { color: 'bg-teal-500', label: 'Excellent' },
  'Good': { color: 'bg-amber-500', label: 'Good' },
  'Fair': { color: 'bg-orange-500', label: 'Fair' },
};

const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const seller = users.find(u => u.id === product.sellerId);
  const condition = conditionConfig[product.condition] || { color: 'bg-slate-500', label: product.condition };

  return (
    <div
      className="group flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-card-hover hover:border-indigo-300/50"
      onClick={() => navigate(`/listing/${product.id}`)}
      data-testid={`product-card-${product.id}`}
    >
      {/* ===== IMAGE ===== */}
      <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
        <img
          src={product.images[0]}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          data-testid="product-card-image"
        />

        {/* Gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Condition Badge */}
        <div className="absolute top-2.5 left-2.5">
          <span
            className={`${condition.color} px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider text-white shadow-sm`}
            data-testid="product-condition-badge"
          >
            {condition.label}
          </span>
        </div>

        {/* Views badge */}
        <div className="absolute top-2.5 right-2.5 bg-black/50 backdrop-blur-sm px-2 py-0.5 rounded-lg flex items-center gap-1">
          <Eye className="h-3 w-3 text-white" />
          <span className="text-[10px] text-white font-medium">{product.views}</span>
        </div>
      </div>

      {/* ===== CONTENT ===== */}
      <div className="p-3.5 flex-1 flex flex-col">
        {/* Title */}
        <h3
          className="text-sm font-bold text-slate-900 mb-1.5 line-clamp-2 leading-snug"
          data-testid="product-title"
        >
          {product.title}
        </h3>

        {/* Price */}
        <div
          className="text-lg font-black text-indigo-600 mb-2"
          data-testid="product-price"
        >
          ₹{product.price.toLocaleString()}
        </div>

        {/* Location */}
        <div className="flex items-center gap-1 text-xs text-slate-400 mb-3">
          <MapPin className="h-3 w-3 flex-shrink-0" />
          <span className="truncate" data-testid="product-location">{product.location}</span>
        </div>

        {/* Seller row */}
        <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-100">
          <img
            src={seller?.avatar}
            alt={seller?.name}
            className="h-6 w-6 rounded-full object-cover ring-1 ring-slate-200 flex-shrink-0"
            data-testid="seller-avatar"
          />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-800 truncate" data-testid="seller-name">
              {seller?.name?.split(' ')[0] || seller?.name}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-auto">
          <button
            className="flex-1 border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 text-xs font-semibold py-2 rounded-xl transition-all duration-200 active:scale-95"
            onClick={(e) => { e.stopPropagation(); navigate(`/listing/${product.id}`); }}
            data-testid="product-view-btn"
          >
            View
          </button>
          <button
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-2 rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-1.5"
            onClick={(e) => { e.stopPropagation(); navigate('/chat'); }}
            data-testid="product-chat-btn"
          >
            <MessageCircle className="h-3.5 w-3.5" />
            Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
