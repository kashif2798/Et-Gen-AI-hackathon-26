# Kiro Agent Prompt: Apply Apple Watch Page Design Language to E-newspaper

> Paste this entire prompt into Kiro as a task. The agent should read your existing `FRONTEND_DESIGN.md` and apply the Apple Watch design system on top of it, updating every screen.

---

## Context

You are refactoring the **E-newspaper** Next.js 14+ app's visual design. The app already has a working design system (serif headings with Playfair Display, red `#ED1C24` brand accent, `#101723` navy-black, Tailwind CSS, Framer Motion). Your job is **not** to change the brand identity — keep the red accent, the logo, and the content structure — but to **overhaul** the visual language, typography treatment, spacing rhythm, layout style, motion approach, and surface aesthetics to match the design language of **apple.com/watch/**.

Do not rewrite business logic. Do not rename components. Only touch visual styling: CSS, Tailwind classes, CSS variables, `globals.css`, and inline style props.

---

## Apple Watch Page Design Language — Reference Spec

### 1. Core Philosophy (apply everywhere)

| Principle | Implementation rule |
|-----------|---------------------|
| **Product/content is the hero** | UI chrome recedes. Reduce decorative elements. Remove box shadows from chrome (nav, tabs, chips). Only shadows on content cards. |
| **Generous white space** | Between sections: `py-24` to `py-32`. Between cards: `gap-8` to `gap-12`. Let content breathe. |
| **Full-bleed sections** | Major screen sections span 100% viewport width. No colored backgrounds on individual cards — use full-bleed section background shifts (white ↔ off-white `#F5F5F7` ↔ deep navy `#1d1d1f`) to create visual separation. |
| **Photography/image-first** | Article thumbnails, hero images, and media are shown large and cropped tightly. Thumbnails should be taller (`h-64` minimum). |
| **Single accent color** | `#ED1C24` remains the one interactive accent. No secondary accent colors. Remove any arbitrary accent grays or blues from interactive states. |

---

### 2. Typography — Full Overhaul

#### Font Stack
Replace the current multi-font system with a cleaner hierarchy:

```css
/* globals.css */

/* Display / Hero headlines */
--font-display: 'Playfair Display', 'Georgia', serif;

/* All UI text, body, labels, buttons, captions */
--font-ui: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',
           'Outfit', 'Helvetica Neue', Arial, sans-serif;

/* Remove Roboto from caption use — consolidate to --font-ui */
```

**Playfair Display stays for article titles and hero headlines only** (h1, h2, article card titles). Everything else — nav, buttons, labels, metadata, body paragraphs, captions — switches to the system UI sans-serif stack.

#### Type Scale — Replace the current scale with Apple's "confident but quiet" sizing:

```css
/* In globals.css, define these as CSS custom properties */

/* Hero / Display (Playfair Display, used sparingly) */
--text-display-xl: clamp(3rem, 6vw, 5.5rem);    /* Welcome hero headline */
--text-display-lg: clamp(2.25rem, 4vw, 3.75rem); /* Section intros, major headings */
--text-display-md: clamp(1.75rem, 3vw, 2.5rem);  /* Article detail hero title */

/* UI Text (system-ui) */
--text-headline: 1.25rem;    /* 20px — card titles, nav section labels */
--text-body-lg: 1.0625rem;   /* 17px — article body (Apple's body floor) */
--text-body: 1rem;           /* 16px — descriptions, secondary body */
--text-caption: 0.8125rem;   /* 13px — dates, tags, metadata */
--text-micro: 0.6875rem;     /* 11px — chip labels, trailing labels */
```

#### Letter Spacing — "Apple Tight" Headlines

Apply negative letter-spacing to all display-size text:

```css
/* Tailwind utilities to add/update in globals.css */
.apple-headline {
  letter-spacing: -0.025em;  /* -0.025em for large display */
  line-height: 1.08;
  font-weight: 700;
}

.apple-headline-sm {
  letter-spacing: -0.015em;  /* -0.015em for card-level headings */
  line-height: 1.2;
  font-weight: 600;
}
```

Apply `.apple-headline` to: Welcome hero (`h1`), persona section header, home screen feed title, article detail `h1`.
Apply `.apple-headline-sm` to: all article card titles, persona card titles.

#### Body copy

```css
body {
  font-family: var(--font-ui);
  font-size: var(--text-body-lg); /* 17px — Apple's reading floor */
  line-height: 1.65;
  font-weight: 400;
  color: #1d1d1f;  /* Apple's near-black, swap from #101723 for body only */
}
```

