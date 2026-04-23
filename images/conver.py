import os
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

def convert_image(filename, folder):
    input_path = os.path.join(folder, filename)

    try:
        img = Image.open(input_path)

        # conversion RGB si nécessaire (PNG transparence etc)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        width, height = img.size

        # si déjà <= 1280px, on skip
        if width <= 1280:
            return filename

        new_width = 1280
        new_height = int((new_width / width) * height)

        img = img.resize((new_width, new_height), Image.LANCZOS)

        img.save(input_path, optimize=True, quality=85)

        return filename

    except Exception as e:
        return f"ERROR {filename}: {e}"


if __name__ == "__main__":
    folder = os.getcwd()

    images = [f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTENSIONS)]
    total = len(images)

    if total == 0:
        print("Aucune image trouvée.")
        exit()

    max_workers = os.cpu_count() // 2

    print(f"{total} images trouvées | {max_workers} workers\n")

    done = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(convert_image, img, folder) for img in images]

        for future in as_completed(futures):
            done += 1
            print(f"[{done}/{total}] terminé")

    print("\n✅ Conversion images terminée !")