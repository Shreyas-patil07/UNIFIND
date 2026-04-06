// Mock data for UNIFIND platform

export const users = [
  {
    id: 1,
    name: "Arjun Sharma",
    avatar: "https://images.unsplash.com/photo-1760552069234-54b9c04bbb05?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxwb3J0cmFpdCUyMHN0dWRlbnQlMjB5b3VuZyUyMHNtaWxpbmd8ZW58MHx8fHwxNzc0NjgxNDg0fDA&ixlib=rb-4.1.0&q=85",
    trustScore: 92,
    college: "IIT Delhi",
    rating: 4.8,
    reviewCount: 34,
    memberSince: "2023"
  },
  {
    id: 2,
    name: "Priya Mehta",
    avatar: "https://images.unsplash.com/photo-1611181355758-089959e2cfb2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxwb3J0cmFpdCUyMHN0dWRlbnQlMjB5b3VuZyUyMHNtaWxpbmd8ZW58MHx8fHwxNzc0NjgxNDg0fDA&ixlib=rb-4.1.0&q=85",
    trustScore: 88,
    college: "BITS Pilani",
    rating: 4.6,
    reviewCount: 28,
    memberSince: "2023"
  },
  {
    id: 3,
    name: "Rahul Verma",
    avatar: "https://images.pexels.com/photos/8617732/pexels-photo-8617732.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    trustScore: 95,
    college: "NIT Trichy",
    rating: 4.9,
    reviewCount: 42,
    memberSince: "2022"
  }
]

