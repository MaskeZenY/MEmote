import os
import subprocess
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

VIDEO_EXTENSIONS = (".mp4", ".webm", ".mov", ".mkv")
def already_720p(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=height", "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip()) <= 720
    except ValueError:
        return False

def convert(video, folder):
    input_path = os.path.join(folder, video)
    output_path = os.path.join(folder, f"temp_{video}")

    # Nettoyer un temp_ résiduel (coupure de courant précédente)
    if os.path.exists(output_path):
        os.remove(output_path)

    command = [
        "ffmpeg",
        "-y",
        "-c:v", "libvpx-vp9",
        "-i", input_path,
        "-vf", "scale=1280:720:flags=lanczos,format=yuva420p",
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0",
        "-b:v", "0",
        "-crf", "30",
        "-c:a", "libopus",
        "-threads", "2",
        output_path
    ]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0 or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        if os.path.exists(output_path):
            os.remove(output_path)
        return video, False

    os.remove(input_path)
    os.rename(output_path, input_path)
    return video, True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-qualite", action="store_true", help="Vérifie la résolution avant de convertir (skip les 720p)")
    args = parser.parse_args()

    folder = os.getcwd()
    all_videos = [f for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXTENSIONS) and not f.startswith("temp_")]

    if args.scan_qualite:
        print(f"Scan de {len(all_videos)} vidéos...", flush=True)
        videos = []
        for i, v in enumerate(all_videos, 1):
            print(f"  [{i}/{len(all_videos)}] {v}", end="\r", flush=True)
            if not already_720p(os.path.join(folder, v)):
                videos.append(v)
        print()
        skipped = len(all_videos) - len(videos)
        if skipped:
            print(f"{skipped} vidéos déjà en 720p → ignorées")
    else:
        videos = all_videos
        print(f"{len(videos)} vidéos trouvées (sans scan qualité)")

    total = len(videos)

    if total == 0:
        print("Aucune vidéo à convertir.")
        exit()

    max_workers = os.cpu_count() // 2
    print(f"{total} vidéos à convertir | {max_workers} workers\n")

    completed = 0
    errors = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert, v, folder): v for v in videos}

        for future in as_completed(futures):
            video, success = future.result()
            completed += 1
            if success:
                print(f"[{completed}/{total}] ✓ {video}", flush=True)
            else:
                errors.append(video)
                print(f"[{completed}/{total}] ✗ ERREUR: {video}", flush=True)

    print(f"\n✅ Conversion terminée !")
    if errors:
        print(f"⚠️  {len(errors)} erreur(s): {', '.join(errors)}")