#### Button Text

```css
/* Apple-style button text: NOT uppercase, NOT tracked wide */
/* Change all button labels from UPPERCASE tracking-wide → Title Case, normal tracking */
.btn-label {
  font-family: var(--font-ui);
  font-size: 0.9375rem; /* 15px */
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: none; /* Remove uppercase from all buttons */
}
```

> **Important:** Remove `uppercase tracking-[0.2em]` from all button components. Apple buttons use sentence-case or Title Case with slightly tight tracking, never wide-tracked uppercase.

#### Section Labels / Eyebrows

Replace `UPPERCASE WIDE-TRACKED` meta labels with Apple's quieter approach:

```css
/* Before: "POWERED BY MULTI-AGENT RAG" in wide-tracked uppercase */
/* After: */
.section-eyebrow {
  font-family: var(--font-ui);
  font-size: 0.6875rem;   /* 11px */
  font-weight: 600;
  letter-spacing: 0.06em; /* Only 0.06em — subtle, not shouted */
  text-transform: uppercase;
  color: #6e6e73;          /* Apple's tertiary label color */
}
```

---

### 3. Color — Refined Palette

Keep the existing brand colors but introduce the Apple web palette for backgrounds and surfaces:

```css
/* Add to :root in globals.css */

/* Apple surface colors — replace #F8F9FB with these */
--apple-white:     #FFFFFF;
--apple-off-white: #F5F5F7;   /* Alternating section background */
--apple-dark:      #1d1d1f;   /* Near-black for dark sections */
--apple-mid-dark:  #3a3a3c;   /* Secondary text on dark sections */

/* Text hierarchy */
--apple-label:           #1d1d1f;   /* Primary text (replaces #101723 for body) */
--apple-secondary-label: #6e6e73;   /* Secondary/meta text (replaces #4A4A4A) */
--apple-tertiary-label:  #aeaeb2;   /* Placeholder, disabled */

/* Borders — lighter than current #E8E8E8 */
--apple-separator:       #d2d2d7;   /* Default separator */
--apple-separator-light: #e8e8ed;   /* Card borders */

/* Interactive */
--apple-blue:  #0066cc;   /* Apple's web interactive blue — use ONLY for external links */
/* Keep --et-red: #ED1C24 for all primary CTAs */
```

#### Section Backgrounds — Full-Bleed Alternation

On the Home screen and Article Detail screen, wrap major sections in full-width background blocks that alternate:

```
Screen flow (top → bottom):
  Section 1: bg-white
  Section 2: bg-[#F5F5F7]   ← off-white
  Section 3: bg-white
  Section 4: bg-[#1d1d1f]   ← dark (for Video Studio, featured panels)
  Section 5: bg-[#F5F5F7]
```

This section-level color shift is Apple's primary visual separator — **remove all card-level colored backgrounds** and rely on this instead.

---

### 4. Layout & Spacing — Apple's Generous Rhythm

#### Global Spacing Rule

Every major section gets `py-24 md:py-32` (96px–128px) vertical padding. This is non-negotiable — it creates the premium, unhurried feel.

```tsx
/* Section wrapper — use on every major content block */
<section className="w-full py-24 md:py-32 bg-white">
  <div className="max-w-[980px] mx-auto px-5 md:px-8">
    {/* content */}
  </div>
</section>
```

#### Max-width

Apple's main content column on apple.com is `980px`. Update the primary container:

```css
/* Replace max-w-7xl (1280px) with: */
.apple-container {
  max-width: 980px;
  margin-inline: auto;
  padding-inline: 1.25rem; /* 20px mobile */
}

@media (min-width: 768px) {
  .apple-container {
    padding-inline: 2rem;
  }
}
```

Keep `max-w-3xl` for article body text (reading column).

#### Grid — Edge-to-Edge Product Tiles on Home Screen

Replace the 3-column card grid with alternating full-bleed article tiles for featured content:

```tsx
/* Featured Article Tile (replaces top article cards) */
<div className="w-full py-16 md:py-24 bg-white border-b border-[#d2d2d7]">
  <div className="max-w-[980px] mx-auto px-5 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
    <div>
      <p className="section-eyebrow mb-3">{category}</p>
      <h2 className="font-serif apple-headline text-[2rem] md:text-[2.75rem] mb-4">{title}</h2>
      <p className="text-[17px] text-[#6e6e73] leading-relaxed mb-6">{summary}</p>
      <a className="text-[#ED1C24] font-medium text-[17px] hover:underline">{cta} →</a>
    </div>
    <div className="rounded-2xl overflow-hidden">
      <img className="w-full aspect-[4/3] object-cover" />
    </div>
  </div>
</div>
```

