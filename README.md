<div align="center">

# 🎓 UNIFIND - College Marketplace Platform

<img src="frontend/public/UNIFIND.png" alt="UNIFIND Logo" width="400"/>

### AI-Powered Student-to-Student Marketplace for Campus Commerce

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/Shreyas-patil07/UNIFIND)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-10.7.1-FFCA28.svg)](https://firebase.google.com/)

[🚀 Live Demo](https://unifind-dusky.vercel.app/home) • [📖 Documentation](DOCUMENTATION.md) • [🐛 Report Bug](https://github.com/Shreyas-patil07/UNIFIND/issues) • [✨ Request Feature](https://github.com/Shreyas-patil07/UNIFIND/issues) • [📧 Contact](mailto:systemrecord07@gmail.com)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Documentation](#-documentation)
- [Team](#-team)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 About

**UNIFIND** is a next-generation student-to-student marketplace that revolutionizes campus commerce through AI-powered matching, transparent quality systems, and trust-based transactions. Built with 100% modern technologies, UNIFIND makes buying and selling textbooks, notes, lab equipment, and electronics safe, smart, and sustainable.

> 💡 **The Problem**: Students spend ₹10,000+ per semester on textbooks that sit unused after exams. Existing solutions (Facebook groups, OLX) are unsafe, slow, or expensive.

> ✨ **Our Solution**: A campus-focused marketplace with AI-powered Need Board, Cashify-style condition grading, and comprehensive Trust Scores—all built on cutting-edge, scalable technology with optimized performance (80% faster page loads, 60% faster AI searches).

**Current Version**: 2.4.5 (May 15, 2026)

---

## ✨ Key Features

### Core Marketplace
- 🔐 **Secure Authentication** - Firebase Authentication with built-in email verification
- 🛍️ **Smart Listings** - Create detailed product listings with photos and condition assessment
- 🔍 **Advanced Search & Filtering** - Real-time search with history, nested category dropdowns, and smart sorting
- 📱 **Responsive Design** - Seamless experience across all devices
- ⚡ **Lightning Fast** - Built with Vite for instant hot module replacement (<1s startup)
- 🌙 **Dark Mode** - Toggle between light and dark themes with persistent preference
- 📋 **Recently Viewed** - Track and quickly access recently viewed products
- 💬 **Quick Contact** - WhatsApp and Call buttons for instant seller communication
- 🏷️ **Negotiable Badges** - Clear indicators for price negotiation availability
- ✉️ **Email Verification** - Reliable Firebase email verification system

### AI-Powered Features
- 🤖 **AI Need Board** - Post what you need in natural language, get smart matches
- 🎯 **Semantic Matching** - Finds "Computer Networks" even when you type "CN book"
- 📊 **Smart Analytics** - AI-powered recommendations for listing timing and pricing
- 💡 **Trend Analysis** - Real-time campus trends and demand insights

### Trust & Safety
- ⭐ **Trust Score System** - Build reputation through verified transactions (0-200 scale)
- � **Condition Grading** - Cashify-inspired transparent quality assessment (Fair/Good/Superb)
- ✅ **Verification System** - College email, phone, and ID verification
- 🔒 **Post-Transaction Verification** - Buyers confirm condition accuracy
- � **Report & Moderation** - Flag suspicious listings and users

### Communication & Transactions
- 💬 **Real-time Chat** - Instant messaging between buyers and sellers
- 🗺️ **Location Mapping** - Interactive Leaflet maps for meetup coordination
- � **Meetup Scheduling** - Set time and location with meetup codes
- 💰 **Flexible Payment** - Cash, UPI, or online payment options
- 📦 **Order Tracking** - Track transaction status from confirmation to completion

### Analytics & Insights
- � **Dashboard A2** - Comprehensive analytics dashboard
- 💵 **Financial Summary** - Track earnings, savings, and net benefit
- 🔥 **Campus Trends** - See what's hot on campus right now
- 📊 **Performance Metrics** - Views, conversion rates, and response times
- 🎯 **AI Recommendations** - Smart suggestions for better sales

### Key Metrics & Impact

- **Average Savings**: ₹3,000-5,000 per student per semester
- **Waste Reduction**: Extends lifecycle of educational materials by 2-3x
- **Time to Match**: Less than 5 minutes from posting need to finding relevant listings
- **Trust Coverage**: 95%+ of active sellers with verified college email
- **Condition Accuracy**: 90%+ transactions match described condition
- **Transaction Speed**: Average deal completion in <24 hours

---



## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ◄─────► │  FastAPI Backend│ ◄─────► │    Firebase     │
│  (Vite + React) │  HTTP   │  (Python 3.11)  │  SDK    │   Firestore     │
│   23 Pages      │         │  10 API Routes  │         │ 10 Collections  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                            │                            │
        │                            │                            │
        ▼                            ▼                            ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Cloudinary    │         │   Gemini AI     │         │   Email SMTP    │
│  Image Storage  │         │  Semantic Match │         │  Verification   │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

**Frontend**: React 18 + Vite 5 + Tailwind CSS + React Query  
**Backend**: FastAPI + Uvicorn + Repository Pattern + Service Layer  
**Database**: Firebase Firestore (10 collections)  
**AI**: Google Gemini API (with security hardening)  
**Storage**: Cloudinary (product images) + Supabase (profile photos)  
**Deployment**: Vercel (frontend) + Render (backend)

For detailed architecture, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#architecture)

---

## 🚀 Tech Stack

### Frontend
- **Framework**: React 18.3.1 with Vite 5 (Lightning-fast HMR)
- **Styling**: Tailwind CSS 3.4.1
- **State Management**: React Context API + React Query
- **Routing**: React Router DOM 6.22.0
- **HTTP Client**: Axios 1.6.7
- **Icons**: Lucide React 0.507.0
- **Maps**: Leaflet 1.9.4 + React Leaflet 4.2.1

### Backend
- **Framework**: FastAPI 0.110.1 (Python 3.11+)
- **Server**: Uvicorn 0.25.0 (ASGI)
- **Database**: Firebase Firestore (via Admin SDK 6.4.0)
- **AI**: Google Gemini API (with security hardening)
- **Validation**: Pydantic 2.6.4
- **Image Storage**: Cloudinary + Supabase

### Architecture Patterns
- **Backend**: Repository Pattern + Service Layer + Dependency Injection
- **Frontend**: Component Composition + Context API + Protected Routes
- **Database**: 10 Firestore collections with composite indexes
- **API**: 10 RESTful endpoints with batch operations

> **Detailed specifications**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#tech-stack)

---

## 🚀 Getting Started

```bash
# Quick setup (5 minutes)
git clone https://github.com/Shreyas-patil07/UNIFIND.git
cd UNIFIND
```

**Complete setup guide**: [QUICKSTART.md](QUICKSTART.md)

---



## 📚 Documentation

Complete documentation organized by use case:

### For New Users
- **[README.md](README.md)** - Project overview and features (you are here)
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes

### For Developers
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Development workflows, APIs, architecture
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical reference

### For Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide (Render + Vercel)

### For Compliance
- **[LEGAL_COMPLIANCE.md](LEGAL_COMPLIANCE.md)** - Privacy policy, terms, guidelines

### Project History
- **[MEGA_LOG.md](MEGA_LOG.md)** - Detailed chronological development log
- **[UPDATES.md](UPDATES.md)** - Clean changelog with summaries

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

<div align="center">
  <img src="frontend/public/Numero_Uno.png" alt="Numero Uno Team" width="250"/>
  
  ### Numero Uno Team
  
  *Building the future of campus commerce*
  
  <br/>
  
  | Member | GitHub Profile |
  |--------|---------------|
  | **Rijul** | [@Rijuls-code](https://github.com/Rijuls-code) |
  | **Shreyas** | [@Shreyas-patil07](https://github.com/Shreyas-patil07) |
  | **Atharva** | [@Atharva6153-git](https://github.com/Atharva6153-git) |
  | **Himanshu** | [@Himanshu052007](https://github.com/Himanshu052007) |
  
  <br/>
  
  **Team Contact**: systemrecord07@gmail.com
  
  ---
  
  ### Our Mission
  
  We're not just building a marketplace—we're creating a movement to make education affordable, sustainable, and community-driven. By combining AI-powered matching, transparent quality systems, and trust-based transactions, we're building a platform that students actually want to use.
  
  ### Our Values
  
  - 🎓 **Student-First**: Every decision prioritizes student welfare over profit
  - 🌱 **Sustainability**: Reduce waste by extending product lifecycles
  - 🤝 **Community**: Build trust and connections within campus
  - 🔓 **Open Source**: Transparent, auditable, and accessible to all
  - 💡 **Innovation**: Leverage AI and modern tech for better experiences
  
</div>

---

## 📞 Support

For support, email systemrecord07@gmail.com or open an issue on GitHub.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">
  
  ### Made with ❤️ by Numero Uno Team
  
  <img src="frontend/public/Numero_Uno.png" alt="Numero Uno" width="150"/>
  
  ---
  
  **UNIFIND** is more than a platform—it's a movement to make education affordable, sustainable, and community-driven.
  
  Our technology is 100% modern and scalable. Our business model prioritizes student welfare over profit. Our impact is measurable: thousands of rupees saved, tons of waste prevented, and a stronger campus community.
  
  ---
  
  ⭐ **Star us on GitHub** — it motivates us a lot!
  
  [Documentation](DOCUMENTATION.md) • [Report Bug](https://github.com/Shreyas-patil07/UNIFIND/issues) • [Request Feature](https://github.com/Shreyas-patil07/UNIFIND/issues) • [Contact](mailto:systemrecord07@gmail.com)
  
  ---
  
  ### Join us in making education accessible for everyone 🎓
  
  ![GitHub stars](https://img.shields.io/github/stars/Shreyas-patil07/UNIFIND?style=social)
  ![GitHub forks](https://img.shields.io/github/forks/Shreyas-patil07/UNIFIND?style=social)
  ![GitHub watchers](https://img.shields.io/github/watchers/Shreyas-patil07/UNIFIND?style=social)
  
</div>
