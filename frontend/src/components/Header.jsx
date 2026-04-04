import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, ShoppingBag, MessageCircle, User, Menu } from 'lucide-react'
import { Button } from './ui/Button'

export default function Header({ hideSearch = false }) {
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200">
      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-4">
        <div className="flex items-center justify-between gap-4">
          <Link 
            to="/" 
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            data-testid="header-logo"
          >
            <img 
              src="/UNIFIND.png" 
              alt="UNIFIND Logo" 
              className="h-8 w-auto"
            />
          </Link>

          {!hideSearch && (
            <div className="hidden md:flex flex-1 max-w-xl mx-8">
              <div className="relative w-full">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  className="w-full rounded-xl border border-slate-200 pl-12 pr-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  data-testid="header-search-input"
                />
              </div>
            </div>
          )}

          <nav className="hidden md:flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/buyer')}
              className="text-slate-700 hover:text-blue-600 transition-colors"
              data-testid="nav-buy-btn"
            >
              <ShoppingBag className="h-4 w-4 mr-2" />
              Buy
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/seller')}
              className="text-slate-700 hover:text-blue-600 transition-colors"
              data-testid="nav-sell-btn"
            >
              Sell
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/chat')}
              className="text-slate-700 hover:text-blue-600 transition-colors relative"
              data-testid="nav-chat-btn"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Chats
              <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center" data-testid="chat-notification-badge">2</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/profile')}
              className="text-slate-700 hover:text-blue-600 transition-colors"
              data-testid="nav-profile-btn"
            >
              <User className="h-4 w-4 mr-2" />
              Profile
            </Button>
            <Button
              onClick={() => navigate('/post-listing')}
              className="bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95 ml-2"
              data-testid="header-post-listing-btn"
            >
              Post Listing
            </Button>
          </nav>

          <button
            className="md:hidden p-2 text-slate-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-btn"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-slate-200 pt-4" data-testid="mobile-menu">
            <nav className="flex flex-col gap-2">
              <Button
                variant="ghost"
                onClick={() => { navigate('/buyer'); setMobileMenuOpen(false) }}
                className="justify-start text-slate-700"
                data-testid="mobile-nav-buy-btn"
              >
                <ShoppingBag className="h-4 w-4 mr-2" />
                Buy
              </Button>
              <Button
                variant="ghost"
                onClick={() => { navigate('/seller'); setMobileMenuOpen(false) }}
                className="justify-start text-slate-700"
                data-testid="mobile-nav-sell-btn"
              >
                Sell
              </Button>
              <Button
                variant="ghost"
                onClick={() => { navigate('/chat'); setMobileMenuOpen(false) }}
                className="justify-start text-slate-700"
                data-testid="mobile-nav-chat-btn"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Chats
              </Button>
              <Button
                variant="ghost"
                onClick={() => { navigate('/profile'); setMobileMenuOpen(false) }}
                className="justify-start text-slate-700"
                data-testid="mobile-nav-profile-btn"
              >
                <User className="h-4 w-4 mr-2" />
                Profile
              </Button>
              <Button
                onClick={() => { navigate('/post-listing'); setMobileMenuOpen(false) }}
                className="bg-blue-600 text-white mt-2"
                data-testid="mobile-post-listing-btn"
              >
                Post Listing
              </Button>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
