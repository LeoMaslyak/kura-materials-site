# Kura Materials Website — Continuation Prompt

Copy-paste the section below into a new session to continue working on the site.

---

## Prompt

You are working on the **Kura Materials website** — a B2B site for a company that transforms mining tailings into sustainable building materials ("From Waste to Worth").

### Repo & Live Site
- **Repo:** `/Users/leozealous/kura-materials-site/` (GitHub: `LeoMaslyak/kura-materials-site`)
- **GitHub Pages (live):** https://leomaslyak.github.io/kura-materials-site/
- **Githack (live):** https://raw.githack.com/LeoMaslyak/kura-materials-site/main/index.html

### Architecture (multi-page, shared CSS/JS)
- `index.html` — Landing page (hero with mine background, problem cards, market opportunity, process, journey video, partners, CTA)
- `investor.html` — Investor page ($400B+ market, problem/solution, competitive advantages, SDGs, team placeholder, CTA)
- `products.html` — Products page (7 product cards with specs, 3-step process, Three.js 3D showcase, CTA)
- `contact.html` — Contact page (audience segmentation, form, sidebar with details)
- `styles.css` — Shared stylesheet
- `nav.js` — Shared navigation, hamburger menu, scroll animations, counters, particles
- `images/` — Hero mine background (`hero-mine.jpg`), journey stage images
- `assets/` — Journey video files (stage1-5 + combined)

### Design System
- **Theme:** Dark — Charcoal `#0f0f0f`, Copper `#C87533`, Sage `#4A7C59`
- **Fonts:** Plus Jakarta Sans (headings) + Inter (body)
- **Style:** Glass-morphism cards, Tailwind CSS via CDN, Three.js for 3D product showcase
- **Footer + Nav:** Consistent across all pages

### What's Done (P0/P1)
- ✅ P0: Fixed non-clickable elements (hamburger menu, back-to-top, footer links, partner cards)
- ✅ P1: Full multi-page architecture with 23 CTAs wired across all pages
- ✅ Hero mine background image restored
- ✅ GitHub Pages enabled and live

### What's Next (P2/P3 — pick up here)
- [ ] **P2: Case studies section** — Add 2-3 short case studies / use cases to the landing page (mining partner, construction company, municipality)
- [ ] **P2: Revolut-style UX patterns** — Smooth scroll-triggered animations, parallax, micro-interactions. Currently scroll animations are basic fade-in; upgrade to staggered reveals, counter animations on scroll, smooth parallax layers
- [ ] **P2: Mobile responsiveness audit** — Test all 4 pages on mobile viewports, fix hamburger menu, card layouts, hero text sizing, 3D showcase touch interaction
- [ ] **P3: Performance optimization** — Lazy load images, compress hero image, consider WebP, optimize Three.js loading
- [ ] **P3: SEO basics** — Meta tags, Open Graph tags, structured data for all pages
- [ ] **P3: Favicon + branding** — Add proper favicon, Apple touch icon
- [ ] **Optional: Hero video loop** — Replace static hero image with a 6-10s cinematic video loop (Veo 3.1)
- [ ] **Optional: Improve 3D product realism** — Better textures, materials, lighting in the Three.js showcase

### Important Notes
- All cross-page navigation links are already wired and verified
- The site uses Tailwind CSS via CDN (no build step needed)
- Three.js is loaded via CDN on the products page only
- Journey section on landing page uses a scroll-pinned video with overlay nodes
- After any changes: `cd /Users/leozealous/kura-materials-site && git add -A && git commit -m "description" && git push origin main`
- GitHub Pages auto-deploys from `main` branch within ~1 min
