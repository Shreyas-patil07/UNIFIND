/**
 * API Service Layer - All backend API calls
 * Uses centralized API client with error handling and retries
 */

import { get, post, put, patch, del } from '../lib/api-client'
import type {
  User,
  UserProfile,
  Product,
  ProductCreate,
  ProductUpdate,
  Message,
  ChatRoom,
  Review,
  NeedBoardResponse,
  NeedBoardHistory,
  Transaction,
  HealthCheck,
} from '../types/api'

// ============= HEALTH CHECK =============

export const healthCheck = () => get<HealthCheck>('/health')

// ============= PRODUCTS =============

export const getProducts = async (filters?: {
  category?: string
  min_price?: number
  max_price?: number
  condition?: string
  seller_id?: string
}) => {
  const response = await get<{ items: Product[]; total: number; page: number; page_size: number; pages: number }>('/products', { params: filters })
  // Backend returns paginated response, extract items array
  return response.items || []
}

export const getProduct = (productId: string) =>
  get<Product>(`/products/${productId}`)

export const createProduct = (product: ProductCreate) =>
  post<Product>('/products', product)

export const updateProduct = (productId: string, product: ProductUpdate) =>
  patch<Product>(`/products/${productId}`, product)

export const deleteProduct = (productId: string) =>
  del<{ message: string }>(`/products/${productId}`)

export const getSellerProducts = () => get<Product[]>('/products/seller/me')

// ============= USERS =============

export const getUsers = () => get<User[]>('/users')

export const getUser = (userId: string) => get<User>(`/users/${userId}`)

export const getUserByFirebaseUid = (firebaseUid: string) =>
  get<User>(`/users/firebase/${firebaseUid}`)

export const searchUsers = (query: string) =>
  get<User[]>(`/users/search/${encodeURIComponent(query)}`)

export const getUserProfile = (userId: string, includePrivate = false) =>
  get<UserProfile>(`/users/${userId}/profile`, {
    params: { include_private: includePrivate },
  })

export const updateUserProfile = (
  userId: string,
  updates: Partial<UserProfile>
) => put<UserProfile>(`/users/${userId}/profile`, updates)

// ============= FRIENDS =============

export const getFriends = (userId: string) =>
  get<User[]>(`/users/${userId}/friends`)

export const getPendingFriendRequests = (userId: string) =>
  get<User[]>(`/users/${userId}/friends/requests/pending`)

export const checkFriendship = (userId: string, friendId: string) =>
  get<{ status: string }>(`/users/${userId}/friends/check/${friendId}`)

export const addFriend = (userId: string, friendId: string) =>
  post<{ message: string; friendship_id: string; status: string }>(
    `/users/${userId}/friends/${friendId}`
  )

export const acceptFriendRequest = (userId: string, friendId: string) =>
  put<{ message: string }>(`/users/${userId}/friends/${friendId}/accept`)

export const rejectFriendRequest = (userId: string, friendId: string) =>
  put<{ message: string }>(`/users/${userId}/friends/${friendId}/reject`)

export const removeFriend = (userId: string, friendId: string) =>
  del<{ message: string }>(`/users/${userId}/friends/${friendId}`)

// ============= CHATS =============

export const getUserChats = (userId: string, friendsOnly = false) =>
  get<ChatRoom[]>(`/chats/${userId}`, { params: { friends_only: friendsOnly } })

export const getChatMessages = (chatRoomId: string) =>
  get<Message[]>(`/chats/room/${chatRoomId}/messages`)

export const sendMessage = (message: {
  text: string
  sender_id: string
  receiver_id: string
  product_id?: string
}) => post<Message>('/chats/messages', message)

export const getOrCreateChatRoom = (
  user1Id: string,
  user2Id: string,
  productId?: string
) => {
  const params = productId ? `?product_id=${productId}` : ''
  return get<ChatRoom>(`/chats/between/${user1Id}/${user2Id}${params}`)
}

export const markChatAsRead = (chatRoomId: string, userId: string) =>
  put<{ message: string }>(`/chats/${chatRoomId}/mark-read/${userId}`)

// ============= REVIEWS =============

export const createReview = (review: {
  rating: number
  comment: string
  reviewer_id: string
  reviewed_user_id: string
  product_id?: string
}) => post<Review>('/reviews', review)

export const getUserReviews = (userId: string) =>
  get<Review[]>(`/reviews/user/${userId}`)

export const getProductReviews = (productId: string) =>
  get<Review[]>(`/reviews/product/${productId}`)

// ============= NEED BOARD =============

export const searchNeedBoard = (query: string) =>
  post<NeedBoardResponse>('/need-board', { query })

export const getNeedBoardHistory = () =>
  get<NeedBoardHistory>('/need-board/history')

// ============= TRANSACTIONS =============

export const getUserTransactions = (
  userId: string,
  transactionType?: 'buy' | 'sell'
) =>
  get<Transaction[]>(`/users/${userId}/transactions`, {
    params: { transaction_type: transactionType },
  })

export const createTransaction = (
  userId: string,
  transaction: {
    user_id: string
    product_id: string
    transaction_type: 'buy' | 'sell'
    amount: number
    status: string
    other_party_id: string
  }
) => post<Transaction>(`/users/${userId}/transactions`, transaction)

// ============= UPLOADS =============

export const uploadProductImage = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return post<{ url: string; public_id: string }>(
    '/upload/product-image',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )
}

export const uploadProductImages = (files: File[]) => {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  return post<{ urls: string[]; public_ids: string[] }>(
    '/upload/product-images',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )
}
