from PIL import Image
import os
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog

def overlay_images(background_path, overlay_path):
    """
    Overlays two images with the overlay image resized and centered on the background image.

    Args:
        background_path (str): The file path to the background image.
        overlay_path (str): The file path to the overlay image.

    Returns:
        Image: The resulting image with the overlay applied.
    """
    # Load the background and overlay images
    background = Image.open(background_path)
    overlay = Image.open(overlay_path)

    # Ensure the images are in RGBA mode
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    # Calculate the scaling factor to make the overlay 60% of the background size, maintaining aspect ratio
    scale_factor = min(background.width / overlay.width, background.height / overlay.height) * 0.7

    # Resize the overlay with the new scale factor
    new_size = (int(overlay.width * scale_factor), int(overlay.height * scale_factor))
    overlay_resized = overlay.resize(new_size, Image.LANCZOS)

    # Calculate the x and y positions
    x = (background.width - overlay_resized.width) // 2  # Center horizontally
    y = int(background.height * 0.35)  # Sets Pokemon to about bottom of background

    # Create a blank canvas the size of the background and paste the resized overlay onto it
    overlay_canvas = Image.new("RGBA", background.size)
    overlay_canvas.paste(overlay_resized, (x, y), overlay_resized)

    return overlay_canvas

if __name__ == "__main__":
    # Code that should not run during Sphinx documentation build
    folder_path = filedialog.askdirectory(title="Select Folder Containing Pokemon Images")  # Path to folder containing pokemon images
    background_path = filedialog.askopenfilename(title="Select Background File", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])  # Path to background image
    # Create a simple GUI to accept a string
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    output_filename = simpledialog.askstring("Input", "Enter the output filename prefix:")

    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            overlay_path = os.path.join(folder_path, filename)
            combined_image = overlay_images(background_path, overlay_path)
            # Create a new folder to save the combined images if it doesn't exist
            output_folder = os.path.join(folder_path, "combined_images")
            os.makedirs(output_folder, exist_ok=True)
            
            # Save the combined image to the new folder
            output_path = os.path.join(output_folder, f"{output_filename}_{filename}")
            combined_image.save(output_path)
            
            # Optionally, show the combined image
            #combined_image.show()