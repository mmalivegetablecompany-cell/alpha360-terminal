"""
Institutional App Icon Generator for Alpha360 Terminal
Generates high-resolution multi-platform launcher icons for Android, Windows, and Web.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')

def create_master_icon(size=1024):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Outer rounded squircle background
    padding = 40
    sq_rect = [padding, padding, size - padding, size - padding]
    corner_radius = 210

    # Gradient background simulation via layered concentric shapes
    for i in range(16):
        shrink = i * 2
        alpha = int(255 - i * 4)
        c = (
            int(7 + i * 0.8),
            int(11 + i * 1.5),
            int(25 + i * 2.8),
            alpha
        )
        draw.rounded_rectangle(
            [padding + shrink, padding + shrink, size - padding - shrink, size - padding - shrink],
            radius=max(10, corner_radius - shrink),
            fill=c
        )

    # 2. Glowing Neon Border
    draw.rounded_rectangle(
        sq_rect,
        radius=corner_radius,
        outline=(0, 176, 255, 230), # Electric Cyan
        width=12
    )

    # Secondary inner highlight border
    draw.rounded_rectangle(
        [padding + 8, padding + 8, size - padding - 8, size - padding - 8],
        radius=corner_radius - 8,
        outline=(0, 230, 118, 120), # Neon Emerald Glow
        width=4
    )

    # 3. Candlestick Bars
    # Bar 1 (Left): (x: 240 to 330)
    # Wick:
    draw.line([(285, 420), (285, 780)], fill=(0, 230, 118, 180), width=8)
    # Body:
    draw.rounded_rectangle([245, 520, 325, 730], radius=16, fill=(0, 230, 118, 240), outline=(0, 255, 130, 255), width=4)

    # Bar 2 (Center): (x: 467 to 557)
    # Wick:
    draw.line([(512, 280), (512, 750)], fill=(0, 176, 255, 200), width=8)
    # Body:
    draw.rounded_rectangle([472, 380, 552, 690], radius=16, fill=(0, 176, 255, 240), outline=(80, 210, 255, 255), width=4)

    # Bar 3 (Right): (x: 694 to 784)
    # Wick:
    draw.line([(739, 180), (739, 680)], fill=(0, 230, 118, 220), width=8)
    # Body:
    draw.rounded_rectangle([699, 240, 779, 580], radius=16, fill=(0, 230, 118, 255), outline=(100, 255, 170, 255), width=4)

    # 4. Dynamic Surging Momentum Chevron / Trend Arc
    trend_points = [
        (190, 750),
        (370, 620),
        (560, 430),
        (790, 210),
        (860, 150),
    ]

    # Glowing trend line shadow
    for offset in range(8, 0, -2):
        draw.line(trend_points, fill=(255, 179, 0, int(35 * (10 - offset))), width=16 + offset * 4)

    # Solid golden-cyan trend arrow
    draw.line(trend_points, fill=(255, 185, 0, 255), width=18)

    # Arrow Head
    arrow_head = [
        (860, 150),
        (780, 150),
        (830, 200),
        (860, 150),
    ]
    draw.polygon(arrow_head, fill=(255, 200, 0, 255))

    # Glowing target node star at the apex
    draw.ellipse([835, 125, 885, 175], fill=(255, 255, 255, 255), outline=(255, 185, 0, 255), width=6)

    # 5. High-Tech Branding Text: "ALPHA 360°"
    # Draw geometric emblem badge at the bottom
    draw.rounded_rectangle([320, 810, 704, 885], radius=22, fill=(13, 23, 44, 230), outline=(0, 176, 255, 180), width=4)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 46)
        draw.text((512, 847), "ALPHA 360°", fill=(255, 255, 255), font=font, anchor="mm")
    except Exception:
        # Fallback text draw
        draw.text((375, 830), "ALPHA 360", fill=(255, 255, 255))

    return img

def export_all_icons():
    print("Generating master 1024x1024 icon...")
    master = create_master_icon(1024)

    # Save master in assets
    os.makedirs('flutter_app/assets/icons', exist_ok=True)
    master.save('flutter_app/assets/icons/alpha360_master.png', 'PNG')
    print("Saved master icon: flutter_app/assets/icons/alpha360_master.png")

    # Android mipmap targets
    android_targets = {
        'flutter_app/android/app/src/main/res/mipmap-mdpi/ic_launcher.png': 48,
        'flutter_app/android/app/src/main/res/mipmap-hdpi/ic_launcher.png': 72,
        'flutter_app/android/app/src/main/res/mipmap-xhdpi/ic_launcher.png': 96,
        'flutter_app/android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png': 144,
        'flutter_app/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png': 192,
    }

    for path, sz in android_targets.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized = master.resize((sz, sz), Image.Resampling.LANCZOS)
        resized.save(path, 'PNG')
        print(f"✅ Generated Android icon: {path} ({sz}x{sz})")

    # Windows multi-resolution .ico
    ico_path = 'flutter_app/windows/runner/resources/app_icon.ico'
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    master.save(ico_path, format='ICO', sizes=ico_sizes)
    print(f"✅ Generated Windows Multi-Resolution ICO: {ico_path}")

    # Web icons
    web_targets = {
        'flutter_app/web/favicon.png': 32,
        'flutter_app/web/icons/Icon-192.png': 192,
        'flutter_app/web/icons/Icon-512.png': 512,
    }
    for path, sz in web_targets.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized = master.resize((sz, sz), Image.Resampling.LANCZOS)
        resized.save(path, 'PNG')
        print(f"✅ Generated Web icon: {path} ({sz}x{sz})")

    print("🎉 All platform icons successfully generated!")

if __name__ == '__main__':
    export_all_icons()
