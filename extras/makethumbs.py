from PIL import Image
import os

def create_thumbnail(image_path):
    if '_thumb.jpeg' not in image_path:
        try:
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA, etc.)
                
                # Create thumbnail filename (e.g., image.jpg -> image_thumb.jpg)
                base, ext = os.path.splitext(image_path)
                thumb_path = f"{base}_thumb{ext}"
                basewidth = 100
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                # Save thumbnail
                img.save(thumb_path)
                print(f"Created thumbnail: {thumb_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

def process_jpegs_in_folders(root_dir):
    # Walk through all subfolders
    for root, _, files in os.walk(root_dir):
        for file in files:
            # Check for JPEG files (case-insensitive)
            if file.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                create_thumbnail(image_path)

if __name__ == "__main__":
    # Set the root directory to the current working directory
    root_directory = os.getcwd()
    print(f"Processing JPEG files in {root_directory} and its subfolders...")
    process_jpegs_in_folders(root_directory)
    print("Thumbnail creation complete!")
