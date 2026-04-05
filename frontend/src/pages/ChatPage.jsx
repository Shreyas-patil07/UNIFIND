import React, { useState } from 'react';
import Header from '../components/Header';
import { chats, users, products } from '../data/mockData';
import { Send, Paperclip, MapPin, IndianRupee } from 'lucide-react';
import { Button } from '../components/ui/Button';

const ChatPage = () => {
  const [selectedChat, setSelectedChat] = useState(chats[0]);
  const [message, setMessage] = useState('');

  const getUser = (userId) => users.find(u => u.id === userId);
  const getProduct = (productId) => products.find(p => p.id === productId);

  const currentUser = users[0]; // Mock current user

  return (
    <div className="min-h-screen bg-slate-50">
      <Header hideSearch />
      
      <div className="h-[calc(100vh-60px)] flex with-bottom-nav">
        {/* Chat List - Left Sidebar */}
        <div className="w-full md:w-72 lg:w-80 bg-white border-r border-slate-200 flex flex-col">
          <div className="px-4 py-4 border-b border-slate-200">
            <h2 className="text-lg font-bold text-slate-900" data-testid="chat-list-title">Messages</h2>
          </div>
          <div className="flex-1 overflow-y-auto">
            {chats.map((chat) => {
              const user = getUser(chat.userId);
              const product = getProduct(chat.productId);
              return (
                <div
                  key={chat.id}
                  onClick={() => setSelectedChat(chat)}
                  className={`p-3.5 border-b border-slate-100 cursor-pointer transition-colors ${
                    selectedChat.id === chat.id ? 'bg-indigo-50' : 'hover:bg-slate-50'
                  }`}
                  data-testid={`chat-item-${chat.id}`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img
                      src={user?.avatar}
                      alt={user?.name}
                      className="h-10 w-10 rounded-full object-cover ring-2 ring-slate-100"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="text-sm font-bold text-slate-900 truncate">{user?.name}</h3>
                        {chat.unread > 0 && (
                          <span className="bg-indigo-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold" data-testid="unread-badge">
                            {chat.unread}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-600 truncate">{chat.lastMessage}</p>
                    </div>
                  </div>
                  <div className="text-xs text-slate-500 truncate">📦 {product?.title}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Chat Window - Right Side */}
        <div className="hidden md:flex flex-1 flex-col bg-slate-50">
          {selectedChat ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b border-slate-200 p-6">
                <div className="flex items-center gap-4">
                  <img
                    src={getUser(selectedChat.userId)?.avatar}
                    alt={getUser(selectedChat.userId)?.name}
                    className="h-12 w-12 rounded-full object-cover"
                  />
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-slate-900" data-testid="chat-header-name">
                      {getUser(selectedChat.userId)?.name}
                    </h3>
                    <p className="text-sm text-slate-600">{getUser(selectedChat.userId)?.college}</p>
                  </div>
                  <div className="text-right">
                    <div className="bg-green-50 px-2 py-1 rounded-lg inline-block">
                      <span className="text-xs font-bold text-green-700">
                        Trust: {getUser(selectedChat.userId)?.trustScore}%
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Product Info */}
                <div className="mt-4 bg-slate-50 rounded-xl p-4 flex items-center gap-4">
                  <img
                    src={getProduct(selectedChat.productId)?.images[0]}
                    alt={getProduct(selectedChat.productId)?.title}
                    className="h-16 w-16 rounded-lg object-cover"
                  />
                  <div className="flex-1">
                    <h4 className="text-sm font-bold text-slate-900 mb-1">
                      {getProduct(selectedChat.productId)?.title}
                    </h4>
                    <p className="text-lg font-black text-indigo-600">
                      ₹{getProduct(selectedChat.productId)?.price.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4" data-testid="messages-container">
                {selectedChat.messages.map((msg) => {
                  const isCurrentUser = msg.senderId === currentUser.id;
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
                        <p className="text-sm">{msg.text}</p>
                        <p className={`text-xs mt-1 ${
                          isCurrentUser ? 'text-blue-100' : 'text-slate-500'
                        }`}>
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Quick Actions */}
              <div className="bg-white border-t border-slate-200 px-6 py-3">
                <div className="flex gap-2 mb-3">
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl text-xs"
                    data-testid="quick-action-location"
                  >
                    <MapPin className="h-3 w-3 mr-1" />
                    Share Location
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl text-xs"
                    data-testid="quick-action-offer"
                  >
                    <IndianRupee className="h-3 w-3 mr-1" />
                    Send Offer
                  </Button>
                </div>
              </div>

              {/* Input Area */}
              <div className="bg-white border-t border-slate-200 p-6">
                <div className="flex items-center gap-3">
                  <Button variant="ghost" size="sm" className="rounded-xl" data-testid="attach-btn">
                    <Paperclip className="h-5 w-5" />
                  </Button>
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="input-premium flex-1 px-4 py-2.5 text-sm"
                    data-testid="message-input"
                  />
                  <Button
                    className="btn-gradient h-10 w-10 p-0 flex items-center justify-center rounded-xl flex-shrink-0"
                    data-testid="send-btn"
                  >
                    <Send className="h-5 w-5" />
                  </Button>
                </div>
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

export default ChatPage;
