import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Shield, Award, TrendingUp, Users, Package, ArrowRight, User } from 'lucide-react';
import { Button } from '../components/ui/Button';
import Footer from '../components/Footer';
import FloatingBadge from '../components/FloatingBadge';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  return (
    <div className="min-h-screen bg-white">
      {/* Floating Badge - Always visible */}
      <FloatingBadge />
      
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200">
        <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3" data-testid="landing-logo">
            <img 
              src="/UNIFIND.png" 
              alt="UNIFIND Logo" 
              className="h-12 w-auto"
            />
            <span className="font-['Outfit'] font-black text-2xl tracking-tight">
              <span className="text-blue-600">UNI</span>
              <span className="text-purple-600">FIND</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            {currentUser ? (
              // Show profile button when logged in
              <Button
                onClick={() => navigate('/profile')}
                className="bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95 flex items-center gap-2"
                data-testid="landing-profile-btn"
              >
                <User className="h-4 w-4" />
                Profile
              </Button>
            ) : (
              // Show login and signup when not logged in
              <>
                <Button
                  variant="ghost"
                  onClick={() => navigate('/login')}
                  className="text-slate-700 hover:text-blue-600"
                  data-testid="landing-login-btn"
                >
                  Login
                </Button>
                <Button
                  onClick={() => navigate('/signup')}
                  className="bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
                  data-testid="landing-signup-btn"
                >
                  Get Started
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-24 md:py-32 px-6 sm:px-8 md:px-12 lg:px-24">
        {/* SIGCE Only Banner - Floating on top */}
        <div className="absolute top-6 left-6 right-6 sm:left-8 sm:right-8 md:left-12 md:right-12 lg:left-24 lg:right-24 z-20">
          <div className="max-w-5xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl border border-blue-700 p-4 text-white shadow-2xl">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <h3 className="text-lg font-bold mb-1">🎓 Currently Open to SIGCE Only</h3>
                <p className="text-sm text-blue-100">
                  Exclusively available for Smt. Indira Gandhi College of Engineering students.
                </p>
              </div>
              <a
                href="https://sigce.edu.in/"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white text-blue-600 font-medium px-5 py-2.5 rounded-lg hover:bg-blue-50 transition-all duration-200 active:scale-95 inline-flex items-center gap-2 text-sm whitespace-nowrap"
                data-testid="sigce-link"
              >
                Visit SIGCE
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>

        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.pexels.com/photos/1454360/pexels-photo-1454360.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
            alt="Students"
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-white/50 to-white" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <div className="mb-6">
            <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600" data-testid="hero-overline">
              College Marketplace Platform
            </span>
          </div>
          <h1 className="font-['Outfit'] text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-none text-slate-900 mb-6" data-testid="hero-title">
            Buy & Sell on Campus
            <br />
            <span className="text-blue-600">Safely & Easily</span>
          </h1>
          <p className="text-lg leading-relaxed text-slate-700 max-w-2xl mx-auto mb-10" data-testid="hero-description">
            Join India's most trusted student marketplace. Buy, sell, and trade with verified college students. 
            AI-powered matching, trust scores, and instant chat.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              onClick={() => navigate('/signup')}
              className="bg-blue-600 text-white font-medium px-8 py-4 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95 text-lg"
              data-testid="hero-get-started-btn"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/buyer')}
              className="bg-white text-slate-700 font-medium px-8 py-4 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-lg transition-all duration-200"
              data-testid="hero-browse-btn"
            >
              Browse Listings
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 md:py-32 px-6 sm:px-8 md:px-12 lg:px-24 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight leading-tight text-slate-900 mb-4" data-testid="features-title">
              Why Choose UNIFIND?
            </h2>
            <p className="text-base leading-relaxed text-slate-600 max-w-2xl mx-auto">
              Built for students, by students. Experience the future of campus commerce.
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
            {/* AI Matching */}
            <div className="group bg-white rounded-2xl border border-slate-200 p-8 transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10" data-testid="feature-card-ai">
              <div className="bg-blue-50 h-14 w-14 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-100 transition-colors">
                <Sparkles className="h-7 w-7 text-blue-600" />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 mb-3">
                AI Matching
              </h3>
              <p className="text-base leading-relaxed text-slate-600">
                Describe what you need, our AI finds the perfect match from thousands of listings instantly.
              </p>
            </div>

            {/* Trust Score */}
            <div className="group bg-white rounded-2xl border border-slate-200 p-8 transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10" data-testid="feature-card-trust">
              <div className="bg-green-50 h-14 w-14 rounded-xl flex items-center justify-center mb-6 group-hover:bg-green-100 transition-colors">
                <Shield className="h-7 w-7 text-green-600" />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 mb-3">
                Trust Score
              </h3>
              <p className="text-base leading-relaxed text-slate-600">
                Every user has a verified trust score based on transactions, reviews, and campus verification.
              </p>
            </div>

            {/* Condition Grading */}
            <div className="group bg-white rounded-2xl border border-slate-200 p-8 transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10" data-testid="feature-card-grading">
              <div className="bg-amber-50 h-14 w-14 rounded-xl flex items-center justify-center mb-6 group-hover:bg-amber-100 transition-colors">
                <Award className="h-7 w-7 text-amber-600" />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 mb-3">
                Condition Grading
              </h3>
              <p className="text-base leading-relaxed text-slate-600">
                Standardized product condition ratings ensure you know exactly what you're buying.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 md:py-32 px-6 sm:px-8 md:px-12 lg:px-24">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="stat-card-users">
              <Users className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-2">8,934</div>
              <div className="text-sm text-slate-500">Active Users</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="stat-card-listings">
              <Package className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-2">1,247</div>
              <div className="text-sm text-slate-500">Total Listings</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="stat-card-deals">
              <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-2">3,421</div>
              <div className="text-sm text-slate-500">Successful Deals</div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center" data-testid="stat-card-rating">
              <Award className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <div className="text-3xl font-black text-slate-900 mb-2">4.7</div>
              <div className="text-sm text-slate-500">Avg Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 md:py-32 px-6 sm:px-8 md:px-12 lg:px-24 bg-gradient-to-br from-blue-600 to-blue-700">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight leading-tight text-white mb-6" data-testid="cta-title">
            Ready to Start Trading?
          </h2>
          <p className="text-lg leading-relaxed text-blue-100 mb-10">
            Join thousands of students buying and selling on campus
          </p>
          <Button
            onClick={() => navigate('/signup')}
            className="bg-white text-blue-600 font-medium px-8 py-4 rounded-xl hover:bg-blue-50 transition-all duration-200 active:scale-95 text-lg"
            data-testid="cta-signup-btn"
          >
            Create Free Account
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default LandingPage;
