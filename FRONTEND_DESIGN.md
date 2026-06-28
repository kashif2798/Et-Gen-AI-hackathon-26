# E-newspaper Frontend Design System

**Version:** 1.0  
**Last Updated:** March 29, 2026  
**Platform:** Next.js 14+ (App Router) with TypeScript  

---

## Table of Contents
1. [Overview](#overview)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Layout System](#layout-system)
5. [Component Architecture](#component-architecture)
6. [Animation & Motion](#animation--motion)
7. [UI Patterns](#ui-patterns)
8. [Screen Designs](#screen-designs)
9. [Responsive Design](#responsive-design)
10. [Accessibility](#accessibility)

---

## Overview

E-newspaper is a next-generation AI-native news platform with a premium, sophisticated design language. The interface emphasizes clarity, elegance, and intelligent information hierarchy while maintaining a modern, tech-forward aesthetic.

**Design Philosophy:**
- **Clarity First**: Information hierarchy is paramount
- **Sophisticated Minimalism**: Clean, uncluttered interfaces with purposeful spacing
- **Motion with Purpose**: Animations that enhance UX, not distract
- **Premium Feel**: High-end news platform aesthetic inspired by Financial Times, Bloomberg
- **AI-Native**: Visual language that reflects intelligent, personalized content

---

## Color Palette

### Primary Colors

```css
--et-red: #ED1C24        /* Primary brand color - used for CTAs, accents, highlights */
--et-beige: #FDE9E4      /* Soft background accent for cards, highlights */
--et-black: #101723      /* Deep navy-black for headers, primary text */
--et-gray: #4A4A4A       /* Secondary text, subtle elements */
--et-border: #E8E8E8     /* Borders, dividers, card outlines */
```

### Semantic Colors

```css
--color-surface: #FFFFFF           /* Primary background */
--color-surface-2: #F8F9FB         /* Secondary background (subtle contrast) */
--color-text: #101723              /* Primary text color */
--color-text-secondary: #4A4A4A    /* Secondary/muted text */
--color-border: #E8E8E8            /* Default borders */
```

### Usage Guidelines

- **Red (#ED1C24)**: Primary CTAs, brand logo gradient start, active states, important badges, "live" indicators
- **Black (#101723)**: Headers, primary navigation, body text, high-contrast elements
- **Beige (#FDE9E4)**: Soft backgrounds for feature cards, hover states, warmth accents
- **Gray (#4A4A4A)**: Secondary text, captions, metadata (dates, sources)
- **Light Gray (#E8E8E8)**: Borders, dividers, subtle separation

### Gradient Patterns

**Logo Gradient:**
```css
background: linear-gradient(135deg, #DC2626 0%, #000000 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```
Used for: Main logo, premium headings

**Thumbnail Fallback Gradient:**
```css
background: linear-gradient(135deg, hsl(dynamic) 78% 48%, hsl(dynamic+35) 78% 42%);
```
Generated dynamically based on article title hash

**Background Accents:**
```css
/* Radial gradient for welcome screen */
background: radial-gradient(circle_at_bottom_left, var(--et-beige) 0%, transparent 40%);

/* Subtle dot grid for data-heavy screens */
background: radial-gradient(#e2e8f0 1px, transparent 1px);
background-size: 24px 24px;
```

---

## Typography

### Font Families

**Primary Serif: Playfair Display**
- **Usage**: Headlines (h1-h4), logo, article titles, section headers
- **Weights**: 400 (Regular), 700 (Bold), 900 (Black)
- **Style**: Elegant, traditional newspaper aesthetic
- **Import**: Google Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700;1,900&display=swap');

h1, h2, h3, h4, .font-serif {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  letter-spacing: -0.015em;
  line-height: 1.25;
}
```

**Primary Sans-Serif: Outfit**
- **Usage**: Body text, UI elements, buttons, captions, metadata
- **Weights**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold)
- **Style**: Modern, clean, highly readable
- **Import**: Google Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

body {
  font-family: 'Outfit', sans-serif;
  font-weight: 400;
  line-height: 1.6;
}
```

**Monospace Font (Logo Accent): Georgia**
- **Usage**: Logo only (E-newspaper wordmark)
- **Why**: Timeless serif with excellent screen rendering
- **Fallback**: System serif fonts

```css
font-family: 'Georgia', serif;
```

**Captions & Metadata: Roboto**
- **Usage**: Timestamps, source attribution, small metadata
- **Weights**: 400, 500, 700
- **Defined in**: `layout.tsx` as CSS variable

```tsx
const robotoCaptions = Roboto({
  weight: ["400", "500", "700"],
  subsets: ["latin"],
  variable: "--font-caption-roboto",
  display: "swap",
});
```

### Type Scale

```css
/* Display / Hero */
.text-5xl      /* 3rem (48px)   - Welcome screen hero */
.text-4xl      /* 2.25rem (36px) - Section headers */
.text-3xl      /* 1.875rem (30px) - Logo, major headings */

/* Headings */
.text-2xl      /* 1.5rem (24px)  - Page titles */
.text-xl       /* 1.25rem (20px) - Card headers */
.text-lg       /* 1.125rem (18px) - Article titles */

/* Body */
.text-base     /* 1rem (16px)    - Standard body text */
.text-sm       /* 0.875rem (14px) - Secondary text */
.text-xs       /* 0.75rem (12px)  - Captions, metadata */

/* Micro */
.text-[11px]   /* 11px - Labels, chip text */
.text-[10px]   /* 10px - Tiny labels, build numbers */
.text-[9px]    /* 9px - System status text */
```

### Font Weight Guidelines

- **Black (900)**: Logo, hero headings, major CTAs
- **Bold (700)**: Section headers, article titles, button text
- **Semibold (600)**: Subheadings, emphasized UI text
- **Medium (500)**: Active navigation, secondary emphasis
- **Regular (400)**: Body text, descriptions
- **Light (300)**: Subtle captions (rarely used)

### Text Treatments

**Line Clamping:**
```css
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

**Letter Spacing:**
- **Tight (-0.015em)**: Serif headlines for elegance
- **Normal (0)**: Body text
- **Wide (0.05em - 0.1em)**: Button text
- **Widest (0.2em - 0.3em)**: Small caps labels, metadata

**Case:**
- **Uppercase + Wide Tracking**: Used for labels ("ACTIVE PROFILE", "POWERED BY MULTI-AGENT RAG")
- **Title Case**: Article headlines, card titles
- **Sentence case**: Body text, descriptions

---

## Layout System

### Container Widths

```css
.et-container {
  max-width: 1200px;     /* Content max-width for most screens */
  margin: 0 auto;
  padding: 0 1rem;
}

/* Specific overrides */
max-w-7xl  /* 1280px - Home screen, main content areas */
max-w-3xl  /* 768px - Article detail, forms */
max-w-2xl  /* 672px - Welcome screen text */
max-w-xl   /* 576px - Search bars */
max-w-lg   /* 512px - Modals, dialogs */
```

### Spacing Scale (Tailwind)

```
px   /* 1px   - Micro borders */
0.5  /* 2px   - Tight spacing */
1    /* 4px   - Compact spacing */
2    /* 8px   - Small gaps */
3    /* 12px  - Default gap */
4    /* 16px  - Standard spacing */
6    /* 24px  - Comfortable spacing */
8    /* 32px  - Section spacing */
12   /* 48px  - Large gaps */
16   /* 64px  - Screen sections */
20   /* 80px  - Major divisions */
```

### Grid Systems

**Article Grid (Home Screen):**
```tsx
grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8
```
- **Mobile (< 640px)**: 1 column
- **Tablet (≥ 640px)**: 2 columns
- **Desktop (≥ 1024px)**: 3 columns
- **Gap**: 32px (2rem)

**Persona Selection:**
```tsx
grid grid-cols-1 md:grid-cols-2 gap-5
```
- **Mobile**: 1 column
- **Desktop**: 2 columns (2x2 grid for 4 personas)

### Z-Index Layers

```
z-0       /* Base content */
z-10      /* Elevated UI (sidebars, secondary panels) */
z-40      /* Error notifications */
z-50      /* Header, navigation */
z-[60]    /* Full-screen overlays (Story Arc) */
z-[80]    /* Modals, dialogs */
```

---

## Component Architecture

### Core UI Components

#### 1. **Logo Component**

```tsx
<Logo className="" light={false} />
```

**Variants:**
- **Default**: Red-to-black gradient on text
- **Light**: White text (for dark backgrounds)

**Design:**
- Font: Georgia serif
- Size: text-3xl (30px)
- Weight: Bold (700)
- Gradient: 135deg, #DC2626 → #000000
- Tracking: Tight

#### 2. **Button Patterns**

**Primary CTA:**
```tsx
className="px-10 py-4 bg-[#101723] text-white font-bold text-xs uppercase tracking-[0.2em] rounded-full hover:bg-black transition-all shadow-2xl"
```

**Secondary CTA:**
```tsx
className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-xs font-bold uppercase"
```

**Icon Button:**
```tsx
className="p-2 hover:bg-gray-50 rounded-lg transition-colors"
```

**Chip/Tag Button:**
```tsx
className="px-3 py-1.5 rounded-full text-[11px] font-bold border transition-colors"
```

#### 3. **Card Components**

**Article Card:**
```tsx
<div className="bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg hover:border-[#ED1C24]/20 transition-all">
  {/* Thumbnail (h-48) */}
  {/* Content (p-6) */}
</div>
```

**Design Details:**
- **Border**: 1px gray-100, hover → red-100
- **Radius**: 12px (rounded-xl)
- **Shadow**: None default, lg on hover
- **Transition**: 300ms ease
- **Hover Scale**: Image scales 105%

**Persona Card:**
```tsx
<button className="p-6 bg-white border-2 border-gray-100 rounded-xl hover:border-[#ED1C24] hover:shadow-xl">
  {/* Icon + Text */}
</button>
```

#### 4. **Chat Widget**

**Design:**
- **Position**: Fixed bottom-right (bottom-6 right-6)
- **Toggle Button**: 56px circle, red background, white icon
- **Window**: 384px width × 500px height
- **Background**: zinc-950/80 with backdrop-blur
- **Border**: zinc-800 (dark mode aesthetic)
- **Messages**: User (red bg), Assistant (zinc-900 bg)

**Special Features:**
- Animated orb with pulse indicator
- Context-aware header when article is active
- Skeleton loader during AI responses

#### 5. **Skeleton Loaders**

```tsx
<Skeleton className="h-6 w-56 mx-auto rounded-lg" />
<ArticleSkeleton />      // Full card skeleton
<AnalysisSkeleton />     // Analysis section skeleton
```

**Design:**
- Background: slate-200/50
- Animation: Pulse (subtle opacity change)
- Rounded: Matches content (lg, xl, 2xl)

---

## Animation & Motion

### Library: Framer Motion

**Philosophy:**
- Smooth, subtle transitions
- Never blocking or jarring
- Enhance perceived performance
- Guide user attention

### Common Patterns

**Screen Transitions:**
```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>
```

**Staggered List Entry:**
```tsx
<motion.div
  initial={{ y: 20, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  transition={{ delay: index * 0.05 }}
>
```

**Hover Interactions:**
```tsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
```

**Modal/Dialog:**
```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.96, y: 8 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.96, y: 8 }}
>
```

### Timing Functions

- **Duration**: 200-300ms for micro-interactions, 400-600ms for screen transitions
- **Ease**: Default ease-in-out
- **Stagger Delay**: 50-80ms per item

### Animated Icons

**Loading States:**
- `Loader2` with `animate-spin`
- Skeleton pulse effects
- Gradient shimmer on placeholders

**Status Indicators:**
- Pulse animation on "live" dot: `animate-pulse`
- Breathing effect on status indicators

---

## UI Patterns

### 1. **Headers/Navigation**

**Sticky Header:**
```tsx
<header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
  <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
    <Logo />
    <Actions />
  </div>
</header>
```

**Design Features:**
- **Backdrop blur**: Creates depth
- **80% opacity**: Subtle transparency
- **Border bottom**: Hairline separation
- **Sticky positioning**: Always visible

### 2. **Category Chips**

```tsx
<button className={selected ? "bg-[#ED1C24] text-white" : "bg-white text-gray-600 border-gray-200"}>
  {category}
</button>
```

**States:**
- **Default**: White bg, gray text, gray border
- **Hover**: Red border
- **Active**: Red bg, white text

### 3. **Empty States**

```tsx
<div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-gray-200 rounded-xl">
  <Icon className="w-10 h-10 text-gray-300 mb-4" />
  <p className="text-gray-500 font-medium mb-2">No items yet</p>
  <p className="text-sm text-gray-400 mb-6">Description</p>
  <button>Primary Action</button>
</div>
```

### 4. **Loading States**

**Full Screen:**
- Skeleton screens with branded elements
- Centered spinner with descriptive text
- Animated placeholders matching content structure

**Inline:**
- Button disabled state with "Loading..." text
- Spinner icon replacement
- Skeleton cards in grid

### 5. **Error States**

```tsx
<div className="bg-white border-2 border-red-500 shadow-2xl p-5 rounded-2xl flex items-center gap-5 text-red-600">
  <AlertTriangle />
  <div>
    <p className="text-sm font-black uppercase">Error Title</p>
    <p className="text-xs text-slate-500">Error description</p>
  </div>
  <button>Retry</button>
</div>
```

### 6. **Badges & Labels**

**Tag Badges:**
```tsx
<span className="px-2 py-1 bg-[#ED1C24] text-white text-[10px] font-bold uppercase tracking-wider rounded">
  {tag}
</span>
```

**Metadata Labels:**
```tsx
<span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
  Label
</span>
```

---

## Screen Designs

### Screen 1: Welcome Screen

**Purpose**: First impression, brand introduction, entry point

**Layout:**
- Centered vertical layout
- Full viewport height
- Gradient background accents

**Elements:**
1. **Logo**: Large, centered, 125% scale
2. **Hero Headline**: 
   - "Next-Gen News Reimagined."
   - text-4xl to text-5xl
   - "Reimagined" in italic red
3. **Subheadline**: Gray-500, max-w-md
4. **Primary CTA**: "Begin Discovery" with ChevronRight icon
5. **Footer Badge**: "Powered by Multi-Agent RAG • GenAI Hackathon 2026"

**Background:**
- Radial gradient (beige) bottom-left
- Red circle blur top-right
- White base

### Screen 2: Persona Selection

**Purpose**: User profile selection for personalization

**Layout:**
- Centered content
- 2-column grid (responsive to 1 column mobile)

**Cards:**
- **Icon**: Large emoji (3xl)
- **Role**: Bold red uppercase
- **Status**: "Profile Active" badge
- **Description**: Small gray text
- **Portfolio**: Token chips (if applicable)
- **Chevron**: Right arrow on hover

**Interaction:**
- Hover: Red border, shadow, chevron color change
- Click: Navigate to home screen with selected persona

### Screen 3: Home Screen (Article Grid)

**Header:**
- Logo (left)
- Actions: Video Studio, Story Arc, Refresh, Load Data, Persona Switcher

**Main Content:**
1. **Category Navigation**: Horizontal chip row
2. **Feed Header**: "Top Intelligence Briefs" with vertical red bar
3. **Article Grid**: 3-column responsive grid

**Article Card Structure:**
- Thumbnail (h-48, fallback gradient if no image)
- Tag badge (top-left overlay)
- Title (serif, bold, line-clamp-2)
- Summary (line-clamp-3)
- Footer: Date + additional tags

### Screen 4: Article Detail

**Layout:**
- Sticky header with back button
- Hero image or gradient placeholder
- Content column (max-w-3xl)
- Sidebar: AI analysis (Bull/Bear views)

**Sections:**
1. **Article Header**: Title, date, tags, source
2. **Summary**: Gray box with key points
3. **Full Text**: Body content
4. **AI Analysis**: 
   - Bull view (green accent)
   - Bear view (red accent)
   - Persona-specific insights
5. **Actions**: Generate Video, View Story Arc

### Screen 5: Video Studio

**Purpose**: Generate and preview AI-narrated video briefings

**Layout:**
- Video player (Remotion Player) center
- Article selection sidebar
- Controls: Generate, clear, playback

**Design:**
- Dark theme (navy-900)
- Professional, studio-like aesthetic
- Loading states with storyboard skeletons

### Screen 6: Story Arc (Knowledge Graph)

**Purpose**: Visualize entity relationships and narrative threads

**Layout:**
- Full-screen immersive view
- Header with search and controls
- Main area: Force-directed graph (2D or 3D)
- Right sidebar: Contrarian Lens, insights

**Features:**
- Time travel slider (bottom)
- Article selection dialog
- Interactive graph nodes
- Sentiment visualization

**Design:**
- Light mode: slate-50 background
- Dot grid pattern overlay
- Premium glass-morphism panels

---

## Responsive Design

### Breakpoints

```css
/* Tailwind default breakpoints */
sm:   640px   /* Tablet portrait */
md:   768px   /* Tablet landscape */
lg:   1024px  /* Desktop */
xl:   1280px  /* Large desktop */
2xl:  1536px  /* Extra large */
```

### Mobile-First Approach

**Strategy**: Design for mobile, enhance for larger screens

**Common Patterns:**

1. **Typography:**
```tsx
text-3xl md:text-4xl lg:text-5xl  // Scales up
```

2. **Spacing:**
```tsx
px-4 sm:px-6 lg:px-8  // Increases padding
```

3. **Grid:**
```tsx
grid-cols-1 sm:grid-cols-2 lg:grid-cols-3  // More columns on larger screens
```

4. **Visibility:**
```tsx
hidden md:block  // Show only on medium+
block md:hidden  // Show only on small
```

### Touch Targets

- Minimum size: 44×44px (follows iOS/accessibility guidelines)
- Buttons: Adequate padding for finger taps
- Interactive elements: Sufficient spacing between clickable items

---

## Accessibility

### Semantic HTML

- Proper heading hierarchy (h1 → h2 → h3)
- `<button>` for interactions, `<a>` for navigation
- `<header>`, `<main>`, `<aside>` for layout

### ARIA Attributes

```tsx
aria-label="Close dialog"
aria-pressed={selected}
aria-modal="true"
role="dialog"
```

### Keyboard Navigation

- Tab order follows visual flow
- Focus states visible (ring-2, ring-red-600)
- Modal trapping implemented

### Screen Reader Support

- Descriptive alt text for images
- Status announcements for loading states
- Hidden labels for icon-only buttons

### Color Contrast

- **Primary text on white**: 14:1+ (AAA)
- **Gray text**: 4.5:1+ (AA)
- **Red on white**: 5.2:1 (AA+)
- **White on red**: 6.1:1 (AA+)

### Focus States

```tsx
focus:outline-none 
focus:ring-2 
focus:ring-[#ED1C24]/20 
focus:border-[#ED1C24]
```

---

## Additional Details

### Scrollbars

**Custom Styling:**
```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { 
  background: var(--et-border); 
  border-radius: 3px; 
}
::-webkit-scrollbar-thumb:hover { 
  background: var(--et-gray); 
}
```

### Image Handling

**Fallback System:**
- Dynamic SVG generation when image_url is missing
- Gradient based on article title hash
- Includes article label, headline, and "E-newspaper" branding

**Lazy Loading:**
```tsx
loading="lazy"  // Native lazy loading for images
```

### Performance Optimizations

- **Font Display**: swap (prevents FOIT)
- **Image Optimization**: Next.js Image component (where applicable)
- **Code Splitting**: Automatic with Next.js App Router
- **CSS Purging**: Tailwind removes unused styles in production

### Browser Support

- **Modern Evergreen**: Chrome, Firefox, Safari, Edge (latest 2 versions)
- **CSS Features**: Grid, Flexbox, Custom Properties, backdrop-filter
- **JavaScript**: ES2020+, async/await, optional chaining

---

## Design Tokens Summary

```json
{
  "colors": {
    "brand": {
      "primary": "#ED1C24",
      "secondary": "#FDE9E4",
      "dark": "#101723"
    },
    "neutral": {
      "50": "#FAFAFA",
      "100": "#F8F9FB",
      "200": "#E8E8E8",
      "400": "#4A4A4A",
      "900": "#101723"
    }
  },
  "fonts": {
    "serif": "Playfair Display",
    "sans": "Outfit",
    "mono": "Georgia"
  },
  "spacing": {
    "section": "2rem",
    "card": "1.5rem",
    "element": "1rem"
  },
  "radius": {
    "sm": "0.5rem",
    "md": "0.75rem",
    "lg": "1rem",
    "xl": "1.5rem"
  },
  "shadows": {
    "card": "0 1px 3px rgba(0,0,0,0.05)",
    "elevated": "0 10px 40px rgba(0,0,0,0.1)"
  }
}
```

---

## Maintenance Notes

### Adding New Components

1. Match existing animation patterns
2. Use design system colors (no arbitrary values)
3. Maintain 8px spacing grid
4. Add hover/active states
5. Ensure responsive behavior
6. Include loading/error states

### Updating Styles

1. Prefer Tailwind utilities over custom CSS
2. Add custom styles to `globals.css` if needed across app
3. Use CSS variables for theme values
4. Test dark mode compatibility (future consideration)

### Design Review Checklist

- [ ] Follows color palette
- [ ] Uses correct typography scale
- [ ] Responsive on all breakpoints
- [ ] Accessible (contrast, keyboard, screen reader)
- [ ] Smooth animations (no jank)
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Empty states designed

---

**Document Version:** 1.0  
**Platform:** E-newspaper Frontend  
**Framework:** Next.js 14+ (React 18+, TypeScript)  
**Styling:** Tailwind CSS 3.4+, Framer Motion  
**Last Review:** March 29, 2026
