#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

def create_title_png(text, output_path, font_path=None, font_size=100, text_color="white"):
    """
    Create a Full HD (1920x1080) PNG image with centered text and transparent background.
    
    Parameters:
    text (str): Text to display on the image
    output_path (str): Path to save the PNG file
    font_path (str): Path to TTF font file (optional, uses default if None)
    font_size (int): Font size for the text
    text_color (str): Color of the text (e.g., "white", "#FFFFFF")
    """
    try:
        # Create a new Full HD image with transparent background (RGBA mode)
        image = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))  # Fully transparent background
        draw = ImageDraw.Draw(image)
        
        # Load font (use default PIL font if none provided)
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
            # Scale default font size (Pillow's default is small)
            if font_size != 100:
                print("Warning: Custom font size ignored when using default font")
        
        # Get text size to center it (use textsize for older Pillow versions)
        text_width, text_height = draw.textsize(text, font=font)
        
        # Calculate centered position
        text_x = (1920 - text_width) // 2
        text_y = (1080 - text_height) // 2
        
        # Draw the text
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        # Save the image as PNG to preserve transparency
        image.save(output_path, 'PNG')
        print(f"Transparent title image saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    title_text = "GONZO PI IS AWESOME"
    output_file = "title001.png"
    
    # Optional: Specify a TTF font file (e.g., Arial, downloaded TTF, etc.)
    # font_path = "path/to/your/font.ttf"  # Uncomment and set path if you have a TTF font
    font_path = None  # Use default font if None
    
    create_title_png(
        text=title_text,
        output_path=output_file,
        font_path='roberta.ttf',
        font_size=100,
        text_color="white"
    )
