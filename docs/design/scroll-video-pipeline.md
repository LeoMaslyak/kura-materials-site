# Scroll-Video Asset Generation Pipeline

> How to create, compress, and integrate scroll-driven videos for Kura Materials and future NT-Investment websites.

---

## 1. Video Generation via Google Flow (Veo 3.1)

### Access
- Authenticated as `lm@avantgaera.com` (AI Ultra Access)
- Flow URL: `https://labs.google/fx/tools/video-fx`
- Model: Veo 3.1 (highest quality, 8s clips)

### Recommended Prompt Structure

Each journey stage needs its own video clip. Use this template:

```
Cinematic aerial drone shot, [SCENE DESCRIPTION], 
golden hour lighting, photorealistic, 
slow dolly movement, 8K quality, 
mining/industrial aesthetic, muted earth tones
```

#### Stage-by-Stage Prompts

**Stage 1 — Mine (Raw Tailings)**
```
Cinematic aerial drone shot slowly flying over vast copper mining tailings ponds, 
gray-brown waste mountains stretching to the horizon, 
dry desert landscape, golden hour lighting, dust particles in air, 
photorealistic industrial mining operation, slow forward dolly
```

**Stage 2 — Collection & Transport**
```
Cinematic tracking shot of industrial conveyor belts and dump trucks 
carrying mining tailings from open pit to processing facility, 
massive scale logistics, dust trails, 
warm sunset lighting on metal structures, photorealistic
```

**Stage 3 — Processing (Alkali Activation)**
```
Cinematic interior shot of modern processing facility, 
chemical mixing chambers with glowing green-copper liquids, 
steam rising from reaction vessels, 
industrial precision equipment, 
dramatic volumetric lighting through factory windows
```

**Stage 4 — Products (Building Materials)**
```
Cinematic close-up of freshly formed building blocks, pavers, and tiles 
emerging from production line, 
warm copper and sage-green tones in the materials, 
shallow depth of field, 
factory conveyor with finished products, 
satisfying symmetry and repetition
```

**Stage 5 — City (Sustainable Future)**
```
Cinematic aerial shot of a modern sustainable city at golden hour, 
buildings made from earth-toned recycled materials, 
green rooftops and solar panels, 
pedestrian-friendly streets, 
warm optimistic lighting, wide establishing shot
```

### Multi-Video Continuation Technique

To create seamless transitions when chaining stages:

1. **Generate Stage 1** normally
2. **Extract last frame** of Stage 1:
   ```bash
   ffmpeg -sseof -0.1 -i stage1.mp4 -frames:v 1 -q:v 2 stage1-last-frame.jpg
   ```
3. **Use last frame as image prompt** for Stage 2 in Flow:
   - Upload `stage1-last-frame.jpg` as the reference image
   - Add prompt: "Continue this scene, transitioning from [previous] to [next]..."
4. Repeat for each subsequent stage

This creates visual continuity across the full scroll narrative.

---

## 2. Video Specifications

### Recommended Specs

| Parameter | Single Video | Multi-Stage (per clip) |
|-----------|-------------|----------------------|
| Duration | 6–10 seconds | 4–6 seconds each |
| Resolution | 1920×1080 | 1280×720 (web) |
| Codec | H.264 (MP4) | H.264 (MP4) |
| Bitrate | 800–1200 kbps | 600–900 kbps |
| FPS | 24 or 30 | 24 |
| File size | < 1 MB | < 500 KB each |
| Aspect ratio | 16:9 | 16:9 |

### Why These Specs

- **6–10s duration**: Maps well to 300–500vh scroll ranges. Shorter = too jumpy, longer = too slow.
- **H.264**: Universal browser support, GPU-accelerated decode.
- **24fps**: Smooth enough for scrub; 60fps doubles file size with no perceptible scroll benefit.
- **< 1MB**: Stays within the performance budget (LCP < 2.5s on 3G+).

---

## 3. FFmpeg Compression Commands

### Standard Web Compression (from Veo output)

```bash
# Single pass, CRF-based (best quality/size ratio)
ffmpeg -i input.mp4 \
  -c:v libx264 -crf 28 -preset slow \
  -vf "scale=1280:720" \
  -movflags +faststart \
  -an \
  -y output_web.mp4
```

**Flags explained:**
- `-crf 28`: Quality level (23 = visually lossless, 28 = good for web, 32 = aggressive)
- `-preset slow`: Better compression at same quality (takes longer)
- `-movflags +faststart`: Moves moov atom to front for progressive loading
- `-an`: Strips audio (not needed for scroll video)

### Aggressive Compression (< 500 KB target)

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -crf 32 -preset veryslow \
  -vf "scale=960:540" \
  -movflags +faststart \
  -an \
  -y output_tiny.mp4
```

### Extract Frame Sequence (for canvas fallback mode)

```bash
# Extract at 12fps (144 frames for 12s video — ~2MB total as WebP)
mkdir -p frames
ffmpeg -i input.mp4 \
  -vf "fps=12,scale=1280:720" \
  -c:v libwebp -quality 75 \
  frames/frame_%04d.webp

