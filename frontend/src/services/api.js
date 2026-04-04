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

// Firebase direct calls - Chats
export const getChats = async (userId) => {
  const q = query(
    collection(db, 'chats'),
    where('participants', 'array-contains', userId),
    orderBy('last_message_time', 'desc')
  )
  const querySnapshot = await getDocs(q)
  return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
}

export const getMessages = async (chatId, limitCount = 50) => {
  const q = query(
    collection(db, 'chats', chatId, 'messages'),
    orderBy('timestamp', 'asc'),
    limit(limitCount)
  )
  const querySnapshot = await getDocs(q)
  return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
}

export const sendMessage = async (chatId, messageData) => {
  const docRef = await addDoc(collection(db, 'chats', chatId, 'messages'), {
    ...messageData,
    timestamp: new Date().toISOString()
  })
  
  const chatRef = doc(db, 'chats', chatId)
  await updateDoc(chatRef, {
    last_message: messageData.text,
    last_message_time: new Date().toISOString()
  })
  
  return { id: docRef.id, ...messageData }
}

export default api
