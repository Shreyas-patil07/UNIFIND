import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { Sparkles, Search, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { products } from '../data/mockData';

const NeedBoardPage = () => {
  const navigate = useNavigate();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!input.trim()) return;
    
    setLoading(true);
    
    // Mock AI processing with skeleton animation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock extracted info and matches
    setResults({
      extracted: {
        item: 'Laptop',
        budget: '₹50,000 - ₹80,000',
        condition: 'Like New or Excellent',
        features: ['Good battery', 'Fast processor']
      },
      matches: products.slice(0, 3)
    });
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header hideSearch />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-purple-50 border border-purple-200 rounded-full px-4 py-2 mb-4">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">AI-Powered Matching</span>
            </div>
            <h1 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 mb-3" data-testid="need-board-title">
              What are you looking for?
            </h1>
            <p className="text-base text-slate-600">
              Describe what you need, and our AI will find the perfect matches
            </p>
          </div>

          {/* Input Area */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8 shadow-sm">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Example: I need a laptop for coding, budget around 70k, good battery life..."
              rows="4"
              className="w-full rounded-xl border border-slate-200 px-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none mb-4"
              data-testid="need-board-input"
            />
            <Button
              onClick={handleSearch}
              disabled={loading || !input.trim()}
              className="w-full bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
              data-testid="find-matches-btn"
            >
              {loading ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  Find Matches
                </>
              )}
            </Button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-2xl border border-slate-200 p-8" data-testid="loading-state">
              <div className="space-y-4">
                <div className="h-4 skeleton w-3/4" />
                <div className="h-4 skeleton w-1/2" />
                <div className="h-4 skeleton w-2/3" />
              </div>
              <div className="mt-6 pt-6 border-t border-slate-200">
                <div className="h-32 skeleton rounded-xl mb-3" />
                <div className="h-32 skeleton rounded-xl" />
              </div>
            </div>
          )}

          {/* Results */}
          {!loading && results && (
            <div className="space-y-8" data-testid="results-section">
              {/* Extracted Information */}
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border border-blue-200 p-8">
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="h-5 w-5 text-blue-600" />
                  <h2 className="text-xl font-bold text-slate-900">What we understood</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-item">
                    <div className="text-sm text-slate-600 mb-1">Looking for</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.item}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-budget">
                    <div className="text-sm text-slate-600 mb-1">Budget</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.budget}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-condition">
                    <div className="text-sm text-slate-600 mb-1">Preferred Condition</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.condition}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-features">
                    <div className="text-sm text-slate-600 mb-1">Key Features</div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {results.extracted.features.map((feature, i) => (
                        <span key={i} className="bg-blue-100 text-blue-700 px-2 py-1 rounded-lg text-xs font-medium">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Matched Products */}
              <div>
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  Top Matches for You
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.matches.map((product) => (
                    <div
                      key={product.id}
                      onClick={() => navigate(`/listing/${product.id}`)}
                      className="group bg-white rounded-2xl border border-slate-200 overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10"
                      data-testid={`match-${product.id}`}
                    >
                      <div className="aspect-[4/3] overflow-hidden bg-slate-100">
                        <img
                          src={product.images[0]}
                          alt={product.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      </div>
                      <div className="p-4">
                        <h3 className="text-lg font-bold text-slate-900 mb-2 line-clamp-1">
                          {product.title}
                        </h3>
                        <div className="text-2xl font-black text-blue-600">
                          ₹{product.price.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NeedBoardPage;