Keep the 3-column grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`) for secondary article listings — just update the cards (see below).

#### Card Design — Simplified

```tsx
/* Article Card — updated */
<div className="group bg-white rounded-2xl overflow-hidden border border-[#e8e8ed]
                hover:border-[#d2d2d7] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)]
                transition-all duration-300">
  {/* Thumbnail */}
  <div className="overflow-hidden aspect-[16/10]">
    <img className="w-full h-full object-cover
                    group-hover:scale-105 transition-transform duration-500" />
  </div>
  {/* Content */}
  <div className="p-6">
    <p className="section-eyebrow mb-2">{category}</p>
    <h3 className="font-serif apple-headline-sm text-[1.125rem] mb-2 line-clamp-2 text-[#1d1d1f]">
      {title}
    </h3>
    <p className="text-[0.8125rem] text-[#6e6e73] line-clamp-2 mb-4">{summary}</p>
    <p className="text-[0.75rem] text-[#aeaeb2]">{date}</p>
  </div>
</div>
```

Remove: colored tag overlay badges (the red pill on thumbnail corner). Move category to eyebrow text above the title instead.

---

### 5. Navigation / Header — Apple's Translucent Bar

```tsx
/* Header — updated */
<header className="sticky top-0 z-50
                   bg-white/80 dark:bg-[#1d1d1f]/80
                   backdrop-blur-xl backdrop-saturate-150
                   border-b border-[#d2d2d7]/60">
  <div className="max-w-[980px] mx-auto px-5 h-[52px] flex items-center justify-between">
    <Logo />
    {/* Nav actions */}
    <nav className="flex items-center gap-4">
      {/* Each nav item */}
      <button className="text-[0.8125rem] text-[#1d1d1f] font-normal hover:text-[#ED1C24]
                         transition-colors px-1 py-1">
        {label}
      </button>
    </nav>
  </div>
</header>
```

Key changes:
- Height: `52px` (Apple's compact nav height)
- Nav text: `13px`, normal weight, NOT uppercase
- No shadow on the header — only the `border-b` hairline
- `backdrop-blur-xl backdrop-saturate-150` for the glass effect

---

### 6. Buttons — CTA Grammar

Apple's web uses exactly two button styles. Replace all current button variants with these two:

```tsx
/* Primary CTA — filled, pill-shaped */
<button className="inline-flex items-center justify-center
                   px-6 py-2.5 rounded-full
                   bg-[#ED1C24] text-white
                   text-[0.9375rem] font-medium
                   tracking-[-0.01em]
                   hover:bg-[#c8151b]
                   transition-colors duration-200">
  {label}
</button>

/* Secondary CTA — outlined, pill-shaped */
<button className="inline-flex items-center justify-center
                   px-6 py-2.5 rounded-full
                   border border-[#ED1C24] text-[#ED1C24]
                   text-[0.9375rem] font-medium
                   tracking-[-0.01em]
                   hover:bg-[#ED1C24] hover:text-white
                   transition-colors duration-200">
  {label}
</button>
```

Remove: `shadow-2xl` from buttons, `uppercase`, `tracking-[0.2em]`.

---

### 7. Category Chips

```tsx
/* Category chip — updated to Apple pill style */
<button className={cn(
  "px-4 py-1.5 rounded-full text-[0.8125rem] font-medium transition-colors duration-200",
  selected
    ? "bg-[#1d1d1f] text-white"           /* Active: dark fill (not red) */
    : "bg-[#F5F5F7] text-[#1d1d1f] hover:bg-[#e8e8ed]"  /* Default: off-white */
)}>
  {label}
</button>
```

Note: Active state is **dark fill** (not red). Red is reserved for primary CTAs only.

---

### 8. Badges & Tags

```tsx
/* Remove the red pill tag overlay on thumbnails */

/* Inline category eyebrow — above card titles */
<span className="text-[0.6875rem] font-semibold uppercase tracking-[0.06em] text-[#6e6e73]">
  {category}
</span>

/* "Live" indicator — keep red but make it minimal */
<span className="flex items-center gap-1.5 text-[#ED1C24] text-[0.6875rem] font-semibold">
  <span className="w-1.5 h-1.5 rounded-full bg-[#ED1C24] animate-pulse" />
  Live
</span>
```

---

### 9. Motion & Animation — Apple's Restrained Approach

Apple's web animations are **slower, smoother, and more purposeful** than typical SaaS apps.

Update Framer Motion defaults across the app:

```tsx
/* Screen / page transition — slower fade */
const pageTransition = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } },
  exit:    { opacity: 0, transition: { duration: 0.3 } }
};

/* Card / staggered list entry — gentle upward drift */
const cardEntry = (index: number) => ({
  initial: { opacity: 0, y: 30 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      delay: index * 0.08,
      ease: [0.25, 0.1, 0.25, 1]  /* Apple's cubic-bezier */
    }
  }
});

/* Hover lift — subtle, not bouncy */
const hoverLift = {
  whileHover: { y: -4, transition: { duration: 0.25, ease: "easeOut" } },
  whileTap:   { y: 0,  scale: 0.99 }
};
```

Remove: `whileHover={{ scale: 1.02 }}` scale-up effects on buttons — replace with the subtle `y: -4` lift on cards only.

---

### 10. Liquid Glass / Glassmorphism (Modal, Chat Widget, Overlays)

Apple's 2025 design system introduced **Liquid Glass** — translucent surfaces that reflect surroundings. Apply this to:
- Chat widget window
- Story Arc sidebar panels
- Video Studio overlays
- Modal dialogs

```tsx
/* Liquid Glass surface */
.liquid-glass {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 18px;  /* Apple's "concentricity" radius */
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.04),
    0 16px 32px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* Dark glass (Video Studio, Story Arc dark panels) */
.liquid-glass-dark {
  background: rgba(28, 28, 30, 0.78);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 18px;
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.2),
    0 16px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
```

Update the existing `bg-zinc-950/80 backdrop-blur` on the chat widget to use `.liquid-glass-dark`.

---

### 11. Welcome Screen — Cinematic Hero

The Welcome screen should feel like an Apple product launch page:

```tsx
<section className="min-h-screen flex flex-col items-center justify-center
                    bg-white relative overflow-hidden px-5">
  {/* Subtle gradient background — no radial blobs, no red circles */}
  <div className="absolute inset-0 bg-gradient-to-b from-[#F5F5F7] via-white to-white pointer-events-none" />

  {/* Content */}
  <div className="relative z-10 text-center max-w-[692px] mx-auto">
    <Logo className="mb-8" />

    {/* Eyebrow */}
    <p className="section-eyebrow mb-4">E-newspaper • AI-Native News</p>

    {/* Hero headline — large, tight, serif */}
    <h1 className="font-serif text-[clamp(2.75rem,6vw,5.5rem)]
                   leading-[1.05] tracking-[-0.03em]
                   text-[#1d1d1f] mb-6">
      Next-Gen News<br />
      <em className="text-[#ED1C24] not-italic">Reimagined.</em>
    </h1>

    {/* Body */}
    <p className="text-[1.1875rem] text-[#6e6e73] leading-relaxed
                  max-w-[500px] mx-auto mb-10">
      Personalized intelligence briefings powered by multi-agent AI.
    </p>

    {/* CTA pair */}
    <div className="flex items-center justify-center gap-4">
      <button className="primary-cta">Begin Discovery</button>
      <button className="secondary-cta">Learn more</button>
    </div>
  </div>
</section>
```

Remove: the red circle blur in top-right corner, the radial beige gradient. Replace with the clean top-to-bottom off-white-to-white gradient.

---

### 12. Scrollbar

```css
/* globals.css */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0, 0, 0, 0.3); }
```

---

## Screen-by-Screen Checklist

Work through each screen in this order and apply all relevant rules above:

### ✅ globals.css
- [ ] Add all CSS custom properties (colors, type scale, glass surfaces)
- [ ] Update `body` font-size to 17px, family to `--font-ui`
- [ ] Add `.apple-headline`, `.apple-headline-sm`, `.section-eyebrow`, `.liquid-glass`, `.liquid-glass-dark` classes
- [ ] Update scrollbar styles
- [ ] Remove the Roboto caption font import

### ✅ Screen 1: Welcome
- [ ] Replace radial blob background → linear gradient `#F5F5F7 → white`
- [ ] Hero headline: `clamp(2.75rem, 6vw, 5.5rem)`, `tracking-[-0.03em]`, `leading-[1.05]`
- [ ] Remove uppercase tracking from "POWERED BY MULTI-AGENT RAG" → use `.section-eyebrow`
- [ ] Primary CTA: pill shape, no shadow, normal-case label
- [ ] Add secondary "Learn more" CTA alongside

### ✅ Screen 2: Persona Selection
- [ ] Section background: `bg-[#F5F5F7]`
- [ ] Section heading: `.apple-headline` sizing
- [ ] Persona cards: white bg, `border-[#e8e8ed]`, `rounded-2xl`, no colored backgrounds
- [ ] Hover: `border-[#d2d2d7]` + `shadow-[0_4px_20px_rgba(0,0,0,0.08)]` (not red border)
- [ ] Role labels: `.section-eyebrow` (not uppercase red bold)
- [ ] "Profile Active" badge: quiet — gray bg, gray text

### ✅ Screen 3: Home Screen (Article Grid)
- [ ] Header: `h-[52px]`, nav text `13px` normal weight, no uppercase
- [ ] Top featured article: full-bleed tile layout (two-column image+text)
- [ ] Category chips: off-white default, dark fill active
- [ ] Remove red pill badges from thumbnail overlays → eyebrow text above title
- [ ] Article cards: `rounded-2xl`, `aspect-[16/10]` thumbnail, minimal border
- [ ] Section spacing between header, featured, and grid: `py-24`
- [ ] Feed title "Top Intelligence Briefs": `.apple-headline` sizing with left-aligned layout

### ✅ Screen 4: Article Detail
- [ ] Hero image: full-bleed, `max-h-[60vh]`, no rounded corners
- [ ] Article `h1`: Playfair Display, `clamp(2rem, 4vw, 3.25rem)`, `.apple-headline`
- [ ] Body text: 17px, `leading-[1.65]`
- [ ] Metadata (date, source, tags): `.section-eyebrow` treatment
- [ ] AI Analysis panels (Bull/Bear): `.liquid-glass` surface
- [ ] Sticky back-button header: same glass nav bar pattern

### ✅ Screen 5: Video Studio
- [ ] Full-screen dark: `bg-[#1d1d1f]`
- [ ] Panels and controls: `.liquid-glass-dark`
- [ ] Section title: white, `.apple-headline`
- [ ] Button labels: normal-case, no uppercase

### ✅ Screen 6: Story Arc (Knowledge Graph)
- [ ] Background: `bg-[#F5F5F7]` (light) or `bg-[#1d1d1f]` (dark mode)
- [ ] Right sidebar panel: `.liquid-glass`
- [ ] Header: same translucent bar pattern
- [ ] Time travel slider: Apple-style thumb, `accent-color: #ED1C24`
- [ ] Dot grid overlay: keep (consistent with Apple's editorial pages)

### ✅ Chat Widget
- [ ] Window: `.liquid-glass-dark` (remove `bg-zinc-950/80`)
- [ ] Toggle button: keep red circle, reduce size from 56px → 48px
- [ ] Input field: `bg-white/10`, `border-white/20`, `rounded-full`
- [ ] User messages: `bg-[#ED1C24]` pill
- [ ] Assistant messages: `bg-white/10` pill

---

## Files to Touch

```
app/
  globals.css                    ← Primary CSS changes
  layout.tsx                     ← Remove Roboto font import
components/
  ui/
    Logo.tsx                     ← No changes needed
    Button.tsx (if exists)       ← Update CTA grammar
  screens/
    WelcomeScreen.tsx
    PersonaScreen.tsx
    HomeScreen.tsx
    ArticleDetail.tsx
    VideoStudio.tsx
    StoryArc.tsx
  ChatWidget.tsx
  Header.tsx
```

---

## What NOT to Change

- Brand colors: `#ED1C24`, `#FDE9E4`, `#101723` remain in the design token file
- Logo component and gradient
- All component names, props, and TypeScript interfaces
- Business logic, API calls, data fetching
- Framer Motion library (update timing/easing only)
- Tailwind config (only add new custom utilities if needed)
- Accessibility attributes (aria labels, focus rings — keep `ring-[#ED1C24]`)
- The 3-column article grid (keep for secondary listings)

---

## Verification

After implementing, verify each screen passes:

1. **Typography**: Display text has `tracking-[-0.025em]` or tighter. No `tracking-[0.2em]` on buttons.
2. **Spacing**: No section has less than `py-16` vertical padding. Preferred: `py-24`.
3. **Backgrounds**: Sections alternate white ↔ `#F5F5F7` ↔ `#1d1d1f`. No colored card backgrounds.
4. **Buttons**: All labels in sentence case or Title Case. No uppercase button text.
5. **Glass**: Modals, Chat, overlays use `backdrop-blur-xl` + semi-transparent bg.
6. **Cards**: `rounded-2xl`, `border-[#e8e8ed]`, shadow only on hover.
7. **Category chips**: Off-white default, dark fill active (not red).
