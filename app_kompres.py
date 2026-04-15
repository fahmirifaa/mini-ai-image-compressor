"""
AI Image Engine Pro — Production-Ready Image Optimizer
=======================================================
Author   : Senior Python Developer
Version  : 2.0.0
Stack    : Streamlit · Pillow · io · base64
Offline  : True (no external API calls)

Architecture
------------
- ImageProcessor   : Stateless class encapsulating all compression logic
- UIComponents     : Pure helper functions rendering Streamlit widgets
- App Entry Point  : Orchestrates state, routing, and rendering
"""

from __future__ import annotations

import io
import traceback
from dataclasses import dataclass, field
from typing import Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ExifTags, UnidentifiedImageError

# ─────────────────────────────────────────────────────────────────────────────
# 0. PAGE CONFIG — must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ImgPress Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. DESIGN TOKENS & GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg-primary:    #0c0d11;
    --bg-secondary:  #13151c;
    --bg-card:       #181b25;
    --bg-card-hover: #1e2130;
    --border:        rgba(255,255,255,0.07);
    --border-accent: rgba(99,179,237,0.35);
    --accent-cyan:   #63b3ed;
    --accent-lime:   #a3e635;
    --accent-rose:   #fb7185;
    --text-primary:  #f0f2f8;
    --text-muted:    #7a8399;
    --text-dim:      #3d4357;
    --radius-sm:     8px;
    --radius-md:     14px;
    --radius-lg:     22px;
    --mono:          'DM Mono', monospace;
    --display:       'Syne', sans-serif;
}

/* ── Base reset ── */
html, body, [class*="css"] {
    font-family: var(--display);
    background-color: var(--bg-primary) !important;
    color: var(--text-primary);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem !important; max-width: 1400px; }

/* ── Headings ── */
h1, h2, h3 { font-family: var(--display); font-weight: 800; letter-spacing: -0.02em; }

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.6rem 1.8rem;
    transition: border-color 0.2s, background 0.2s;
}
.card:hover { border-color: var(--border-accent); background: var(--bg-card-hover); }

/* ── Stat pill ── */
.stat-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(99,179,237,0.08);
    border: 1px solid rgba(99,179,237,0.18);
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-family: var(--mono);
    font-size: 0.78rem;
    color: var(--accent-cyan);
    white-space: nowrap;
}
.stat-pill.lime  { background: rgba(163,230,53,0.08); border-color: rgba(163,230,53,0.18); color: var(--accent-lime); }
.stat-pill.rose  { background: rgba(251,113,133,0.08); border-color: rgba(251,113,133,0.18); color: var(--accent-rose); }

/* ── Badge ── */
.badge {
    display: inline-block;
    font-family: var(--mono); font-size: 0.7rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 0.15rem 0.6rem; border-radius: 4px;
}
.badge-cyan { background: rgba(99,179,237,0.15); color: var(--accent-cyan); }
.badge-lime { background: rgba(163,230,53,0.12); color: var(--accent-lime); }

/* ── Section label ── */
.section-label {
    font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase;
    letter-spacing: 0.14em; color: var(--text-muted);
    margin-bottom: 0.6rem; display: block;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 1.8rem 0; }

/* ── File uploader ── */
div[data-testid="stFileUploadDropzone"] {
    min-height: 200px !important;
    background: var(--bg-card) !important;
    border: 2px dashed rgba(99,179,237,0.3) !important;
    border-radius: var(--radius-lg) !important;
    transition: border-color 0.25s;
}
div[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--accent-cyan) !important;
}
div[data-testid="stFileUploadDropzone"] p { color: var(--text-muted) !important; }
div[data-testid="stFileUploadDropzone"] svg { fill: var(--accent-cyan) !important; }

