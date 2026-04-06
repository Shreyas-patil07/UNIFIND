import { Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogIn, UserPlus, Mail } from 'lucide-react';
import { Button } from './ui/Button';
import LandingPage from '../pages/LandingPage';

const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-[100dvh] flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication modal if not authenticated
  if (!currentUser) {
    return (
      <div className="relative min-h-[100dvh]">
        {/* Background: Landing page with blur */}
        <div className="absolute inset-0 overflow-hidden" style={{ filter: 'blur(8px)' }}>
          <LandingPage />
        </div>
        
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-slate-900/60"></div>

        {/* Authentication Modal */}
        <div className="relative z-50 min-h-[100dvh] flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-8 max-w-md w-full shadow-2xl">
            <div className="flex justify-center mb-6">
              <div className="bg-blue-50 h-16 w-16 rounded-full flex items-center justify-center">
                <LogIn className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 text-center mb-3">
              Authentication Required
            </h2>
            <p className="text-slate-600 text-center mb-8">
              You need to be logged in to access this page. Please login or create a new account to continue.
            </p>
            <div className="flex flex-col gap-3">
              <Button
                onClick={() => navigate('/login')}
                className="w-full rounded-xl bg-blue-600 text-white hover:bg-blue-700 flex items-center justify-center gap-2"
                data-testid="modal-login-btn"
              >
                <LogIn className="h-4 w-4" />
                Login to Account
              </Button>
              <Button
                onClick={() => navigate('/signup')}
                variant="outline"
                className="w-full rounded-xl flex items-center justify-center gap-2"
                data-testid="modal-signup-btn"
              >
                <UserPlus className="h-4 w-4" />
                Create New Account
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="ghost"
                className="w-full rounded-xl text-slate-600"
                data-testid="modal-back-btn"
              >
                Back to Home
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Check if email is verified (allow profile page access even if not verified)
  const isProfilePage = location.pathname === '/profile' || location.pathname.startsWith('/profile/');
  
  if (!currentUser.emailVerified && !isProfilePage) {
    return (
      <div className="relative min-h-[100dvh]">
        {/* Background: Landing page with blur */}
        <div className="absolute inset-0 overflow-hidden" style={{ filter: 'blur(8px)' }}>
          <LandingPage />
        </div>
        
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-slate-900/60"></div>

        {/* Email Verification Modal */}
        <div className="relative z-50 min-h-[100dvh] flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-8 max-w-md w-full shadow-2xl">
            <div className="flex justify-center mb-6">
              <div className="bg-amber-50 h-16 w-16 rounded-full flex items-center justify-center">
                <Mail className="h-8 w-8 text-amber-600" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 text-center mb-3">
              Email Verification Required
            </h2>
            <p className="text-slate-600 text-center mb-4">
              Please verify your email address to access this page. Check your inbox for the verification link we sent to <span className="font-semibold">{currentUser.email}</span>.
            </p>
            <p className="text-sm text-amber-600 font-medium text-center mb-8">
              ⚠️ Check in spam folder if you don't see the email
            </p>
            <div className="flex flex-col gap-3">
              <Button
                onClick={() => navigate(`/profile/${currentUser.uid}`)}
                className="w-full rounded-xl bg-blue-600 text-white hover:bg-blue-700"
                data-testid="modal-profile-btn"
              >
                Go to Profile
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
                className="w-full rounded-xl"
                data-testid="modal-home-btn"
              >
                Back to Home
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render the protected component if authenticated and verified (or on profile page)
  return children;
};

export default ProtectedRoute;

