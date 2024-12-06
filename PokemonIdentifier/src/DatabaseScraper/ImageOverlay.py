from PIL import Image
from tkinter.filedialog import askopenfilename, askdirectory
import os
import tkinter as tk
from tkinter import simpledialog

def overlay_images(background_path, overlay_path): #Function to Overlay two images
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

    # Composite the images together
    combined = Image.alpha_composite(background, overlay_canvas)
    return combined

folder_path = askdirectory(title="Select Folder Containing Pokemon Images") #Path to folder containing pokemon images
background_path = askopenfilename(title="Select Background File", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]) #Path to background image
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

print('Images have been combined and saved to the folder "combined_images"')