import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Mail, Lock, User, GraduationCap, Eye, EyeOff, Calendar } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { sendEmailVerification } from 'firebase/auth';
import { auth, actionCodeSettings } from '../services/firebase';

const SignupPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { signup } = useAuth();
  
  // Get pre-filled data from login page if available
  const prefilledEmail = location.state?.email || '';
  const prefilledPassword = location.state?.password || '';
  
  const [formData, setFormData] = useState({ 
    name: '', 
    email: prefilledEmail, 
    college: '', 
    yearOfAdmission: '',
    password: prefilledPassword 
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showCollegeDropdown, setShowCollegeDropdown] = useState(false);
  const [collegeSearch, setCollegeSearch] = useState('');
  const [collegeSelected, setCollegeSelected] = useState(false);
  const [showYearDropdown, setShowYearDropdown] = useState(false);

  // List of colleges
  const colleges = [
    'Smt. Indira Gandhi College of Engineering (SIGCE)',
    'Other'
  ];

  // Generate years from current year back to 10 years
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 10 }, (_, i) => currentYear - i);

  // Filter colleges based on search
  const filteredColleges = colleges.filter(college =>
    college.toLowerCase().includes(collegeSearch.toLowerCase())
  );

  const handleCollegeSelect = (college) => {
    setFormData({ ...formData, college });
    setCollegeSearch(college);
    setShowCollegeDropdown(false);
    setCollegeSelected(true);
  };

  const handleCollegeClear = () => {
    setFormData({ ...formData, college: '' });
    setCollegeSearch('');
    setCollegeSelected(false);
    setShowCollegeDropdown(true);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate that a college was selected from the dropdown
    if (!collegeSelected || !formData.college) {
      setError('Please select a college from the dropdown list.');
      return;
    }

    // Validate that year of admission is selected
    if (!formData.yearOfAdmission) {
      setError('Please select your year of admission.');
      return;
    }
    
    // Validate email domain
    if (!formData.email.endsWith('@sigce.edu.in')) {
      setError('Only SIGCE email addresses (@sigce.edu.in) are allowed.');
      return;
    }
    
    setLoading(true);
    try {
      await signup(formData.email, formData.password, formData.name, formData.college, formData.yearOfAdmission);
      // Send verification email with custom settings
      if (auth.currentUser) {
        await sendEmailVerification(auth.currentUser, actionCodeSettings);
      }
      // Pass email to OTP page so it can display it
      navigate('/otp-verification', { state: { email: formData.email } });
    } catch (err) {
      setError(getErrorMessage(err.code));
    } finally {
      setLoading(false);
    }
  };

  const field = (key) => ({
    value: formData[key],
    onChange: (e) => setFormData({ ...formData, [key]: e.target.value }),
  });

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Side - Form */}
      <div className="flex items-center justify-center p-6 sm:p-8 md:p-12 lg:p-24 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="mb-10">
            <Link to="/" className="flex items-center gap-3" data-testid="signup-logo">
              <img 
                src="/UNIFIND.png" 
                alt="UNIFIND Logo" 
                className="h-16 w-auto"
              />
              <span className="font-['Outfit'] font-black text-3xl tracking-tight">
                <span className="text-blue-600">UNI</span>
                <span className="text-purple-600">FIND</span>
              </span>
            </Link>
          </div>

          <div className="mb-8">
            <h1 className="font-['Outfit'] text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mb-2" data-testid="signup-title">
              Create Account
            </h1>
            <p className="text-base text-slate-600">Join the student marketplace community</p>
          </div>

          {error && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600" data-testid="signup-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2" htmlFor="name">Full Name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  id="name" type="text" placeholder="Arjun Sharma" required
                  className="w-full rounded-xl border border-slate-200 pl-12 pr-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  data-testid="signup-name-input" {...field('name')}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2" htmlFor="email">
                SIGCE Email <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  id="email" type="email" placeholder="your.name@sigce.edu.in" required
                  className="w-full rounded-xl border border-slate-200 pl-12 pr-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  data-testid="signup-email-input" {...field('email')}
                />
              </div>
              <p className="mt-1 text-xs text-slate-500">Must be a valid @sigce.edu.in email address</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2" htmlFor="college">College/University</label>
              <div className="relative">
                <GraduationCap className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 z-10" />
                <input
                  id="college" 
                  type="text" 
                  placeholder={collegeSelected ? "" : "Search your college..."} 
                  required
                  value={collegeSearch}
                  onChange={(e) => {
                    if (!collegeSelected) {
                      setCollegeSearch(e.target.value);
                      setFormData({ ...formData, college: '' });
                      setShowCollegeDropdown(true);
                    }
                  }}
                  onFocus={() => {
                    if (!collegeSelected) {
                      setShowCollegeDropdown(true);
                    }
                  }}
                  readOnly={collegeSelected}
                  className={`w-full rounded-xl border border-slate-200 pl-12 ${collegeSelected ? 'pr-12' : 'pr-4'} py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all ${collegeSelected ? 'bg-slate-50 cursor-default' : ''}`}
                  data-testid="signup-college-input"
                  autoComplete="off"
                />
                {collegeSelected && (
                  <button
                    type="button"
                    onClick={handleCollegeClear}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    data-testid="clear-college-btn"
                    title="Change college"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
                {showCollegeDropdown && !collegeSelected && filteredColleges.length > 0 && (
                  <div className="absolute z-20 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                    {filteredColleges.map((college, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleCollegeSelect(college)}
                        className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors text-sm text-slate-700 border-b border-slate-100 last:border-b-0"
                        data-testid={`college-option-${index}`}
                      >
                        {college}
                      </button>
                    ))}
                  </div>
                )}
                {showCollegeDropdown && !collegeSelected && filteredColleges.length === 0 && collegeSearch && (
                  <div className="absolute z-20 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg p-4 text-sm text-slate-500 text-center">
                    No colleges found. Try a different search.
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2" htmlFor="yearOfAdmission">Year of Admission</label>
              <div className="relative">
                <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 z-10" />
                <select
                  id="yearOfAdmission"
                  required
                  value={formData.yearOfAdmission}
                  onChange={(e) => setFormData({ ...formData, yearOfAdmission: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 pl-12 pr-4 py-3 text-slate-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all appearance-none bg-white cursor-pointer"
                  data-testid="signup-year-input"
                >
                  <option value="" disabled>Select year...</option>
                  {years.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
                <svg className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2" htmlFor="password">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  id="password" type={showPassword ? "text" : "password"} placeholder="Min. 6 characters" required minLength={6}
                  className="w-full rounded-xl border border-slate-200 pl-12 pr-12 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  data-testid="signup-password-input" {...field('password')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  data-testid="toggle-password-visibility"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading || !collegeSelected}
              className="w-full bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed"
              data-testid="signup-submit-btn"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium" data-testid="login-link">
              Login
            </Link>
          </p>
        </div>
      </div>

      {/* Right Side - Image */}
      <div className="hidden lg:block relative bg-slate-900">
        <img
          src="https://images.pexels.com/photos/1454360/pexels-photo-1454360.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
          alt="Students"
          className="w-full h-full object-cover opacity-60"
        />
        <div className="absolute inset-0 flex items-center justify-center p-12">
          <div className="text-center text-white">
            <h2 className="font-['Outfit'] text-4xl font-bold mb-4">Join UNIFIND</h2>
            <p className="text-lg text-slate-300">Start buying and selling with verified students</p>
          </div>
        </div>
      </div>
    </div>
  );
};

function getErrorMessage(code) {
  switch (code) {
    case 'auth/email-already-in-use':
      return 'An account with this email already exists.';
    case 'auth/invalid-email':
      return 'Invalid email address.';
    case 'auth/weak-password':
      return 'Password must be at least 6 characters.';
    case 'auth/too-many-requests':
      return 'Too many attempts. Try again later.';
    default:
      return 'Something went wrong. Please try again.';
  }
}

export default SignupPage;
