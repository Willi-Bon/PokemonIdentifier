def unzip_folder(folder_path, zip_file_name, extract_to=None):
    """
    Unzips a .zip file in the given folder and deletes the .zip file afterwards.
    
    folder_path: Path to the folder containing the .zip file.
    zip_file_name: Name of the .zip file (with extension).
    extract_to: Path to extract the contents to (default: same as folder_path).
    """
    zip_path = os.path.join(folder_path, zip_file_name)  # Full path to the zip file
    
    # Default extraction path is the folder containing the zip file
    if extract_to is None:
        extract_to = folder_path
    
    # Check if the .zip file exists
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"The file {zip_file_name} was not found in {folder_path}")
    
    # Unzipping the file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Extracted {zip_file_name} to {extract_to}")
    
    try:
        os.remove(zip_path)
        print(f"Deleted the zip file: {zip_file_name}")
    except OSError as e:
        print(f"Error while deleting the zip file: {e}")


def parse_filename(filename):
    """
    Parses the filename to extract metadata.

    Args:
        filename (str): The name of the image file.

    Returns:
        pokemon_name (str): Name of Pokemon
        shiny_form (int): 1 if Pokemon is shiny, 0 if Pokemon is Normal
        gender (str): Gender of Pokemon

    """
    parts = filename.replace('.jpg', '').split(' ')  # Remove the file extension and split by spaces
    location_name = parts[0]  # Extract the location and name part
    shiny = 1 if 'Shiny' in parts else 0  # Determine if the Pokémon is shiny
    gender = 'Unknown'  # Default gender
    if 'Male & Female' in filename:
        gender = 'Male & Female'  # Check for both genders
    elif 'Male' in filename:
        gender = 'Male'  # Check for male gender
    elif 'Female' in filename:
        gender = 'Female'  # Check for female gender
    
    location, name = location_name.split('_', 1)  # Split location and name
    
    return name, shiny, gender  # Return the parsed values


def preprocess_images(filepaths, labels, batch_size):
    """
    Preprocesses images and labels for a machine learning model.

    This function creates a TensorFlow dataset from a list of image file paths and corresponding labels.
    It loads each image, resizes it with padding, normalizes pixel values, and structures the labels
    into a dictionary format suitable for model outputs.

    Args:
        filepaths (list of str): List of file paths to the images.
        labels (list of tuples): List of tuples where each tuple contains three elements:
            - name_output (int): The label for the name output.
            - shiny_output (int): The label for the shiny output.
            - gender_output (int): The label for the gender output.
        batch_size (int): The size of the batches to be generated.

    Returns:
        tf.data.Dataset: A TensorFlow dataset yielding batches of images and corresponding label dictionaries.
    """
    def generator():
        for filepath, label in zip(filepaths, labels):
            # Load the image
            image = tf.keras.utils.load_img(filepath)
            image = tf.keras.utils.img_to_array(image) / 255.0 #Normalize pixel values
            # Resize with padding
            image = tf.image.resize_with_pad(image, target_height=IMG_SIZE[0], target_width=IMG_SIZE[1])
            # Restructure labels into a dictionary for model outputs
            label_dict = {
                "name_output": label[0],
                "shiny_output": label[1],
                "gender_output": label[2]
            }
            yield image, label_dict  # Yield the image and label dictionary
    return tf.data.Dataset.from_generator(
        generator,  # Use the generator function to create the dataset
        output_signature=(
            tf.TensorSpec(shape=(*IMG_SIZE, 3), dtype=tf.float32),  # Define the shape and type of the image tensor
            {
                "name_output": tf.TensorSpec(shape=(), dtype=tf.int32),  # Define the shape and type of the name output
                "shiny_output": tf.TensorSpec(shape=(), dtype=tf.int32),  # Define the shape and type of the shiny output
                "gender_output": tf.TensorSpec(shape=(), dtype=tf.int32),  # Define the shape and type of the gender output
            },
        )
    ).batch(batch_size)  # Batch the dataset with the specified batch size

def visualize_preprocessed_images(dataset, num_images=5):
    """
    Visualizes a few random preprocessed images from the dataset.

    Args:
        dataset: A TensorFlow Dataset object containing preprocessed images and labels.
        num_images: Number of images to visualize.
    """
    plt.figure(figsize=(15, 5))
    for image_batch, label_batch in dataset.take(1):  # Take one batch from the dataset
        total_images = image_batch.shape[0]
        random_indices = random.sample(range(total_images), num_images)  # Randomly select indices
        for i, idx in enumerate(random_indices):
            plt.subplot(1, num_images, i + 1)
            plt.imshow(image_batch[idx].numpy())
            plt.axis('off')
            # Display the labels for the selected image
            label = label_batch
            name = label["name_output"][idx].numpy()
            shiny = "Shiny" if label["shiny_output"][idx].numpy() == 1 else "Normal"
            gender = unique_genders[label["gender_output"][idx].numpy()]
            plt.title(f"{unique_names[name]}\n{shiny}, {gender}")
        break  # Only process the first batch
    plt.tight_layout()
    plt.show()

