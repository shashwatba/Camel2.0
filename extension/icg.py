#!/usr/bin/env python3
"""
Simple script to generate icon placeholders for the Chrome extension.
Run this script in the extension directory to create icon files.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the specified size."""
    # Create a new image with a gradient background
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient background
    for i in range(size):
        color_value = int(255 * (i / size))
        color = (102, 126, 234)  # Blue gradient
        draw.rectangle([(0, i), (size, i+1)], fill=color)
    
    # Draw a circle in the center
    margin = size // 4
    draw.ellipse(
        [(margin, margin), (size-margin, size-margin)],
        fill='white',
        outline=None
    )
    
    # Draw text in the center
    text = "L"
    try:
        # Try to use a nice font
        font = ImageFont.truetype("Arial.ttf", size//2)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size//10
    
    # Draw the text
    draw.text((x, y), text, font=font, fill=(102, 126, 234))
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename}")

# Create icons in different sizes
sizes = {
    'icon-16.png': 16,
    'icon-48.png': 48,
    'icon-128.png': 128
}

for filename, size in sizes.items():
    create_icon(size, filename)

print("\nIcons created successfully!")
print("\nNote: If you don't have PIL/Pillow installed, you can:")
print("1. Install it with: pip install Pillow")
print("2. Or create simple colored square PNG files manually")
print("3. Or use any image editor to create 16x16, 48x48, and 128x128 pixel icons")