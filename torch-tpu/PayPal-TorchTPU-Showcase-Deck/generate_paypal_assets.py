#!/usr/bin/env python3
"""
Generates custom PayPal-branded visual assets for PayPal-TorchTPU-Showcase-Deck/assets/:
- logo_paypal_header.png: PayPal double-P monogram + PayPal wordmark + AI & Accelerator Engineering badge
- logo_paypal_footer.png: PayPal footer lockup
- paypal_monogram_badge.png: PayPal double-P badge icon for dividers
- bg_paypal_cover.png: PayPal Deep Navy / Blue / Cyan / Gold geometric hero graphic for Slide 1
- bg_paypal_speaker.png: PayPal geometric wave background for Speaker & Thank You slides
- autokernel_how_it_works_static.png: Frame 5 composite still from 00-autokernel-how-it-works.gif for PPTX
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Official PayPal Brand Palette
PP_DARK_NAVY = (0, 28, 100)     # #001C64
PP_NAVY = (0, 48, 135)          # #003087
PP_BLUE = (0, 112, 186)         # #0070BA
PP_CYAN = (0, 156, 222)         # #009CDE
PP_GOLD = (255, 196, 57)        # #FFC439
PP_SLATE = (245, 247, 250)      # #F5F7FA
PP_GRAY = (108, 115, 127)       # #6C737F
WHITE = (255, 255, 255)


def load_font(size, bold=False, mono=False):
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/Supplemental/Menlo.ttc",
            "/System/Library/Fonts/Menlo.ttc",
            "/Library/Fonts/SF-Mono-Bold.otf" if bold else "/Library/Fonts/SF-Mono-Regular.otf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_paypal_monogram(draw, x, y, scale=1.0):
    """Draws the signature overlapping double-P PayPal geometric mark."""
    # Back P (Deep Navy #003087)
    w_stem = int(18 * scale)
    h_stem = int(58 * scale)
    bowl_w = int(38 * scale)
    bowl_h = int(34 * scale)
    r = int(12 * scale)

    # Back P
    draw.rounded_rectangle([x, y, x + w_stem, y + h_stem], radius=int(5 * scale), fill=PP_NAVY)
    draw.rounded_rectangle([x, y, x + bowl_w, y + bowl_h], radius=r, fill=PP_NAVY)
    draw.rounded_rectangle(
        [x + w_stem, y + int(9 * scale), x + bowl_w - int(9 * scale), y + bowl_h - int(9 * scale)],
        radius=int(5 * scale),
        fill=WHITE,
    )

    # Front P (shifted right and down, PayPal Cyan #009CDE + overlap in #0070BA)
    ox = x + int(11 * scale)
    oy = y + int(9 * scale)
    draw.rounded_rectangle([ox, oy, ox + w_stem, oy + h_stem], radius=int(5 * scale), fill=PP_CYAN)
    draw.rounded_rectangle([ox, oy, ox + bowl_w, oy + bowl_h], radius=r, fill=PP_CYAN)
    # Overlap region in PP_BLUE
    draw.rounded_rectangle(
        [ox, oy, x + bowl_w, y + bowl_h],
        radius=int(6 * scale),
        fill=PP_BLUE,
    )
    # Inner counter of Front P
    draw.rounded_rectangle(
        [ox + w_stem, oy + int(9 * scale), ox + bowl_w - int(9 * scale), oy + bowl_h - int(9 * scale)],
        radius=int(5 * scale),
        fill=WHITE,
    )


def build_header_logo():
    img = Image.new("RGBA", (680, 96), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw_paypal_monogram(draw, 12, 12, scale=1.05)

    f_brand = load_font(44, bold=True)
    f_sub = load_font(22, bold=True)

    # "Pay" in Deep Navy, "Pal" in Cyan
    draw.text((78, 18), "Pay", font=f_brand, fill=PP_NAVY)
    pay_w = draw.textlength("Pay", font=f_brand)
    draw.text((78 + pay_w, 18), "Pal", font=f_brand, fill=PP_CYAN)
    pal_w = draw.textlength("Pal", font=f_brand)

    # Divider line
    div_x = int(78 + pay_w + pal_w + 20)
    draw.line([(div_x, 20), (div_x, 72)], fill=(210, 218, 230), width=3)

    # Subtitle pill
    draw.rounded_rectangle([div_x + 18, 22, 615, 70], radius=14, fill=(235, 244, 255), outline=PP_BLUE, width=2)
    draw.text((div_x + 34, 33), "AI & Cloud TPU Engineering", font=f_sub, fill=PP_NAVY)

    img.crop((0, 0, 625, 96)).save(os.path.join(ASSETS_DIR, "logo_paypal_header.png"))


def build_footer_logo():
    img = Image.new("RGBA", (720, 44), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw_paypal_monogram(draw, 6, 4, scale=0.52)
    f_b = load_font(22, bold=True)
    f_r = load_font(18, bold=False)
    draw.text((42, 9), "Pay", font=f_b, fill=PP_NAVY)
    pw = draw.textlength("Pay", font=f_b)
    draw.text((42 + pw, 9), "Pal", font=f_b, fill=PP_CYAN)
    lw = draw.textlength("Pal", font=f_b)
    draw.text((42 + pw + lw + 14, 12), "•   Full-Stack PyTorch on Cloud TPU (torch_tpu)   •   Engineering Showcase", font=f_r, fill=PP_GRAY)
    img.save(os.path.join(ASSETS_DIR, "logo_paypal_footer.png"))


def build_monogram_badge():
    img = Image.new("RGBA", (120, 120), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 116, 116], fill=(235, 244, 255), outline=PP_BLUE, width=4)
    draw_paypal_monogram(draw, 34, 24, scale=1.0)
    img.save(os.path.join(ASSETS_DIR, "paypal_monogram_badge.png"))


def build_cover_bg():
    w, h = 960, 1080
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Deep Navy angled backdrop polygon
    draw.polygon([(140, 0), (w, 0), (w, h), (20, h)], fill=PP_DARK_NAVY)
    # PayPal Navy secondary ribbon
    draw.polygon([(210, 0), (w, 0), (w, h), (95, h)], fill=PP_NAVY)
    # PayPal Blue diagonal wave
    draw.polygon([(310, 0), (w, 0), (w, 760), (160, h)], fill=PP_BLUE)
    # PayPal Cyan accent slice
    draw.polygon([(470, 0), (w, 0), (w, 420), (260, 740)], fill=PP_CYAN)
    # Gold highlight stripe
    draw.polygon([(140, 0), (168, 0), (48, h), (20, h)], fill=PP_GOLD)

    # Architectural cards floating on the right hero panel
    f_hdr = load_font(22, bold=True)
    f_sub = load_font(20, bold=False)
    f_mono = load_font(18, bold=True, mono=True)

    cards = [
        (
            210,
            150,
            925,
            345,
            "STAGE 1 • FINTECH & SECOPS DOMAIN LoRA",
            "Qwen2.5-0.5B (PCI-DSS v4.0) & Qwen3-0.6B (SecOps)",
            "PPL: 50.31 -> 1.00  |  105.2 ms/step on tpu7x Chip 0",
            PP_GOLD,
        ),
        (
            185,
            405,
            925,
            600,
            "STAGE 2 • AUTOKERNEL PALLAS VMEM FUSION",
            "In-VMEM Fused RMSNorm + SwiGLU (73 HF Submodules)",
            "6.32x Isolated  |  5.47x 24L Norm  |  1.21x E2E Model",
            (0, 229, 255),
        ),
        (
            160,
            660,
            925,
            855,
            "STAGE 3 • SPECGUARD SGLANG PREFIX CACHE",
            "1,280-Token Shared Compliance Rubric Cached in HBM",
            "2.46x Warm TTFT (41.8 ms)  |  16-File Burst: 2.05 s",
            (105, 240, 174),
        ),
    ]

    for x1, y1, x2, y2, tag, title, metric, accent in cards:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=22, fill=(6, 26, 78, 235), outline=accent, width=3)
        draw.rounded_rectangle([x1 + 24, y1 + 22, x1 + 520, y1 + 58], radius=10, fill=(0, 72, 148))
        draw.text((x1 + 36, y1 + 29), tag, font=load_font(17, bold=True), fill=accent)
        draw.text((x1 + 24, y1 + 76), title, font=f_hdr, fill=WHITE)
        draw.text((x1 + 24, y1 + 124), metric, font=f_mono, fill=accent)

    # Bottom badge
    draw.rounded_rectangle([240, 915, 890, 995], radius=18, fill=PP_GOLD)
    draw.text((275, 940), "PayPal AI Infrastructure  •  Native torch_tpu Playbook", font=load_font(23, bold=True), fill=PP_DARK_NAVY)

    img.save(os.path.join(ASSETS_DIR, "bg_paypal_cover.png"))


def build_speaker_bg():
    w, h = 900, 1080
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([(0, 0), (760, 0), (540, h), (0, h)], fill=PP_DARK_NAVY)
    draw.polygon([(0, 0), (650, 0), (430, h), (0, h)], fill=PP_NAVY)
    draw.polygon([(0, 0), (500, 0), (280, h), (0, h)], fill=PP_BLUE)
    draw.polygon([(0, 0), (310, 0), (120, h), (0, h)], fill=PP_CYAN)
    draw.polygon([(745, 0), (770, 0), (550, h), (525, h)], fill=PP_GOLD)
    img.save(os.path.join(ASSETS_DIR, "bg_paypal_speaker.png"))


def extract_autokernel_static():
    gif_path = os.path.join(ASSETS_DIR, "00-autokernel-how-it-works.gif")
    if os.path.exists(gif_path):
        with Image.open(gif_path) as im:
            im.seek(im.n_frames - 1)
            frame = im.convert("RGB")
            frame.save(os.path.join(ASSETS_DIR, "autokernel_how_it_works_static.png"))


if __name__ == "__main__":
    build_header_logo()
    build_footer_logo()
    build_monogram_badge()
    build_cover_bg()
    build_speaker_bg()
    extract_autokernel_static()
    print("Generated all PayPal brand assets in:", ASSETS_DIR)
