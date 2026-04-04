import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'

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

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/otp-verification" element={<OTPVerificationPage />} />
          <Route path="/dashboard" element={<DashboardHome />} />
          <Route path="/buyer" element={<BuyerPage />} />
          <Route path="/listing/:id" element={<ListingDetailPage />} />
          <Route path="/seller" element={<SellerPage />} />
          <Route path="/post-listing" element={<PostListingPage />} />
          <Route path="/need-board" element={<NeedBoardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