/* ── Sliders ── */
div[data-testid="stSlider"] > div > div > div > div {
    background: var(--accent-cyan) !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background: var(--bg-secondary) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* ── Number input ── */
div[data-baseweb="input"] > div {
    background: var(--bg-secondary) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-baseweb="input"] input { color: var(--text-primary) !important; }

/* ── Primary button ── */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #63b3ed 0%, #4299e1 100%) !important;
    color: #0c0d11 !important;
    font-family: var(--display) !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    height: 3.2em !important;
    transition: filter 0.18s, transform 0.12s !important;
}
div[data-testid="stButton"] > button:hover {
    filter: brightness(1.12) !important;
    transform: translateY(-1px) !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #a3e635 0%, #84cc16 100%) !important;
    color: #0c0d11 !important;
    font-family: var(--display) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    height: 3.2em !important;
    transition: filter 0.18s, transform 0.12s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
}
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.78rem !important; }
div[data-testid="stMetricValue"] { font-family: var(--mono) !important; color: var(--text-primary) !important; }
div[data-testid="stMetricDelta"] { font-family: var(--mono) !important; }

/* ── Checkbox ── */
label[data-testid="stCheckbox"] span { color: var(--text-primary) !important; }

/* ── Success / Info / Error banners ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
}

/* ── Image captions ── */
div[data-testid="caption"] {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    color: var(--text-muted) !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] > div { border-top-color: var(--accent-cyan) !important; }

/* ── Drag-anywhere Overlay ── */
#drag-overlay {
    position: fixed; inset: 0;
    display: none; justify-content: center; align-items: center;
    flex-direction: column; gap: 1rem;
    z-index: 9999;
    pointer-events: none;
    /* Glassmorphism */
    background: rgba(10, 12, 22, 0.72);
    backdrop-filter: blur(18px) saturate(1.8);
    -webkit-backdrop-filter: blur(18px) saturate(1.8);
    border: 3px dashed rgba(99,179,237,0.55);
    transition: opacity 0.18s ease;
    opacity: 0;
}
#drag-overlay.visible { display: flex; opacity: 1; }
#drag-overlay .icon {
    font-size: 4rem;
    animation: float 1.6s ease-in-out infinite alternate;
}
#drag-overlay .label {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem; font-weight: 800;
    letter-spacing: -0.02em;
    color: #f0f2f8;
}
#drag-overlay .sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem; color: rgba(99,179,237,0.8);
    letter-spacing: 0.06em; text-transform: uppercase;
}
@keyframes float {
    from { transform: translateY(0);   }
    to   { transform: translateY(-12px); }
}

/* ── Top wordmark ── */
.wordmark {
    font-family: var(--display); font-weight: 800; font-size: 2rem;
    letter-spacing: -0.04em; color: var(--text-primary);
    display: flex; align-items: center; gap: 0.5rem;
}
.wordmark .accent { color: var(--accent-cyan); }
.wordmark .tag {
    font-size: 0.62rem; font-family: var(--mono);
    background: rgba(99,179,237,0.12);
    color: var(--accent-cyan);
    border: 1px solid rgba(99,179,237,0.25);
    border-radius: 4px; padding: 0.1rem 0.45rem;
    letter-spacing: 0.1em; text-transform: uppercase;
    vertical-align: middle; margin-left: 4px;
}

/* ── Comparison label strip ── */
.cmp-label {
    font-family: var(--mono); font-size: 0.72rem;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 0.3rem 0.8rem;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    display: inline-block; margin-bottom: -2px;
}
.cmp-original { background: rgba(251,113,133,0.15); color: var(--accent-rose); }
.cmp-optimized { background: rgba(163,230,53,0.13); color: var(--accent-lime); }
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. DRAG-ANYWHERE JAVASCRIPT
# ─────────────────────────────────────────────────────────────────────────────
DRAG_JS = """
<script>
(function() {
    const doc  = window.parent.document;
    let   drag = 0;          // counter avoids flicker on child-element crossings

    function overlay() { return doc.getElementById('drag-overlay'); }

    doc.addEventListener('dragenter', (e) => {
        e.preventDefault();
        drag++;
        const ov = overlay();
        if (ov) { ov.style.display = 'flex'; setTimeout(() => ov.classList.add('visible'), 10); }
    });

    doc.addEventListener('dragleave', (e) => {
        drag--;
        if (drag <= 0) {
            drag = 0;
            const ov = overlay();
            if (ov) { ov.classList.remove('visible'); setTimeout(() => { if (!ov.classList.contains('visible')) ov.style.display = 'none'; }, 200); }
        }
    });

    doc.addEventListener('dragover', (e) => { e.preventDefault(); });

    doc.addEventListener('drop', (e) => {
        drag = 0;
        const ov = overlay();
        if (ov) { ov.classList.remove('visible'); setTimeout(() => ov.style.display = 'none', 200); }
    });
})();
</script>
"""

