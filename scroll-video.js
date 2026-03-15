/**
 * ScrollVideo — Reusable scroll-driven video/frame-sequence module
 * 
 * Zero dependencies. Apple-style scroll scrubbing with cinematic easing.
 * Supports video mode (MP4/WebM currentTime scrub) and frame mode (canvas + image sequence).
 * 
 * @version 1.0.0
 * @license MIT
 * @author Zealous (OpenClaw) for Leo Maslyak
 * 
 * Usage:
 *   ScrollVideo.init({
 *     element: '#my-video',
 *     mode: 'video',
 *     startOffset: 0,
 *     endOffset: 3000,
 *     easing: 'smooth',
 *     onProgress: (p) => console.log(p),
 *   });
 */
;(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ScrollVideo = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // ─── Helpers ──────────────────────────────────────────────
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const lerp  = (a, b, t) => a + (b - a) * t;

  const prefersReducedMotion = () =>
    typeof matchMedia === 'function' &&
    matchMedia('(prefers-reduced-motion: reduce)').matches;

  const resolveElement = (ref) => {
    if (typeof ref === 'string') return document.querySelector(ref);
    if (ref instanceof HTMLElement) return ref;
    return null;
  };

  const resolveScrollContainer = (ref) => {
    if (!ref || ref === window || ref === document) return window;
    return resolveElement(ref) || window;
  };

  const getScrollY = (container) =>
    container === window
      ? window.scrollY || document.documentElement.scrollTop
      : container.scrollTop;

  // ─── Instance tracker (for resize / cleanup) ─────────────
  const instances = [];
  let resizeRAF = null;

  function handleResize() {
    if (resizeRAF) return;
    resizeRAF = requestAnimationFrame(() => {
      instances.forEach((inst) => inst._recalc && inst._recalc());
      resizeRAF = null;
    });
  }

  let resizeListenerBound = false;
  function ensureResizeListener() {
    if (resizeListenerBound) return;
    window.addEventListener('resize', handleResize, { passive: true });
    window.addEventListener('orientationchange', handleResize, { passive: true });
    resizeListenerBound = true;
  }

  // ─── ScrollVideo Instance ────────────────────────────────
  class ScrollVideoInstance {
    /**
     * @param {Object} opts
     * @param {string|HTMLElement} opts.element     - video or canvas element
     * @param {'video'|'frames'}   opts.mode        - scrub mode (default: 'video')
     * @param {Window|string|HTMLElement} opts.scrollContainer - scroll source
     * @param {number}   opts.startOffset  - px from document top (or element top if offsetMode='viewport')
     * @param {number}   opts.endOffset    - px from document top (or scroll range if offsetMode='viewport')
     * @param {string[]|null} opts.frames  - array of image URLs (frames mode only)
     * @param {number}   opts.fps          - target fps for frame mode (default: 30)
     * @param {'linear'|'smooth'} opts.easing - easing (default: 'smooth')
     * @param {number}   opts.smoothing    - lerp factor 0-1 (default: 0.08)
     * @param {Function} opts.onProgress   - callback(progress: 0-1)
     * @param {Function} opts.onReady      - callback when media loaded
     * @param {string|null} opts.poster    - static image for reduced-motion fallback
     * @param {boolean}  opts.debug        - log to console
     * @param {'viewport'|'document'} opts.offsetMode
     *   'document' (default): absolute px from document top
     *   'viewport': element-relative — startOffset added to element top,
     *               endOffset is the scroll range length
     */
    constructor(opts) {
      this.opts = Object.assign(
        {
          mode: 'video',
          scrollContainer: window,
          startOffset: 0,
          endOffset: 3000,
          frames: null,
          fps: 30,
          easing: 'smooth',
          smoothing: 0.08,
          onProgress: null,
          onReady: null,
          poster: null,
          debug: false,
          offsetMode: 'document',
        },
        opts,
      );

      this.el = resolveElement(this.opts.element);
      if (!this.el) {
        console.error('[ScrollVideo] element not found:', this.opts.element);
        return;
      }

      this.container = resolveScrollContainer(this.opts.scrollContainer);
      this._destroyed = false;
      this._ready = false;
      this._currentProgress = 0;
      this._targetProgress = 0;
      this._rafId = null;

      // Reduced-motion: show poster & bail
      if (prefersReducedMotion()) {
        this._applyReducedMotion();
        return;
      }

      this._frameImages = [];
      this._framesLoaded = 0;
      this._startPx = 0;
      this._endPx = 0;

      this._init();
    }

    _init() {
      ensureResizeListener();
      instances.push(this);

      if (this.opts.mode === 'video') {
        this._initVideo();
      } else {
        this._initFrames();
      }
    }

    // ─── Video Mode ──────────────────────────────────────
    _initVideo() {
      const video = this.el;
      video.preload = 'auto';
      video.muted = true;
      video.playsInline = true;
      video.pause();
      video.removeAttribute('autoplay');
      video.removeAttribute('loop');

      const onMeta = () => {
        this._duration = video.duration;
        this._recalc();
        this._ready = true;
        this.opts.onReady && this.opts.onReady(this);
        this._startLoop();
        if (this.opts.debug) console.log('[ScrollVideo] video ready, duration:', this._duration);
      };

      if (video.readyState >= 1) {
        onMeta();
      } else {
        video.addEventListener('loadedmetadata', onMeta, { once: true });
      }
      video.load();
    }

    // ─── Frame Sequence Mode ─────────────────────────────
    _initFrames() {
      const frames = this.opts.frames;
      if (!frames || !frames.length) {
        console.error('[ScrollVideo] frames mode requires opts.frames array');
        return;
      }

      const canvas = this.el;
      if (canvas.tagName !== 'CANVAS') {
        console.error('[ScrollVideo] frames mode requires a <canvas> element');
        return;
      }
      this._ctx = canvas.getContext('2d');

      let loaded = 0;
      this._frameImages = frames.map((src, i) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          loaded++;
          if (loaded === frames.length) {
            canvas.width = this._frameImages[0].naturalWidth;
            canvas.height = this._frameImages[0].naturalHeight;
            this._recalc();
            this._ready = true;
            this.opts.onReady && this.opts.onReady(this);
            this._startLoop();
            if (this.opts.debug) console.log('[ScrollVideo] all', frames.length, 'frames loaded');
          }
        };
        img.onerror = () => {
          console.warn('[ScrollVideo] failed to load frame', i, src);
          loaded++;
        };
        img.src = src;
        return img;
      });
    }

    // ─── Offset Calculation ──────────────────────────────
    _recalc() {
      if (this.opts.offsetMode === 'viewport') {
        const rect = this.el.getBoundingClientRect();
        const scrollY = getScrollY(this.container);
        const elTop = rect.top + scrollY;
        this._startPx = elTop + this.opts.startOffset;
        this._endPx = this._startPx + this.opts.endOffset;
      } else {
        this._startPx = this.opts.startOffset;
        this._endPx = this.opts.endOffset;
      }
    }

    // ─── Main RAF Loop ───────────────────────────────────
    _startLoop() {
      const tick = () => {
        if (this._destroyed) return;
        this._update();
        this._rafId = requestAnimationFrame(tick);
      };
      this._rafId = requestAnimationFrame(tick);
    }

    _update() {
      const scrollY = getScrollY(this.container);
      const range = this._endPx - this._startPx;
      if (range <= 0) return;

      this._targetProgress = clamp((scrollY - this._startPx) / range, 0, 1);

      if (this.opts.easing === 'smooth') {
        this._currentProgress = lerp(
          this._currentProgress,
          this._targetProgress,
          this.opts.smoothing,
        );
        if (Math.abs(this._currentProgress - this._targetProgress) < 0.0005) {
          this._currentProgress = this._targetProgress;
        }
      } else {
        this._currentProgress = this._targetProgress;
      }

      if (this.opts.mode === 'video') {
        this._scrubVideo(this._currentProgress);
      } else {
        this._drawFrame(this._currentProgress);
      }

      if (this.opts.onProgress) {
        this.opts.onProgress(this._currentProgress);
      }
    }

    _scrubVideo(progress) {
      const video = this.el;
      if (!this._duration) return;
      const targetTime = progress * this._duration;
      if (Math.abs(video.currentTime - targetTime) > 0.03) {
        video.currentTime = targetTime;
      }
    }

    _drawFrame(progress) {
      const totalFrames = this._frameImages.length;
      if (!totalFrames) return;
      const idx = Math.min(Math.floor(progress * totalFrames), totalFrames - 1);
      const img = this._frameImages[idx];
      if (img && img.complete && img.naturalWidth) {
        this._ctx.drawImage(img, 0, 0, this.el.width, this.el.height);
      }
    }

    // ─── Reduced Motion Fallback ─────────────────────────
    _applyReducedMotion() {
      if (this.opts.poster) {
        if (this.opts.mode === 'video') {
          this.el.poster = this.opts.poster;
          this.el.removeAttribute('autoplay');
          this.el.pause && this.el.pause();
        } else if (this.el.tagName === 'CANVAS') {
          const img = new Image();
          img.onload = () => {
            this.el.width = img.naturalWidth;
            this.el.height = img.naturalHeight;
            const ctx = this.el.getContext('2d');
            ctx.drawImage(img, 0, 0);
          };
          img.src = this.opts.poster;
        }
      } else if (this.opts.mode === 'video') {
        this.el.removeAttribute('autoplay');
        this.el.pause && this.el.pause();
      }
      if (this.opts.debug) console.log('[ScrollVideo] reduced-motion: static fallback');
    }

    // ─── Public API ──────────────────────────────────────
    get progress() { return this._currentProgress; }

    seekTo(progress) {
      const p = clamp(progress, 0, 1);
      this._currentProgress = p;
      this._targetProgress = p;
      if (this.opts.mode === 'video') this._scrubVideo(p);
      else this._drawFrame(p);
    }

    destroy() {
      this._destroyed = true;
      if (this._rafId) cancelAnimationFrame(this._rafId);
      const idx = instances.indexOf(this);
      if (idx >= 0) instances.splice(idx, 1);
    }
  }

  // ─── Public Static API ────────────────────────────────

  function init(opts) {
    return new ScrollVideoInstance(opts);
  }

  function destroyAll() {
    [...instances].forEach((inst) => inst.destroy());
  }

  /**
   * Chain multiple scroll-video sections sequentially.
   * @param {Object[]} sections - array of section configs (no startOffset/endOffset needed)
   * @param {Object}   chainOpts
   * @param {number}   chainOpts.totalScroll - total px for all sections
   * @param {number}   chainOpts.startAt     - px offset for first section
   * @returns {ScrollVideoInstance[]}
   */
  function chain(sections, chainOpts = {}) {
    const total = chainOpts.totalScroll || 5000;
    const startAt = chainOpts.startAt || 0;
    const perSection = total / sections.length;

    return sections.map((cfg, i) => {
      return init(
        Object.assign({}, cfg, {
          startOffset: startAt + i * perSection,
          endOffset: startAt + (i + 1) * perSection,
        }),
      );
    });
  }

  return { init, chain, destroyAll, _instances: instances };
});
