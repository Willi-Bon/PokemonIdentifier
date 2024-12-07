import os
from tkinter import Tk, filedialog
from PIL import Image

def convert_png_to_jpg(input_folder):
    """
    Converts all PNG files in the input folder to JPG format
    and saves them in a subfolder named 'output'.

    Args:
        input_folder (str): Path to the folder containing PNG files.
    """
    # Define the output folder
    output_folder = os.path.join(input_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Get a list of all PNG files in the input folder
    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]

    if not png_files:
        print("No PNG files found in the selected folder.")
        return

    for file_name in png_files:
        try:
            # Open the PNG file
            file_path = os.path.join(input_folder, file_name)
            img = Image.open(file_path).convert("RGB")

            # Generate the new file name and save it as JPG
            new_file_name = os.path.splitext(file_name)[0] + ".jpg"
            output_path = os.path.join(output_folder, new_file_name)
            img.save(output_path, "JPEG")

            #print(f"Converted: {file_name} -> {new_file_name}")
        except Exception as e:
            print(f"Failed to convert {file_name}: {e}")

    print(f"Conversion process completed. JPG files are saved in '{output_folder}'.")

if __name__ == "__main__":
    # Create a file dialog to select the input folder
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    input_folder = filedialog.askdirectory(title="Select Folder Containing PNG Files")

    if input_folder:
        convert_png_to_jpg(input_folder)
    else:
        print("No folder selected. Exiting.")
