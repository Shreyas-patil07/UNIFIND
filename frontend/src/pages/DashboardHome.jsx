import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { ShoppingBag, Package, MessageCircle, BarChart3, Sparkles, List, TrendingUp, Clock } from 'lucide-react';
import { recentActivity, userStats } from '../data/mockData';
import { useAuth } from '../contexts/AuthContext';

const DashboardHome = () => {
  const navigate = useNavigate();
  const { currentUser, userProfile } = useAuth();

  // Use real user data if available, fallback to defaults
  const displayName = currentUser?.displayName || userProfile?.name || 'User';
  const trustScore = userProfile?.trust_score || 0;
  const itemsBought = userProfile?.items_bought || 0;
  const itemsSold = userProfile?.items_sold || 0;
  const rating = userProfile?.rating || 0.0;

  const navCards = [
    { icon: ShoppingBag, title: 'Browse & Buy', description: 'Explore listings', path: '/buyer', color: 'bg-blue-50', iconColor: 'text-blue-600', testId: 'nav-card-buyer' },
    { icon: Package, title: 'My Listings', description: 'Manage your items', path: '/seller', color: 'bg-green-50', iconColor: 'text-green-600', testId: 'nav-card-seller' },
    { icon: Sparkles, title: 'Need Board', description: 'AI-powered matching', path: '/need-board', color: 'bg-purple-50', iconColor: 'text-purple-600', testId: 'nav-card-need-board' },
    { icon: BarChart3, title: 'Analytics', description: 'Track your stats', path: '/analytics', color: 'bg-amber-50', iconColor: 'text-amber-600', testId: 'nav-card-analytics' },
    { icon: MessageCircle, title: 'Chats', description: 'Your conversations', path: '/chat', color: 'bg-pink-50', iconColor: 'text-pink-600', testId: 'nav-card-chat' },
    { icon: List, title: 'Orders', description: 'Purchase history', path: '/analytics', color: 'bg-teal-50', iconColor: 'text-teal-600', testId: 'nav-card-orders' }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Header hideSearch />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h1 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 mb-2" data-testid="dashboard-welcome-title">
            Welcome back, {displayName}! 👋
          </h1>
          <p className="text-base text-slate-600">Your marketplace dashboard</p>
          
          {/* Trust Score - Only show if verified */}
          {currentUser?.emailVerified && (
            <div className="mt-6 inline-flex items-center gap-3 bg-green-50 border border-green-200 rounded-2xl px-6 py-3">
              <div className="text-sm font-medium text-green-900">Trust Score</div>
              <div className="text-3xl font-black text-green-600" data-testid="dashboard-trust-score">{trustScore}%</div>
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
          )}
        </div>

        {/* Navigation Grid */}
        <div className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Quick Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
            {navCards.map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.title}
                  onClick={() => navigate(card.path)}
                  className="group bg-white rounded-2xl border border-slate-200 p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10"
                  data-testid={card.testId}
                >
                  <div className={`${card.color} h-12 w-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className={`h-6 w-6 ${card.iconColor}`} />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-1">{card.title}</h3>
                  <p className="text-sm text-slate-600">{card.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Quick Stats</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="stat-bought">
              <div className="text-sm text-slate-600 mb-1">Items Bought</div>
              <div className="text-3xl font-black text-slate-900">{itemsBought}</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="stat-sold">
              <div className="text-sm text-slate-600 mb-1">Items Sold</div>
              <div className="text-3xl font-black text-slate-900">{itemsSold}</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6" data-testid="stat-rating">
              <div className="text-sm text-slate-600 mb-1">Your Rating</div>
              <div className="text-3xl font-black text-slate-900">{rating.toFixed(1)} ⭐</div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-6">Recent Activity</h2>
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            {recentActivity.map((activity, index) => (
              <div
                key={activity.id}
                className={`flex items-center justify-between p-5 ${index !== recentActivity.length - 1 ? 'border-b border-slate-100' : ''}`}
                data-testid={`activity-item-${activity.id}`}
              >
                <div className="flex items-center gap-4">
                  <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${
                    activity.type === 'purchase' ? 'bg-blue-50' :
                    activity.type === 'sale' ? 'bg-green-50' : 'bg-amber-50'
                  }`}>
                    {activity.type === 'purchase' && <ShoppingBag className="h-5 w-5 text-blue-600" />}
                    {activity.type === 'sale' && <Package className="h-5 w-5 text-green-600" />}
                    {activity.type === 'review' && <TrendingUp className="h-5 w-5 text-amber-600" />}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-900">{activity.title}</div>
                    <div className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                      <Clock className="h-3 w-3" />
                      {activity.date}
                    </div>
                  </div>
                </div>
                {activity.amount && (
                  <div className="text-lg font-bold text-slate-900">
                    ₹{activity.amount.toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
