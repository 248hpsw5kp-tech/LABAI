import os
import sys
import cv2

# ==========================
# GET BASE PATH (PY + EXE SAFE)
# ==========================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as .py
        return os.path.dirname(os.path.abspath(__file__))


# ==========================
# FIND IMAGE AUTOMATICALLY
# ==========================
def find_image(image_name):
    base_dir = get_base_dir()

    # Allow user to pass with or without extension
    possible_extensions = ["", ".jpg", ".jpeg", ".png", ".bmp"]

    # Also check inside "images" folder
    search_dirs = [
        base_dir,
        os.path.join(base_dir, "images")
    ]

    for folder in search_dirs:
        for ext in possible_extensions:
            path = os.path.join(folder, image_name + ext)

            if os.path.exists(path):
                return path

    return None


# ==========================
# MAIN GEL ANALYSIS FUNCTION
# ==========================
def analyze_gel(image_input, ladder=None):
    """
    image_input can be:
    - "gel1"
    - "gel1.jpeg"
    - "images/gel1.jpeg"
    """

    # Normalize input (remove accidental extensions duplication)
    image_input = image_input.replace(",", "").strip()

    # If user already gave full path, try it directly
    if os.path.exists(image_input):
        image_path = image_input
    else:
        # Try smart search
        name_only = os.path.splitext(os.path.basename(image_input))[0]
        image_path = find_image(name_only)

    if image_path is None:
        return f"Error: Image not found. Tried searching for '{image_input}'"

    print("DEBUG: Loading image from:", image_path)

    # Load image
    img = cv2.imread(image_path)

    if img is None:
        return "Error: OpenCV could not read the image file (corrupted or unsupported format)."

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Simple thresholding for band detection
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)

    # Find contours (bands)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bands = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h > 3:  # filter noise
            bands.append((y, h))

    # Sort top to bottom
    bands = sorted(bands, key=lambda x: x[0])

    # Estimate results
    results = []
    for i, (y, h) in enumerate(bands):
        intensity = h
        results.append({
            "band": i + 1,
            "position": y,
            "intensity": intensity
        })

    return {
        "image_path": image_path,
        "bands_detected": len(results),
        "results": results
    }
