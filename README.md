# Load Image from Custom Folder Node for ComfyUI

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that allows you to browse and load images from a specified folder within your system.

## Overview

This extension adds a "📂 Load Image from Folder" node to ComfyUI. This node provides a convenient way to select images from any directory you specify, instead of relying solely on the default ComfyUI input directory. It dynamically lists image files (PNG, JPG, JPEG) found in the chosen folder.

## Features

- **Browse Custom Folders**: Input any folder path to browse its contents.
- **Dynamic Image List**: The list of available image files in the "image_file" dropdown updates automatically when the "folder_path" changes.
- **Supported Formats**: Loads `.png`, `.jpg`, and `.jpeg` image files.
- **Error Handling**: Provides feedback if the specified folder doesn't exist or if an image file is not found.
- **Easy Integration**: Seamlessly integrates into your ComfyUI workflow.

## Installation

1.  **Navigate to Custom Nodes Directory**:
    Open your terminal or command prompt and navigate to your ComfyUI installation directory, then into the `custom_nodes` folder.
    ```bash
    cd path/to/your/ComfyUI/custom_nodes
    ```

2.  **Download the Node File**:
    Place the `load_image_from_custom_folder.py` file into this `custom_nodes` directory. You can do this by:
    *   Cloning a repository if it's part of one:
        ```bash
        # Replace with the actual git clone command if applicable
        # git clone https://github.com/yourusername/your-repo-name.git
        # cd your-repo-name 
        # cp load_image_from_custom_folder.py ../
        ```
    *   Or by manually downloading/copying the `.py` file into `ComfyUI/custom_nodes/`.

3.  **Restart ComfyUI**:
    If ComfyUI is currently running, you will need to restart it for the new custom node to be recognized.

## Usage

1.  **Add the Node**:
    *   In your ComfyUI workflow, right-click to open the context menu.
    *   Navigate to "Add Node" -> "image" -> "load".
    *   Select "📂 Load Image from Folder".

2.  **Configure the Node**:
    *   **`folder_path`**: Enter the absolute or relative path to the directory containing your images. The default is `./input` (relative to your ComfyUI root directory or wherever ComfyUI was started from).
    *   **`image_file`**: Once a valid `folder_path` is provided, this dropdown will populate with all `.png`, `.jpg`, and `.jpeg` files found in that folder. Select the image you want to load. If no images are found, it will display `<no images found>`. If the path is invalid, it will show `<invalid path>`.

3.  **Connect Output**:
    *   The node has one output: `image`. Connect this to the image input of another node in your workflow (e.g., VAE Encode, Image Resize).

## How it Works

The node takes a folder path and an image file name as input.
- It first validates if the `folder_path` exists.
- Then, it dynamically generates a list of image files (`.png`, `.jpg`, `.jpeg`) from the given `folder_path` for the `image_file` dropdown.
- When an image is selected, it constructs the full path to the image and uses ComfyUI's utility functions to load it.
- The `IS_CHANGED` method ensures that the `image_file` dropdown is refreshed whenever the `folder_path` input changes, providing an interactive file selection experience.
- The `VALIDATE_INPUTS` method provides real-time feedback in the UI if the folder path is incorrect or the image file doesn't exist.

## Troubleshooting

-   **Node Not Appearing**: Ensure ComfyUI was restarted after placing the `.py` file in `custom_nodes`. Check the console output when ComfyUI starts for any errors related to loading custom nodes.
-   **`<invalid path>` in `image_file`**: Double-check that the `folder_path` you entered is correct and accessible by the ComfyUI process.
-   **`<no images found>` in `image_file`**: Verify that the specified folder contains images with `.png`, `.jpg`, or `.jpeg` extensions.
-   **Permissions**: On some systems, you might need to ensure that ComfyUI has the necessary read permissions for the folder you are trying to access.

---

This README provides a comprehensive guide for users to install and use your custom ComfyUI node. 