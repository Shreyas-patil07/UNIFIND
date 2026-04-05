import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { Button } from '../components/ui/Button';
import { ArrowLeft, MapPin, Eye, Share2, Heart, MessageCircle, Shield } from 'lucide-react';
import { products, users } from '../data/mockData';

const ListingDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const product = products.find(p => p.id === id) || products[0];
  const seller = users.find(u => u.id === product.sellerId);

  return (
    <div className="min-h-[100dvh] bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8 transition-colors"
          data-testid="back-btn"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Left - Images */}
          <div>
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden mb-4">
              <img
                src={product.images[0]}
                alt={product.title}
                className="w-full aspect-square object-cover"
                data-testid="product-main-image"
              />
            </div>
            <div className="grid grid-cols-4 gap-3">
              {product.images.slice(0, 4).map((img, i) => (
                <div key={i} className="bg-white rounded-xl border border-slate-200 overflow-hidden cursor-pointer hover:border-blue-500 transition-colors">
                  <img src={img} alt="" className="w-full aspect-square object-cover" />
                </div>
              ))}
            </div>
          </div>

          {/* Right - Details */}
          <div>
            <div className="bg-white rounded-2xl border border-slate-200 p-8">
              <h1 className="font-['Outfit'] text-2xl sm:text-3xl font-bold text-slate-900 mb-4" data-testid="product-title">
                {product.title}
              </h1>
              
              <div className="text-4xl font-black text-blue-600 mb-6" data-testid="product-price">
                ₹{product.price.toLocaleString()}
              </div>

              <div className="flex flex-wrap items-center gap-2 sm:gap-4 mb-6 pb-6 border-b border-slate-100">
                <span className="bg-green-100 text-green-700 px-3 py-1.5 rounded-lg text-sm font-semibold">
                  {product.condition}
                </span>
                <div className="flex items-center gap-1 text-slate-600">
                  <MapPin className="h-4 w-4" />
                  <span className="text-sm">{product.location}</span>
                </div>
                <div className="flex items-center gap-1 text-slate-600">
                  <Eye className="h-4 w-4" />
                  <span className="text-sm">{product.views} views</span>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-semibold text-slate-900 mb-2">Description</h3>
                <p className="text-slate-600 leading-relaxed">{product.description}</p>
              </div>

              <div className="mb-6 pb-6 border-b border-slate-100">
                <h3 className="text-sm font-semibold text-slate-900 mb-3">Seller Information</h3>
                <div className="flex items-center gap-4">
                  <img src={seller?.avatar} alt={seller?.name} className="h-12 w-12 rounded-full object-cover" />
                  <div className="flex-1">
                    <p className="font-semibold text-slate-900">{seller?.name}</p>
                    <p className="text-sm text-slate-500">{seller?.college}</p>
                  </div>
                  <div className="bg-green-50 px-3 py-1.5 rounded-lg">
                    <div className="flex items-center gap-1">
                      <Shield className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-bold text-green-700">{seller?.trustScore}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => navigate('/chat')}
                  className="flex-1 bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
                  data-testid="contact-seller-btn"
                >
                  <MessageCircle className="h-5 w-5 mr-2" />
                  Contact Seller
                </Button>
                <Button
                  variant="outline"
                  className="rounded-xl border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all"
                  data-testid="save-btn"
                >
                  <Heart className="h-5 w-5" />
                </Button>
                <Button
                  variant="outline"
                  className="rounded-xl border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all"
                  data-testid="share-btn"
                >
                  <Share2 className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListingDetailPage;

