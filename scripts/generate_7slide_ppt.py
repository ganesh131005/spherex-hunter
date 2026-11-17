"""
Generate the 7-Slide NASA Space Apps Pitch Deck (.pptx and .html) for SPHEREx Hunter.
Slide structure requested by user:
- Slide 1: Project & Team Introduction
- Slide 2: About the Project
- Slide 3: Resources Used (Space Archives, Portals, Science & Web Tech Stack)
- Slide 4: Web UI & Architecture — Observatory Workspace & Multi-Epoch Blink Comparator (with UI screenshots)
- Slide 5: Web UI — Time-Step Controller, ZOGY Difference Imaging & Gaia Vetting (with UI screenshots)
- Slide 6: Web UI — 102-Band IR Spectroscopy, Aladin HiPS Sky & Multi-Band Light Curves (with UI screenshots)
- Slide 7: Web UI — Citizen Science Onboarding, AI Co-Pilot, Discovery Ledger & Validation (with UI screenshots)
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT_PPTX_DELIV = ROOT / "06 - Deliverables & Submission" / "SPHEREx_Hunter_NASA_Pitch_Deck.pptx"
OUT_PPTX_ROOT = ROOT / "SPHEREx_Hunter_7_Slide_Presentation.pptx"

# Color Palette (Dark Observatory Theme)
BG_DARK = RGBColor(7, 11, 20)         # #070B14
CARD_BG = RGBColor(15, 23, 42)        # #0F172A
CARD_ALT = RGBColor(23, 33, 56)       # #172138
BORDER_CLR = RGBColor(51, 65, 85)     # #334155
CYAN = RGBColor(56, 189, 248)         # #38BDF8
AMBER = RGBColor(245, 158, 11)        # #F59E0B
EMERALD = RGBColor(52, 211, 153)      # #34D399
PURPLE = RGBColor(192, 132, 252)      # #C084FC
WHITE = RGBColor(248, 250, 252)       # #F8FAFC
SLATE_LIGHT = RGBColor(203, 213, 225) # #CBD5E1
SLATE_MUTED = RGBColor(148, 163, 184) # #94A3B8


def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK


def add_header(slide, slide_num: int, category: str, title: str, subtitle: str = ""):
    # Top badge bar
    badge_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.28), Inches(12.33), Inches(0.32))
    tf = badge_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r1 = p.add_run()
    r1.text = f"SLIDE {slide_num} OF 7  •  {category.upper()}"
    r1.font.size = Pt(10.5)
    r1.font.bold = True
    r1.font.color.rgb = CYAN
    r1.font.name = "Consolas"

    r2 = p.add_run()
    r2.text = "    |    NASA SPACE APPS CHALLENGE 2026  •  TEAM RIP (SPHEREx HUNTER)"
    r2.font.size = Pt(10)
    r2.font.color.rgb = SLATE_MUTED
    r2.font.name = "Consolas"

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.56), Inches(12.33), Inches(0.55))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0
    tp = ttf.paragraphs[0]
    tr = tp.add_run()
    tr.text = title
    tr.font.size = Pt(24)
    tr.font.bold = True
    tr.font.color.rgb = WHITE
    tr.font.name = "Calibri"

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.06), Inches(12.33), Inches(0.32))
        stf = sub_box.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0
        sp = stf.paragraphs[0]
        sr = sp.add_run()
        sr.text = subtitle
        sr.font.size = Pt(13)
        sr.font.color.rgb = AMBER
        sr.font.bold = True
        sr.font.name = "Calibri"


def add_footer(slide, text_left="SPHEREx Hunter Observatory  •  github.com/joker0210G/spherex-hunter", text_right="100% Verified  |  103 Automated Tests Passing"):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(7.12), Inches(12.33), Inches(0.28))
    tf = box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r1 = p.add_run()
    r1.text = text_left
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = SLATE_MUTED
    r1.font.name = "Consolas"

    r2 = p.add_run()
    r2.text = f"          •          {text_right}"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = CYAN
    r2.font.name = "Consolas"


def add_card(slide, left, top, width, height, title, items, accent_color=CYAN, bg_color=CARD_BG, title_size=14, body_size=11.5):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.adjustments[0] = 0.04
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = BORDER_CLR
    shape.line.width = Pt(1.2)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14)
    tf.margin_bottom = Inches(0.12)

    p0 = tf.paragraphs[0]
    p0.space_after = Pt(6)
    r0 = p0.add_run()
    r0.text = title
    r0.font.size = Pt(title_size)
    r0.font.bold = True
    r0.font.color.rgb = accent_color
    r0.font.name = "Calibri"

    for item in items:
        p = tf.add_paragraph()
        p.space_after = Pt(4)
        if isinstance(item, tuple):
            lead, body = item
            rl = p.add_run()
            rl.text = f"▸ {lead}: "
            rl.font.size = Pt(body_size)
            rl.font.bold = True
            rl.font.color.rgb = WHITE
            rl.font.name = "Calibri"

            rb = p.add_run()
            rb.text = body
            rb.font.size = Pt(body_size)
            rb.font.color.rgb = SLATE_LIGHT
            rb.font.name = "Calibri"
        else:
            rb = p.add_run()
            rb.text = f"▸ {item}"
            rb.font.size = Pt(body_size)
            rb.font.color.rgb = SLATE_LIGHT
            rb.font.name = "Calibri"

    return shape


def add_image_with_caption(slide, img_path: Path, left, top, width, height, caption: str):
    # Frame behind image
    frame = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left - 0.05), Inches(top - 0.05), Inches(width + 0.10), Inches(height + 0.42)
    )
    frame.adjustments[0] = 0.02
    frame.fill.solid()
    frame.fill.fore_color.rgb = CARD_BG
    frame.line.color.rgb = CYAN
    frame.line.width = Pt(1.2)

    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(left), Inches(top), width=Inches(width), height=Inches(height))

    cap_box = slide.shapes.add_textbox(Inches(left), Inches(top + height + 0.04), Inches(width), Inches(0.30))
    ctf = cap_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0
    cp = ctf.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cr = cp.add_run()
    cr.text = caption
    cr.font.size = Pt(9.5)
    cr.font.bold = True
    cr.font.color.rgb = CYAN
    cr.font.name = "Consolas"


def build_presentation() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: PROJECT & TEAM INTRODUCTION
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_header(
        s1,
        1,
        "Project & Team Introduction",
        "SPHEREx Hunter: 102-Band Infrared Sky Observatory",
        "Interactive Time-Domain All-Sky Browser, ZOGY Difference Engine & Citizen Science Discovery Platform",
    )

    # Left: Project Overview & Mission Identity
    add_card(
        s1,
        left=0.5,
        top=1.50,
        width=5.6,
        height=2.55,
        title="🛰️ Mission Identity & Hackathon Brief",
        accent_color=CYAN,
        items=[
            ("Event", "NASA International Space Apps Challenge 2026"),
            ("Challenge", "Planet X and SPHEREx"),
            ("Team", "Team RIP — Coimbatore, Tamil Nadu, India"),
            ("Core Vision", "Replace speculative Planet X hype with mathematical truth—turning 62 MB SPHEREx infrared exposures into sub-300ms interactive discoveries."),
            ("Target Users", "Dual-mode platform built for both complete beginners (Citizen Scientists) and professional astronomers (Scientist Mode)."),
        ],
    )

    add_card(
        s1,
        left=0.5,
        top=4.20,
        width=5.6,
        height=2.70,
        title="🏆 Key Engineering Milestones Achieved",
        accent_color=AMBER,
        items=[
            ("100% Benchmark Pass", "Verified on all 5 NASA targets (WISE 0855, Barnard's Star, Epsilon Indi B, RW Aurigae, R Draconis)."),
            ("26.2-Year Baseline", "Sub-pixel TAN WCS registration across 1999 2MASS, 2010/2020 unWISE, and 2025 SPHEREx."),
            ("Scientific Honesty", "5 strict evidence tiers; 0 fabricated confidence scores; honest reporting of archival gaps."),
            ("Production Rigor", "47 OpenAPI v1 routes, 103 passing automated tests, 0 open GitHub issues."),
        ],
    )

    # Right: Team Roster Cards (5 Members)
    add_card(
        s1,
        left=6.3,
        top=1.50,
        width=6.53,
        height=5.40,
        title="👥 Team RIP — Asymmetric Engineering Roster (5 Tracks)",
        accent_color=EMERALD,
        items=[
            ("👑 jokerodu (Team Lead & System Architect — branch: main)",
             "Spec-Kit architecture, asymmetric compute/token matrix, GitHub Bridge CLI orchestrator, CI/CD verification & master branch integration."),
            ("🔭 darkodu (Astro-Data & Backend Lead — branch: darkodu/astro-backend)",
             "Contract-first FastAPI v1, Astropy SkyCoord space-motion propagation, NASA IRSA TAP/ADQL cutout engine, 144 KB precomputed demo cache, IVOA VOTable/FITS exports."),
            ("💻 coolodu (Frontend & Blink UI Lead — branch: coolodu/web-frontend)",
             "4-mode Web Observatory (Blink, Difference, Spectra, Aladin Sky), reactive Layer Tree, time-step morph controller, BYOK Google Gemini AI co-pilot, NEOSSat/WiseView bridges."),
            ("🧮 iceodu (Image Math, Science Core & AI Lead — branch: iceodu/image-math-ai)",
             "Fourier-space ZOGY optimal image subtraction (S_corr in σ), 29-bit quality bitmasking, 2D zodiacal light removal, 400-trial synthetic injection-recovery validation."),
            ("🎨 astrodu (UX, Citizen Science & Pitch Lead — branch: astrodu/ui-story-pitch)",
             "Snappy 3-step Cosmic Quick-Start onboarding, 5-tier scientific evidence badges, Citizen Science candidate ledger (SPX-2026-XXXX), and hackathon presentation."),
        ],
        body_size=11.0,
    )
    add_footer(s1)

    # =========================================================================
    # SLIDE 2: ABOUT THE PROJECT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(
        s2,
        2,
        "About The Project",
        "Why SPHEREx Hunter? Solving the Outer Solar System Problem",
        "Bridging Petabyte Infrared Space Surveys and Human-in-the-Loop Discovery",
    )

    add_card(
        s2,
        left=0.5,
        top=1.50,
        width=4.0,
        height=2.65,
        title="1. The Observational Bottleneck",
        accent_color=AMBER,
        items=[
            ("Optical Blindness (1/r⁴)", "Distant bodies (Planet X at 300–800 AU) and cold Y-dwarfs (T ≈ 250 K) reflect almost zero sunlight, rendering them invisible to Gaia & optical surveys."),
            ("Infrared Advantage (1/r²)", "NASA's SPHEREx maps the entire sky every 6 months in 102 near-IR channels (0.75–5.0 µm), capturing intrinsic thermal glow."),
            ("Data Overload", "Each Level-2 FITS exposure is 62 MB (>1B sources/epoch), filled with zodiacal light and diffraction artifacts."),
        ],
        body_size=10.8,
    )

    add_card(
        s2,
        left=4.66,
        top=1.50,
        width=4.0,
        height=2.65,
        title="2. Core Scientific Engine",
        accent_color=CYAN,
        items=[
            ("26.2-Yr Temporal Baseline", "Pairs 1999 2MASS & 2010–2020 unWISE with 2025 SPHEREx on a shared Gnomonic TAN WCS grid (RMS < 0.18\")."),
            ("ZOGY Optimal Subtraction", "Fourier-space PSF-weighted differencing: S_corr = (D - R⊗P)/√Var suppresses stationary starlight into flat 128 mid-gray."),
            ("29-Bit Flag & Zodi Veto", "Masks cosmic rays, hot pixels, and 2D zodiacal gradients—achieving 88.4% false-positive suppression."),
        ],
        body_size=10.8,
    )

    add_card(
        s2,
        left=8.83,
        top=1.50,
        width=4.0,
        height=2.65,
        title="3. 102-Band Chemical Fingerprinting",
        accent_color=EMERALD,
        items=[
            ("6 LVF Detector Arrays", "Extracts continuous Spectral Energy Distributions across Arrays A1–A6 (0.75 µm to 5.00 µm)."),
            (">4× SNR Array Co-Addition", "Stacks multi-channel exposures to boost faint moving object detectability down to 17.9 mag (AB)."),
            ("Molecular Absorption", "Pinpoints H₂O vapor (1.4 µm), H₂O ice (3.05 µm), CH₄ methane (3.30 µm), and CO₂ (4.27 µm) dips directly on the SED curve."),
        ],
        body_size=10.8,
    )

    add_card(
        s2,
        left=0.5,
        top=4.32,
        width=12.33,
        height=2.60,
        title="4. End-to-End Workflow & 100% Validated NASA Benchmark Suite",
        accent_color=PURPLE,
        items=[
            ("Sub-300ms Streaming Architecture", "Precomputed 128×128 Float32 binary cutouts with SHA-256 manifest verification deliver instant 60 FPS WebGL/Canvas rendering without 62 MB FITS downloads."),
            ("5-Tier Scientific Evidence Classification", "Every source is vetted into (1) Known Solar System Object, (2) Confirmed Stellar/Brown Dwarf, (3) Unknown Mover, (4) Slow IR-Excess Candidate (No Optical Gaia Match), or (5) Likely Artifact."),
            ("100% Verified Across All 5 Official NASA Benchmarks",
             "• WISE 0855-0714 (250 K Y-Dwarf, 8.15\"/yr shift, 24.85σ dipole, Gaia optical dropout)   • Barnard's Star (10.36\"/yr proper motion standard)   • Epsilon Indi B (4.70\"/yr binary brown dwarf)   • RW Aurigae (2.8× eruptive flare light curve)   • R Draconis (3.4× Mira pulsating giant with Lomb-Scargle periodogram)."),
        ],
        body_size=11.0,
    )
    add_footer(s2)

    # =========================================================================
    # SLIDE 3: RESOURCES USED
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(
        s3,
        3,
        "Resources & Tech Stack Used",
        "Space Agency Data Archives, Scientific Libraries & Web Stack",
        "Built on Authentic NASA, Caltech/IPAC, ESA, CSA & IVOA Open Science Standards",
    )

    add_card(
        s3,
        left=0.5,
        top=1.50,
        width=6.05,
        height=2.65,
        title="🛰️ Primary NASA & IRSA Infrared Archives",
        accent_color=CYAN,
        items=[
            ("NASA/IPAC IRSA SPHEREx Archive", "QR1/DR1 Multi-Extension FITS spectral images, TAP ADQL geometric queries (spherex.artifact & spherex.plane), and AWS s3://nasa-irsa-spherex public buckets."),
            ("Caltech-IPAC SPHEREx Notebooks", "Official Python workflows for spectral cutouts, wavelength-dependent 2D ePSF reconstruction, multi-band mosaics, and HiPS spectral cubes."),
            ("2MASS & unWISE / WiseView", "1999 2MASS All-Sky Survey (J, H, Ks) + 2010–2020 WISE/unWISE time-resolved co-adds (W1 3.4 µm, W2 4.6 µm) & Dan Caselden's WiseView comparator."),
        ],
        body_size=10.8,
    )

    add_card(
        s3,
        left=6.78,
        top=1.50,
        width=6.05,
        height=2.65,
        title="🌍 International Partner Catalogs & Orbital Databases",
        accent_color=AMBER,
        items=[
            ("ESA / STScI MAST Gaia DR3", "1.8-billion star astrometric catalog used for real-time proper motion vectors (μα cos δ, μδ), parallax distances, and optical dropout vetting."),
            ("Canadian Space Agency (CSA) NEOSSat & CADC", "Near-Earth Object Surveillance Satellite FITS archive queried via Canadian Astronomy Data Centre (CAOM-2 TAP & astroquery.cadc) for asteroid/debris tracking."),
            ("CDS SIMBAD, IMCCE SkyBoT & JPL Horizons", "Automated solar system minor-planet ephemeris cross-matching and stellar taxonomy verification."),
        ],
        body_size=10.8,
    )

    add_card(
        s3,
        left=0.5,
        top=4.32,
        width=6.05,
        height=2.60,
        title="🐍 Backend, Science Core & Data Standards",
        accent_color=EMERALD,
        items=[
            ("FastAPI v1 & Uvicorn", "47 contract-first REST endpoints with RFC 7807 Problem Details and SHA-256 cached binary ArrayBuffer streaming."),
            ("Astropy, Astroquery & Reproject", "ICRS SkyCoord space-motion propagation, TAN WCS projection, forced aperture photometry, and ePSF centroiding."),
            ("NumPy & SciPy Math Engine", "2D FFT ZOGY optimal subtraction, MAD background estimation, arcsinh dynamic range stretch, and Lomb-Scargle periodograms."),
            ("IVOA Interoperability", "Native exports to IVOA VOTable XML, Astropy binary FITS tables, and CSV."),
        ],
        body_size=10.8,
    )

    add_card(
        s3,
        left=6.78,
        top=4.32,
        width=6.05,
        height=2.60,
        title="💻 Frontend UI, Visualization & QA Tooling",
        accent_color=PURPLE,
        items=[
            ("HTML5 2D/WebGL Canvas & Aladin Lite v3", "Hardware-accelerated multi-tile FITS mosaic renderer + CDS Strasbourg Aladin Lite v3 HiPS all-sky survey viewer."),
            ("Tailwind CSS, Chart.js & Lucide/FA Icons", "WCAG 2.2 AA dark observatory UI (#070a11), interactive 102-band SED curve with 10× zoom/pan, and multi-band light curves."),
            ("Google Gemini AI (BYOK)", "Client-configurable Gemini API integration for grounded spectral & target analysis."),
            ("Pytest, Playwright & Ruff CI", "103 automated unit/contract/E2E tests & synthetic injection-recovery suite."),
        ],
        body_size=10.8,
    )
    add_footer(s3)

    # =========================================================================
    # SLIDE 4: WEB UI — OBSERVATORY WORKSPACE & BLINK COMPARATOR
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(
        s4,
        4,
        "Web Application & User Interface (1/4)",
        "Main Observatory Workspace & Multi-Epoch Blink Comparator",
        "4-Zone Mission Control Layout Engineered for Instant Motion Detection Across 26.2 Years",
    )

    add_card(
        s4,
        left=0.5,
        top=1.50,
        width=4.65,
        height=5.40,
        title="🖥️ Main Web Observatory UI Highlights",
        accent_color=CYAN,
        items=[
            ("Top Command Bar", "Instant mode switcher (Blink [B], Difference [D], Spectra [S], Aladin Sky [A]), Ctrl+K command palette, 1-click NASA benchmark presets, and validated RA/Dec/FOV coordinate popover."),
            ("Left Tool Rail", "High-contrast celestial SVG reticle, Pan, Angular Distance ruler, Quick Flip, Gaia DR3 vector toggle [G], Recenter [R], 1:1 pixel zoom, and 6DOF WASD Walk navigation."),
            ("Digital Blink Comparator", "Flips rapidly (0.5–10 FPS) between 1999 2MASS, 2010/2020 unWISE, and 2025 SPHEREx. Stationary stars stay fixed while moving brown dwarfs jump across the canvas."),
            ("Space-Motion Centering", "Automatically propagates fast movers (e.g., WISE 0855 at 8.15\"/yr → Δθ = 207.1\") via Astropy SkyCoord so targets never exit the field of view."),
            ("Right Scene Inspector", "Live Scene Collection tree with 4 tabs (Layers, Target, Candidates, Photometry), real-time opacity sliders, and literature citations."),
        ],
        body_size=10.5,
    )

    add_image_with_caption(
        s4,
        ROOT / "after_screenshot.png",
        left=5.35,
        top=1.55,
        width=7.40,
        height=4.85,
        caption="Live Web UI: SPHEREx Hunter Blink Comparator on WISE 0855-0714 (26.2-Year Baseline & Scene Inspector)",
    )
    add_footer(s4)

    # =========================================================================
    # SLIDE 5: WEB UI — TIME-STEP CONTROLLER, ZOGY DIFFERENCE & GAIA VETTING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(
        s5,
        5,
        "Web Application & User Interface (2/4)",
        "Time-Step Morphing, ZOGY Difference UI & Gaia DR3 Vetting",
        "Interactive Temporal Blending, Sub-Pixel Astrometric HUD & Optical Dropout Identification",
    )

    add_card(
        s5,
        left=0.5,
        top=1.50,
        width=4.65,
        height=5.40,
        title="⚡ Interactive Viewport & Difference Controls",
        accent_color=AMBER,
        items=[
            ("Time-Step Controller HUD", "Floating/pinnable HUD with continuous epoch blend slider (0–100% alpha morphing between 1999 t₁ and 2025 t₂) plus 1-click ZOGY Diff (Δ) toggle."),
            ("ZOGY Dipole Visualization", "Renders arcsinh-stretched Fourier significance maps around neutral 128 mid-gray—highlighting WISE 0855 as a 24.85σ dipole pair."),
            ("Gaia DR3 Optical Dropout Alert", "Overlays cyan Gaia star reticles (G 13.3–G 17.9) and triggers an amber banner: 'Slow IR-Excess Candidate (No Optical Gaia DR3 Match)' for cold IR-only sources."),
            ("Continuous Multi-Tile Mosaic", "Dynamic frustum LOD streaming (LOD 2 wide 360p overview → LOD 1 720p HD master FITS tiles at 0.18\"/dev_px) with interactive zoom slider."),
            ("Live Astrometric Telemetry", "Bottom HUD displays ICRS RA/Dec, FOV, zoom scale, compass rose, and verified Astrometric RMS: 0.12\" (0.02 native px)."),
        ],
        body_size=10.5,
    )

    add_image_with_caption(
        s5,
        ROOT / "docs" / "figures" / "continuous_viewport_blended.png",
        left=5.35,
        top=1.55,
        width=3.62,
        height=2.65,
        caption="Time-Step Controller & Epoch Morph HUD",
    )
    add_image_with_caption(
        s5,
        ROOT / "docs" / "figures" / "viewport_rectified_04x.png",
        left=9.13,
        top=1.55,
        width=3.62,
        height=2.65,
        caption="Multi-Tile FITS Mosaic & Gaia DR3 Overlays",
    )
    add_image_with_caption(
        s5,
        ROOT / "docs" / "figures" / "coords_popover_validation.png",
        left=5.35,
        top=4.72,
        width=3.62,
        height=1.75,
        caption="Real-Time Coordinate & Sky Scale Validator",
    )
    add_card(
        s5,
        left=9.08,
        top=4.67,
        width=3.72,
        height=2.22,
        title="🎯 Viewport Precision Metrics",
        accent_color=EMERALD,
        items=[
            ("Astrometric RMS", "0.12\" (0.02 native pixels)"),
            ("ZOGY Peak SNR", "24.85σ on WISE 0855-0714"),
            ("Stretch Modes", "Gray, Invert & Thermal LUTs"),
            ("Tile Streaming", "Multi-res spatial frustum cache"),
        ],
        title_size=12.5,
        body_size=10.2,
    )
    add_footer(s5)

    # =========================================================================
    # SLIDE 6: WEB UI — 102-BAND SPECTRA, ALADIN HIPS SKY & LIGHT CURVES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(
        s6,
        6,
        "Web Application & User Interface (3/4)",
        "102-Band Spectral Inspector, Aladin HiPS Sky & Light Curves",
        "Full 0.75–5.00 µm Spectrophotometry, All-Sky HiPS Context & Multi-Band Variability Analysis",
    )

    add_card(
        s6,
        left=0.5,
        top=1.50,
        width=4.65,
        height=5.40,
        title="🌈 Spectral & All-Sky Navigation Interfaces",
        accent_color=EMERALD,
        items=[
            ("SPHEREx DR1 HiPS Sky Map", "Integrates CDS Aladin Lite with scale presets (180° All-Sky, 30°, 5°, 0.1° HD), real 2MASS/DSS2 base surveys, and 5 benchmark target pins."),
            ("102-Channel Wavelength Selector", "Interactive top overlay stepping across all 102 SPHEREx channels (Ch 1: 0.753 µm Band 1 → Ch 102: 5.00 µm Band 6)."),
            ("Curve-Pinned Molecular Markers", "Bottom 102-Band Spectrum dock plots flux (µJy) with diamond markers pinned to H₂O (1.4/1.9/3.05 µm), CH₄ (3.3 µm), CO₂ (4.3 µm), and CO (4.7 µm)."),
            ("Segregated Multi-Band Light Curves", "Plots 2MASS Ks, WISE W1/W2, and SPHEREx epochs separately with upper-limit arrows and Lomb-Scargle periodograms (RW Aur 2.8×, R Dra 3.4×)."),
            ("Scientific Honesty Notices", "Warns users when multi-array spectra come from non-simultaneous dates for variable stars."),
        ],
        body_size=10.5,
    )

    add_image_with_caption(
        s6,
        ROOT / "docs" / "figures" / "google_maps_spherex_01_hd_stars.png",
        left=5.35,
        top=1.55,
        width=7.40,
        height=2.30,
        caption="Aladin Sky Mode: SPHEREx DR1 102-Channel Selector (0.75–5.0 µm) & Multi-Scale Navigation HUD",
    )
    add_image_with_caption(
        s6,
        ROOT / "docs" / "figures" / "spectrum_honesty_notice.png",
        left=5.35,
        top=4.35,
        width=7.40,
        height=2.15,
        caption="Spectra Mode UI: Bottom 102-Band Spectrum Dock, Molecular Absorption Legend & Honesty Banner",
    )
    add_footer(s6)

    # =========================================================================
    # SLIDE 7: WEB UI — CITIZEN SCIENCE, AI CO-PILOT & VALIDATION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(
        s7,
        7,
        "Web Application & User Interface (4/4)",
        "Citizen Science Tour, Gemini AI Co-Pilot & Empirical Validation",
        "Democratizing Deep-Space Discovery with Guided Onboarding, Standardized Flagging & Proven Depth",
    )

    add_card(
        s7,
        left=0.5,
        top=1.50,
        width=4.65,
        height=5.40,
        title="🚀 Citizen Science UX, AI & Validation Proof",
        accent_color=PURPLE,
        items=[
            ("3-Step Cosmic Quick-Start Tour", "Visual onboarding modal explaining (1) The Infrared Secret, (2) Blink to Spot Movement, and (3) Discovery Ledger, with a '🚀 Quick Start (15s)' button."),
            ("Dual-Mode Toggle & Gemini AI", "1-click Beginner vs Scientist Mode switch, plus BYOK Google Gemini AI modal for grounded spectral & astrometric interpretation."),
            ("Candidate Flagging & Export", "Logs discoveries with unique IDs (SPX-2026-XXXX), CSA NEOSSat / WiseView verification links, and 1-click CSV, IVOA VOTable & FITS exports."),
            ("400-Trial Empirical Validation", "Real flight-exposure injection-recovery proves 17.9 mag (AB) 50% completeness limit (matching 18.06 mag 5σ theory) and 88.4% artifact veto efficiency."),
            ("Shareable Permalinks", "Every coordinate, mode, and frame syncs to the URL hash (#target=wise0855&mode=blink) for instant peer review."),
        ],
        body_size=10.5,
    )

    add_image_with_caption(
        s7,
        ROOT / "docs" / "figures" / "onboarding_step1_mission.png",
        left=5.35,
        top=1.55,
        width=3.62,
        height=2.25,
        caption="Onboarding Step 1: Optical vs SPHEREx IR",
    )
    add_image_with_caption(
        s7,
        ROOT / "docs" / "figures" / "onboarding_step3_discoveries.png",
        left=9.13,
        top=1.55,
        width=3.62,
        height=2.25,
        caption="Onboarding Step 3: Discovery Ledger & 15s Launch",
    )
    add_image_with_caption(
        s7,
        ROOT / "docs" / "figures" / "completeness_vs_mag.png",
        left=5.35,
        top=4.30,
        width=3.62,
        height=2.20,
        caption="Empirical Validation: 400-Injection Recovery Curve",
    )
    add_image_with_caption(
        s7,
        ROOT / "docs" / "figures" / "detectability_map.png",
        left=9.13,
        top=4.30,
        width=3.62,
        height=2.20,
        caption="Thermal + Reflected Flux Detectability at 4.5 µm",
    )
    add_footer(s7)

    return prs


if __name__ == "__main__":
    prs = build_presentation()
    OUT_PPTX_DELIV.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT_PPTX_DELIV))
    prs.save(str(OUT_PPTX_ROOT))
    print(f"Saved PPTX to:\n  - {OUT_PPTX_DELIV}\n  - {OUT_PPTX_ROOT}")
