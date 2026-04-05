import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Search, ShoppingBag, MessageCircle, User, Menu, X, LayoutDashboard, Sparkles, Package } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Header({ hideSearch = false }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleProfileClick = () => {
    if (currentUser?.uid) {
      navigate(`/profile/${currentUser.uid}`)
    } else {
      navigate('/profile')
    }
    setMobileMenuOpen(false)
  }

  const isActive = (path) => location.pathname === path || (path !== '/home' && location.pathname.startsWith(path))
  const isOnBuyerPage = location.pathname === '/buyer'
  const isOnSellerPage = location.pathname === '/seller'
  const isOnNeedBoardPage = location.pathname === '/need-board'
  const isOnChatPage = location.pathname === '/chat'
  const isOnDashboardPage = location.pathname === '/dashboard'
  const isOnProfilePage = location.pathname.startsWith('/profile')

  const navLinks = [
    { label: 'Buy', path: '/buyer', icon: ShoppingBag },
    { label: 'Sell', path: '/seller', icon: Package },
    { label: 'NeedBoard AI', path: '/need-board', icon: Sparkles },
    { label: 'Chats', path: '/chat', icon: MessageCircle, badge: 2 },
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  ]

  // Bottom nav items (mobile only)
  const bottomNavItems = [
    { label: 'Buy', path: '/buyer', icon: ShoppingBag },
    { label: 'Sell', path: '/seller', icon: Package },
    { label: 'NeedBoard', path: '/need-board', icon: Sparkles },
    { label: 'Chats', path: '/chat', icon: MessageCircle, badge: 2 },
    { label: 'Profile', path: null, icon: User, action: handleProfileClick },
  ]

  return (
    <>
      {/* ===== TOP HEADER ===== */}
      <header className="sticky top-0 z-50 glass-white border-b border-slate-200/80">
        <div className="px-4 sm:px-6 md:px-10 lg:px-20 py-3">
          <div className="flex items-center justify-between gap-4">

            {/* Logo */}
            <Link
              to="/home"
              className="flex items-center gap-2 hover:opacity-80 transition-opacity flex-shrink-0"
              data-testid="header-logo"
            >
              <img src="/UNIFIND.png" alt="UNIFIND Logo" className="h-9 w-auto" />
              <span className="font-['Outfit'] font-black text-xl tracking-tight">
                <span className="text-indigo-600">UNI</span>
                <span className="text-violet-600">FIND</span>
              </span>
            </Link>

            {/* Search Bar - Desktop */}
            {!hideSearch && (
              <div className="hidden md:flex flex-1 max-w-sm lg:max-w-md mx-4">
                <div className="relative w-full">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search products..."
                    className="input-premium w-full pl-10 pr-4 py-2.5 text-sm"
                    data-testid="header-search-input"
                  />
                </div>
              </div>
            )}

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map(({ label, path, icon: Icon, badge }) => {
                const active = isActive(path)
                return (
                  <button
                    key={path}
                    onClick={() => navigate(path)}
                    className={`relative flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-indigo-50 text-indigo-600'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slateigo-600'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                    {badge && !active && (
                      <span className="absolute -top-0.5 -right-0.5 bg-indigo-600 text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center font-bold">
                        {badge}
                      </span>
                    )}
                  </button>
                )
              })}

              {/* Profile Button */}
              <button
                onClick={() => navigate(currentUser?.uid ? `/profile/${currentUser.uid}` : '/profile')}
                className={`ml-2 relative flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  isOnProfilePage
                    ? 'bg-indigo-600 text-white shadow-glow-indigo'
                    : 'btn-gradient'
                }`}
                data-testid="header-profile-btn"
              >
                {currentUser?.photoURL ? (
                  <img src={currentUser.photoURL} alt="avatar" className="h-5 w-5 rounded-full object-cover" />
                ) : (
                  <User className="h-4 w-4" />
                )}
                Profile
              </button>
            </nav>

            {/* Mobile Menu Toggle */}
            <button
              className="md:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>

          {/* Mobile Search */}
          {!hideSearch && (
            <div className="md:hidden mt-2.5">
              <div className="relative w-full">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  className="input-premium w-full pl-10 pr-4 py-2.5 text-sm"
                />
              </div>
            </div>
          )}
        </div>

        {/* Mobile Drawer Menu */}
        {mobileMenuOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 top-0 bg-black/20 backdrop-blur-sm z-40 md:hidden animate-fade-in"
              onClick={() => setMobileMenuOpen(false)}
            />
            {/* Drawer */}
            <div className="absolute top-full left-0 right-0 z-50 md:hidden glass-white border-b border-slate-200 shadow-xl animate-fade-in-up">
              <div className="px-4 py-4 space-y-1">
                {navLinks.map(({ label, path, icon: Icon, badge }) => {
                  const active = isActive(path)
                  return (
                    <button
                      key={path}
                      onClick={() => { navigate(path); setMobileMenuOpen(false) }}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                        active
                          ? 'bg-indigo-50 text-indigo-700'
                          : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <Icon className={`h-5 w-5 ${active ? 'text-indigo-600' : 'text-slate-400'}`} />
                      {label}
                      {badge && (
                        <span className="ml-auto bg-indigo-100 text-indigo-700 text-xs rounded-full px-2 py-0.5 font-bold">
                          {badge}
                        </span>
                      )}
                    </button>
                  )
                })}
                <div className="pt-2 border-t border-slate-100">
                  <button
                    onClick={handleProfileClick}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold btn-gradient"
                  >
                    <User className="h-5 w-5" />
                    My Profile
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </header>

      {/* ===== MOBILE BOTTOM NAV ===== */}
      <nav className="mobile-bottom-nav" data-testid="mobile-bottom-nav">
        {bottomNavItems.map(({ label, path, icon: Icon, badge, action }) => {
          const active = path ? isActive(path) : isOnProfilePage
          return (
            <button
              key={label}
              onClick={() => {
                if (action) { action() }
                else { navigate(path); setMobileMenuOpen(false) }
              }}
              className={`mobile-nav-item ${active ? 'active' : ''}`}
              data-testid={`bottom-nav-${label.toLowerCase()}`}
            >
              <div className="relative">
                <Icon className={`h-5 w-5 transition-transform duration-200 ${active ? 'scale-110' : ''}`} />
                {badge && !active && (
                  <span className="absolute -top-1.5 -right-1.5 bg-indigo-600 text-white text-[9px] rounded-full h-3.5 w-3.5 flex items-center justify-center font-bold">
                    {badge}
                  </span>
                )}
              </div>
              <span className={`text-[10px] font-semibold leading-none transition-all duration-200 ${active ? 'text-indigo-600' : 'text-slate-400'}`}>
                {label}
              </span>
              {active && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-0.5 bg-indigo-600 rounded-full" />
              )}
            </button>
          )
        })}
      </nav>
    </>
  )
}
