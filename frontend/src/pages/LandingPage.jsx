import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Shield, Award, TrendingUp, Users, Package, ArrowRight, User, Star, Zap, BookOpen, CheckCircle } from 'lucide-react';
import Footer from '../components/Footer';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const heroRef = useRef(null);

  // Floating orb animation using CSS only — no heavy libs

  const features = [
    {
      icon: Sparkles,
      title: 'AI Matching',
      desc: 'Describe what you need, our AI finds the perfect match from thousands of listings instantly.',
      gradient: 'from-violet-500 to-indigo-600',
      bg: 'bg-violet-50',
      iconColor: 'text-violet-600',
    },
    {
      icon: Shield,
      title: 'Trust Score',
      desc: 'Every user has a verified trust score based on transactions, reviews, and campus verification.',
      gradient: 'from-emerald-500 to-teal-600',
      bg: 'bg-emerald-50',
      iconColor: 'text-emerald-600',
    },
    {
      icon: Award,
      title: 'Condition Grading',
      desc: 'Standardized product condition ratings ensure you know exactly what you\'re buying.',
      gradient: 'from-amber-500 to-orange-500',
      bg: 'bg-amber-50',
      iconColor: 'text-amber-600',
    },
    {
      icon: Zap,
      title: 'Instant Chat',
      desc: 'Reach sellers instantly with our built-in chat system. No waiting, no delays.',
      gradient: 'from-blue-500 to-cyan-500',
      bg: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      icon: BookOpen,
      title: 'Need Board',
      desc: 'Post what you need, let sellers find you. AI-powered matching for your perfect deal.',
      gradient: 'from-pink-500 to-rose-500',
      bg: 'bg-pink-50',
      iconColor: 'text-pink-600',
    },
    {
      icon: CheckCircle,
      title: 'Verified Students',
      desc: 'Only verified college students. Safe, secure, and scam-free campus commerce.',
      gradient: 'from-indigo-500 to-purple-600',
      bg: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
    },
  ];

  const stats = [
    { icon: Users, value: '8,934', label: 'Active Students', color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { icon: Package, value: '1,247', label: 'Total Listings', color: 'text-violet-600', bg: 'bg-violet-50' },
    { icon: TrendingUp, value: '3,421', label: 'Deals Completed', color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { icon: Star, value: '4.7★', label: 'Average Rating', color: 'text-amber-600', bg: 'bg-amber-50' },
  ];

  const testimonials = [
    { name: 'Riya Sharma', branch: 'Computer Engg', text: 'Sold my old laptop in 2 hours! The trust score system made everyone feel safe.', rating: 5 },
    { name: 'Arjun Patel', branch: 'AI & Data Science', text: 'Found exactly what I needed through NeedBoard AI. Unbelievably fast!', rating: 5 },
    { name: 'Priya Desai', branch: 'Electrical Engg', text: 'The barcode scanner for textbooks is genius. Saved so much time searching.', rating: 5 },
  ];

  return (
    <div className="min-h-[100dvh] bg-slate-900 overflow-x-hidden">

      {/* ===== NAVBAR ===== */}
      <header className="sticky top-0 z-50 glass-dark border-b border-white/10">
        <div className="px-3 sm:px-4 md:px-6 lg:px-10 xl:px-20 py-2.5 sm:py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3" data-testid="landing-logo">
            <img src="/UNIFIND.png" alt="UNIFIND Logo" className="h-12 sm:h-14 md:h-16 w-auto" />
            <span className="font-['Outfit'] font-black text-2xl sm:text-3xl md:text-4xl tracking-tight">
              <span className="text-indigo-400">UNI</span>
              <span className="text-violet-400">FIND</span>
            </span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            {currentUser ? (
              <button
                onClick={() => navigate('/profile')}
                className="btn-gradient px-3 sm:px-4 md:px-5 py-1.5 sm:py-2 text-xs sm:text-sm flex items-center gap-1.5 sm:gap-2"
                data-testid="landing-profile-btn"
              >
                <User className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Profile</span>
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="px-2.5 sm:px-3 md:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-lg sm:rounded-xl transition-all duration-200"
                  data-testid="landing-login-btn"
                >
                  Login
                </button>
                <button
                  onClick={() => navigate('/signup')}
                  className="btn-gradient px-3 sm:px-4 md:px-5 py-1.5 sm:py-2 text-xs sm:text-sm"
                  data-testid="landing-signup-btn"
                >
                  <span className="hidden sm:inline">Get Started</span>
                  <span className="sm:hidden">Sign Up</span>
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ===== HERO SECTION ===== */}
      <section className="relative overflow-hidden pt-4 pb-20 md:pb-28 lg:pb-40 px-4 sm:px-6 md:px-10 lg:px-20 bg-gradient-hero min-h-[80vh] md:min-h-[85vh] flex flex-col justify-center">
        {/* Decorative orbs */}
        <div className="absolute top-0 left-1/4 w-[450px] h-[450px] bg-indigo-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-[350px] h-[350px] bg-violet-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-0 w-72 h-72 bg-blue-600/15 rounded-full blur-3xl pointer-events-none" />

        {/* SIGCE Banner */}
        <div className="relative z-10 flex justify-center mb-4 md:mb-6">
          <div className="glass border border-indigo-500/40 rounded-xl md:rounded-2xl px-3 py-2.5 md:px-5 md:py-3.5 inline-flex items-center gap-2 md:gap-3 animate-fade-in-up shadow-xl max-w-full">
            <span className="text-xl md:text-2xl lg:text-3xl flex-shrink-0">🎓</span>
            <div className="flex-1 min-w-0">
              <p className="text-white font-bold text-xs sm:text-sm md:text-base">Currently Open to SIGCE Students</p>
              <p className="text-slate-400 text-[10px] sm:text-xs md:text-sm hidden sm:block">Exclusively for Smt. Indira Gandhi College of Engineering</p>
            </div>
            <a
              href="https://sigce.edu.in/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white text-xs md:text-sm font-semibold px-3 py-1.5 md:px-4 md:py-2 rounded-lg md:rounded-xl transition-all duration-200 active:scale-95 whitespace-nowrap shadow-lg hover:shadow-xl"
              data-testid="sigce-link"
            >
              Visit
            </a>
          </div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center" ref={heroRef}>
          <div className="mb-3 md:mb-4 animate-fade-in-up animate-delay-100">
            <span className="inline-flex items-center gap-1.5 md:gap-2 bg-indigo-900/60 border border-indigo-500/40 rounded-full px-3 py-1.5 md:px-5 md:py-2.5 text-[10px] sm:text-xs md:text-sm lg:text-base font-bold uppercase tracking-widest text-indigo-300 shadow-lg">
              <Sparkles className="h-3 w-3 md:h-4 md:w-4 lg:h-5 lg:w-5" />
              AI-Powered College Marketplace
            </span>
          </div>

          <h1
            className="font-['Outfit'] text-3xl sm:text-4xl md:text-5xl lg:text-7xl xl:text-8xl font-black tracking-tight leading-[1.1] mb-3 md:mb-4 lg:mb-5 animate-fade-in-up animate-delay-200 px-2"
            data-testid="hero-title"
          >
            <span className="text-white">Buy &amp; Sell </span>
            <br />
            <span className="gradient-text-hero">on Campus</span>
            <br />
            <span className="text-white text-xl sm:text-2xl md:text-3xl lg:text-5xl xl:text-6xl font-bold">Safely &amp; Easily</span>
          </h1>

          <p
            className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl leading-relaxed text-slate-300 max-w-3xl mx-auto mb-6 md:mb-8 lg:mb-12 animate-fade-in-up animate-delay-300 px-4"
            data-testid="hero-description"
          >
            India's most trusted student marketplace. Buy, sell, and trade with verified college students.
            <span className="text-indigo-400 font-semibold"> AI-powered matching</span>, trust scores, and instant chat.
          </p>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 md:gap-4 lg:gap-5 animate-fade-in-up animate-delay-400 px-4">
            <button
              onClick={() => navigate('/signup')}
              className="btn-gradient w-full sm:w-auto px-6 py-3 md:px-8 md:py-3.5 lg:px-9 lg:py-4 text-sm md:text-base lg:text-lg font-bold flex items-center justify-center gap-2 shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 hover:scale-105"
              data-testid="hero-get-started-btn"
            >
              Get Started Free
              <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
            </button>
            <button
              onClick={() => navigate('/buyer')}
              className="w-full sm:w-auto glass border border-white/20 text-white font-bold px-6 py-3 md:px-8 md:py-3.5 lg:px-9 lg:py-4 rounded-xl text-sm md:text-base lg:text-lg hover:bg-white/10 transition-all duration-300 active:scale-95 shadow-xl hover:shadow-2xl"
              data-testid="hero-browse-btn"
            >
              Browse Listings
            </button>
          </div>

          {/* Social Proof */}
          <div className="mt-8 md:mt-12 lg:mt-16 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6 animate-fade-in-up animate-delay-500 px-4">
            <div className="flex -space-x-2">
              {['bg-indigo-500', 'bg-violet-500', 'bg-emerald-500', 'bg-blue-500'].map((c, i) => (
                <div key={i} className={`h-8 w-8 md:h-10 md:w-10 lg:h-11 lg:w-11 ${c} rounded-full border-2 md:border-3 border-slate-900 flex items-center justify-center text-white text-sm md:text-base lg:text-lg font-bold shadow-lg`}>
                  {['R', 'A', 'P', 'S'][i]}
                </div>
              ))}
            </div>
            <p className="text-slate-300 text-xs sm:text-sm md:text-base text-center sm:text-left">
              <span className="text-white font-bold text-base sm:text-lg md:text-xl">8,900+</span> students already joined
            </p>
          </div>
        </div>
      </section>

      {/* ===== STATS SECTION ===== */}
      <section className="py-16 px-4 sm:px-6 md:px-10 lg:px-20 bg-slate-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            {stats.map(({ icon: Icon, value, label, color, bg }, i) => (
              <div
                key={label}
                className="glass border border-white/10 rounded-2xl p-6 text-center hover:border-indigo-500/40 transition-all duration-300 hover:-translate-y-1"
                style={{ animationDelay: `${i * 100}ms` }}
                data-testid={`stat-card-${label.toLowerCase().replace(' ', '-')}`}
              >
                <div className={`${bg} h-12 w-12 rounded-xl flex items-center justify-center mx-auto mb-3`}>
                  <Icon className={`h-6 w-6 ${color}`} />
                </div>
                <div className="text-2xl sm:text-3xl font-black text-white mb-1">{value}</div>
                <div className="text-xs text-slate-400">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FEATURES SECTION ===== */}
      <section className="py-16 md:py-20 px-4 sm:px-6 md:px-10 lg:px-20 bg-slate-900" data-testid="features-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block bg-indigo-900/60 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4">
              Why UNIFIND
            </span>
            <h2
              className="font-['Outfit'] text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mb-4"
              data-testid="features-title"
            >
              Everything you need to{' '}
              <span className="gradient-text-hero">trade on campus</span>
            </h2>
            <p className="text-slate-400 text-base max-w-2xl mx-auto">
              Built for students, by students. Experience the future of campus commerce.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6">
            {features.map(({ icon: Icon, title, desc, gradient, bg, iconColor }, i) => (
              <div
                key={title}
                className="group glass border border-white/10 rounded-2xl p-6 hover:border-indigo-500/40 transition-all duration-300 hover:-translate-y-1 hover:bg-white/5"
                data-testid={`feature-card-${title.toLowerCase().replace(' ', '-')}`}
              >
                <div className={`${bg} h-12 w-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className={`h-6 w-6 ${iconColor}`} />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section className="py-20 px-4 sm:px-6 md:px-10 lg:px-20 bg-slate-800/40">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="font-['Outfit'] text-3xl sm:text-4xl font-black text-white mb-3">
              Loved by <span className="gradient-text-hero">Students</span>
            </h2>
            <p className="text-slate-400">See what your fellow students are saying</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {testimonials.map(({ name, branch, text, rating }, i) => (
              <div key={name} className="glass border border-white/10 rounded-2xl p-6 hover:border-indigo-500/30 transition-all duration-300">
                <div className="flex items-center gap-1 mb-4">
                  {Array.from({ length: rating }).map((_, j) => (
                    <Star key={j} className="h-4 w-4 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-slate-300 text-sm leading-relaxed mb-5">"{text}"</p>
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {name[0]}
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold">{name}</p>
                    <p className="text-slate-500 text-xs">{branch}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CTA SECTION ===== */}
      <section className="py-20 px-4 sm:px-6 md:px-10 lg:px-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-primary opacity-90" />
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-1/2 -left-1/4 w-80 h-80 bg-white/5 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10 max-w-3xl mx-auto text-center">
          <h2
            className="font-['Outfit'] text-3xl sm:text-4xl lg:text-5xl font-black text-white mb-5"
            data-testid="cta-title"
          >
            Ready to Start Trading?
          </h2>
          <p className="text-lg text-indigo-100 mb-10">
            Join thousands of students buying and selling safely on campus
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/signup')}
              className="w-full sm:w-auto bg-white text-indigo-600 font-bold px-8 py-4 rounded-xl text-base hover:bg-slate-50 transition-all duration-200 active:scale-95 flex items-center justify-center gap-2"
              data-testid="cta-signup-btn"
            >
              Create Free Account
              <ArrowRight className="h-5 w-5" />
            </button>
            <button
              onClick={() => navigate('/buyer')}
              className="w-full sm:w-auto glass border border-white/30 text-white font-semibold px-8 py-4 rounded-xl text-base hover:bg-white/10 transition-all duration-200 active:scale-95"
            >
              Browse Listings
            </button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage;

