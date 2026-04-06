import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Search, ShoppingBag, MessageCircle, User, Menu, X, LayoutDashboard, Sparkles, Package, UserPlus, Bell, CheckCircle, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { getUserChats, searchUsers, getPendingFriendRequests, acceptFriendRequest, rejectFriendRequest } from '../services/api'

export default function Header({ hideSearch = false }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser } = useAuth()
  const { darkMode } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [friendRequests, setFriendRequests] = useState([])
  const [requestsLoading, setRequestsLoading] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const searchRef = useRef(null)

  // Fetch unread message count
  useEffect(() => {
    if (!currentUser?.uid) return;

    const fetchUnreadCount = async () => {
      try {
        const chats = await getUserChats(currentUser.uid);
        const totalUnread = chats.reduce((sum, chat) => {
          const count = chat.user1_id === currentUser.uid 
            ? chat.unread_count_user1 
            : chat.unread_count_user2;
          return sum + count;
        }, 0);
        setUnreadCount(totalUnread);
      } catch (error) {
        console.error('Failed to fetch unread count:', error);
      }
    };

    fetchUnreadCount();
    
    // Poll for updates every 10 seconds
    const interval = setInterval(fetchUnreadCount, 10000);
    return () => clearInterval(interval);
  }, [currentUser]);

  const handleProfileClick = () => {
    if (currentUser?.uid) {
      navigate(`/profile/${currentUser.uid}`)
    } else {
      navigate('/profile')
    }
    setMobileMenuOpen(false)
  }

  // Handle user search
  const handleSearch = async (query) => {
    setSearchQuery(query)
    
    if (query.trim().length < 2) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }

    setSearchLoading(true)
    try {
      const results = await searchUsers(query.trim())
      setSearchResults(results)
      setShowSearchResults(true)
    } catch (error) {
      console.error('Search failed:', error)
      setSearchResults([])
    } finally {
      setSearchLoading(false)
    }
  }

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSearchResults(false)
        setShowNotifications(false)
      }
    }

    const handleKeyDown = (event) => {
      // Don't close dropdown on Shift, Backspace, or any typing keys
      if (event.key === 'Escape') {
        setShowSearchResults(false)
        setShowNotifications(false)
      }
    }

    if (showSearchResults) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('keydown', handleKeyDown)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [showSearchResults])

  // Fetch friend requests
  const fetchFriendRequests = async () => {
    if (!currentUser?.uid) return
    
    try {
      const requests = await getPendingFriendRequests(currentUser.uid)
      setFriendRequests(requests)
    } catch (error) {
      console.error('Failed to fetch friend requests:', error)
    }
  }

  useEffect(() => {
    fetchFriendRequests()
    
    // Poll for new requests every 30 seconds
    const interval = setInterval(fetchFriendRequests, 30000)
    return () => clearInterval(interval)
  }, [currentUser])

  const handleAcceptRequest = async (friendId) => {
    if (!currentUser?.uid) return
    
    setRequestsLoading(true)
    try {
      await acceptFriendRequest(currentUser.uid, friendId)
      await fetchFriendRequests()
      setSuccessMessage('Friend request accepted!')
      setShowSuccessModal(true)
    } catch (error) {
      console.error('Failed to accept request:', error)
      setErrorMessage('Failed to accept friend request. Please try again.')
      setShowErrorModal(true)
    } finally {
      setRequestsLoading(false)
    }
  }

  const handleRejectRequest = async (friendId) => {
    if (!currentUser?.uid) return
    
    setRequestsLoading(true)
    try {
      await rejectFriendRequest(currentUser.uid, friendId)
      await fetchFriendRequests()
      setSuccessMessage('Friend request declined')
      setShowSuccessModal(true)
    } catch (error) {
      console.error('Failed to reject request:', error)
      setErrorMessage('Failed to decline friend request. Please try again.')
      setShowErrorModal(true)
    } finally {
      setRequestsLoading(false)
    }
  }

  const handleUserClick = (userId) => {
    navigate(`/profile/${userId}`)
    setShowSearchResults(false)
    setSearchQuery('')
    setSearchResults([])
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
    { label: 'Chats', path: '/chat', icon: MessageCircle, badge: unreadCount },
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  ]

  // Bottom nav items (mobile only)
  const bottomNavItems = [
    { label: 'Buy', path: '/buyer', icon: ShoppingBag },
    { label: 'Sell', path: '/seller', icon: Package },
    { label: 'NeedBoard', path: '/need-board', icon: Sparkles },
    { label: 'Chats', path: '/chat', icon: MessageCircle, badge: unreadCount },
    { label: 'Profile', path: null, icon: User, action: handleProfileClick },
  ]

  return (
    <>
      {/* ===== TOP HEADER ===== */}
      <header className={`sticky top-0 z-50 backdrop-blur-md border-b ${darkMode ? 'bg-slate-800/95 border-slate-700/80' : 'bg-white/95 border-slate-200/80'}`}>
        <div className="px-4 sm:px-6 md:px-10 lg:px-20 py-2 sm:py-3">
          <div className="flex items-center justify-between gap-4">

            {/* Logo */}
            <Link
              to="/home"
              className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity flex-shrink-0"
              data-testid="header-logo"
            >
              <img src="/UNIFIND.png" alt="UNIFIND Logo" className="h-10 sm:h-14 md:h-16 w-auto" />
              <span className="font-['Outfit'] font-black text-2xl sm:text-3xl md:text-4xl tracking-tight">
                <span className="text-indigo-600">UNI</span>
                <span className="text-violet-600">FIND</span>
              </span>
            </Link>

            {/* Search Bar - Desktop */}
            {!hideSearch && (
              <div className="hidden lg:flex flex-1 max-w-sm lg:max-w-md mx-4">
                <div className="relative w-full">
                  <Search className={`absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                  <input
                    type="text"
                    placeholder="Search products..."
                    className={`input-premium w-full pl-10 pr-4 py-2.5 text-[16px] sm:text-sm ${darkMode ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400' : ''}`}
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
                        ? darkMode ? 'bg-indigo-900/50 text-indigo-300' : 'bg-indigo-50 text-indigo-600'
                        : darkMode ? 'text-slate-300 hover:bg-slate-700 hover:text-indigo-400' : 'text-slate-600 hover:bg-slate-100 hover:text-slateigo-600'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                    {badge > 0 && !active && (
                      <span className="absolute -top-0.5 -right-0.5 bg-indigo-600 text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center font-bold">
                        {badge}
                      </span>
                    )}
                  </button>
                )
              })}

              {/* Notifications Bell - Removed from here */}

              {/* User Search Button */}
              <div className="relative ml-2" ref={searchRef}>
                <button
                  onClick={() => {
                    setShowSearchResults(!showSearchResults)
                    if (!showSearchResults) fetchFriendRequests()
                  }}
                  className={`relative flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    darkMode ? 'text-slate-300 hover:bg-slate-700 hover:text-indigo-400' : 'text-slate-600 hover:bg-slate-100 hover:text-indigo-600'
                  }`}
                  title="Find Users & Notifications"
                >
                  <UserPlus className="h-4 w-4" />
                  <span className="hidden xl:inline">Find Users</span>
                  {friendRequests.length > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-600 text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center font-bold">
                      {friendRequests.length}
                    </span>
                  )}
                </button>

                {/* User Search & Notifications Dropdown */}
                {showSearchResults && (
                  <div className={`absolute top-full right-0 mt-2 w-96 rounded-xl shadow-xl border z-50 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                    {/* Tabs */}
                    <div className={`flex border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                      <button
                        onClick={() => setShowNotifications(false)}
                        className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                          !showNotifications
                            ? darkMode 
                              ? 'text-indigo-400 border-b-2 border-indigo-400' 
                              : 'text-indigo-600 border-b-2 border-indigo-600'
                            : darkMode ? 'text-slate-400 hover:text-slate-300' : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        Search Users
                      </button>
                      <button
                        onClick={() => setShowNotifications(true)}
                        className={`relative flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                          showNotifications
                            ? darkMode 
                              ? 'text-indigo-400 border-b-2 border-indigo-400' 
                              : 'text-indigo-600 border-b-2 border-indigo-600'
                            : darkMode ? 'text-slate-400 hover:text-slate-300' : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        Notifications
                        {friendRequests.length > 0 && (
                          <span className="ml-1.5 bg-red-600 text-white text-[10px] rounded-full px-1.5 py-0.5 font-bold">
                            {friendRequests.length}
                          </span>
                        )}
                      </button>
                    </div>

                    {/* Search Tab Content */}
                    {!showNotifications && (
                      <>
                        <div className={`p-3 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                          <div className="relative">
                            <Search className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                            <input
                              type="text"
                              placeholder="Search users..."
                              value={searchQuery}
                              onChange={(e) => handleSearch(e.target.value)}
                              onFocus={() => setShowSearchResults(true)}
                              autoFocus
                              className={`w-full pl-9 pr-3 py-2 rounded-lg border outline-none text-sm ${
                                darkMode 
                                  ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-indigo-500' 
                                  : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20'
                              }`}
                            />
                          </div>
                        </div>
                        <div className="max-h-96 overflow-y-auto">
                          {searchLoading ? (
                            <div className="p-4 text-center">
                              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div>
                            </div>
                          ) : searchResults.length > 0 ? (
                            <div className="py-2">
                              {searchResults.map((user) => (
                                <button
                                  key={user.id}
                                  onClick={() => handleUserClick(user.id)}
                                  className={`w-full px-4 py-3 flex items-center gap-3 transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}
                                >
                                  <img
                                    src={user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}`}
                                    alt={user.name}
                                    className="h-10 w-10 rounded-full object-cover"
                                  />
                                  <div className="flex-1 text-left">
                                    <p className={`font-semibold text-sm ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{user.name}</p>
                                    {user.college && (
                                      <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{user.college}</p>
                                    )}
                                  </div>
                                </button>
                              ))}
                            </div>
                          ) : searchQuery.length >= 2 ? (
                            <div className="p-4 text-center">
                              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>No users found</p>
                            </div>
                          ) : (
                            <div className="p-8 text-center">
                              <UserPlus className={`h-12 w-12 mx-auto mb-3 ${darkMode ? 'text-slate-600' : 'text-slate-300'}`} />
                              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Type to search users...</p>
                            </div>
                          )}
                        </div>
                      </>
                    )}

                    {/* Notifications Tab Content */}
                    {showNotifications && (
                      <div className="max-h-96 overflow-y-auto">
                        {friendRequests.length > 0 ? (
                          <div className="py-2">
                            {friendRequests.map((request) => (
                              <div
                                key={request.id}
                                className={`px-4 py-3 border-b last:border-b-0 ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}
                              >
                                <div className="flex items-center gap-3 mb-3">
                                  <img
                                    src={request.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(request.name || 'User')}`}
                                    alt={request.name}
                                    className="h-10 w-10 rounded-full object-cover cursor-pointer"
                                    onClick={() => {
                                      navigate(`/profile/${request.id}`)
                                      setShowSearchResults(false)
                                    }}
                                  />
                                  <div className="flex-1">
                                    <p 
                                      className={`font-semibold text-sm cursor-pointer hover:text-indigo-600 ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}
                                      onClick={() => {
                                        navigate(`/profile/${request.id}`)
                                        setShowSearchResults(false)
                                      }}
                                    >
                                      {request.name}
                                    </p>
                                    {request.college && (
                                      <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{request.college}</p>
                                    )}
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => handleAcceptRequest(request.id)}
                                    disabled={requestsLoading}
                                    className="flex-1 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-all disabled:opacity-50"
                                  >
                                    Accept
                                  </button>
                                  <button
                                    onClick={() => handleRejectRequest(request.id)}
                                    disabled={requestsLoading}
                                    className={`flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
                                      darkMode 
                                        ? 'bg-slate-700 hover:bg-slate-600 text-slate-200' 
                                        : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                                    }`}
                                  >
                                    Decline
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-8 text-center">
                            <Bell className={`h-12 w-12 mx-auto mb-3 ${darkMode ? 'text-slate-600' : 'text-slate-300'}`} />
                            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>No pending friend requests</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

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

            {/* Mobile Top-Right Action */}
            {isOnChatPage ? (
              <button
                className={`md:hidden p-2 rounded-xl transition-colors ${darkMode ? 'text-slate-300 hover:bg-slate-700' : 'text-slate-600 hover:bg-slate-100'}`}
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                data-testid="mobile-menu-btn"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            ) : (
              <button
                className={`md:hidden p-2 rounded-xl transition-colors ${darkMode ? 'text-indigo-400 hover:bg-slate-700' : 'text-indigo-600 hover:bg-indigo-50'}`}
                onClick={() => navigate('/dashboard')}
                data-testid="mobile-dashboard-btn"
                aria-label="Dashboard"
              >
                <LayoutDashboard className="h-5 w-5" />
              </button>
            )}
          </div>

          {/* Mobile Search */}
          {!hideSearch && (
            <div className="lg:hidden mt-2.5">
              <div className="relative w-full">
                <Search className={`absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                <input
                  type="text"
                  placeholder="Search products..."
                  className={`input-premium w-full pl-10 pr-4 py-2.5 text-[16px] sm:text-sm ${darkMode ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400' : ''}`}
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
              className="absolute top-full left-0 w-screen h-[100dvh] bg-black/40 z-40 md:hidden animate-fade-in"
              onClick={() => setMobileMenuOpen(false)}
            />
            {/* Drawer */}
            <div className={`absolute top-full left-0 right-0 z-50 md:hidden border-b shadow-xl animate-fade-in-up max-h-[calc(100dvh-80px)] overflow-y-auto ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
              <div className="px-4 py-4 space-y-1">
                {navLinks.map(({ label, path, icon: Icon, badge }) => {
                  const active = isActive(path)
                  return (
                    <button
                      key={path}
                      onClick={() => { navigate(path); setMobileMenuOpen(false) }}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                        active
                          ? darkMode ? 'bg-indigo-900/50 text-indigo-300' : 'bg-indigo-50 text-indigo-700'
                          : darkMode ? 'text-slate-300 hover:bg-slate-700' : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <Icon className={`h-5 w-5 ${active ? (darkMode ? 'text-indigo-400' : 'text-indigo-600') : (darkMode ? 'text-slate-500' : 'text-slate-400')}`} />
                      {label}
                      {badge > 0 && (
                        <span className={`ml-auto text-xs rounded-full px-2 py-0.5 font-bold ${darkMode ? 'bg-indigo-900 text-indigo-300' : 'bg-indigo-100 text-indigo-700'}`}>
                          {badge}
                        </span>
                      )}
                    </button>
                  )
                })}
                <div className={`pt-2 border-t ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
                  {/* User Search in Mobile */}
                  <button
                    onClick={() => setShowSearchResults(!showSearchResults)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 mb-2 ${
                      darkMode ? 'text-slate-300 hover:bg-slate-700' : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <UserPlus className={`h-5 w-5 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                    Find Users
                  </button>

                  {/* Mobile User Search Dropdown */}
                  {showSearchResults && (
                    <div className={`mb-3 rounded-xl border ${darkMode ? 'bg-slate-700 border-slate-600' : 'bg-slate-50 border-slate-200'}`}>
                      <div className="p-3">
                        <div className="relative">
                          <Search className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                          <input
                            type="text"
                            placeholder="Search users..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            onFocus={() => setShowSearchResults(true)}
                            className={`w-full pl-9 pr-3 py-2 rounded-lg border outline-none text-sm ${
                              darkMode 
                                ? 'bg-slate-800 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-indigo-500' 
                                : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20'
                            }`}
                          />
                        </div>
                      </div>
                      <div className="max-h-60 overflow-y-auto">
                        {searchLoading ? (
                          <div className="p-4 text-center">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div>
                          </div>
                        ) : searchResults.length > 0 ? (
                          <div className="pb-2">
                            {searchResults.map((user) => (
                              <button
                                key={user.id}
                                onClick={() => {
                                  handleUserClick(user.id)
                                  setMobileMenuOpen(false)
                                }}
                                className={`w-full px-4 py-3 flex items-center gap-3 transition-colors ${darkMode ? 'hover:bg-slate-600' : 'hover:bg-slate-100'}`}
                              >
                                <img
                                  src={user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}`}
                                  alt={user.name}
                                  className="h-10 w-10 rounded-full object-cover"
                                />
                                <div className="flex-1 text-left">
                                  <p className={`font-semibold text-sm ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{user.name}</p>
                                  {user.college && (
                                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{user.college}</p>
                                  )}
                                </div>
                              </button>
                            ))}
                          </div>
                        ) : searchQuery.length >= 2 ? (
                          <div className="p-4 text-center">
                            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>No users found</p>
                          </div>
                        ) : (
                          <div className="p-4 text-center">
                            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Type to search users...</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

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
      {!isOnChatPage && (
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
                  {badge > 0 && !active && (
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
      )}

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className={`w-full max-w-md rounded-2xl shadow-xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`}>
            <div className="p-6 text-center">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h3 className={`text-xl font-bold mb-2 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                Success!
              </h3>
              <p className={`text-sm mb-6 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                {successMessage}
              </p>
              <button
                onClick={() => setShowSuccessModal(false)}
                className="w-full px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className={`w-full max-w-md rounded-2xl shadow-xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`}>
            <div className="p-6 text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
              <h3 className={`text-xl font-bold mb-2 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                Error
              </h3>
              <p className={`text-sm mb-6 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                {errorMessage}
              </p>
              <button
                onClick={() => setShowErrorModal(false)}
                className="w-full px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
