import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import { Send, MapPin, IndianRupee, ArrowLeft, Check, CheckCheck, Smile, Search, MoreVertical, Flag, UserPlus } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { getUserChats, getChatMessages, sendChatMessage, getOrCreateChatRoom, getPublicProfile, getProduct, markChatAsRead } from '../services/api';

// Static emoji data - moved outside component to avoid recreation on every render
const EMOJIS = {
  'Smileys': ['😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🥸', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓'],
  'Gestures': ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏'],
  'Hearts': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟'],
  'Objects': ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛼', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂'],
  'Food': ['🍎', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞', '🧇', '🥓', '🥩', '🍗', '🍖', '🦴', '🌭', '🍔', '🍟', '🍕', '🫓', '🥪', '🥙', '🧆', '🌮', '🌯', '🫔', '🥗', '🥘', '🫕', '🥫', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱', '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠', '🥮', '🍢', '🍡', '🍧', '🍨', '🍦', '🥧', '🧁', '🍰', '🎂', '🍮', '🍭', '🍬', '🍫', '🍿', '🍩', '🍪', '🌰', '🥜', '🍯'],
};

const ChatPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { currentUser } = useAuth();
  const { darkMode } = useTheme();
  
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [otherUser, setOtherUser] = useState(null);
  const [product, setProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [showChatMenu, setShowChatMenu] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetails, setReportDetails] = useState('');
  const [reportSubmitting, setReportSubmitting] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [friendsOnly, setFriendsOnly] = useState(false);
  const [chatUserProfiles, setChatUserProfiles] = useState({}); // Cache user profiles for search
  
  const messagesEndRef = useRef(null);
  const messageInputRef = useRef(null);
  const chatMenuRef = useRef(null);
  const emojiPickerRef = useRef(null);
  const messageRefs = useRef({});
  const observerRef = useRef(null);
  const markedAsReadRef = useRef(new Set());

  // Get user ID from URL params (for starting new chat)
  const targetUserId = searchParams.get('user');
  const productId = searchParams.get('product');

  // Handle initial chat creation from URL params
  useEffect(() => {
    if (!currentUser || !targetUserId || targetUserId === currentUser.uid) return;

    let isActive = true;

    const initializeChat = async () => {
      try {
        const chatRoom = await getOrCreateChatRoom(currentUser.uid, targetUserId, productId);
        if (isActive) {
          setSelectedChat(chatRoom);
        }
        
        // Load other user's profile
        const profile = await getPublicProfile(targetUserId);
        if (isActive) {
          setOtherUser(profile);
        }
        
        // Load product if specified
        if (productId) {
          const prod = await getProduct(productId);
          if (isActive) {
            setProduct(prod);
          }
        }
      } catch (error) {
        console.error('Failed to initialize chat:', error);
      }
    };

    initializeChat();

    return () => {
      isActive = false;
    };
  }, [targetUserId, productId, currentUser?.uid]);

  // Get message status for read receipts
  const getMessageStatus = (msg) => {
    if (msg.sender_id !== currentUser?.uid) return null;
    
    // Use actual is_read field from database
    if (msg.is_read) {
      return 'read';
    }
    
    // If message has been stored in database (has an id), it's delivered
    // Messages are delivered once they're successfully saved to Firestore
    if (msg.id) {
      return 'delivered';
    }
    
    // Otherwise it's just sent (in transit)
    return 'sent';
  };

  // Format time for chat list
  const formatChatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d`;
    
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  // Format date separator
  const formatDateSeparator = (timestamp) => {
    const date = timestamp?.seconds ? new Date(timestamp.seconds * 1000) : new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now - date) / 86400000);
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return date.toLocaleDateString([], { weekday: 'long' });
    
    return date.toLocaleDateString([], { month: 'long', day: 'numeric', year: 'numeric' });
  };

  // Check if should show date separator
  const shouldShowDateSeparator = (currentMsg, previousMsg) => {
    if (!previousMsg) return true;
    
    const currentDate = currentMsg.timestamp?.seconds 
      ? new Date(currentMsg.timestamp.seconds * 1000) 
      : new Date(currentMsg.timestamp);
    const previousDate = previousMsg.timestamp?.seconds 
      ? new Date(previousMsg.timestamp.seconds * 1000) 
      : new Date(previousMsg.timestamp);
    
    return currentDate.toDateString() !== previousDate.toDateString();
  };

  // Mark individual message as read
  const markMessageAsRead = async (messageId) => {
    if (!selectedChat || !currentUser || markedAsReadRef.current.has(messageId)) return;
    
    try {
      markedAsReadRef.current.add(messageId);
      
      // Use markChatAsRead API from services
      await markChatAsRead(selectedChat.id, currentUser.uid);
      
      // Update local state
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId ? { ...msg, is_read: true } : msg
        )
      );
      
      // Update unread count in chat list
      setChats(prevChats => 
        prevChats.map(c => {
          if (c.id === selectedChat.id) {
            const unreadField = c.user1_id === currentUser.uid ? 'unread_count_user1' : 'unread_count_user2';
            const currentCount = c.user1_id === currentUser.uid ? c.unread_count_user1 : c.unread_count_user2;
            return {
              ...c,
              [unreadField]: Math.max(0, currentCount - 1)
            };
          }
          return c;
        })
      );
    } catch (error) {
      console.error('Failed to mark message as read:', error);
      // Don't delete from markedAsReadRef on error to prevent retry loops
    }
  };

  // Setup Intersection Observer to track visible messages
  useEffect(() => {
    if (!selectedChat || !currentUser) return;

    // Clean up previous observer
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    // Create new observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const messageId = entry.target.dataset.messageId;
            const senderId = entry.target.dataset.senderId;
            const isRead = entry.target.dataset.isRead === 'true';
            
            // Only mark as read if it's from the other user and not already read
            if (senderId !== currentUser.uid && !isRead && messageId) {
              markMessageAsRead(messageId);
            }
          }
        });
      },
      {
        root: null,
        rootMargin: '0px',
        threshold: 0.5 // Message must be 50% visible
      }
    );

    // Observe all message elements
    Object.values(messageRefs.current).forEach((ref) => {
      if (ref) {
        observerRef.current.observe(ref);
      }
    });

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [messages, selectedChat, currentUser]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Track page visibility to pause/resume polling
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('Chat page hidden - pausing updates');
      } else {
        console.log('Chat page visible - resuming updates');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Load user's chats with smart polling
  useEffect(() => {
    if (!currentUser) {
      navigate('/login');
      return;
    }

    let isActive = true;
    let pollInterval = null;

    const loadChats = async () => {
      if (!isActive || document.hidden) return; // Don't load if page is hidden
      try {
        const userChats = await getUserChats(currentUser.uid, friendsOnly);
        if (isActive) {
          setChats(userChats);
          setLoading(false);
        }
      } catch (error) {
        console.error('Failed to load chats:', error);
        if (isActive) {
          setLoading(false);
        }
      }
    };

    // Initial load
    loadChats();
    
    // Start polling only when page is visible
    const startPolling = () => {
      if (pollInterval) return; // Already polling
      
      pollInterval = setInterval(() => {
        if (!document.hidden && isActive) {
          loadChats();
        }
      }, 10000); // Poll every 10 seconds when visible
    };

    const stopPolling = () => {
      if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    };

    // Handle visibility changes
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling();
      } else {
        loadChats(); // Refresh immediately when page becomes visible
        startPolling();
      }
    };

    // Start initial polling if page is visible
    if (!document.hidden) {
      startPolling();
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      isActive = false;
      stopPolling();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentUser?.uid, friendsOnly, navigate]);

  // Load messages when chat is selected with smart polling
  useEffect(() => {
    if (!selectedChat || !currentUser) return;

    const otherId = selectedChat.user1_id === currentUser.uid 
      ? selectedChat.user2_id 
      : selectedChat.user1_id;

    let isActive = true;
    let pollInterval = null;

    const loadMessages = async () => {
      if (!isActive || document.hidden) return;
      try {
        const chatMessages = await getChatMessages(selectedChat.id);
        if (isActive) {
          // CRITICAL: Merge logic - never blindly overwrite
          setMessages(prev => {
            // Create map with existing messages (preserves optimistic)
            const messageMap = new Map();
            
            // Add existing messages first
            prev.forEach(msg => {
              messageMap.set(msg.id, msg);
            });
            
            // Merge backend messages (replaces optimistic if ID matches)
            chatMessages.forEach(msg => {
              // If this is a real message from backend, it replaces any optimistic version
              messageMap.set(msg.id, { ...msg, status: 'sent' });
            });
            
            // Remove optimistic messages that have been confirmed
            // (Check if backend has a message with same content/sender/time)
            const optimisticMessages = prev.filter(m => m._optimistic);
            optimisticMessages.forEach(optMsg => {
              const isConfirmed = chatMessages.some(backendMsg => 
                backendMsg.text === optMsg.text &&
                backendMsg.sender_id === optMsg.sender_id &&
                Math.abs(new Date(backendMsg.timestamp).getTime() - new Date(optMsg.timestamp).getTime()) < 5000
              );
              
              if (isConfirmed) {
                messageMap.delete(optMsg.id); // Remove optimistic, keep backend version
              }
            });
            
            // Convert map to sorted array
            return Array.from(messageMap.values()).sort((a, b) => {
              const timeA = a.timestamp?.seconds 
                ? new Date(a.timestamp.seconds * 1000).getTime()
                : new Date(a.timestamp).getTime();
              const timeB = b.timestamp?.seconds 
                ? new Date(b.timestamp.seconds * 1000).getTime()
                : new Date(b.timestamp).getTime();
              return timeA - timeB;
            });
          });
        }
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    };

    // Load initial data
    const loadInitialData = async () => {
      try {
        // Load other user's profile
        const profile = await getPublicProfile(otherId);
        if (isActive) {
          setOtherUser(profile);
        }
        
        // Load product if specified
        if (selectedChat.product_id) {
          const prod = await getProduct(selectedChat.product_id);
          if (isActive) {
            setProduct(prod);
          }
        }
        
        // Load messages
        await loadMessages();
        
        // Reset marked as read tracking when switching chats
        markedAsReadRef.current.clear();
      } catch (error) {
        console.error('Failed to load initial chat data:', error);
      }
    };

    loadInitialData();
    
    // Start polling only when page is visible
    const startPolling = () => {
      if (pollInterval) return; // Already polling
      
      pollInterval = setInterval(() => {
        if (!document.hidden && isActive) {
          loadMessages();
        }
      }, 5000); // Poll every 5 seconds when visible
    };

    const stopPolling = () => {
      if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    };

    // Handle visibility changes
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling();
      } else {
        loadMessages(); // Refresh immediately when page becomes visible
        startPolling();
      }
    };

    // Start initial polling if page is visible
    if (!document.hidden) {
      startPolling();
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      isActive = false;
      stopPolling();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [selectedChat?.id, currentUser?.uid]);

  // Helper function to check if other user is online
  const isOtherUserOnline = (messages, otherId) => {
    if (!messages || messages.length === 0) return false;
    
    // Find the last message from the other user
    const otherUserMessages = messages.filter(msg => msg.sender_id === otherId);
    if (otherUserMessages.length === 0) return false;
    
    const lastMessage = otherUserMessages[otherUserMessages.length - 1];
    const lastMessageTime = lastMessage.timestamp?.seconds 
      ? new Date(lastMessage.timestamp.seconds * 1000)
      : new Date(lastMessage.timestamp);
    
    const now = new Date();
    const diffMinutes = (now - lastMessageTime) / 60000;
    
    return diffMinutes < 5;
  };

  // Compute online status once per render
  const otherUserId = otherUser?.user_id || otherUser?.id;
  const isOnline = otherUserId ? isOtherUserOnline(messages, otherUserId) : false;

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || !selectedChat || !currentUser || sending) return;

    const otherId = selectedChat.user1_id === currentUser.uid 
      ? selectedChat.user2_id 
      : selectedChat.user1_id;

    setSending(true);
    const messageText = message.trim(); // Capture message before clearing
    
    // Create optimistic message with temporary ID
    const optimisticMessage = {
      id: `temp-${Date.now()}`,
      text: messageText,
      sender_id: currentUser.uid,
      receiver_id: otherId,
      product_id: selectedChat.product_id || null,
      chat_room_id: selectedChat.id,
      timestamp: new Date(),
      is_read: false,
      _optimistic: true // Flag to identify optimistic messages
    };
    
    // Add optimistic message immediately
    setMessages(prev => [...prev, optimisticMessage]);
    setMessage('');
    messageInputRef.current?.focus();
    
    try {
      const newMessage = await sendChatMessage({
        text: messageText,
        sender_id: currentUser.uid,
        receiver_id: otherId,
        product_id: selectedChat.product_id || null
      });
      
      // Replace optimistic message with real message from backend
      setMessages(prev => 
        prev.map(msg => 
          msg.id === optimisticMessage.id ? newMessage : msg
        )
      );
      
      // Update chat list locally instead of reloading from backend
      setChats(prevChats => 
        prevChats.map(c => {
          if (c.id === selectedChat.id) {
            return {
              ...c,
              last_message: messageText,
              last_message_time: new Date().toISOString()
            };
          }
          return c;
        })
      );
      
      // Update selected chat
      setSelectedChat(prev => ({
        ...prev,
        last_message: messageText,
        last_message_time: new Date().toISOString()
      }));
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic message on error
      setMessages(prev => prev.filter(msg => msg.id !== optimisticMessage.id));
      alert('Failed to send message. Please try again.');
      // Restore message text so user can retry
      setMessage(messageText);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Filter chats based on search
  const filteredChats = (Array.isArray(chats) ? chats : []).filter(chat => {
    if (!searchQuery) return true;
    
    const searchLower = searchQuery.toLowerCase();
    
    // Search in last message
    if (chat.last_message?.toLowerCase().includes(searchLower)) return true;
    
    // Search in user name (from cached profiles)
    const otherId = chat.user1_id === currentUser?.uid ? chat.user2_id : chat.user1_id;
    const userProfile = chatUserProfiles[otherId];
    if (userProfile?.name?.toLowerCase().includes(searchLower)) return true;
    
    return false;
  });

  const handleChatSelect = useCallback((chat) => {
    // Clear previous chat data
    setMessages([]);
    setOtherUser(null);
    setProduct(null);
    markedAsReadRef.current.clear();
    
    // Set new chat
    setSelectedChat(chat);
  }, []);

  // Memoize the profile loaded callback
  const handleUserProfileLoaded = useCallback((userId, profile) => {
    setChatUserProfiles(prev => ({ ...prev, [userId]: profile }));
  }, []);

  // Handle report user
  const handleReportUser = async () => {
    if (!reportReason) {
      alert('Please select a reason for reporting');
      return;
    }

    setReportSubmitting(true);
    try {
      // TODO: Implement actual report API call when backend endpoint is ready
      // await api.post('/reports/user', {
      //   reported_user_id: otherUser?.user_id || otherUser?.id,
      //   reported_by: currentUser.uid,
      //   reason: reportReason,
      //   details: reportDetails
      // });
      
      console.log('Report submitted:', {
        reportedUserId: otherUser?.user_id || otherUser?.id,
        reportedBy: currentUser.uid,
        reason: reportReason,
        details: reportDetails,
        timestamp: new Date().toISOString()
      });
      
      alert('Report submitted successfully. Our team will review it shortly.');
      setShowReportModal(false);
      setReportReason('');
      setReportDetails('');
    } catch (error) {
      console.error('Failed to submit report:', error);
      alert('Failed to submit report. Please try again.');
    } finally {
      setReportSubmitting(false);
    }
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatMenuRef.current && !chatMenuRef.current.contains(event.target)) {
        setShowChatMenu(false);
      }
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
        setShowEmojiPicker(false);
      }
    };

    if (showChatMenu || showEmojiPicker) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showChatMenu, showEmojiPicker]);

  // Handle emoji selection
  const handleEmojiSelect = (emoji) => {
    setMessage(prev => prev + emoji);
    messageInputRef.current?.focus();
  };

  if (loading) {
    return (
      <div className={`h-[100dvh] flex flex-col overflow-hidden ${darkMode ? 'bg-[#0f0f0f]' : 'bg-slate-50'}`}>
        <Header hideSearch />
        <div className="flex items-center justify-center flex-1">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className={darkMode ? 'text-neutral-400' : 'text-slate-600'}>Loading chats...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`h-[100dvh] flex flex-col overflow-hidden ${darkMode ? 'bg-[#0f0f0f]' : 'bg-slate-50'}`}>
      <Header hideSearch />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Chat List - Left Sidebar */}
        <div className={`${selectedChat ? 'hidden md:flex' : 'flex'} w-full md:w-72 lg:w-80 border-r flex-col shadow-sm h-full ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
          <div className={`px-4 py-4 border-b flex-shrink-0 ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center justify-between mb-3">
              <h2 className={`text-xl font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`} data-testid="chat-list-title">
                Chats
              </h2>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`rounded-full p-2 ${darkMode ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'}`}
                onClick={() => setShowSearch(!showSearch)}
              >
                <Search className={`h-5 w-5 ${darkMode ? 'text-neutral-400' : 'text-slate-600'}`} />
              </Button>
            </div>
            
            {/* Friends Filter Toggle */}
            <div className={`flex gap-2 mb-3 p-1 rounded-lg ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
              <button
                onClick={() => setFriendsOnly(false)}
                className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                  !friendsOnly
                    ? darkMode
                      ? 'bg-[#212121] text-indigo-400 shadow-sm'
                      : 'bg-white text-indigo-600 shadow-sm'
                    : darkMode
                      ? 'text-neutral-400 hover:text-neutral-300'
                      : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All Chats
              </button>
              <button
                onClick={() => setFriendsOnly(true)}
                className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                  friendsOnly
                    ? darkMode
                      ? 'bg-[#212121] text-indigo-400 shadow-sm'
                      : 'bg-white text-indigo-600 shadow-sm'
                    : darkMode
                      ? 'text-neutral-400 hover:text-neutral-300'
                      : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Friends Only
              </button>
            </div>
            
            {showSearch && (
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats..."
                className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-all ${
                  darkMode 
                    ? 'bg-slate-700 border-slate-600 text-neutral-200 placeholder-slate-400 focus:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20'
                }`}
              />
            )}
          </div>
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
            {filteredChats.length === 0 ? (
              <div className={`p-8 text-center flex flex-col items-center justify-center h-full ${darkMode ? 'text-neutral-400' : 'text-slate-500'}`}>
                <div className={`h-20 w-20 rounded-full flex items-center justify-center mb-4 ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                  <Send className={`h-10 w-10 ${darkMode ? 'text-slate-500' : 'text-neutral-400'}`} />
                </div>
                <p className={`font-semibold mb-1 ${darkMode ? 'text-neutral-300' : 'text-slate-700'}`}>No messages yet</p>
                <p className="text-sm">Start a conversation from a product listing</p>
              </div>
            ) : (
              filteredChats.map((chat) => (
                <ChatListItem
                  key={chat.id}
                  chat={chat}
                  currentUserId={currentUser.uid}
                  isSelected={selectedChat?.id === chat.id}
                  onClick={() => handleChatSelect(chat)}
                  formatTime={formatChatTime}
                  searchQuery={searchQuery}
                  darkMode={darkMode}
                  onUserProfileLoaded={handleUserProfileLoaded}
                />
              ))
            )}
          </div>
        </div>

        {/* Chat Window - Right Side */}
        <div className={`${selectedChat ? 'flex' : 'hidden md:flex'} flex-1 flex-col overflow-hidden ${darkMode ? 'bg-[#0f0f0f]' : 'bg-slate-50'}`}>
          {selectedChat && otherUser ? (
            <>
              {/* Chat Header */}
              <div className={`border-b p-3 md:p-4 shadow-sm flex-shrink-0 z-10 ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setSelectedChat(null)}
                    className={`md:hidden p-2 -ml-2 rounded-full transition-all flex items-center justify-center active:scale-95 ${darkMode ? 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
                    aria-label="Back to chats"
                  >
                    <ArrowLeft className="h-6 w-6" />
                  </button>
                  <div className="relative group">
                    <img
                      src={otherUser.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name || 'User')}`}
                      alt={otherUser.name}
                      className="h-11 w-11 rounded-full object-cover cursor-pointer ring-2 ring-indigo-100 hover:ring-indigo-300 transition-all"
                      onClick={() => navigate(`/profile/${otherUser.user_id || otherUser.id}`)}
                    />
                    <div className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white ${
                      isOnline ? 'bg-green-500' : 'bg-slate-400'
                    }`}></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 
                      className={`text-base font-semibold cursor-pointer hover:text-indigo-600 transition-colors truncate ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}
                      data-testid="chat-header-name"
                      onClick={() => navigate(`/profile/${otherUser.user_id || otherUser.id}`)}
                    >
                      {otherUser.name}
                    </h3>
                    <p className={`text-xs ${
                      isOnline 
                        ? 'text-green-600' 
                        : darkMode ? 'text-neutral-400' : 'text-slate-500'
                    }`}>
                      {isOnline ? 'online' : 'offline'}
                    </p>
                  </div>
                  <div className="relative" ref={chatMenuRef}>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className={`rounded-full p-2 ${darkMode ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'}`}
                      onClick={() => setShowChatMenu(!showChatMenu)}
                    >
                      <MoreVertical className={`h-5 w-5 ${darkMode ? 'text-neutral-400' : 'text-slate-600'}`} />
                    </Button>
                    
                    {/* Dropdown Menu */}
                    {showChatMenu && (
                      <div className={`absolute right-0 mt-2 w-48 rounded-lg shadow-lg border z-50 ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
                        <button
                          onClick={() => {
                            setShowChatMenu(false);
                            setShowReportModal(true);
                          }}
                          className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors ${darkMode ? 'hover:bg-neutral-800 text-neutral-300' : 'hover:bg-slate-50 text-slate-700'}`}
                        >
                          <Flag className="h-4 w-4 text-red-500" />
                          <span className="text-sm font-medium">Report User</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Product Info */}
                {product && (
                  <div className="mt-3 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-lg p-3 flex items-center gap-3 cursor-pointer hover:bg-slate-100 transition-all border border-slate-200"
                    onClick={() => navigate(`/listing/${product.id}`)}>
                    <img
                      src={product.images?.[0] || '/placeholder.png'}
                      alt={product.title}
                      className="h-12 w-12 rounded-md object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-slate-900 mb-1 truncate">
                        {product.title}
                      </h4>
                      <p className="text-sm font-bold text-indigo-600">
                        ₹{product.price?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div 
                className={`flex-1 overflow-y-auto p-3 md:p-4 flex flex-col scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent overscroll-contain ${darkMode ? 'bg-[#0f0f0f]' : 'bg-slate-50'}`}
                data-testid="messages-container"
              >
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="bg-indigo-100 h-24 w-24 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Send className="h-12 w-12 text-indigo-600" />
                      </div>
                      <p className={`text-lg font-semibold mb-1 ${darkMode ? 'text-neutral-300' : 'text-slate-700'}`}>No messages yet</p>
                      <p className={`text-sm ${darkMode ? 'text-neutral-400' : 'text-slate-500'}`}>Start the conversation!</p>
                    </div>
                  </div>
                ) : (
                  (Array.isArray(messages) ? messages : []).map((msg, index) => {
                    const isCurrentUser = msg.sender_id === currentUser.uid;
                    const showDateSeparator = shouldShowDateSeparator(msg, messages[index - 1]);
                    // Only group messages that are from the same sender and same day
                    const isSameSenderAsPrev = index > 0 && messages[index - 1].sender_id === msg.sender_id && !showDateSeparator;
                    const showAvatar = !isSameSenderAsPrev;
                    const status = getMessageStatus(msg);
                    
                    const mtClass = showDateSeparator ? 'mt-0' : (isSameSenderAsPrev ? 'mt-[2px]' : 'mt-4');
                    
                    // Use msg.id or temporary ID for optimistic messages
                    const messageKey = msg.id || `temp-${index}`;

                    return (
                      <React.Fragment key={messageKey}>
                        {showDateSeparator && (
                          <div className={`flex justify-center ${index === 0 ? 'mt-0 mb-4' : 'my-4'}`}>
                            <span className={`text-xs px-4 py-1.5 rounded-full shadow-sm font-medium ${darkMode ? 'bg-[#212121] text-neutral-400' : 'bg-white text-slate-600'}`}>
                              {formatDateSeparator(msg.timestamp)}
                            </span>
                          </div>
                        )}
                        <div
                          ref={(el) => {
                            if (el && msg.id && !msg._optimistic) {
                              messageRefs.current[msg.id] = el;
                            }
                          }}
                          data-message-id={msg.id}
                          data-sender-id={msg.sender_id}
                          data-is-read={msg.is_read}
                          className={`flex gap-2 ${mtClass} ${isCurrentUser ? 'justify-end' : 'justify-start'} ${msg._optimistic ? 'opacity-70' : ''}`}
                          data-testid={`message-${msg.id}`}
                        >
                          {!isCurrentUser && showAvatar && (
                            <img
                              src={otherUser?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser?.name || 'User')}`}
                              alt={otherUser?.name}
                              className="h-8 w-8 rounded-full object-cover flex-shrink-0 mt-auto ring-2 ring-white shadow-sm"
                            />
                          )}
                          {!isCurrentUser && !showAvatar && <div className="w-8 flex-shrink-0" />}
                          
                          <div 
                            className={`inline-flex items-end gap-2 px-3.5 py-2 shadow-sm max-w-[85%] md:max-w-[75%] ${
                              isCurrentUser
                                ? `bg-indigo-600 text-white rounded-2xl ${isSameSenderAsPrev ? 'rounded-r-sm' : 'rounded-br-sm'}`
                                : `border rounded-2xl ${isSameSenderAsPrev ? 'rounded-l-sm' : 'rounded-bl-sm'} ${
                                    darkMode 
                                      ? 'bg-[#212121] text-neutral-200 border-neutral-700' 
                                      : 'bg-white text-slate-900 border-slate-200'
                                  }`
                            }`}
                          >
                            <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{msg.text}</p>
                            <div className="flex items-center gap-1 flex-shrink-0 pb-0.5">
                              <span className={`text-[10px] whitespace-nowrap ${
                                isCurrentUser ? 'text-indigo-200' : 'text-slate-500'
                              }`}>
                                {(() => {
                                  const timestamp = msg.timestamp?.seconds 
                                    ? new Date(msg.timestamp.seconds * 1000) 
                                    : new Date(msg.timestamp);
                                  
                                  const hours = timestamp.getHours().toString().padStart(2, '0');
                                  const minutes = timestamp.getMinutes().toString().padStart(2, '0');
                                  
                                  return `${hours}:${minutes}`;
                                })()}
                              </span>
                              {isCurrentUser && status && (
                                <span className="inline-flex" title={
                                  status === 'sent' ? 'Sent' : 
                                  status === 'delivered' ? 'Delivered' : 
                                  'Read'
                                }>
                                  {status === 'sent' && <Check className="h-3 w-3 text-indigo-200 opacity-70" />}
                                  {status === 'delivered' && <CheckCheck className="h-3 w-3 text-indigo-200" />}
                                  {status === 'read' && <CheckCheck className="h-3 w-3 text-orange-400 drop-shadow-sm" />}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </React.Fragment>
                    );
                  })
                )}
                
                {/* Read Receipt Indicator */}
                {Array.isArray(messages) && messages.length > 0 && (() => {
                  const lastMessage = messages[messages.length - 1];
                  const isMyMessage = lastMessage.sender_id === currentUser.uid;
                  const isRead = lastMessage.is_read;
                  
                  if (isMyMessage && isRead && otherUser) {
                    return (
                      <div className="flex justify-end mt-2 mb-1">
                        <div className={`flex items-center gap-1.5 text-xs ${darkMode ? 'text-slate-500' : 'text-neutral-400'}`}>
                          <img
                            src={otherUser.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name || 'User')}`}
                            alt={otherUser.name}
                            className="h-3.5 w-3.5 rounded-full object-cover ring-1 ring-white"
                          />
                          <span>Seen</span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                })()}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className={`border-t p-2 sm:p-3 shadow-[0_-4px_10px_rgba(0,0,0,0.02)] flex-shrink-0 pb-[calc(0.5rem+env(safe-area-inset-bottom))] md:pb-3 ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
                <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                  <div className="relative" ref={emojiPickerRef}>
                    <Button 
                      type="button"
                      variant="ghost" 
                      size="sm" 
                      className={`rounded-full p-2 flex-shrink-0 ${darkMode ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'}`}
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                    >
                      <Smile className={`h-6 w-6 ${darkMode ? 'text-neutral-400' : 'text-slate-500'}`} />
                    </Button>
                    
                    {/* Emoji Picker */}
                    {showEmojiPicker && (
                      <div className={`absolute bottom-full left-0 mb-2 w-80 max-h-96 rounded-2xl shadow-2xl border overflow-hidden z-50 ${darkMode ? 'bg-[#212121] border-neutral-700' : 'bg-white border-slate-200'}`}>
                        <div className={`px-4 py-3 border-b ${darkMode ? 'border-neutral-700' : 'border-slate-200'}`}>
                          <h4 className={`text-sm font-semibold ${darkMode ? 'text-neutral-200' : 'text-slate-900'}`}>Pick an emoji</h4>
                        </div>
                        <div className="overflow-y-auto max-h-80 p-3">
                          {Object.entries(EMOJIS).map(([category, emojiList]) => (
                            <div key={category} className="mb-4">
                              <h5 className={`text-xs font-semibold mb-2 ${darkMode ? 'text-neutral-400' : 'text-slate-600'}`}>{category}</h5>
                              <div className="grid grid-cols-8 gap-1">
                                {emojiList.map((emoji, idx) => (
                                  <button
                                    key={idx}
                                    type="button"
                                    onClick={() => handleEmojiSelect(emoji)}
                                    className={`text-2xl p-2 rounded-lg transition-all hover:scale-110 ${darkMode ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'}`}
                                  >
                                    {emoji}
                                  </button>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <input
                    ref={messageInputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Message..."
                    maxLength={5000}
                    className={`flex-1 px-4 py-2.5 sm:py-3 text-[16px] sm:text-sm rounded-full border outline-none transition-all ${
                      darkMode 
                        ? 'bg-slate-700 border-slate-600 text-neutral-200 placeholder-slate-400 focus:border-indigo-500 focus:bg-slate-700'
                        : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-white'
                    }`}
                    data-testid="message-input"
                    disabled={sending}
                  />
                  <Button
                    type="submit"
                    disabled={!message.trim() || sending}
                    className="bg-indigo-600 hover:bg-indigo-700 h-10 w-10 sm:h-11 sm:w-11 p-0 flex items-center justify-center rounded-full flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition-all active:scale-95 ml-1"
                    data-testid="send-btn"
                    aria-label="Send message"
                  >
                    {sending ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                    ) : (
                      <Send className="h-5 w-5 ml-0.5" />
                    )}
                  </Button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className={darkMode ? 'text-neutral-400' : 'text-slate-500'}>Select a chat to start messaging</p>
            </div>
          )}
        </div>
      </div>

      {/* Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className={`w-full max-w-md rounded-2xl shadow-xl ${darkMode ? 'bg-[#212121]' : 'bg-white'}`}>
            <div className={`px-6 py-4 border-b ${darkMode ? 'border-neutral-700' : 'border-slate-200'}`}>
              <h3 className={`text-lg font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>Report User</h3>
              <p className={`text-sm mt-1 ${darkMode ? 'text-neutral-400' : 'text-slate-600'}`}>
                Help us understand what's wrong
              </p>
            </div>
            
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className={`block text-sm font-semibold mb-2 ${darkMode ? 'text-neutral-300' : 'text-slate-700'}`}>
                  Reason for reporting <span className="text-red-500">*</span>
                </label>
                <select
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  className={`w-full px-4 py-2.5 rounded-lg border outline-none transition-all ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-neutral-200 focus:border-indigo-500' 
                      : 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20'
                  }`}
                >
                  <option value="">Select a reason...</option>
                  <option value="spam">Spam or misleading</option>
                  <option value="harassment">Harassment or bullying</option>
                  <option value="inappropriate">Inappropriate content</option>
                  <option value="scam">Scam or fraud</option>
                  <option value="fake">Fake profile</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className={`block text-sm font-semibold mb-2 ${darkMode ? 'text-neutral-300' : 'text-slate-700'}`}>
                  Additional details (optional)
                </label>
                <textarea
                  value={reportDetails}
                  onChange={(e) => setReportDetails(e.target.value)}
                  placeholder="Provide more context about this report..."
                  rows={4}
                  maxLength={1000}
                  className={`w-full px-4 py-2.5 rounded-lg border outline-none transition-all resize-none ${
                    darkMode 
                      ? 'bg-slate-700 border-slate-600 text-neutral-200 placeholder-slate-400 focus:border-indigo-500' 
                      : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20'
                  }`}
                />
                <p className={`text-xs mt-1 ${darkMode ? 'text-slate-500' : 'text-neutral-400'}`}>
                  {reportDetails.length}/1000 characters
                </p>
              </div>
            </div>

            <div className={`px-6 py-4 border-t flex gap-3 ${darkMode ? 'border-neutral-700' : 'border-slate-200'}`}>
              <button
                onClick={() => {
                  setShowReportModal(false);
                  setReportReason('');
                  setReportDetails('');
                }}
                disabled={reportSubmitting}
                className={`flex-1 px-4 py-2.5 rounded-lg font-medium transition-all ${
                  darkMode 
                    ? 'bg-slate-700 hover:bg-neutral-700 text-neutral-200' 
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                Cancel
              </button>
              <button
                onClick={handleReportUser}
                disabled={reportSubmitting || !reportReason}
                className="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {reportSubmitting ? 'Submitting...' : 'Submit Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Chat List Item Component - Memoized to prevent unnecessary re-renders
const ChatListItem = React.memo(({ chat, currentUserId, isSelected, onClick, formatTime, searchQuery, darkMode, onUserProfileLoaded }) => {
  const [user, setUser] = useState(null);
  const [product, setProduct] = useState(null);
  const isFriend = chat.is_friend || false;

  useEffect(() => {
    let isActive = true;

    const loadData = async () => {
      try {
        const otherId = chat.user1_id === currentUserId ? chat.user2_id : chat.user1_id;
        const userProfile = await getPublicProfile(otherId);
        
        if (isActive) {
          setUser(userProfile);
          
          // Cache the profile for search filtering
          if (onUserProfileLoaded) {
            onUserProfileLoaded(otherId, userProfile);
          }
        }
        
        if (chat.product_id && isActive) {
          const prod = await getProduct(chat.product_id);
          if (isActive) {
            setProduct(prod);
          }
        }
      } catch (error) {
        console.error('Failed to load chat data:', error);
      }
    };

    loadData();

    return () => {
      isActive = false;
    };
  }, [chat.id, currentUserId, chat.product_id]);

  // Filter based on search query
  if (searchQuery && user) {
    const searchLower = searchQuery.toLowerCase();
    const matchesUser = user.name?.toLowerCase().includes(searchLower);
    const matchesMessage = chat.last_message?.toLowerCase().includes(searchLower);
    const matchesProduct = product?.title?.toLowerCase().includes(searchLower);
    
    if (!matchesUser && !matchesMessage && !matchesProduct) {
      return null;
    }
  }

  if (!user) {
    return (
      <div className={`p-4 border-b animate-pulse ${darkMode ? 'border-neutral-700' : 'border-slate-100'}`}>
        <div className="flex items-center gap-3">
          <div className={`h-12 w-12 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}></div>
          <div className="flex-1">
            <div className={`h-4 rounded w-3/4 mb-2 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}></div>
            <div className={`h-3 rounded w-1/2 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}></div>
          </div>
        </div>
      </div>
    );
  }

  const unreadCount = chat.user1_id === currentUserId 
    ? chat.unread_count_user1 
    : chat.unread_count_user2;

  return (
    <div
      onClick={onClick}
      className={`p-3 sm:p-4 border-b cursor-pointer transition-all active:bg-slate-100 ${
        darkMode 
          ? `border-neutral-700 hover:bg-neutral-800/50 ${isSelected ? 'bg-indigo-900/30 border-l-4 border-l-indigo-600' : ''}`
          : `border-slate-100 hover:bg-slate-50 ${isSelected ? 'bg-indigo-50 border-l-4 border-l-indigo-600' : ''}`
      }`}
      data-testid={`chat-item-${chat.id}`}
    >
      <div className="flex items-center gap-3 mb-1.5 sm:mb-2 text-sm sm:text-base">
        <div className="relative">
          <img
            src={user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}`}
            alt={user.name}
            className={`h-11 w-11 sm:h-12 sm:w-12 rounded-full object-cover ${isFriend ? 'ring-2 ring-indigo-500' : 'ring-2 ring-slate-100'}`}
          />
          {isFriend && (
            <div className="absolute -top-1 -right-1 h-5 w-5 bg-indigo-600 rounded-full flex items-center justify-center border-2 border-white">
              <UserPlus className="h-3 w-3 text-white" />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className={`text-sm font-semibold truncate ${darkMode ? 'text-neutral-200' : 'text-slate-900'}`}>
              {user.name}
            </h3>
            <span className={`text-xs ${darkMode ? 'text-neutral-400' : 'text-slate-500'}`}>
              {formatTime(chat.last_message_time)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <p className={`text-sm truncate flex-1 ${darkMode ? 'text-neutral-400' : 'text-slate-600'}`}>{chat.last_message || 'No messages yet'}</p>
            {unreadCount > 0 && (
              <span className="bg-indigo-600 text-white text-xs rounded-full h-5 min-w-[20px] px-1.5 flex items-center justify-center ml-2 font-medium" data-testid="unread-badge">
                {unreadCount}
              </span>
            )}
          </div>
        </div>
      </div>
      {product && (
        <div className={`text-xs truncate ml-15 flex items-center gap-1 ${darkMode ? 'text-neutral-400' : 'text-slate-500'}`}>
          <span>📦</span>
          <span>{product.title}</span>
        </div>
      )}
    </div>
  );
});

export default React.memo(ChatPage);

