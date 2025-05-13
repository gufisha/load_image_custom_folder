import os
# from PIL import Image # This line should be removed or commented if not used
from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from comfy.utils import load_image

class LoadImageFromCustomFolder:
    @classmethod
    def INPUT_TYPES(cls):
        # Get initial list of images using the generator and default folder_path
        default_folder_path = "./input"
        try:
            # Call the generator with default inputs
            generated_inputs = cls.INPUT_TYPES_GENERATOR({"folder_path": default_folder_path})
            image_files_list = generated_inputs["image_file"][0]
        except Exception:
            image_files_list = ["<error loading initial files>"]

        return {
            "required": {
                "folder_path": ("STRING", {"default": default_folder_path}),
                "image_file": (image_files_list, ), # Define as a dropdown
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

        image = load_image(image_path)
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