import os
# from PIL import Image # This line should be removed or commented if not used
from PIL import Image, ImageOps
import numpy as np
import torch
from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
# from comfy.utils import load_image # This will be replaced
import folder_paths  # For robust path management
import shutil  # For file copying

# ==> Define your custom subfolder name here <==
CUSTOM_SUBFOLDER_NAME = "custom" 
# <=============================================>

# Renaming class for clarity and to reflect its fixed path and upload capability
class LoadImageFixedCustom:
    # Define FIXED_FOLDER_PATH relative to ComfyUI's main input directory
    # This makes it more robust than a simple relative path.
    BASE_INPUT_PATH = folder_paths.get_input_directory()
    # Use the constant for the subfolder name
    FIXED_FOLDER_PATH = os.path.join(BASE_INPUT_PATH, CUSTOM_SUBFOLDER_NAME)

    @classmethod
    def INPUT_TYPES(cls):
        # Ensure the fixed custom directory exists
        if not os.path.isdir(cls.FIXED_FOLDER_PATH):
            os.makedirs(cls.FIXED_FOLDER_PATH, exist_ok=True)
            print(f"[LoadImageFixedCustom] Created directory: {cls.FIXED_FOLDER_PATH}")

        # Populate dropdown from FIXED_FOLDER_PATH
        current_image_files = [f"<No images in ./{CUSTOM_SUBFOLDER_NAME}>"] # Updated placeholder
        try:
            # Call the generator to get current files (generator itself ensures dir exists)
            generated_inputs = cls.INPUT_TYPES_GENERATOR({}) 
            if ("image_file" in generated_inputs and
                isinstance(generated_inputs["image_file"], tuple) and
                len(generated_inputs["image_file"]) > 0 and
                isinstance(generated_inputs["image_file"][0], list)):
                dropdown_files = generated_inputs["image_file"][0]
                # Check against more specific placeholder messages from the generator
                if dropdown_files and dropdown_files != ["<no images found>"] and dropdown_files != ["<invalid path or error>"] and dropdown_files != [f"<Default folder '{CUSTOM_SUBFOLDER_NAME}' created, add images>"]:
                    current_image_files = dropdown_files
        except Exception as e:
            print(f"[LoadImageFixedCustom] Error populating dropdown in INPUT_TYPES: {e}")
            current_image_files = ["<Error loading files. Check console.>"]
        
        return {
            "required": {
                "image_file": (current_image_files, ),
                # This widget tells ComfyUI to show an upload button.
                # The value of 'upload_image' will be the filename of the uploaded image
                # as ComfyUI placed it in its *main* input directory.
                "upload_image": ("IMAGEUPLOAD", ) 
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_image_with_upload_priority" # Renamed function
    CATEGORY = "image/load" # Or a custom category like "image/custom_load"

    def load_image_with_upload_priority(self, image_file, upload_image):
        # upload_image is the filename (e.g., "example.png") if a file was just uploaded
        # via the widget. Otherwise, it might be None or not a string.
        
        final_image_name_in_custom_folder = None
        image_source_info = "dropdown"

        if upload_image and isinstance(upload_image, str) and upload_image != 'None':
            # A file was uploaded via the widget.
            # Source path is in ComfyUI's main input directory.
            source_path = os.path.join(self.BASE_INPUT_PATH, upload_image)
            # Destination path is in our fixed custom folder.
            destination_path = os.path.join(self.FIXED_FOLDER_PATH, upload_image)

            try:
                if os.path.isfile(source_path):
                    # Ensure destination directory exists (should have been by INPUT_TYPES, but double check)
                    if not os.path.isdir(self.FIXED_FOLDER_PATH):
                        os.makedirs(self.FIXED_FOLDER_PATH, exist_ok=True)
                    
                    shutil.copy2(source_path, destination_path)
                    print(f"[LoadImageFixedCustom] Copied uploaded file '{upload_image}' to '{destination_path}'")
                    final_image_name_in_custom_folder = upload_image
                    image_source_info = f"newly uploaded file '{upload_image}' copied to custom folder"
                    # Consider if the original uploaded file in BASE_INPUT_PATH should be deleted.
                    # For now, we'll leave it. Some nodes might expect it if IMAGEUPLOAD has side effects.
                else:
                    # This case might happen if the IS_CHANGED logic isn't perfect and an old upload_image value persists
                    print(f"[LoadImageFixedCustom] Uploaded file '{upload_image}' not found at source '{source_path}'. It might be a stale value or already moved.")
                    # Attempt to use it directly if it exists in custom folder (already processed)
                    if os.path.isfile(os.path.join(self.FIXED_FOLDER_PATH, upload_image)):
                        final_image_name_in_custom_folder = upload_image
                        image_source_info = f"stale upload value '{upload_image}', but found in custom folder"
                    # else, will fall through to dropdown logic

            except Exception as e:
                print(f"[LoadImageFixedCustom] Error processing uploaded file '{upload_image}': {e}")
                # Fall through to dropdown logic or raise if critical
                pass # Let dropdown logic try

        if not final_image_name_in_custom_folder:
            if image_file and not image_file.startswith("<"): # Check for placeholder
                final_image_name_in_custom_folder = image_file
                image_source_info = f"dropdown selection '{image_file}'"
            else:
                # No valid upload, no valid dropdown. Try to pick first available if any.
                try:
                    generated_inputs = self.INPUT_TYPES_GENERATOR({})
                    available_files = generated_inputs["image_file"][0]
                    if available_files and not available_files[0].startswith("<"):
                        final_image_name_in_custom_folder = available_files[0]
                        image_source_info = f"fallback to first available image '{final_image_name_in_custom_folder}'"
                        print(f"[LoadImageFixedCustom] No selection, defaulting to first image: {final_image_name_in_custom_folder}")
                    else:
                         raise Exception("No image selected, no image uploaded, and no images available in the custom folder.")
                except Exception as e_fallback:
                     raise Exception(f"No image selected or uploaded. Fallback error: {e_fallback}")


        if not final_image_name_in_custom_folder:
            raise Exception("Could not determine a valid image to load. Upload an image or select one from the dropdown if available.")

        actual_image_path = os.path.join(self.FIXED_FOLDER_PATH, final_image_name_in_custom_folder)
        
        print(f"[LoadImageFixedCustom] Attempting to load: '{actual_image_path}' (Source: {image_source_info})")

        if not os.path.isfile(actual_image_path):
            # This can happen if file was deleted after list generation, or an error in logic.
            # Triggering a refresh via IS_CHANGED might be good here if possible.
            raise Exception(f"Image file not found at expected path: {actual_image_path}. The image list might be outdated. Please try uploading again or refreshing the UI if the file exists.")

        pil_image = Image.open(actual_image_path)
        pil_image = ImageOps.exif_transpose(pil_image) # Apply EXIF orientation
        img = pil_image.convert("RGB") # Convert to RGB
        img_array = np.array(img).astype(np.float32) / 255.0 # Normalize to 0-1
        image_tensor = torch.from_numpy(img_array)[None,] # Add batch dimension

        return (image_tensor,)

    @classmethod
    def IS_CHANGED(cls, image_file, upload_image):
        # This method is crucial for ComfyUI to know when to refresh UI elements
        # or re-run the node if an input that *doesn't* trigger execution directly changes.
        # The `upload_image` widget value (filename) might persist across executions
        # even if the actual file it refers to has been processed.
        # To ensure the dropdown list ('image_file') updates after an upload and copy:
        # We can check if the `upload_image` refers to a file in the main input that 
        # is NOT yet in our custom folder, signaling a pending copy.
        # For simplicity and robustness in updating the dropdown after an upload action,
        # always returning float("nan") will force re-evaluation of inputs,
        # which re-runs INPUT_TYPES_GENERATOR.
        
        # A more precise check for a new upload:
        if upload_image and isinstance(upload_image, str) and upload_image != 'None':
            source_path = os.path.join(cls.BASE_INPUT_PATH, upload_image)
            destination_path = os.path.join(cls.FIXED_FOLDER_PATH, upload_image)
            if os.path.isfile(source_path) and not os.path.isfile(destination_path):
                # File exists at source (ComfyUI main input) but not yet in our custom folder.
                # This indicates a new upload that needs processing and list refresh.
                return float("nan") # Trigger refresh

        # Otherwise, let changes to image_file also trigger normal refresh if needed by ComfyUI.
        # Forcing refresh always ensures UI consistency after potential uploads.
        return float("nan")


    @classmethod
    def VALIDATE_INPUTS(cls, image_file, upload_image): # Added upload_image
        # This is mostly for providing messages to the user in the UI if an input is invalid.
        if image_file and not image_file.startswith("<"): # It's a specific file, not a placeholder
            full_path = os.path.join(cls.FIXED_FOLDER_PATH, image_file)
            if not os.path.isfile(full_path):
                return f"Selected image '{image_file}' no longer exists in {cls.FIXED_FOLDER_PATH}."
        # No specific validation for upload_image needed here as it's handled by ComfyUI's widget
        # and our processing logic.
        return True

    @classmethod
    def INPUT_TYPES_GENERATOR(cls, inputs): # inputs not used here as path is fixed
        # This is called by INPUT_TYPES or when IS_CHANGED suggests a refresh.
        # Its job is to provide the list of files for the 'image_file' dropdown.
        try:
            if not os.path.isdir(cls.FIXED_FOLDER_PATH):
                os.makedirs(cls.FIXED_FOLDER_PATH, exist_ok=True)
                print(f"[LoadImageFixedCustom] Created directory in GENERATOR: {cls.FIXED_FOLDER_PATH}")
                return {"image_file": ([f"<Default folder '{CUSTOM_SUBFOLDER_NAME}' created, add images>"],)}

            files = os.listdir(cls.FIXED_FOLDER_PATH)
            image_files = sorted([f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))])
            
            if not image_files:
                return {"image_file": (["<no images found>"],)}
            return {"image_file": (image_files,)}
        except Exception as e:
            print(f"[LoadImageFixedCustom] Error in INPUT_TYPES_GENERATOR: {e}")
            return {"image_file": (["<invalid path or error>"],)}

# Original class name was LoadImageFromCustomFolder. Now it's LoadImageFixedCustom.
# This means __init__.py needs to be updated.
# (No direct NODE_CLASS_MAPPINGS here as it should be in __init__.py)

# NODE_CLASS_MAPPINGS["LoadImageFromCustomFolder"] = LoadImageFromCustomFolder
# NODE_DISPLAY_NAME_MAPPINGS["LoadImageFromCustomFolder"] = "📂 Load Image from Folder"