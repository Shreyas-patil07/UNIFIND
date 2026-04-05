import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import { Send, Paperclip, MapPin, IndianRupee, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { getUserChats, getChatMessages, sendChatMessage, getOrCreateChatRoom, getPublicProfile, getProduct } from '../services/api';

const ChatPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { currentUser } = useAuth();
  
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [otherUser, setOtherUser] = useState(null);
  const [product, setProduct] = useState(null);
  
  const messagesEndRef = useRef(null);
  const messageInputRef = useRef(null);

  // Get user ID from URL params (for starting new chat)
  const targetUserId = searchParams.get('user');
  const productId = searchParams.get('product');

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
        } else if (userChats.length > 0) {
          // Select first chat by default
          setSelectedChat(userChats[0]);
        }
        
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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || !selectedChat || !currentUser || sending) return;

    const otherId = selectedChat.user1_id === currentUser.uid 
      ? selectedChat.user2_id 
      : selectedChat.user1_id;

    setSending(true);
    try {
      const newMessage = await sendChatMessage({
        text: message.trim(),
        sender_id: currentUser.uid,
        receiver_id: otherId,
        product_id: selectedChat.product_id || null
      });
      
      setMessages(prev => [...prev, newMessage]);
      setMessage('');
      messageInputRef.current?.focus();
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleChatSelect = async (chat) => {
    setSelectedChat(chat);
    setMessages([]);
    setOtherUser(null);
    setProduct(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header hideSearch />
        <div className="flex items-center justify-center h-[calc(100vh-80px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading chats...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Header hideSearch />
      
      <div className="h-[calc(100vh-60px)] flex">
        {/* Chat List - Left Sidebar */}
        <div className={`${selectedChat ? 'hidden md:flex' : 'flex'} w-full md:w-72 lg:w-80 bg-white border-r border-slate-200 flex-col`}>
          <div className="px-4 py-4 border-b border-slate-200">
            <h2 className="text-lg font-bold text-slate-900" data-testid="chat-list-title">Messages</h2>
          </div>
          <div className="flex-1 overflow-y-auto">
            {chats.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <p>No messages yet</p>
                <p className="text-sm mt-2">Start a conversation from a product listing</p>
              </div>
            ) : (
              chats.map((chat) => (
                <ChatListItem
                  key={chat.id}
                  chat={chat}
                  currentUserId={currentUser.uid}
                  isSelected={selectedChat?.id === chat.id}
                  onClick={() => handleChatSelect(chat)}
                />
              ))
            )}
          </div>
        </div>

        {/* Chat Window - Right Side */}
        <div className={`${selectedChat ? 'flex' : 'hidden md:flex'} flex-1 flex-col bg-slate-50`}>
          {selectedChat && otherUser ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b border-slate-200 p-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setSelectedChat(null)}
                    className="md:hidden text-slate-600 hover:text-slate-900"
                  >
                    <ArrowLeft className="h-6 w-6" />
                  </button>
                  <img
                    src={otherUser.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name || 'User')}`}
                    alt={otherUser.name}
                    className="h-12 w-12 rounded-full object-cover cursor-pointer"
                    onClick={() => navigate(`/profile/${otherUser.user_id || otherUser.id}`)}
                  />
                  <div className="flex-1">
                    <h3 
                      className="text-lg font-bold text-slate-900 cursor-pointer hover:text-indigo-600" 
                      data-testid="chat-header-name"
                      onClick={() => navigate(`/profile/${otherUser.user_id || otherUser.id}`)}
                    >
                      {otherUser.name}
                    </h3>
                    <p className="text-sm text-slate-600">{otherUser.college}</p>
                  </div>
                  {otherUser.trust_score !== undefined && (
                    <div className="text-right">
                      <div className="bg-green-50 px-2 py-1 rounded-lg inline-block">
                        <span className="text-xs font-bold text-green-700">
                          Trust: {otherUser.trust_score}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Product Info */}
                {product && (
                  <div className="mt-4 bg-slate-50 rounded-xl p-4 flex items-center gap-4 cursor-pointer hover:bg-slate-100 transition-colors"
                    onClick={() => navigate(`/listing/${product.id}`)}>
                    <img
                      src={product.images?.[0] || '/placeholder.png'}
                      alt={product.title}
                      className="h-16 w-16 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <h4 className="text-sm font-bold text-slate-900 mb-1">
                        {product.title}
                      </h4>
                      <p className="text-lg font-black text-indigo-600">
                        ₹{product.price?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4" data-testid="messages-container">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-slate-500">No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  messages.map((msg) => {
                    const isCurrentUser = msg.sender_id === currentUser.uid;
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                        data-testid={`message-${msg.id}`}
                      >
                        <div className={`max-w-[75%] sm:max-w-[65%] rounded-2xl px-4 py-2.5 ${
                          isCurrentUser
                            ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white'
                            : 'bg-white border border-slate-200 text-slate-900 shadow-sm'
                        }`}>
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.text}</p>
                          <p className={`text-xs mt-1 ${
                            isCurrentUser ? 'text-blue-100' : 'text-slate-500'
                          }`}>
                            {new Date(msg.timestamp?.seconds ? msg.timestamp.seconds * 1000 : msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="bg-white border-t border-slate-200 p-4">
                <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                  <input
                    ref={messageInputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                    data-testid="message-input"
                    disabled={sending}
                  />
                  <Button
                    type="submit"
                    disabled={!message.trim() || sending}
                    className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 h-10 w-10 p-0 flex items-center justify-center rounded-xl flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
                    data-testid="send-btn"
                  >
                    <Send className="h-5 w-5" />
                  </Button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-slate-500">Select a chat to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Chat List Item Component
const ChatListItem = ({ chat, currentUserId, isSelected, onClick }) => {
  const [user, setUser] = useState(null);
  const [product, setProduct] = useState(null);

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
      } catch (error) {
        console.error('Failed to load chat data:', error);
      }
    };

    loadData();
  }, [chat, currentUserId]);

  if (!user) {
    return (
      <div className="p-3.5 border-b border-slate-100 animate-pulse">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-slate-200"></div>
          <div className="flex-1">
            <div className="h-4 bg-slate-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-slate-200 rounded w-1/2"></div>
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
      className={`p-3.5 border-b border-slate-100 cursor-pointer transition-colors ${
        isSelected ? 'bg-indigo-50' : 'hover:bg-slate-50'
      }`}
      data-testid={`chat-item-${chat.id}`}
    >
      <div className="flex items-center gap-3 mb-2">
        <img
          src={user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}`}
          alt={user.name}
          className="h-10 w-10 rounded-full object-cover ring-2 ring-slate-100"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-bold text-slate-900 truncate">{user.name}</h3>
            {unreadCount > 0 && (
              <span className="bg-indigo-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold" data-testid="unread-badge">
                {unreadCount}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-600 truncate">{chat.last_message || 'No messages yet'}</p>
        </div>
      </div>
      {product && (
        <div className="text-xs text-slate-500 truncate">📦 {product.title}</div>
      )}
    </div>
  );
};

export default ChatPage;
