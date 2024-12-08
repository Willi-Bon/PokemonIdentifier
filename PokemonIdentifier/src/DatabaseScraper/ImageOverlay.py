from PIL import Image
from tkinter.filedialog import askopenfilenames, askdirectory
import os

def overlay_images(background_path, overlay_path):  # Function to Overlay two images
    # Load the background and overlay images
    background = Image.open(background_path)
    overlay = Image.open(overlay_path)

    # Resize the background to 768x1666 (this distorts the background if necessary)
    background = background.resize((768, 1666), Image.LANCZOS).convert("RGBA")

    # Ensure the overlay image is in RGBA mode
    overlay = overlay.convert("RGBA")

    # Calculate the scaling factor to make the overlay 60% of the background width while maintaining aspect ratio
    scale_factor = 0.8 * background.width / overlay.width

    # Resize the overlay with the new scale factor
    new_size = (int(overlay.width * scale_factor), int(overlay.height * scale_factor))
    overlay_resized = overlay.resize(new_size, Image.LANCZOS)

    # Calculate the x and y positions to center the overlay horizontally
    x = (background.width - overlay_resized.width) // 2  # Center horizontally
    y = int(background.height * 0.45)  # Place at 35% of the background height

    # Create a blank canvas the size of the background and paste the resized overlay onto it
    overlay_canvas = Image.new("RGBA", background.size)
    overlay_canvas.paste(overlay_resized, (x, y), overlay_resized)

    # Composite the images together
    combined = Image.alpha_composite(background, overlay_canvas)
    return combined

folder_path = askdirectory(title="Select Folder Containing Pokemon Images")  # Path to folder containing Pokémon images
background_paths = askopenfilenames(title="Select Background Files", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])  # Paths to background images

# Process each background image
for background_path in background_paths:
    output_filename_prefix = os.path.splitext(os.path.basename(background_path))[0]  # Get the background name without extension
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            overlay_path = os.path.join(folder_path, filename)
            combined_image = overlay_images(background_path, overlay_path)
            # Create a new folder to save the combined images if it doesn't exist
            output_folder = os.path.join(folder_path, "combined_images")
            os.makedirs(output_folder, exist_ok=True)
            
            # Save the combined image as a JPEG file
            output_filename = f"{output_filename_prefix}_{os.path.splitext(filename)[0]}.jpg"
            output_path = os.path.join(output_folder, output_filename)
            combined_image.convert("RGB").save(output_path, "JPEG")
            
            # Optionally, show the combined image
            # combined_image.show()

print('Images have been combined and saved as JPG files in the folder "combined_images"')
