import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import PublicRoute from './components/PublicRoute'
import { useAuth } from './contexts/AuthContext'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import OTPVerificationPage from './pages/OTPVerificationPage'
import DashboardHome from './pages/DashboardHome'
import BuyerPage from './pages/BuyerPage'
import ListingDetailPage from './pages/ListingDetailPage'
import SellerPage from './pages/SellerPage'
import PostListingPage from './pages/PostListingPage'
import NeedBoardPage from './pages/NeedBoardPage'
import ChatPage from './pages/ChatPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ProfilePage from './pages/ProfilePage'
import EditProfilePage from './pages/EditProfilePage'

// Profile redirect component
function ProfileRedirect() {
  const { currentUser } = useAuth();
  if (currentUser?.uid) {
    return <Navigate to={`/profile/${currentUser.uid}`} replace />;
  }
  return <Navigate to="/login" replace />;
}

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/home" element={<LandingPage />} />
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
            <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
            <Route path="/otp-verification" element={<OTPVerificationPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardHome /></ProtectedRoute>} />
            <Route path="/buyer" element={<ProtectedRoute><BuyerPage /></ProtectedRoute>} />
            <Route path="/listing/:id" element={<ProtectedRoute><ListingDetailPage /></ProtectedRoute>} />
            <Route path="/seller" element={<ProtectedRoute><SellerPage /></ProtectedRoute>} />
            <Route path="/post-listing" element={<ProtectedRoute><PostListingPage /></ProtectedRoute>} />
            <Route path="/need-board" element={<ProtectedRoute><NeedBoardPage /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfileRedirect /></ProtectedRoute>} />
            <Route path="/profile/:userId" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/profile/:userId/edit" element={<ProtectedRoute><EditProfilePage /></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </AuthProvider>
  )
}

export default App
