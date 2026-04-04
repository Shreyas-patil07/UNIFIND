# Footer & Numero Uno Badge Usage Guide

## Overview

This project includes professional footer components with "Created by Numero Uno" branding, similar to AyurTrace's "Created by Gambit" style.

## Components

### 1. Footer Component (`Footer.jsx`)

A complete footer with:
- Brand information
- Quick links
- Contact details
- Team member links
- "Created by Numero Uno" badge
- Copyright notice (© 2026)

**Usage:**
```jsx
import Footer from '../components/Footer';

function MyPage() {
  return (
    <div>
      {/* Your page content */}
      <Footer />
    </div>
  );
}
```

### 2. NumeroUnoBadge Component (`NumeroUnoBadge.jsx`)

A standalone badge component with multiple variants.

**Variants:**

#### Default Variant
Full badge with logo and text
```jsx
import NumeroUnoBadge from '../components/NumeroUnoBadge';

<NumeroUnoBadge variant="default" />
```

#### Compact Variant
Smaller badge for tight spaces
```jsx
<NumeroUnoBadge variant="compact" />
```

#### Minimal Variant
Just the logo with hover effect
```jsx
<NumeroUnoBadge variant="minimal" />
```

#### Banner Variant
Full-width banner style
```jsx
<NumeroUnoBadge variant="banner" />
```

## Features

### Footer Features
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Gradient background (slate-900 to slate-800)
- ✅ Hover effects on all links
- ✅ Team member GitHub links
- ✅ Animated "Created by Numero Uno" badge
- ✅ Green pulse indicator (online status)
- ✅ Copyright year: 2026

### Badge Features
- ✅ Multiple variants for different use cases
- ✅ Smooth hover animations
- ✅ Links to GitHub repository
- ✅ Responsive and accessible
- ✅ Uses Numero Uno logo from `/public/Numero_Uno.png`

## Customization

### Change Colors
Edit the Tailwind classes in the components:
- `from-slate-800 to-slate-700` - Badge background
- `hover:from-blue-600 hover:to-blue-500` - Hover state
- `text-slate-400` - Secondary text color

### Change Links
Update the GitHub repository link:
```jsx
href="https://github.com/Shreyas-patil07/UniFind"
```

### Change Team Members
Edit the team members section in `Footer.jsx`:
```jsx
<a href="https://github.com/username">Member Name</a>
```

### Change Year
Update the copyright year in `Footer.jsx`:
```jsx
<p>© 2026 UNIFIND. All rights reserved.</p>
```

## Where to Use

### Footer Component
- Landing Page ✅ (Already added)
- Dashboard pages
- All authenticated pages
- Any page that needs a complete footer

### NumeroUnoBadge Component
- Login/Signup pages (compact variant)
- Dashboard header (minimal variant)
- About page (default variant)
- Bottom of forms (compact variant)
- Standalone pages (banner variant)

## Examples

### Add to Dashboard
```jsx
import Footer from '../components/Footer';

function DashboardPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        {/* Dashboard content */}
      </main>
      <Footer />
    </div>
  );
}
```

### Add Badge to Login Page
```jsx
import NumeroUnoBadge from '../components/NumeroUnoBadge';

function LoginPage() {
  return (
    <div className="min-h-screen">
      {/* Login form */}
      <div className="mt-8 flex justify-center">
        <NumeroUnoBadge variant="compact" />
      </div>
    </div>
  );
}
```

### Add Banner to About Page
```jsx
import NumeroUnoBadge from '../components/NumeroUnoBadge';

function AboutPage() {
  return (
    <div>
      {/* About content */}
      <NumeroUnoBadge variant="banner" />
    </div>
  );
}
```

## Logo Requirements

Make sure you have the Numero Uno logo in your public folder:
- Path: `/public/Numero_Uno.png`
- Recommended size: 200x200px or larger
- Format: PNG with transparent background

## Accessibility

All components include:
- Proper alt text for images
- Semantic HTML elements
- Keyboard navigation support
- Screen reader friendly
- ARIA labels where needed

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Notes

- The green pulse indicator shows "online" status
- All external links open in new tabs (`target="_blank"`)
- Hover effects use smooth transitions (300ms)
- Components are fully responsive
- Year is set to 2026 as per project context

## Support

For issues or questions:
- Email: systemrecord07@gmail.com
- GitHub: https://github.com/Shreyas-patil07/UniFind

---

**Created by Numero Uno Team** 🚀