# Or as JPEG (wider compat, slightly larger)
ffmpeg -i input.mp4 \
  -vf "fps=12,scale=1280:720" \
  -q:v 4 \
  frames/frame_%04d.jpg
```

### Concatenate Multi-Stage Videos

```bash
# Create file list
echo "file 'stage1.mp4'" > concat.txt
echo "file 'stage2.mp4'" >> concat.txt
echo "file 'stage3.mp4'" >> concat.txt
echo "file 'stage4.mp4'" >> concat.txt
echo "file 'stage5.mp4'" >> concat.txt

# Concatenate (if same codec/resolution)
ffmpeg -f concat -safe 0 -i concat.txt \
  -c copy -movflags +faststart \
  -y journey_full.mp4

# If resolutions differ, re-encode:
ffmpeg -f concat -safe 0 -i concat.txt \
  -c:v libx264 -crf 26 -preset slow \
  -vf "scale=1280:720" \
  -movflags +faststart -an \
  -y journey_full.mp4
```

### Add Crossfade Between Stages

```bash
# 0.5s crossfade between two clips
ffmpeg -i stage1.mp4 -i stage2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=5.5[v]" \
  -map "[v]" -c:v libx264 -crf 26 -preset slow \
  -movflags +faststart -an \
  -y stage1_2_merged.mp4
```

---

## 4. Integration Patterns

### Single Long Video (Current Approach)

```javascript
ScrollVideo.init({
  element: '#journey-video',
  mode: 'video',
  easing: 'smooth',
  smoothing: 0.08,
  onProgress: function(progress) {
    // Update overlay cards, progress bar, etc.
  }
});
```

Best for: one continuous narrative video (like the current Veo-generated one).

### Chained Multi-Video (Stage-by-Stage)

```javascript
ScrollVideo.chain([
  { element: '#stage1-video', startVh: 0,   endVh: 100 },
  { element: '#stage2-video', startVh: 100, endVh: 200 },
  { element: '#stage3-video', startVh: 200, endVh: 300 },
  { element: '#stage4-video', startVh: 300, endVh: 400 },
  { element: '#stage5-video', startVh: 400, endVh: 500 },
]);
```

Best for: when each stage has a distinct Veo-generated clip with different visual character.

### Frame Sequence Fallback (iOS Safari Compatibility)

iOS Safari can be unreliable with video `currentTime` scrubbing. Frame sequence mode is more robust:

```javascript
ScrollVideo.init({
  element: '#journey-canvas',
  mode: 'frames',
  frameCount: 144,
  framePath: 'frames/frame_{index}.webp',
  easing: 'smooth',
  smoothing: 0.06
});
```

### Lazy Loading Pattern

To hit LCP < 2.5s, defer video loading until the section is near viewport:

```javascript
// In the existing IntersectionObserver setup:
const journeyObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const video = document.getElementById('journey-video');
      video.src = 'Industrial_Waste_to_Sustainable_City_web.mp4';
      video.load();
      journeyObserver.unobserve(entry.target);
    }
  });
}, { rootMargin: '200px' }); // Start loading 200px before visible

journeyObserver.observe(document.getElementById('process-video'));
```

---

## 5. Performance Checklist

- [ ] Video is `< 1 MB` (use `ffmpeg -crf 28` or higher)
- [ ] Video has `preload="none"` or lazy-load via IntersectionObserver
- [ ] `movflags +faststart` applied (progressive loading)
- [ ] Audio track stripped (`-an`)
- [ ] Scroll section has explicit `height` set (CLS < 0.1)
- [ ] Poster image set on `<video>` for pre-load visual
- [ ] `prefers-reduced-motion` respected (static poster shown instead)
- [ ] Tested on: Chrome, Safari, Firefox, iOS Safari, Android Chrome

---

## 6. Design System Compliance

All overlays must use the Kura design tokens:

```css
--charcoal: #0f0f0f;
--copper:   #C87533;
--sage:     #4A7C59;
```

- Glass-morphism cards: `backdrop-blur-xl bg-white/[0.06] border border-white/[0.08]`
- Typography: Plus Jakarta Sans (headings), Inter (body/mono labels)
- Stage labels: `font-family: 'Inter', monospace; font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase`
- Gradient overlays: `from-[#0f0f0f]/80 via-transparent to-[#0f0f0f]/40`

---

## 7. References

- [Apple AirPods Pro Scroll Technique](https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/) — Canvas + image sequence approach
- [Brad Holmes: "Why Most Scroll Animations Miss What Apple Gets Right"](https://bradhomes.com) — Viewport-relative ranges, decoupled from asset height
- [CSS scroll-timeline API (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-timeline) — Native browser scroll binding (Chrome 115+, no Safari yet)
- [Google Flow / Veo 3.1](https://labs.google/fx/tools/video-fx) — AI video generation
- Kura Materials Site: `/Users/leozealous/kura-materials-site/` (v3.3, single `index.html`)
- ScrollVideo Module: `/Users/leozealous/kura-materials-site/scroll-video.js`
