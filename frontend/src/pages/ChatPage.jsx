import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import { Send, MapPin, IndianRupee, ArrowLeft, Check, CheckCheck, Smile, Search, MoreVertical } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { getUserChats, getChatMessages, sendChatMessage, getOrCreateChatRoom, getPublicProfile, getProduct } from '../services/api';

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
  
  const messagesEndRef = useRef(null);
  const messageInputRef = useRef(null);

  // Get user ID from URL params (for starting new chat)
  const targetUserId = searchParams.get('user');
  const productId = searchParams.get('product');

  // Get message status for read receipts
  const getMessageStatus = (msg) => {
    if (msg.sender_id !== currentUser?.uid) return null;
    // You can add status field to Firebase messages
    // For now, simulate: recent messages = sent, older = delivered, oldest = read
    const msgTime = msg.timestamp?.seconds ? new Date(msg.timestamp.seconds * 1000) : new Date(msg.timestamp);
    const now = new Date();
    const diffMinutes = (now - msgTime) / 60000;
    
    if (diffMinutes < 2) return 'sent';
    if (diffMinutes < 5) return 'delivered';
    return 'read';
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

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load user's chats
  useEffect(() => {
    if (!currentUser) {
      navigate('/login');
      return;
    }

    const loadChats = async () => {
      try {
        const userChats = await getUserChats(currentUser.uid);
        setChats(userChats);
        
        // If there's a target user, create/get chat room
        if (targetUserId && targetUserId !== currentUser.uid) {
          const chatRoom = await getOrCreateChatRoom(currentUser.uid, targetUserId, productId);
          setSelectedChat(chatRoom);
          
          // Load other user's profile
          const profile = await getPublicProfile(targetUserId);
          setOtherUser(profile);
          
          // Load product if specified
          if (productId) {
            const prod = await getProduct(productId);
            setProduct(prod);
          }
        }
        // Don't auto-select first chat - let user choose
        
        setLoading(false);
      } catch (error) {
        console.error('Failed to load chats:', error);
        setLoading(false);
      }
    };

    loadChats();
  }, [currentUser, targetUserId, productId, navigate]);

  // Load messages when chat is selected
  useEffect(() => {
    if (!selectedChat) return;

    const loadMessages = async () => {
      try {
        const chatMessages = await getChatMessages(selectedChat.id);
        setMessages(chatMessages);
        
        // Load other user's profile if not already loaded
        if (!otherUser) {
          const otherId = selectedChat.user1_id === currentUser.uid 
            ? selectedChat.user2_id 
            : selectedChat.user1_id;
          const profile = await getPublicProfile(otherId);
          setOtherUser(profile);
        }
        
        // Load product if specified and not already loaded
        if (selectedChat.product_id && !product) {
          const prod = await getProduct(selectedChat.product_id);
          setProduct(prod);
        }
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    };

    loadMessages();
    
    // Poll for new messages every 3 seconds
    const interval = setInterval(loadMessages, 3000);
    return () => clearInterval(interval);
  }, [selectedChat, currentUser, otherUser, product]);

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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || !selectedChat || !currentUser || sending) return;

    const otherId = selectedChat.user1_id === currentUser.uid 
      ? selectedChat.user2_id 
      : selectedChat.user1_id;

    setSending(true);
    const messageText = message.trim(); // Capture message before clearing
    try {
      const newMessage = await sendChatMessage({
        text: messageText,
        sender_id: currentUser.uid,
        receiver_id: otherId,
        product_id: selectedChat.product_id || null
      });
      
      setMessages(prev => [...prev, newMessage]);
      setMessage('');
      messageInputRef.current?.focus();
      
      // Reload chats from backend to get updated last_message and timestamp
      const updatedChats = await getUserChats(currentUser.uid);
      setChats(updatedChats);
      
      // Update selected chat to match the updated one from backend
      const updatedSelectedChat = updatedChats.find(chat => chat.id === selectedChat.id);
      if (updatedSelectedChat) {
        setSelectedChat(updatedSelectedChat);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Filter chats based on search
  const filteredChats = chats.filter(chat => {
    if (!searchQuery) return true;
    
    const searchLower = searchQuery.toLowerCase();
    
    // Search in last message
    if (chat.last_message?.toLowerCase().includes(searchLower)) return true;
    
    // The actual user name filtering happens in ChatListItem component
    // So we return true here and let ChatListItem handle the filtering
    return true;
  });

  const handleChatSelect = async (chat) => {
    setSelectedChat(chat);
    setMessages([]);
    setOtherUser(null);
    setProduct(null);
  };

  if (loading) {
    return (
      <div className={`h-[100dvh] flex flex-col overflow-hidden ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <Header hideSearch />
        <div className="flex items-center justify-center flex-1">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className={darkMode ? 'text-slate-400' : 'text-slate-600'}>Loading chats...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`h-[100dvh] flex flex-col overflow-hidden ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header hideSearch />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Chat List - Left Sidebar */}
        <div className={`${selectedChat ? 'hidden md:flex' : 'flex'} w-full md:w-72 lg:w-80 border-r flex-col shadow-sm h-full ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`px-4 py-4 border-b flex-shrink-0 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center justify-between mb-3">
              <h2 className={`text-xl font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`} data-testid="chat-list-title">
                Chats
              </h2>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`rounded-full p-2 ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}
                onClick={() => setShowSearch(!showSearch)}
              >
                <Search className={`h-5 w-5 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`} />
              </Button>
            </div>
            {showSearch && (
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats..."
                className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-all ${
                  darkMode 
                    ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-indigo-500'
                    : 'bg-white border-slate-200 text-slate-900 placeholder-slate-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20'
                }`}
              />
            )}
          </div>
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
            {filteredChats.length === 0 ? (
              <div className={`p-8 text-center flex flex-col items-center justify-center h-full ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                <div className={`h-20 w-20 rounded-full flex items-center justify-center mb-4 ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                  <Send className={`h-10 w-10 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                </div>
                <p className={`font-semibold mb-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>No messages yet</p>
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
                />
              ))
            )}
          </div>
        </div>

        {/* Chat Window - Right Side */}
        <div className={`${selectedChat ? 'flex' : 'hidden md:flex'} flex-1 flex-col overflow-hidden ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
          {selectedChat && otherUser ? (
            <>
              {/* Chat Header */}
              <div className={`border-b p-3 md:p-4 shadow-sm flex-shrink-0 z-10 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setSelectedChat(null)}
                    className={`md:hidden p-2 -ml-2 rounded-full transition-all flex items-center justify-center active:scale-95 ${darkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
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
                      isOtherUserOnline(messages, otherUser.user_id || otherUser.id) ? 'bg-green-500' : 'bg-slate-400'
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
                      isOtherUserOnline(messages, otherUser.user_id || otherUser.id) 
                        ? 'text-green-600' 
                        : darkMode ? 'text-slate-400' : 'text-slate-500'
                    }`}>
                      {isOtherUserOnline(messages, otherUser.user_id || otherUser.id) ? 'online' : 'offline'}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" className={`rounded-full p-2 ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}>
                    <MoreVertical className={`h-5 w-5 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`} />
                  </Button>
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
                className={`flex-1 overflow-y-auto p-3 md:p-4 flex flex-col scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent overscroll-contain ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}
                data-testid="messages-container"
              >
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="bg-indigo-100 h-24 w-24 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Send className="h-12 w-12 text-indigo-600" />
                      </div>
                      <p className={`text-lg font-semibold mb-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>No messages yet</p>
                      <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Start the conversation!</p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg, index) => {
                    const isCurrentUser = msg.sender_id === currentUser.uid;
                    const showDateSeparator = shouldShowDateSeparator(msg, messages[index - 1]);
                    // Only group messages that are from the same sender and same day
                    const isSameSenderAsPrev = index > 0 && messages[index - 1].sender_id === msg.sender_id && !showDateSeparator;
                    const showAvatar = !isSameSenderAsPrev;
                    const status = getMessageStatus(msg);
                    
                    const mtClass = showDateSeparator ? 'mt-0' : (isSameSenderAsPrev ? 'mt-[2px]' : 'mt-4');

                    return (
                      <React.Fragment key={msg.id}>
                        {showDateSeparator && (
                          <div className={`flex justify-center ${index === 0 ? 'mt-0 mb-4' : 'my-4'}`}>
                            <span className={`text-xs px-4 py-1.5 rounded-full shadow-sm font-medium ${darkMode ? 'bg-slate-800 text-slate-400' : 'bg-white text-slate-600'}`}>
                              {formatDateSeparator(msg.timestamp)}
                            </span>
                          </div>
                        )}
                        <div
                          className={`flex gap-2 ${mtClass} ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
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
                                      ? 'bg-slate-800 text-slate-200 border-slate-700' 
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
                                <span className="inline-flex">
                                  {status === 'sent' && <Check className="h-3 w-3 text-indigo-200" />}
                                  {status === 'delivered' && <CheckCheck className="h-3 w-3 text-indigo-200" />}
                                  {status === 'read' && <CheckCheck className="h-3 w-3 text-blue-300" />}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </React.Fragment>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className={`border-t p-2 sm:p-3 shadow-[0_-4px_10px_rgba(0,0,0,0.02)] flex-shrink-0 pb-[calc(0.5rem+env(safe-area-inset-bottom))] md:pb-3 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                  <Button 
                    type="button"
                    variant="ghost" 
                    size="sm" 
                    className={`rounded-full p-2 flex-shrink-0 ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}
                  >
                    <Smile className={`h-6 w-6 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`} />
                  </Button>
                  <input
                    ref={messageInputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Message..."
                    className={`flex-1 px-4 py-2.5 sm:py-3 text-[16px] sm:text-sm rounded-full border outline-none transition-all ${
                      darkMode 
                        ? 'bg-slate-700 border-slate-600 text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:bg-slate-700'
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
              <p className={darkMode ? 'text-slate-400' : 'text-slate-500'}>Select a chat to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Chat List Item Component
const ChatListItem = ({ chat, currentUserId, isSelected, onClick, formatTime, searchQuery, darkMode }) => {
  const [user, setUser] = useState(null);
  const [product, setProduct] = useState(null);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const otherId = chat.user1_id === currentUserId ? chat.user2_id : chat.user1_id;
        const userProfile = await getPublicProfile(otherId);
        setUser(userProfile);
        
        if (chat.product_id) {
          const prod = await getProduct(chat.product_id);
          setProduct(prod);
        }

        // Check if other user is online by getting their last message
        const messages = await getChatMessages(chat.id);
        const otherUserMessages = messages.filter(msg => msg.sender_id === otherId);
        
        if (otherUserMessages.length > 0) {
          const lastMessage = otherUserMessages[otherUserMessages.length - 1];
          const lastMessageTime = lastMessage.timestamp?.seconds 
            ? new Date(lastMessage.timestamp.seconds * 1000)
            : new Date(lastMessage.timestamp);
          
          const now = new Date();
          const diffMinutes = (now - lastMessageTime) / 60000;
          setIsOnline(diffMinutes < 5);
        }
      } catch (error) {
        console.error('Failed to load chat data:', error);
      }
    };

    loadData();
  }, [chat, currentUserId]);

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
      <div className={`p-4 border-b animate-pulse ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
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
          ? `border-slate-700 hover:bg-slate-700/50 ${isSelected ? 'bg-indigo-900/30 border-l-4 border-l-indigo-600' : ''}`
          : `border-slate-100 hover:bg-slate-50 ${isSelected ? 'bg-indigo-50 border-l-4 border-l-indigo-600' : ''}`
      }`}
      data-testid={`chat-item-${chat.id}`}
    >
      <div className="flex items-center gap-3 mb-1.5 sm:mb-2 text-sm sm:text-base">
        <div className="relative">
          <img
            src={user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}`}
            alt={user.name}
            className="h-11 w-11 sm:h-12 sm:w-12 rounded-full object-cover ring-2 ring-slate-100"
          />
          {isOnline && (
            <div className="absolute bottom-0 right-0 h-3 w-3 bg-green-500 rounded-full border-2 border-white"></div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className={`text-sm font-semibold truncate ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
              {user.name}
            </h3>
            <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {formatTime(chat.last_message_time)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <p className={`text-sm truncate flex-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{chat.last_message || 'No messages yet'}</p>
            {unreadCount > 0 && (
              <span className="bg-indigo-600 text-white text-xs rounded-full h-5 min-w-[20px] px-1.5 flex items-center justify-center ml-2 font-medium" data-testid="unread-badge">
                {unreadCount}
              </span>
            )}
          </div>
        </div>
      </div>
      {product && (
        <div className={`text-xs truncate ml-15 flex items-center gap-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
          <span>📦</span>
          <span>{product.title}</span>
        </div>
      )}
    </div>
  );
};

export default ChatPage;
