import React, { useState } from 'react';
import Header from '../components/Header';
import { Sparkles, Search, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { searchNeedBoard } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';

const NeedBoardPage = () => {
  const { darkMode } = useTheme();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await searchNeedBoard(input);
      setResults({ extracted: data.extracted, rankedResults: data.rankedResults });
    } catch (err) {
      // Handle rate limiting
      if (err?.response?.status === 429) {
        const detail = err?.response?.data?.detail || 'Please wait before trying again.';
        setError(`⏱️ ${detail}`);
      } else {
        const msg =
          err?.response?.data?.detail ||
          err?.response?.data?.error ||
          err?.message ||
          'Something went wrong. Please try again.';
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTryAgain = () => {
    setError(null);
    setResults(null);
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 70) return 'bg-green-100 text-green-700';
    if (score >= 40) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  return (
    <div className={`min-h-[100dvh] pb-20 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header hideSearch />

      <div className="px-6 sm:px-8 md:px-12 lg:px-24 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-purple-50 border border-purple-200 rounded-full px-4 py-2 mb-4">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">AI-Powered Matching</span>
            </div>
            <h1
              className={`font-['Outfit'] text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}
              data-testid="need-board-title"
            >
              What are you looking for?
            </h1>
            <p className={`text-base ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              Describe what you need, and our AI will find the perfect matches
            </p>
          </div>

          {/* Input Area */}
          <div className={`rounded-2xl border p-8 mb-8 shadow-sm ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Example: I need a laptop for coding, budget around 70k, good battery life..."
              rows="4"
              className={`w-full rounded-xl border px-4 py-3 text-[16px] sm:text-base outline-none transition-all resize-none mb-4 ${
                darkMode 
                  ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-blue-500'
                  : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
              }`}
              data-testid="need-board-input"
            />
            <Button
              onClick={handleSearch}
              disabled={loading || !input.trim()}
              className="w-full bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 shadow-[0_0_0_1px_rgba(37,99,235,1)_inset] transition-all duration-200 active:scale-95"
              data-testid="find-matches-btn"
            >
              {loading ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                  AI analyzing...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  Find Matches
                </>
              )}
            </Button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className={`rounded-2xl border p-8 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`} data-testid="loading-state">
              <div className="space-y-4">
                <div className={`h-4 w-3/4 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} rounded animate-pulse`} />
                <div className={`h-4 w-1/2 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} rounded animate-pulse`} />
                <div className={`h-4 w-2/3 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} rounded animate-pulse`} />
              </div>
              <div className={`mt-6 pt-6 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                <div className={`h-32 rounded-xl mb-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} animate-pulse`} />
                <div className={`h-32 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} animate-pulse`} />
              </div>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div
              className="bg-red-50 border border-red-200 rounded-2xl p-8 flex flex-col items-center text-center gap-4"
              data-testid="error-state"
            >
              <AlertCircle className="h-8 w-8 text-red-500" />
              <p className="text-red-700 font-medium">{error}</p>
              <Button
                onClick={handleTryAgain}
                className="bg-white border border-red-300 text-red-600 px-5 py-2 rounded-xl hover:bg-red-50 transition-all"
                data-testid="try-again-btn"
              >
                Try again
              </Button>
            </div>
          )}

          {/* Results */}
          {!loading && results && (
            <div className="space-y-8" data-testid="results-section">
              {/* Extracted Intent */}
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border border-blue-200 p-8">
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="h-5 w-5 text-blue-600" />
                  <h2 className="text-xl font-bold text-slate-900">What we understood</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-category">
                    <div className="text-sm text-slate-600 mb-1">Category</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.category}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-subject">
                    <div className="text-sm text-slate-600 mb-1">Subject</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.subject}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-semester">
                    <div className="text-sm text-slate-600 mb-1">Semester</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.semester}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-max-price">
                    <div className="text-sm text-slate-600 mb-1">Max Budget</div>
                    <div className="text-lg font-bold text-slate-900">
                      {results.extracted.max_price != null
                        ? `₹${Number(results.extracted.max_price).toLocaleString()}`
                        : 'Not specified'}
                    </div>
                  </div>
                  <div className="bg-white rounded-xl p-4" data-testid="extracted-condition">
                    <div className="text-sm text-slate-600 mb-1">Preferred Condition</div>
                    <div className="text-lg font-bold text-slate-900">{results.extracted.condition}</div>
                  </div>
                  <div className="bg-white rounded-xl p-4 md:col-span-2" data-testid="extracted-intent-summary">
                    <div className="text-sm text-slate-600 mb-1">Summary</div>
                    <div className="text-base font-medium text-slate-900">{results.extracted.intent_summary}</div>
                  </div>
                </div>
              </div>

              {/* Ranked Results */}
              <div>
                <h2 className={`text-xl font-bold mb-6 flex items-center gap-2 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  Top Matches for You
                </h2>
                <div className="space-y-4">
                  {results.rankedResults.map((result) => (
                    <div
                      key={result.id}
                      className={`rounded-2xl border p-6 flex flex-col sm:flex-row sm:items-start gap-4 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}
                      data-testid={`match-${result.id}`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-3 mb-2">
                          <h3 className={`text-lg font-bold line-clamp-1 ${darkMode ? 'text-slate-100' : 'text-slate-900'}`} data-testid={`match-title-${result.id}`}>
                            {result.title}
                          </h3>
                          <span
                            className={`text-xs font-semibold px-2 py-1 rounded-full ${getScoreBadgeClass(result.match_score)}`}
                            data-testid={`match-score-${result.id}`}
                          >
                            {result.match_score}% match
                          </span>
                        </div>
                        <div className="text-xl font-black text-blue-600 mb-2" data-testid={`match-price-${result.id}`}>
                          {result.price != null ? `₹${Number(result.price).toLocaleString()}` : '—'}
                        </div>
                        <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`} data-testid={`match-reason-${result.id}`}>
                          {result.reason}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NeedBoardPage;

