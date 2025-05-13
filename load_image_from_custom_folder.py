import os
# from PIL import Image # This line should be removed or commented if not used
from PIL import Image, ImageOps
import numpy as np
import torch
from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
# from comfy.utils import load_image # This will be replaced

class LoadImageFromCustomFolder:
    @classmethod
    def INPUT_TYPES(cls):
        initial_image_files = ["<Select folder to see images>"]
        default_folder_path = "./input"  # Default path for initial load

        try:
            # Check if the default directory exists before trying to list files
            # This makes the initial population more robust.
            if os.path.isdir(default_folder_path):
                # Call the generator with default inputs to get initial files
                generated_inputs = cls.INPUT_TYPES_GENERATOR({"folder_path": default_folder_path})
                # Ensure the generator returned the expected structure
                if ("image_file" in generated_inputs and 
                    isinstance(generated_inputs["image_file"], tuple) and 
                    len(generated_inputs["image_file"]) > 0 and
                    isinstance(generated_inputs["image_file"][0], list)):
                    initial_image_files = generated_inputs["image_file"][0]
                elif not image_files: # If empty list returned by generator
                    initial_image_files = ["<no images found in default>"]
            else:
                initial_image_files = ["<default input folder not found>"]
        except Exception as e:
            # If any error occurs during initial population (e.g., permissions, unexpected error in generator)
            # fall back to a safe default. This ensures the class definition doesn't fail.
            print(f"[LoadImageFromCustomFolder] Error during initial INPUT_TYPES: {e}")
            initial_image_files = ["<Error populating initial images. Check console.>"]

        return {
            "required": {
                "folder_path": ("STRING", {"default": default_folder_path}),
                "image_file": (initial_image_files, ), # Defines image_file as a dropdown
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_selected_image"
    CATEGORY = "image/load"

    def load_selected_image(self, folder_path, image_file):
        folder_path = folder_path.strip()

        if not os.path.isdir(folder_path):
            raise Exception(f"Folder does not exist: {folder_path}")

        image_path = os.path.join(folder_path, image_file)
        if not os.path.isfile(image_path):
            raise Exception(f"Image not found: {image_path}")

        # image = load_image(image_path) # Replace this line
        pil_image = Image.open(image_path)
        pil_image = ImageOps.exif_transpose(pil_image)
        img = pil_image.convert("RGB")
        img_array = np.array(img).astype(np.float32) / 255.0
        image = torch.from_numpy(img_array)[None,]

        return (image,)

    @classmethod
    def IS_CHANGED(cls, folder_path, image_file):
        """Force UI to refresh options when folder changes."""
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, folder_path, image_file):
        if not os.path.isdir(folder_path):
            return f"Folder does not exist: {folder_path}"
        full_path = os.path.join(folder_path, image_file)
        if not os.path.isfile(full_path):
            return f"Image not found: {image_file}"
        return True

    @classmethod
    def INPUT_TYPES_GENERATOR(cls, inputs):
        folder_path = inputs.get("folder_path", "./input")
        try:
            files = os.listdir(folder_path)
            image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            return {
                "image_file": (image_files if image_files else ["<no images found>"],)
            }
        except Exception as e:
            return {
                "image_file": (["<invalid path>"],)
            }

# NODE_CLASS_MAPPINGS["LoadImageFromCustomFolder"] = LoadImageFromCustomFolder
# NODE_DISPLAY_NAME_MAPPINGS["LoadImageFromCustomFolder"] = "📂 Load Image from Folder"