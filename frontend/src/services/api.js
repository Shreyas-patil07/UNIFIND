import axios from 'axios'
import {
  collection,
  doc,
  getDoc,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  limit
} from 'firebase/firestore'
import { db } from './firebase'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Backend API calls
export const createStatusCheck = async (clientName) => {
  const response = await api.post('/status', { client_name: clientName })
  return response.data
}

export const getStatusChecks = async () => {
  const response = await api.get('/status')
  return response.data
}

// Firebase direct calls - Users
export const getUser = async (userId) => {
  const docRef = doc(db, 'users', userId)
  const docSnap = await getDoc(docRef)
  if (docSnap.exists()) {
    return { id: docSnap.id, ...docSnap.data() }
  }
  throw new Error('User not found')
}

// Get public user profile via backend API
export const getPublicProfile = async (userId, includePrivate = false) => {
  const response = await api.get(`/users/${userId}/profile`, {
    params: { include_private: includePrivate }
  })
  return response.data
}

export const getUsers = async (limitCount = 100) => {
  const q = query(collection(db, 'users'), limit(limitCount))
  const querySnapshot = await getDocs(q)
  return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
}

// Firebase direct calls - Products
export const getProduct = async (productId) => {
  const docRef = doc(db, 'products', productId)
  const docSnap = await getDoc(docRef)
  if (docSnap.exists()) {
    return { id: docSnap.id, ...docSnap.data() }
  }
  throw new Error('Product not found')
}

export const getProducts = async (filters = {}) => {
  let q = collection(db, 'products')
  
  if (filters.category && filters.category !== 'All') {
    q = query(q, where('category', '==', filters.category))
  }
  
  if (filters.seller_id) {
    q = query(q, where('seller_id', '==', filters.seller_id))
  }
  
  q = query(q, orderBy('created_at', 'desc'), limit(filters.limit || 100))
  
  const querySnapshot = await getDocs(q)
  return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
}

export const createProduct = async (productData) => {
  const docRef = await addDoc(collection(db, 'products'), {
    ...productData,
    created_at: new Date().toISOString(),
    views: 0
  })
  return { id: docRef.id, ...productData }
}

export const updateProduct = async (productId, productData) => {
  const docRef = doc(db, 'products', productId)
  await updateDoc(docRef, productData)
  return { id: productId, ...productData }
}

export const deleteProduct = async (productId) => {
  const docRef = doc(db, 'products', productId)
  await deleteDoc(docRef)
  return { id: productId }
}

// Chat API calls via backend
export const getUserChats = async (userId) => {
  const response = await api.get(`/chats/${userId}`)
  return response.data
}

export const getChatMessages = async (chatRoomId) => {
  const response = await api.get(`/chats/room/${chatRoomId}/messages`)
  return response.data
}

export const sendChatMessage = async (messageData) => {
  const response = await api.post('/chats/messages', messageData)
  return response.data
}

export const getOrCreateChatRoom = async (user1Id, user2Id, productId = null) => {
  const params = productId ? `?product_id=${productId}` : ''
  const response = await api.get(`/chats/between/${user1Id}/${user2Id}${params}`)
  return response.data
}

export const markChatAsRead = async (chatRoomId, userId) => {
  const response = await api.put(`/chats/${chatRoomId}/mark-read/${userId}`)
  return response.data
}

export default api


// AI Need Board
export const searchNeedBoard = async (query) => {
  const response = await api.post('/need-board', { query })
  return response.data // { extracted, rankedResults }
}
