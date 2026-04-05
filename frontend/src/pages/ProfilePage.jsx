import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Header from '../components/Header';
import { Shield, Star, Award, Calendar, GraduationCap, LogOut, Mail, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { sendEmailVerification } from 'firebase/auth';
import { actionCodeSettings } from '../services/firebase';

const ProfilePage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { logout, currentUser: authUser, userProfile, syncEmailVerificationStatus } = useAuth();
  
  // Determine if viewing own profile or another user's profile
  const isOwnProfile = !userId || userId === authUser?.uid;
  
  // Use real user data from userProfile
  const displayName = authUser?.displayName || userProfile?.name || 'User';
  const displayEmail = authUser?.email || '';
  const displayCollege = userProfile?.college || 'College';
  const memberSince = userProfile?.member_since || new Date().getFullYear().toString();
  const trustScore = userProfile?.trust_score || 0;
  const itemsSold = userProfile?.items_sold || 0;
  const rating = userProfile?.rating || 0.0;
  const reviewCount = userProfile?.review_count || 0;
  const avatar = userProfile?.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(displayName);
  
  // Real reviews from database (empty for now until we fetch from Firestore)
  const userReviews = userProfile?.reviews || [];
  
  const [showLogoutModal, setShowLogoutModal] = React.useState(false);
  const [resendingEmail, setResendingEmail] = React.useState(false);
  const [resendSuccess, setResendSuccess] = React.useState(false);
  const [isVerified, setIsVerified] = React.useState(authUser?.emailVerified || false);

  // Auto-check verification status every 5 seconds if not verified
  React.useEffect(() => {
    if (!authUser || isVerified) return;

    const checkVerificationStatus = async () => {
      try {
        const { reload } = await import('firebase/auth');
        await reload(authUser);
        if (authUser.emailVerified) {
          setIsVerified(true);
          // Sync verification status to database
          await syncEmailVerificationStatus(authUser);
          // Force re-render by updating state
          window.location.reload();
        }
      } catch (err) {
        console.error('Auto-check failed:', err);
      }
    };

    // Check immediately on mount
    checkVerificationStatus();

    // Then check every 5 seconds
    const interval = setInterval(checkVerificationStatus, 5000);

    return () => clearInterval(interval);
  }, [authUser, isVerified, syncEmailVerificationStatus]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  const handleResendVerification = async () => {
    if (!authUser) return;
    setResendingEmail(true);
    setResendSuccess(false);
    try {
      await sendEmailVerification(authUser, actionCodeSettings);
      setResendSuccess(true);
      setTimeout(() => setResendSuccess(false), 5000);
    } catch (error) {
      console.error('Failed to resend verification email:', error);
    } finally {
      setResendingEmail(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Profile Header */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6 mb-6">
              <img
                src={avatar}
                alt={displayName}
                className="h-24 w-24 rounded-full object-cover border-4 border-blue-100"
                data-testid="profile-avatar"
              />
              <div className="flex-1">
                <h1 className="font-['Outfit'] text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mb-2" data-testid="profile-name">
                  {displayName}
                  {isOwnProfile && authUser && authUser.emailVerified && (
                    <span className="inline-flex items-center gap-1 ml-3 px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full border border-green-200">
                      <CheckCircle className="h-4 w-4" />
                      Verified
                    </span>
                  )}
                </h1>
                <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                  <div className="flex items-center gap-1">
                    <GraduationCap className="h-4 w-4" />
                    <span data-testid="profile-college">{displayCollege}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>Member since {memberSince}</span>
                  </div>
                  {isOwnProfile && authUser && authUser.emailVerified && (
                    <div className="flex items-center gap-1 text-green-600">
                      <Mail className="h-4 w-4" />
                      <span>{displayEmail}</span>
                    </div>
                  )}
                </div>
              </div>
              {isOwnProfile && (
                <div className="flex gap-3">
                  <Button variant="outline" className="rounded-xl" data-testid="edit-profile-btn">
                    Edit Profile
                  </Button>
                  <Button 
                    onClick={() => setShowLogoutModal(true)}
                    variant="outline" 
                    className="rounded-xl text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300" 
                    data-testid="logout-btn"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              )}
            </div>

            {/* Trust Score - Big and Prominent - Only for verified users */}
            {authUser && authUser.emailVerified && isOwnProfile && (
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
                      strokeDasharray={`${(trustScore / 100) * 339} 339`}
                      strokeLinecap="round"
                      transform="rotate(-90 60 60)"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-4xl font-black text-green-600" data-testid="profile-trust-score">
                      {trustScore}%
                    </div>
                  </div>
                </div>
                <p className="text-sm text-green-700 mt-3">Trusted Seller</p>
              </div>
            )}

            {/* Email Verification Status - Only for unverified users viewing their own profile */}
            {isOwnProfile && authUser && !authUser.emailVerified && (
              <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-amber-100 h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="h-6 w-6 text-amber-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-amber-900 mb-2">Email Verification Required</h3>
                    <p className="text-sm text-amber-700 mb-4">
                      Your email <span className="font-semibold">{displayEmail}</span> is not verified yet. 
                      Please check your inbox and click the verification link to access all features and view your trust score.
                      <span className="block mt-2 font-medium">⚠️ Check in spam folder if you don't see the email</span>
                    </p>
                    {resendSuccess && (
                      <div className="mb-3 px-4 py-2 rounded-lg bg-green-100 border border-green-200 text-sm text-green-700">
                        ✓ Verification email sent successfully! Check in spam folder if you don't see it.
                      </div>
                    )}
                    <Button
                      onClick={handleResendVerification}
                      disabled={resendingEmail}
                      className="bg-amber-600 text-white hover:bg-amber-700 rounded-xl px-4 py-2 text-sm"
                    >
                      {resendingEmail ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Mail className="h-4 w-4 mr-2" />
                          Resend Verification Email
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stats Grid - Only for verified users */}
          {authUser && authUser.emailVerified && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-sold">
              <Package className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{itemsSold}</div>
              <div className="text-sm text-slate-600">Items Sold</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-rating">
              <Star className="h-8 w-8 text-amber-400 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{rating.toFixed(1)}</div>
              <div className="text-sm text-slate-600">Average Rating</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="profile-stat-reviews">
              <Award className="h-8 w-8 text-purple-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-1">{reviewCount}</div>
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

          {/* Reviews - Only show if there are reviews */}
          {userReviews && userReviews.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-8">
              <h2 className="text-xl font-bold text-slate-900 mb-6">Recent Reviews</h2>
              <div className="space-y-6">
                {userReviews.map((review, index) => (
                  <div key={index} className="border-b border-slate-100 last:border-0 pb-6 last:pb-0" data-testid={`review-${index}`}>
                    <div className="flex items-start gap-4">
                      <img
                        src={review.reviewerAvatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(review.reviewerName || 'User')}
                        alt={review.reviewerName}
                        className="h-12 w-12 rounded-full object-cover"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-bold text-slate-900">{review.reviewerName}</h3>
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
                ))}
              </div>
            </div>
          )}
            </>
          )}
        </div>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" data-testid="logout-modal">
          <div className="bg-white rounded-2xl border border-slate-200 p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex justify-center mb-6">
              <div className="bg-red-50 h-16 w-16 rounded-full flex items-center justify-center">
                <LogOut className="h-8 w-8 text-red-600" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 text-center mb-3">
              Logout Confirmation
            </h2>
            <p className="text-slate-600 text-center mb-8">
              Are you sure you want to logout? You'll need to login again to access your account.
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => setShowLogoutModal(false)}
                variant="outline"
                className="flex-1 rounded-xl"
                data-testid="cancel-logout-btn"
              >
                Cancel
              </Button>
              <Button
                onClick={handleLogout}
                className="flex-1 rounded-xl bg-red-600 text-white hover:bg-red-700"
                data-testid="confirm-logout-btn"
              >
                Yes, Logout
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const Package = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

export default ProfilePage;