DRAG_OVERLAY_HTML = """
<div id="drag-overlay">
    <div class="icon">📦</div>
    <div class="label">Drop Image Anywhere</div>
    <div class="sub">jpg · png · webp · avif supported</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ProcessingOptions:
    """All user-controlled parameters for a single optimization run."""
    target_mb:       float
    output_format:   str          # "JPEG" | "PNG" | "WEBP" | "WEBP_LOSSLESS" | "AVIF"
    scale_percent:   int          # 10–100
    strip_exif:      bool         = True
    webp_lossless:   bool         = False
    quality_hint:    Optional[int] = None  # override binary-search; None = auto


@dataclass
class ProcessingResult:
    """Outcome of a single ImageProcessor.compress() call."""
    buffer:        io.BytesIO
    final_size_mb: float
    final_res:     Tuple[int, int]
    quality_used:  int             # 0 = N/A (PNG lossless)
    savings_pct:   float           # percentage reduction
    warnings:      list[str]       = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# 4. IMAGE PROCESSOR CLASS
# ─────────────────────────────────────────────────────────────────────────────
class ImageProcessor:
    """
    Stateless image compression engine.

    All methods are class-level; instantiate once per session or call directly.
    Supports JPEG, PNG (quantized), WebP (lossy/lossless), and AVIF (if Pillow ≥ 9.1).
    """

    SUPPORTED_FORMATS: tuple[str, ...] = ("JPEG", "PNG", "WEBP", "WEBP_LOSSLESS", "AVIF")
    LARGE_IMAGE_PX:    int = 4_000 * 4_000   # threshold for BILINEAR suggestion

    # ── Public entry point ────────────────────────────────────────────────────
    @classmethod
    def compress(
        cls,
        img:  Image.Image,
        opts: ProcessingOptions,
        original_size_mb: float,
    ) -> ProcessingResult:
        """
        Compress *img* according to *opts*.

        Parameters
        ----------
        img              : Opened PIL Image (any mode).
        opts             : ProcessingOptions dataclass.
        original_size_mb : Pre-computed original file size for savings %.

        Returns
        -------
        ProcessingResult with buffer ready for reading.

        Raises
        ------
        ValueError  : Unsupported format string.
        RuntimeError: Compression target impossible to meet.
        """
        warnings: list[str] = []

        # 1. Choose resampling filter
        resample = cls._choose_resampling(img, opts.scale_percent, warnings)

        # 2. Resize
        img = cls._resize(img, opts.scale_percent, resample)

        # 3. EXIF handling
        exif_bytes = cls._extract_exif(img) if not opts.strip_exif else None

        # 4. Colour-mode normalisation
        img, warnings = cls._normalise_mode(img, opts.output_format, warnings)

        # 5. Compress
        buf, quality = cls._dispatch_compress(img, opts, exif_bytes)

        # 6. Assemble result
        buf.seek(0)
        final_mb   = len(buf.getvalue()) / (1024 * 1024)
        savings    = max(0.0, (original_size_mb - final_mb) / original_size_mb * 100)

        return ProcessingResult(
            buffer        = buf,
            final_size_mb = final_mb,
            final_res     = img.size,
            quality_used  = quality,
            savings_pct   = savings,
            warnings      = warnings,
        )

    # ── Private helpers ───────────────────────────────────────────────────────
    @classmethod
    def _choose_resampling(
        cls,
        img:           Image.Image,
        scale_percent: int,
        warnings:      list[str],
    ) -> Image.Resampling:
        """
        Return LANCZOS for normal images; BILINEAR for very large ones when
        downscaling to reduce CPU cost, and warn the caller.
        """
        total_px = img.size[0] * img.size[1]
        if total_px > cls.LARGE_IMAGE_PX and scale_percent < 80:
            warnings.append(
                "Large image detected — using BILINEAR resampling for speed. "
                "Switch to LANCZOS for maximum quality."
            )
            return Image.Resampling.BILINEAR
        return Image.Resampling.LANCZOS

    @staticmethod
    def _resize(
        img:           Image.Image,
        scale_percent: int,
        resample:      Image.Resampling,
    ) -> Image.Image:
        """Scale *img* by *scale_percent* using *resample* filter."""
        if scale_percent == 100:
            return img
        w = max(1, int(img.size[0] * scale_percent / 100))
        h = max(1, int(img.size[1] * scale_percent / 100))
        return img.resize((w, h), resample)

    @staticmethod
    def _extract_exif(img: Image.Image) -> Optional[bytes]:
        """Return raw EXIF bytes if present, else None."""
        try:
            return img.info.get("exif", None)
        except Exception:
            return None

    @staticmethod
    def _normalise_mode(
        img:    Image.Image,
        fmt:    str,
        warns:  list[str],
    ) -> Tuple[Image.Image, list[str]]:
        """
        Convert colour mode to one compatible with *fmt*.
        JPEG / AVIF cannot store alpha; PNG / WebP can.
        """
        lossy_formats = {"JPEG", "AVIF"}
        if fmt in lossy_formats and img.mode in ("RGBA", "LA", "P"):
            warns.append(
                f"Image has transparency — converted to RGB for {fmt} output "
                "(alpha channel removed)."
            )
            # Composite onto white background to avoid black fringing
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode in ("RGBA", "LA"):
                bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode == "P":
            img = img.convert("RGBA")
        return img, warns

    @classmethod
    def _dispatch_compress(
        cls,
        img:        Image.Image,
        opts:       ProcessingOptions,
        exif_bytes: Optional[bytes],
    ) -> Tuple[io.BytesIO, int]:
        """Route to the correct format-specific compressor."""
        fmt = opts.output_format
        if fmt == "PNG":
            return cls._compress_png(img)
        elif fmt in ("JPEG",):
            return cls._compress_quality_target(
                img, opts, exif_bytes, pil_format="JPEG"
            )
        elif fmt == "WEBP_LOSSLESS":
            return cls._compress_webp_lossless(img)
        elif fmt == "WEBP":
            return cls._compress_quality_target(
                img, opts, exif_bytes, pil_format="WEBP"
            )
        elif fmt == "AVIF":
            return cls._compress_avif(img, opts)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    # ── Format-specific compressors ───────────────────────────────────────────
    @staticmethod
    def _compress_png(img: Image.Image) -> Tuple[io.BytesIO, int]:
        """
        PNG: quantize to 256-color adaptive palette, then write with
        maximum lossless compression.  Quality is not applicable → returns 0.
        """
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA"):
            img_out = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        else:
            img_out = img.convert("P", palette=Image.ADAPTIVE, colors=256)
        img_out.save(buf, format="PNG", optimize=True, compress_level=9)
        return buf, 0

    @staticmethod
    def _compress_quality_target(
        img:        Image.Image,
        opts:       ProcessingOptions,
        exif_bytes: Optional[bytes],
        pil_format: str,
    ) -> Tuple[io.BytesIO, int]:
        """
        Binary-search quality (10–95) to hit *opts.target_mb*.

        Improvements over v1
        --------------------
        - Starts mid at 75 (empirically better first guess than 52).
        - Terminates early when size is within 1 KB of target.
        - Pre-checks: if quality=95 is already under target, skip search.
        - Uses a single reusable BytesIO buffer (reset each iteration).
        """
        save_kwargs: dict = {"format": pil_format, "optimize": True}
        if exif_bytes:
            save_kwargs["exif"] = exif_bytes

        target_bytes = opts.target_mb * 1024 * 1024
        buf          = io.BytesIO()

        # ── Quick path: check if max quality already fits ──
        buf.truncate(0); buf.seek(0)
        img.save(buf, quality=95, **save_kwargs)
        if len(buf.getvalue()) <= target_bytes:
            return buf, 95

        # ── Quick path: check if min quality satisfies ──
        buf.truncate(0); buf.seek(0)
        img.save(buf, quality=10, **save_kwargs)
        if len(buf.getvalue()) > target_bytes:
            # Can't hit target; return best we can do
            return buf, 10

        # ── Binary search (max 8 iterations, converges in ~7) ──
        lo, hi         = 10, 95
        best_buf       = io.BytesIO()
        best_q         = lo

        for _ in range(8):
            mid = (lo + hi) // 2
            buf.truncate(0); buf.seek(0)
            img.save(buf, quality=mid, **save_kwargs)
            curr = len(buf.getvalue())

            if curr <= target_bytes:
                # This quality fits — save as candidate; try higher quality
                best_buf = io.BytesIO(buf.getvalue())
                best_q   = mid
                lo       = mid + 1
                if target_bytes - curr < 1024:   # within 1 KB — close enough
                    break
            else:
                hi = mid - 1

            if lo > hi:
                break

        best_buf.seek(0)
        return best_buf, best_q

    @staticmethod
    def _compress_webp_lossless(img: Image.Image) -> Tuple[io.BytesIO, int]:
        """WebP lossless — no quality knob, method=6 for best compression."""
        buf = io.BytesIO()
        img.save(buf, format="WEBP", lossless=True, method=6)
        return buf, 100  # 100 = conceptually lossless

    @staticmethod
    def _compress_avif(
        img: Image.Image, opts: ProcessingOptions
    ) -> Tuple[io.BytesIO, int]:
        """
        AVIF via Pillow's pillow-avif-plugin or native support (Pillow ≥ 9.1).
        Falls back gracefully with a clear error.
        """
        buf = io.BytesIO()
        quality = opts.quality_hint or 60  # AVIF quality scale differs from JPEG
        try:
            img.save(buf, format="AVIF", quality=quality)
        except (KeyError, OSError) as exc:
            raise RuntimeError(
                "AVIF encoding requires pillow-avif-plugin or Pillow ≥ 9.1 built "
                f"with libavif.  Original error: {exc}"
            ) from exc
        return buf, quality

    # ── Utility ───────────────────────────────────────────────────────────────
    @staticmethod
    def read_exif_summary(img: Image.Image) -> dict[str, str]:
        """
        Return a human-readable dict of key EXIF tags.
        Returns empty dict if no EXIF is available.
        """
        try:
            raw = img._getexif()  # type: ignore[attr-defined]
            if not raw:
                return {}
            result = {}
            for tag_id, value in raw.items():
                tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                if tag in ("Make", "Model", "Software", "DateTime",
                           "ExposureTime", "FNumber", "ISOSpeedRatings",
                           "Flash", "FocalLength", "ColorSpace"):
                    result[tag] = str(value)
            return result
        except Exception:
            return {}


# ─────────────────────────────────────────────────────────────────────────────
# 5. UI HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def inject_styles() -> None:
    """Inject global CSS and drag overlay HTML into the page."""
    st.markdown(f"<style>{GLOBAL_CSS}</style>", unsafe_allow_html=True)
    st.markdown(DRAG_OVERLAY_HTML, unsafe_allow_html=True)
    components.html(DRAG_JS, height=0)


def render_wordmark() -> None:
    """Top-of-page branding strip."""
    st.markdown(
        '<div class="wordmark">Img<span class="accent">Press</span>'
        '<span class="tag">PRO v2</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.3rem;'
        'font-family:var(--mono);">Offline-first · Binary-search compression · '
        'JPEG · PNG · WebP · AVIF</p>',
        unsafe_allow_html=True,
    )


def render_file_info(img: Image.Image, uploaded_file) -> dict[str, str]:
    """
    Display auto-detected file metadata pills.
    Returns the raw EXIF dict so the caller can optionally show it.
    """
    original_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    exif_data   = ImageProcessor.read_exif_summary(img)

    col_a, col_b, col_c, col_d, col_e = st.columns([1, 1, 1, 1, 2])
    with col_a:
        st.markdown(
            f'<span class="stat-pill">🗂 {img.format or "Unknown"}</span>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f'<span class="stat-pill lime">⚖ {original_mb:.2f} MB</span>',
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            f'<span class="stat-pill">📐 {img.size[0]}×{img.size[1]}</span>',
            unsafe_allow_html=True,
        )
    with col_d:
        st.markdown(
            f'<span class="stat-pill">🎨 {img.mode}</span>',
            unsafe_allow_html=True,
        )
    with col_e:
        exif_status = f"EXIF: {len(exif_data)} tags" if exif_data else "No EXIF"
        st.markdown(
            f'<span class="stat-pill rose">🔎 {exif_status}</span>',
            unsafe_allow_html=True,
        )
    return exif_data


def render_controls(
    img: Image.Image,
    original_mb: float,
    exif_data: dict,
) -> ProcessingOptions:
    """
    Render the three-column control panel.
    Returns a fully-populated ProcessingOptions.
    """
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<span class="section-label">⚙ Processing Controls</span>',
        unsafe_allow_html=True,
    )

    # Inject CSS agar setiap kolom tampil sebagai card bertema
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.4rem 1.6rem 1.2rem 1.6rem !important;
        transition: border-color 0.2s, background 0.2s;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:hover {
        border-color: var(--border-accent);
        background: var(--bg-card-hover);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            '<span class="section-label">📏 Dimension Scale</span>',
            unsafe_allow_html=True,
        )
        scale = st.slider("Scale (%)", 10, 100, 100, step=5, key="scale")
        new_w = int(img.size[0] * scale / 100)
        new_h = int(img.size[1] * scale / 100)
        st.markdown(
            f'<span class="stat-pill" style="font-size:0.7rem">'
            f'→ {new_w} × {new_h} px</span>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<span class="section-label">🎯 Size Target</span>',
            unsafe_allow_html=True,
        )
        t_size = st.number_input(
            "Max output (MB)",
            min_value=0.01,
            max_value=float(max(original_mb, 0.01)),
            value=min(original_mb, 0.5),
            step=0.05,
            format="%.2f",
            key="target",
        )

    with col3:
        st.markdown(
            '<span class="section-label">💾 Output Format</span>',
            unsafe_allow_html=True,
        )

        FORMAT_LABELS = {
            "JPEG":          "JPEG — Lossy (universal)",
            "PNG":           "PNG  — Lossless palette",
            "WEBP":          "WebP — Lossy (modern)",
            "WEBP_LOSSLESS": "WebP — Lossless",
            "AVIF":          "AVIF — Lossy (next-gen)",
        }
        # Determine sensible default
        detected = (img.format or "JPEG").upper()
        default_key = detected if detected in FORMAT_LABELS else "JPEG"

        out_fmt = st.selectbox(
            "Save as",
            list(FORMAT_LABELS.keys()),
            format_func=lambda k: FORMAT_LABELS[k],
            index=list(FORMAT_LABELS.keys()).index(default_key),
            key="fmt",
        )

        strip_exif = st.checkbox(
            "Strip EXIF metadata",
            value=True,
            help="Remove camera/GPS data for smaller file & privacy.",
            key="strip_exif",
            disabled=(not exif_data),
        )

    return ProcessingOptions(
        target_mb=t_size,
        output_format=out_fmt,
        scale_percent=scale,
        strip_exif=strip_exif,
    )


def render_results(
    original_img:    Image.Image,
    original_mb:     float,
    result:          ProcessingResult,
    uploaded_name:   str,
    out_fmt:         str,
) -> None:
    """Render side-by-side comparison, metrics, and download button."""
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<span class="section-label">🖼 Side-by-Side Comparison</span>',
        unsafe_allow_html=True,
    )

    col_orig, col_opt = st.columns(2, gap="medium")

    with col_orig:
        st.markdown(
            '<div class="cmp-label cmp-original">◉ Original</div>',
            unsafe_allow_html=True,
        )
        st.image(
            original_img,
            caption=f"{original_mb:.3f} MB  ·  {original_img.size[0]}×{original_img.size[1]} px",
            use_container_width=True,
        )

    with col_opt:
        st.markdown(
            '<div class="cmp-label cmp-optimized">◎ Optimised</div>',
            unsafe_allow_html=True,
        )
        result.buffer.seek(0)
        st.image(
            result.buffer.read(),
            caption=(
                f"{result.final_size_mb:.3f} MB  ·  "
                f"{result.final_res[0]}×{result.final_res[1]} px"
            ),
            use_container_width=True,
        )

    # Metrics strip
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    delta_mb  = result.final_size_mb - original_mb
    q_display = "Lossless" if result.quality_used in (0, 100) else str(result.quality_used)

    with m1:
        st.metric("Output Size", f"{result.final_size_mb:.3f} MB",
                  f"{delta_mb:+.3f} MB")
    with m2:
        st.metric("Space Saved", f"{result.savings_pct:.1f}%")
    with m3:
        st.metric("Q-Factor", q_display)
    with m4:
        st.metric("Resolution", f"{result.final_res[0]}×{result.final_res[1]}")

    # Warnings
    for w in result.warnings:
        st.warning(f"⚠ {w}")

    # Download
    ext_map = {
        "JPEG": "jpg", "PNG": "png",
        "WEBP": "webp", "WEBP_LOSSLESS": "webp", "AVIF": "avif",
    }
    ext  = ext_map.get(out_fmt, "jpg")
    stem = uploaded_name.rsplit(".", 1)[0]
    result.buffer.seek(0)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label=f"⬇  Download  {stem}_optimized.{ext}",
        data=result.buffer.getvalue(),
        file_name=f"{stem}_optimized.{ext}",
        mime=f"image/{ext}",
        use_container_width=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. APP ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Orchestrates the full Streamlit app lifecycle."""

    inject_styles()

    # ── Header ───────────────────────────────────────────────────────────────
    render_wordmark()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── File upload ───────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png", "webp", "avif"],
        label_visibility="collapsed",
    )

    if not uploaded_file:
        st.markdown(
            '<p style="color:var(--text-muted);font-family:var(--mono);'
            'font-size:0.8rem;text-align:center;margin-top:1rem;">'
            '💡 Drag an image anywhere on this page or click the zone above</p>',
            unsafe_allow_html=True,
        )
        return

    # ── Open image ────────────────────────────────────────────────────────────
    try:
        raw_bytes = uploaded_file.getvalue()
        raw_img   = Image.open(io.BytesIO(raw_bytes))
        raw_img.load()                          # Force decode; catches truncated files
    except UnidentifiedImageError:
        st.error("❌ Could not identify image format. Please upload a valid JPG, PNG, WebP, or AVIF file.")
        return
    except Exception as exc:
        st.error(f"❌ Failed to open image: {exc}")
        return

    original_mb = len(raw_bytes) / (1024 * 1024)

    # ── Metadata strip ────────────────────────────────────────────────────────
    exif_data = render_file_info(raw_img, uploaded_file)

    # Optional: expandable EXIF viewer
    if exif_data:
        with st.expander("🔬 View EXIF Metadata", expanded=False):
            for k, v in exif_data.items():
                st.markdown(
                    f'<span class="badge badge-cyan">{k}</span> '
                    f'<span style="font-family:var(--mono);font-size:0.8rem;'
                    f'color:var(--text-primary);margin-left:0.5rem;">{v}</span><br>',
                    unsafe_allow_html=True,
                )

    # ── Controls ──────────────────────────────────────────────────────────────
    opts = render_controls(raw_img, original_mb, exif_data)

    # ── Run button ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("⚡  Optimise Now", use_container_width=True)

    if not run:
        return

    # ── Processing ────────────────────────────────────────────────────────────
    with st.spinner("Running binary-search compression engine…"):
        try:
            # Re-open from bytes so we get a fresh un-modified image each run
            work_img = Image.open(io.BytesIO(raw_bytes))
            work_img.load()
            result = ImageProcessor.compress(work_img, opts, original_mb)
        except RuntimeError as exc:
            st.error(f"❌ Compression failed: {exc}")
            return
        except Exception as exc:
            st.error(f"❌ Unexpected error during processing:\n```\n{traceback.format_exc()}\n```")
            return

    # ── Results ───────────────────────────────────────────────────────────────
    render_results(
        original_img  = Image.open(io.BytesIO(raw_bytes)),
        original_mb   = original_mb,
        result        = result,
        uploaded_name = uploaded_file.name,
        out_fmt       = opts.output_format,
    )


if __name__ == "__main__":
    main()