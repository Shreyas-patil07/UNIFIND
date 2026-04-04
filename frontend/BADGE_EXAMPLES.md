# Numero Uno Badge Examples

## Visual Reference

### Default Badge (Recommended for Footer)
```
┌─────────────────────────────────────┐
│  [Logo]  Created by                 │
│    🟢    Numero Uno                 │
└─────────────────────────────────────┘
```
- Size: Medium
- Best for: Footer, About pages
- Features: Full text, animated pulse

### Compact Badge
```
┌──────────────────────┐
│ [Logo] Numero Uno    │
└──────────────────────┘
```
- Size: Small
- Best for: Login/Signup pages, Headers
- Features: Minimal text

### Minimal Badge
```
┌────────┐
│ [Logo] │
│   🟢   │
└────────┘
```
- Size: Tiny
- Best for: Tight spaces, Icons
- Features: Logo only with pulse

### Banner Badge
```
┌─────────────────────────────────────────────┐
│                                             │
│         [Logo]    Created by                │
│                   Numero Uno                │
│              © 2026 • All Rights Reserved   │
│                                             │
└─────────────────────────────────────────────┘
```
- Size: Full width
- Best for: Page bottoms, Standalone sections
- Features: Full branding with copyright

## Color Schemes

### Dark Theme (Default)
- Background: Slate-800 to Slate-700 gradient
- Text: White
- Hover: Blue-600 to Blue-500 gradient
- Border: Slate-600 → Blue-400 on hover

### Hover Effects
- Scale: 1.0 → 1.05 (5% larger)
- Shadow: Subtle → Blue glow
- Border: Gray → Blue
- Duration: 300ms smooth transition

## Animation Details

### Pulse Animation
The green dot has a continuous pulse animation:
- Color: Green-500
- Animation: Pulse (infinite)
- Position: Top-right of logo
- Size: 3px × 3px

### Hover Animation
On hover, the entire badge:
1. Scales up 5%
2. Changes background to blue gradient
3. Adds blue shadow glow
4. Changes border color to blue
5. Transitions text color

## Usage Recommendations

### Landing Page
```jsx
<Footer /> // Uses default badge
```

### Dashboard
```jsx
<div className="dashboard-footer">
  <NumeroUnoBadge variant="compact" />
</div>
```

### Login/Signup
```jsx
<div className="auth-footer">
  <NumeroUnoBadge variant="compact" />
</div>
```

### About/Team Page
```jsx
<section className="team-section">
  <h2>Our Team</h2>
  {/* Team content */}
  <NumeroUnoBadge variant="default" />
</section>
```

### Sidebar
```jsx
<aside className="sidebar">
  {/* Sidebar content */}
  <div className="sidebar-footer">
    <NumeroUnoBadge variant="minimal" />
  </div>
</aside>
```

## Responsive Behavior

### Desktop (>1024px)
- Full size badges
- All text visible
- Hover effects active

### Tablet (768px - 1024px)
- Slightly smaller badges
- All text visible
- Touch-friendly sizing

### Mobile (<768px)
- Compact variants recommended
- Touch-optimized
- Stacks vertically in footer

## Accessibility

### Screen Readers
```html
<a aria-label="Created by Numero Uno Team - Visit our GitHub">
  <!-- Badge content -->
</a>
```

### Keyboard Navigation
- Tab: Focus on badge
- Enter/Space: Open GitHub link
- Focus indicator: Blue outline

### Color Contrast
- Text on dark background: WCAG AAA compliant
- Hover states: High contrast maintained

## Integration Checklist

- [ ] Logo file exists at `/public/Numero_Uno.png`
- [ ] Footer component imported
- [ ] Badge variant selected
- [ ] GitHub link updated (if needed)
- [ ] Team member links updated
- [ ] Copyright year set to 2026
- [ ] Tested on mobile devices
- [ ] Tested hover effects
- [ ] Verified accessibility

## Common Issues

### Logo Not Showing
**Problem:** Image path incorrect
**Solution:** Ensure `/public/Numero_Uno.png` exists

### Badge Not Clickable
**Problem:** Link not working
**Solution:** Check GitHub URL is correct

### Styling Issues
**Problem:** Badge looks different
**Solution:** Ensure Tailwind CSS is properly configured

### Animation Not Working
**Problem:** Pulse not animating
**Solution:** Check Tailwind animation utilities are enabled

## Customization Tips

### Change Badge Color
```jsx
// In NumeroUnoBadge.jsx
className="bg-gradient-to-r from-purple-800 to-purple-700"
```

### Change Hover Color
```jsx
hover:from-purple-600 hover:to-purple-500
```

### Remove Pulse
```jsx
// Remove this line:
<div className="... animate-pulse"></div>
```

### Add More Text
```jsx
<div className="text-left">
  <p className="text-xs">Created by</p>
  <p className="text-sm font-bold">Numero Uno</p>
  <p className="text-xs">Est. 2026</p> {/* New line */}
</div>
```

## Team Links

Current team members in footer:
1. Rijul (Leader) - [@Rijuls-code](https://github.com/Rijuls-code)
2. Shreyas - [@Shreyas-patil07](https://github.com/Shreyas-patil07)
3. Atharva - [@Atharva6153-git](https://github.com/Atharva6153-git)
4. Himanshu - [@Himanshu052007](https://github.com/Himanshu052007)

## Copyright Notice

All badges include:
- © 2026 UNIFIND
- "All rights reserved" text
- Team attribution
- GitHub repository link

---

**Need help?** Contact systemrecord07@gmail.com
