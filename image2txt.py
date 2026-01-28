import os
import numpy as np
from PIL import Image

# --- Configuration ---

IMAGE_INPUT_PATH = os.getcwd()
SCREEN_SIZE = (96, 54)  # (Width, Height)

OUTPUT_PATH = os.getcwd()
DEBUG_PATH = os.getcwd()

WRITE_DEBUG_TXT = True

# File extensions considered images
IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}


def resize_image(file_path, size):
    """Open, resize, and convert to RGB. Returns PIL Image or None."""
    try:
        with Image.open(file_path) as img:
            img_resized = img.resize(size)
            return img_resized.convert("RGB")
    except Exception as e:
        print(f"[SKIP] {file_path}: {e}")
        return None


def image_to_rgb_planes(img):
    """
    Convert PIL Image (RGB) -> numpy (H,W,3) -> reshape to (3, N)
    Returns (3, N) uint8 array: rows are [R..., G..., B...]
    """
    arr = np.array(img, dtype=np.uint8)  # (H,W,3)
    planes = arr.reshape(-1, 3).T  # (3, N)
    return planes


def channel_to_str(chan):
    """uint8 1D array -> single concatenated string of 3-digit values."""
    return "".join(f"{v:03d}" for v in chan.tolist())


def format_rgb_planes_to_strings(planes3xN):
    r_str = channel_to_str(planes3xN[0])
    g_str = channel_to_str(planes3xN[1])
    b_str = channel_to_str(planes3xN[2])
    return r_str, g_str, b_str


def process_one_image(in_path, out_base):
    """Process one image and write output .txt (+ optional debug)."""
    img = resize_image(in_path, SCREEN_SIZE)
    if img is None:
        return False

    planes = image_to_rgb_planes(img)
    r_all, g_all, b_all = format_rgb_planes_to_strings(planes)
    final_str = r_all + g_all + b_all

    # Output .txt with same base name
    out_txt = os.path.join(OUTPUT_PATH, out_base + ".txt")
    try:
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(final_str)
        print(f"[OK] {out_txt} (chars: {len(final_str):,})")
    except Exception as e:
        print(f"[ERR] writing {out_txt}: {e}")
        return False

    # Optional debug file (spaced values)
    if WRITE_DEBUG_TXT:
        debug_txt = os.path.join(DEBUG_PATH, out_base + "_debug.txt")
        try:
            r_dbg = " ".join(r_all[i:i + 3] for i in range(0, len(r_all), 3))
            g_dbg = " ".join(g_all[i:i + 3] for i in range(0, len(g_all), 3))
            b_dbg = " ".join(b_all[i:i + 3] for i in range(0, len(b_all), 3))
            dbg = (
                    "--- RED CHANNEL ---\n" + r_dbg + "\n\n" +
                    "--- GREEN CHANNEL ---\n" + g_dbg + "\n\n" +
                    "--- BLUE CHANNEL ---\n" + b_dbg + "\n"
            )
            with open(debug_txt, "w", encoding="utf-8") as f:
                f.write(dbg)
            print(f"      [DEBUG] {debug_txt}")
        except Exception as e:
            print(f"[WARN] debug write failed for {debug_txt}: {e}")

    return True


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    if WRITE_DEBUG_TXT:
        os.makedirs(DEBUG_PATH, exist_ok=True)

    if not os.path.isdir(IMAGE_INPUT_PATH):
        print(f"[ERR] IMAGE_INPUT_PATH not found: {IMAGE_INPUT_PATH}")
        return

    files = sorted(os.listdir(IMAGE_INPUT_PATH))
    any_done = False
    for name in files:
        root, ext = os.path.splitext(name)
        if ext.lower() not in IMG_EXTS:
            continue
        in_path = os.path.join(IMAGE_INPUT_PATH, name)
        out_base = root
        print(f"Processing: {in_path}")
        ok = process_one_image(in_path, out_base)
        any_done = any_done or ok

    if not any_done:
        print("[NOTE] No images processed (check extensions and input path).")
    else:
        print("[DONE] Batch conversion complete.")


if __name__ == "__main__":
    print(os.getcwd())
    main()
