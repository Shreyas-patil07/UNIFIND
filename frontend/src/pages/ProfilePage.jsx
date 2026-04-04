import React from 'react';
import Header from '../components/Header';
import { users, userStats, reviews } from '../data/mockData';
import { Shield, Star, Award, Calendar, GraduationCap } from 'lucide-react';
import { Button } from '../components/ui/Button';

const ProfilePage = () => {
  const currentUser = users[0]; // Mock current user

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Profile Header */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6 mb-6">
              <img
                src={currentUser.avatar}
                alt={currentUser.name}
                className="h-24 w-24 rounded-full object-cover border-4 border-blue-100"
                data-testid="profile-avatar"
              />
              <div className="flex-1">
                <h1 className="font-['Outfit'] text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mb-2" data-testid="profile-name">
                  {currentUser.name}
                </h1>
                <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                  <div className="flex items-center gap-1">
                    <GraduationCap className="h-4 w-4" />
                    <span data-testid="profile-college">{currentUser.college}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>Member since {currentUser.memberSince}</span>
                  </div>
                </div>
              </div>
              <Button variant="outline" className="rounded-xl" data-testid="edit-profile-btn">
                Edit Profile
              </Button>
            </div>

            {/* Trust Score - Big and Prominent */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 p-8 text-center">
              <div className="flex items-center justify-center gap-2 mb-3">
                <Shield className="h-6 w-6 text-green-600" />
                <h2 className="text-lg font-bold text-green-900">Trust Score</h2>
              </div>
              <div className="relative inline-block">
                <svg className="w-32 h-32" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="#E2E8F0"
                    strokeWidth="8"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="8"
                    strokeDasharray={`${(userStats.trustScore / 100) * 339} 339`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-4xl font-black text-green-600" data-testid="profile-trust-score">
                    {userStats.trustScore}%
                  </div>
                </div>
              </div>
              <p className="text-sm text-green-700 mt-3">Verified & Trusted Seller</p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-sold">
              <Package className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{userStats.sold}</div>
              <div className="text-sm text-slate-600">Items Sold</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-rating">
              <Star className="h-8 w-8 text-amber-400 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{currentUser.rating}</div>
              <div className="text-sm text-slate-600">Average Rating</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-reviews">
              <Award className="h-8 w-8 text-purple-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{currentUser.reviewCount}</div>
              <div className="text-sm text-slate-600">Reviews</div>
            </div>
          </div>

          {/* Badges */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Achievements</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center" data-testid="badge-verified">
                <div className="bg-blue-50 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Shield className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-sm font-medium text-slate-900">Verified</div>
              </div>
              <div className="text-center" data-testid="badge-trusted">
                <div className="bg-green-50 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Award className="h-8 w-8 text-green-600" />
                </div>
                <div className="text-sm font-medium text-slate-900">Trusted Seller</div>
              </div>
              <div className="text-center" data-testid="badge-star">
                <div className="bg-amber-50 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Star className="h-8 w-8 text-amber-400" />
                </div>
                <div className="text-sm font-medium text-slate-900">Top Rated</div>
              </div>
              <div className="text-center" data-testid="badge-pro">
                <div className="bg-purple-50 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Award className="h-8 w-8 text-purple-600" />
                </div>
                <div className="text-sm font-medium text-slate-900">Pro Seller</div>
              </div>
            </div>
          </div>

          {/* Reviews */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Recent Reviews</h2>
            <div className="space-y-6">
              {reviews.map((review) => {
                const reviewer = users.find(u => u.id === review.userId);
                return (
                  <div key={review.id} className="border-b border-slate-100 last:border-0 pb-6 last:pb-0" data-testid={`review-${review.id}`}>
                    <div className="flex items-start gap-4">
                      <img
                        src={reviewer?.avatar}
                        alt={reviewer?.name}
                        className="h-12 w-12 rounded-full object-cover"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-bold text-slate-900">{reviewer?.name}</h3>
                          <div className="flex items-center gap-1">
                            {Array.from({ length: review.rating }).map((_, i) => (
                              <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />
                            ))}
                          </div>
                        </div>
                        <p className="text-sm text-slate-700 mb-2">{review.comment}</p>
                        <p className="text-xs text-slate-500">{review.date}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Package = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

export default ProfilePage;