def plot_training_history(history):
    """
    Plots the training and validation accuracy for different outputs and the learning rate over epochs.

    Parameters:
    history (keras.callbacks.History): A History object returned by the fit method of a Keras model. 
                                       It contains the training and validation metrics for each epoch.

    The function will plot:
    - Training and validation accuracy for 'name_output', 'shiny_output', and 'gender_output'.
    - Learning rate over epochs if 'learning_rate' is present in the history.

    Returns:
    None
    """
    # Extract history metrics
    history_dict = history.history

    # Outputs to plot
    outputs = ['name_output', 'shiny_output', 'gender_output']

    # Create a separate plot for each output
    for output in outputs:
        train_acc = history_dict[f"{output}_accuracy"]  # Training accuracy for the current output
        val_acc = history_dict[f"val_{output}_accuracy"]  # Validation accuracy for the current output

        plt.figure(figsize=(10, 6))  # Set the figure size
        plt.plot(train_acc, label=f"Train {output} Accuracy")  # Plot training accuracy
        plt.plot(val_acc, label=f"Validation {output} Accuracy")  # Plot validation accuracy
        plt.title(f"Training vs. Validation Accuracy for {output.capitalize()}")  # Set the title
        plt.xlabel("Epochs")  # Set the x-axis label
        plt.ylabel("Accuracy")  # Set the y-axis label
        plt.legend()  # Show the legend
        plt.grid(True)  # Show the grid
        plt.show()  # Display the plot

    # Plot learning rate vs. epochs if learning rate is present in the history
    if 'learning_rate' in history_dict:
        learning_rate = history_dict['learning_rate']  # Extract learning rate
        plt.figure(figsize=(10, 6))  # Set the figure size
        plt.plot(learning_rate, label="Learning Rate")  # Plot learning rate
        plt.title("Learning Rate vs. Epochs")  # Set the title
        plt.xlabel("Epochs")  # Set the x-axis label
        plt.ylabel("Learning Rate")  # Set the y-axis label
        plt.legend()  # Show the legend
        plt.grid(True)  # Show the grid
        plt.show()  # Display the plot




def predict_from_image(filepath, model, img_size, class_names, gender_labels):
    """
    Predicts the Pokémon name, shiny status, and gender from an image, and visualizes preprocessing.

    Args:
        filepath (str): Path to the image file.
        model (tf.keras.Model): Trained model for predictions.
        img_size (tuple): Image size expected by the model (height, width).
        class_names (list): List of Pokémon names corresponding to indices.
        gender_labels (list): List of gender labels corresponding to indices.

    Returns:
        dict: Prediction results containing name, shiny status, and gender.
    """
    # Load the image
    image = tf.keras.utils.load_img(filepath)
    image_array = tf.keras.utils.img_to_array(image) / 255.0  # Normalize pixel values
    
    # Resize with padding (to preserve aspect ratio)
    preprocessed_image = tf.image.resize_with_pad(image_array, img_size[0], img_size[1])
    
    # Add batch dimension
    image_batch = tf.expand_dims(preprocessed_image, axis=0)

    # Predict
    predictions = model.predict(image_batch)

    # Decode predictions
    name_idx = tf.argmax(predictions[0], axis=1).numpy()[0]  # Get the index of the predicted Pokémon name
    shiny_status = int(predictions[1][0] > 0.5)  # Determine shiny status (binary classification)
    gender_idx = tf.argmax(predictions[2], axis=1).numpy()[0]  # Get the index of the predicted gender

    # Prepare prediction results
    result = {
        "name": class_names[name_idx],
        "shiny": "Shiny" if shiny_status == 1 else "Normal",
        "gender": gender_labels[gender_idx],
    }

    # Display prediction on the image
    plt.figure(figsize=(6, 6))
    plt.imshow(preprocessed_image.numpy())
    plt.axis('off')
    plt.title(
        f"Name: {result['name']}\n"
        f"Shiny Status: {result['shiny']}\n"
        f"Gender: {result['gender']}"
    )
    plt.show()

    return result