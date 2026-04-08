import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { TrendingUp, TrendingDown, Eye, Heart, MessageCircle, Package, IndianRupee } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { getProducts } from '../services/api';

const AnalyticsPage = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  
  // Load user's products
  useEffect(() => {
    const loadProducts = async () => {
      if (!currentUser) return;
      
      try {
        const userProducts = await getProducts({ seller_id: currentUser.uid });
        setProducts(Array.isArray(userProducts) ? userProducts : []);
      } catch (error) {
        console.error('Failed to load products:', error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [currentUser]);

  // Calculate stats from real data
  const safeProducts = Array.isArray(products) ? products : [];
  
  const stats = {
    totalViews: safeProducts.reduce((sum, p) => sum + (p.views || 0), 0),
    totalLikes: 0, // TODO: Implement likes feature
    totalMessages: 0, // TODO: Get from chats API
    totalRevenue: safeProducts.reduce((sum, p) => sum + (p.is_active ? 0 : p.price), 0),
    activeListings: safeProducts.filter(p => p.is_active).length,
    soldItems: safeProducts.filter(p => !p.is_active).length,
    viewsChange: 0, // TODO: Calculate change
    revenueChange: 0 // TODO: Calculate change
  };

  const userStats = {
    bought: 0, // TODO: Implement transaction history
    sold: safeProducts.filter(p => !p.is_active).length,
    rating: 0, // TODO: Get from reviews
    earnings: safeProducts.reduce((sum, p) => sum + (p.is_active ? 0 : p.price), 0),
    savings: 0, // TODO: Calculate from transactions
    trustScore: 0 // TODO: Get from user profile
  };

  const monthlyData = [
    // TODO: Calculate from real transaction data
    { month: 'Jan', sales: 0, revenue: 0 },
    { month: 'Feb', sales: 0, revenue: 0 },
    { month: 'Mar', sales: 0, revenue: 0 },
    { month: 'Apr', sales: 0, revenue: 0 },
    { month: 'May', sales: safeProducts.filter(p => !p.is_active).length, revenue: safeProducts.reduce((sum, p) => sum + (p.is_active ? 0 : p.price), 0) }
  ];

  const topProducts = [
    { name: 'MacBook Pro 14"', views: 342, likes: 28, messages: 45 },
    { name: 'iPhone 13 Pro', views: 289, likes: 31, messages: 38 },
    { name: 'Sony WH-1000XM4', views: 234, likes: 19, messages: 27 }
  ];

  return (
    <div className="min-h-[100dvh] bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <h1 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 mb-2" data-testid="analytics-title">
          Analytics Dashboard
        </h1>
        <p className="text-base text-slate-600 mb-12">Track your performance and insights</p>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="metric-views">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-50 h-12 w-12 rounded-xl flex items-center justify-center">
                <Eye className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex items-center gap-1 text-green-600 text-sm font-medium">
                <TrendingUp className="h-4 w-4" />
                {stats.viewsChange}%
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 mb-1">{stats.totalViews.toLocaleString()}</div>
            <div className="text-sm text-slate-600">Total Views</div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="metric-likes">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-pink-50 h-12 w-12 rounded-xl flex items-center justify-center">
                <Heart className="h-6 w-6 text-pink-600" />
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 mb-1">{stats.totalLikes}</div>
            <div className="text-sm text-slate-600">Total Likes</div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="metric-messages">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-50 h-12 w-12 rounded-xl flex items-center justify-center">
                <MessageCircle className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 mb-1">{stats.totalMessages}</div>
            <div className="text-sm text-slate-600">Messages</div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="metric-revenue">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-50 h-12 w-12 rounded-xl flex items-center justify-center">
                <IndianRupee className="h-6 w-6 text-green-600" />
              </div>
              <div className="flex items-center gap-1 text-green-600 text-sm font-medium">
                <TrendingUp className="h-4 w-4" />
                {stats.revenueChange}%
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 mb-1">₹{(stats.totalRevenue / 1000).toFixed(0)}k</div>
            <div className="text-sm text-slate-600">Total Revenue</div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          {/* Monthly Sales Chart */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Monthly Sales</h2>
            <div className="space-y-4">
              {(Array.isArray(monthlyData) ? monthlyData : []).map((data, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-12 text-sm font-medium text-slate-600">{data.month}</div>
                  <div className="flex-1">
                    <div className="bg-slate-100 rounded-full h-8 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full rounded-full flex items-center justify-end pr-3"
                        style={{ width: `${(data.sales / 20) * 100}%` }}
                      >
                        <span className="text-xs font-bold text-white">{data.sales}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Monthly Revenue Chart */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Monthly Revenue</h2>
            <div className="space-y-4">
              {(Array.isArray(monthlyData) ? monthlyData : []).map((data, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-12 text-sm font-medium text-slate-600">{data.month}</div>
                  <div className="flex-1">
                    <div className="bg-slate-100 rounded-full h-8 overflow-hidden">
                      <div
                        className="bg-green-600 h-full rounded-full flex items-center justify-end pr-3"
                        style={{ width: `${(data.revenue / 150000) * 100}%` }}
                      >
                        <span className="text-xs font-bold text-white">₹{(data.revenue / 1000).toFixed(0)}k</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Products Table */}
        <div className="bg-white rounded-2xl border border-slate-200 p-8">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Top Performing Products</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Product</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Views</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Likes</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Messages</th>
                </tr>
              </thead>
              <tbody>
                {(Array.isArray(topProducts) ? topProducts : []).map((product, i) => (
                  <tr key={i} className="border-b border-slate-100 last:border-0" data-testid={`top-product-${i}`}>
                    <td className="py-4 px-4 text-sm font-medium text-slate-900">{product.name}</td>
                    <td className="py-4 px-4 text-center">
                      <div className="inline-flex items-center gap-1 bg-blue-50 px-3 py-1 rounded-lg">
                        <Eye className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-bold text-blue-600">{product.views}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <div className="inline-flex items-center gap-1 bg-pink-50 px-3 py-1 rounded-lg">
                        <Heart className="h-4 w-4 text-pink-600" />
                        <span className="text-sm font-bold text-pink-600">{product.likes}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <div className="inline-flex items-center gap-1 bg-purple-50 px-3 py-1 rounded-lg">
                        <MessageCircle className="h-4 w-4 text-purple-600" />
                        <span className="text-sm font-bold text-purple-600">{product.messages}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;