export const products = [
  {
    id: 1,
    title: "MacBook Air M2 2023",
    price: 75000,
    condition: "Like New",
    conditionScore: 95,
    category: "Laptops",
    images: [
      "https://images.unsplash.com/photo-1592041275490-dcac548bad2e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwzfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85",
      "https://images.unsplash.com/photo-1627691673558-cf76f304f273?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwyfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "Gently used MacBook Air M2 with 8GB RAM and 256GB SSD. No scratches, battery health at 98%. Comes with original charger and box.",
    sellerId: 1,
    location: "Delhi",
    postedDate: "2024-01-15",
    views: 234,
    specifications: {
      processor: "Apple M2",
      ram: "8GB",
      storage: "256GB SSD",
      battery: "98% Health"
    }
  },
  {
    id: 2,
    title: "iPhone 13 Pro 128GB",
    price: 52000,
    condition: "Good",
    conditionScore: 85,
    category: "Phones",
    images: [
      "https://images.unsplash.com/photo-1759863639101-d1ad4923d655?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "iPhone 13 Pro in Sierra Blue. Minor scratches on the back. Battery health 87%. All features working perfectly.",
    sellerId: 2,
    location: "Mumbai",
    postedDate: "2024-01-14",
    views: 189,
    specifications: {
      storage: "128GB",
      battery: "87% Health",
      color: "Sierra Blue"
    }
  },
  {
    id: 3,
    title: "Sony WH-1000XM5 Headphones",
    price: 18000,
    condition: "Excellent",
    conditionScore: 92,
    category: "Accessories",
    images: [
      "https://images.unsplash.com/photo-1627691673558-cf76f304f273?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwyfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "Premium noise-canceling headphones. Used for 3 months. All accessories included.",
    sellerId: 3,
    location: "Bangalore",
    postedDate: "2024-01-13",
    views: 156,
    specifications: {
      type: "Over-Ear",
      features: "Active Noise Cancellation",
      warranty: "Extended till Dec 2024"
    }
  },
  {
    id: 4,
    title: "Canon EOS M50 Camera",
    price: 38000,
    condition: "Like New",
    conditionScore: 94,
    category: "Cameras",
    images: [
      "https://images.unsplash.com/photo-1592041275490-dcac548bad2e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwzfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "Mirrorless camera with 15-45mm kit lens. Barely used, perfect for beginners.",
    sellerId: 1,
    location: "Pune",
    postedDate: "2024-01-12",
    views: 98,
    specifications: {
      megapixels: "24.1 MP",
      lens: "15-45mm Kit Lens",
      condition: "Mint"
    }
  },
  {
    id: 5,
    title: "iPad Air 5th Gen 256GB",
    price: 45000,
    condition: "Good",
    conditionScore: 88,
    category: "Tablets",
    images: [
      "https://images.unsplash.com/photo-1759863639101-d1ad4923d655?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "Space Gray iPad Air with Apple Pencil 2nd gen. Light scratches on screen.",
    sellerId: 2,
    location: "Chennai",
    postedDate: "2024-01-11",
    views: 167,
    specifications: {
      storage: "256GB",
      color: "Space Gray",
      includes: "Apple Pencil 2"
    }
  },
  {
    id: 6,
    title: "Dell XPS 13 i7 11th Gen",
    price: 68000,
    condition: "Excellent",
    conditionScore: 90,
    category: "Laptops",
    images: [
      "https://images.unsplash.com/photo-1592041275490-dcac548bad2e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA4Mzl8MHwxfHNlYXJjaHwzfHxsYXB0b3AlMjBzbWFydHBob25lJTIwaGVhZHBob25lcyUyMGNhbWVyYXxlbnwwfHx8fDE3NzQ2ODE0ODJ8MA&ixlib=rb-4.1.0&q=85"
    ],
    description: "Premium ultrabook with 16GB RAM and 512GB SSD. Perfect for coding and design work.",
    sellerId: 3,
    location: "Hyderabad",
    postedDate: "2024-01-10",
    views: 201,
    specifications: {
      processor: "Intel i7 11th Gen",
      ram: "16GB",
      storage: "512GB SSD"
    }
  }
]

export const chats = [
  {
    id: 1,
    userId: 2,
    productId: 1,
    lastMessage: "Is the laptop still available?",
    timestamp: "2024-01-15T10:30:00",
    unread: 2,
    messages: [
      {
        id: 1,
        senderId: 2,
        text: "Hi! Is the MacBook still available?",
        timestamp: "2024-01-15T10:00:00"
      },
      {
        id: 2,
        senderId: 1,
        text: "Yes, it's available! Would you like to check it out?",
        timestamp: "2024-01-15T10:15:00"
      },
      {
        id: 3,
        senderId: 2,
        text: "Is the laptop still available?",
        timestamp: "2024-01-15T10:30:00"
      }
    ]
  },
  {
    id: 2,
    userId: 3,
    productId: 2,
    lastMessage: "Can you do ₹50k?",
    timestamp: "2024-01-14:15:45:00",
    unread: 0,
    messages: [
      {
        id: 1,
        senderId: 3,
        text: "Interested in the iPhone. Can you do ₹50k?",
        timestamp: "2024-01-14T15:30:00"
      },
      {
        id: 2,
        senderId: 2,
        text: "Can you do ₹50k?",
        timestamp: "2024-01-14T15:45:00"
      }
    ]
  }
]

export const stats = {
  totalListings: 1247,
  totalUsers: 8934,
  successfulDeals: 3421,
  avgRating: 4.7
}

export const userStats = {
  bought: 12,
  sold: 8,
  rating: 4.8,
  earnings: 124500,
  savings: 89300,
  trustScore: 92
}

export const recentActivity = [
  {
    id: 1,
    type: "purchase",
    title: "Bought MacBook Air M2",
    amount: 75000,
    date: "2024-01-15"
  },
  {
    id: 2,
    type: "sale",
    title: "Sold iPhone 12",
    amount: 35000,
    date: "2024-01-14"
  },
  {
    id: 3,
    type: "review",
    title: "Received 5-star review",
    date: "2024-01-13"
  }
]

export const reviews = [
  {
    id: 1,
    userId: 2,
    rating: 5,
    comment: "Great seller! Product exactly as described. Fast delivery.",
    date: "2024-01-13"
  },
  {
    id: 2,
    userId: 3,
    rating: 5,
    comment: "Smooth transaction. Highly recommended!",
    date: "2024-01-10"
  },
  {
    id: 3,
    userId: 1,
    rating: 4,
    comment: "Good product, minor delay in meetup.",
    date: "2024-01-08"
  }
]

export const categories = [
  "All",
  "Laptops",
  "Phones",
  "Tablets",
  "Cameras",
  "Accessories",
  "Books",
  "Furniture"
]
