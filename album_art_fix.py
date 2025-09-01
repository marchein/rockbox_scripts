import os
import shutil
import sys
import tempfile
import base64
import PIL
from PIL import Image, UnidentifiedImageError
from mutagen import File
from mutagen.flac import Picture as FLACPicture, error as FLACError
from mutagen.id3 import APIC
from mutagen.mp4 import MP4, MP4Cover

SUPPORTED_EXTENSIONS = (".mp3", ".flac", ".opus", ".ogg", ".m4a")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
COVER_FILENAME = "cover.jpg"
TEMP_FOLDER_NAME = "cover_extraction_temp"

# ... (all other functions remain the same) ...

def extract_art_mutagen(file_path: str) -> str | None:
    try:
        file_obj = File(file_path, easy=False)
        if file_obj is None:
            # print(f"Could not load file with mutagen: {file_path}")
            return None

        pictures_data = []
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".mp3":
            if hasattr(file_obj, 'tags') and file_obj.tags:
                for key in file_obj.tags.keys():
                    if key.startswith("APIC:"):
                        apic_frame = file_obj.tags[key]
                        pictures_data.append({'data': apic_frame.data, 'mime': apic_frame.mime})
                        break
        elif file_ext == ".flac":
            if hasattr(file_obj, 'pictures') and file_obj.pictures:
                for pic in file_obj.pictures:
                    pictures_data.append({'data': pic.data, 'mime': pic.mime})
                    break
        elif file_ext in (".opus", ".ogg"):
            if hasattr(file_obj, 'tags') and file_obj.tags:
                b64_picture_tags = []
                if isinstance(file_obj.tags.get('METADATA_BLOCK_PICTURE'), list):
                    b64_picture_tags.extend(file_obj.tags.get('METADATA_BLOCK_PICTURE'))
                elif isinstance(file_obj.tags.get('METADATA_BLOCK_PICTURE'), str):
                    b64_picture_tags.append(file_obj.tags.get('METADATA_BLOCK_PICTURE'))

                for b64_data in b64_picture_tags:
                    try:
                        pic_data_bytes = base64.b64decode(b64_data)
                        flac_pic = FLACPicture(pic_data_bytes)
                        pictures_data.append({'data': flac_pic.data, 'mime': flac_pic.mime})
                        break
                    except (TypeError, ValueError, base64.binascii.Error, FLACError):
                        continue
        elif file_ext == ".m4a":
            try:
                mp4_obj = MP4(file_path)
                covr = mp4_obj.tags.get("covr")
                if covr:
                    cover_obj = covr[0]
                    if isinstance(cover_obj, MP4Cover):
                        mime = "image/jpeg" if cover_obj.imageformat == MP4Cover.FORMAT_JPEG else "image/png"
                        pictures_data.append({'data': cover_obj, 'mime': mime})
            except Exception as e:
                print(f"Error extracting cover from M4A: {file_path}: {e}")

        if not pictures_data:
            return None

        selected_picture = pictures_data[0]
        pic_data_bytes = selected_picture['data']
        mime_type = selected_picture['mime']

        extensions = {"image/jpeg": "jpeg", "image/png": "png", "image/gif": "gif"}
        ext = extensions.get(mime_type, "jpeg")

        temp_extraction_dir = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME + "_extract")
        os.makedirs(temp_extraction_dir, exist_ok=True)

        temp_art_filename = os.path.splitext(os.path.basename(file_path))[0] + f".{ext}"
        temp_art_path = os.path.join(temp_extraction_dir, temp_art_filename)

        with open(temp_art_path, "wb") as h:
            h.write(pic_data_bytes)

        process_cover_image(temp_art_path)
        return temp_art_path

    except Exception as e:
        print(f"Error extracting art from {file_path} with mutagen: {e}")
        return None

def handle_audio_files(directory: str, temp_folder: str):
    audio_files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith(SUPPORTED_EXTENSIONS)
    ]

    for audio_file_path in audio_files:
        cover_path = extract_art_mutagen(audio_file_path)
        if cover_path:
            final_cover_dest = os.path.join(directory, COVER_FILENAME)
            shutil.move(cover_path, final_cover_dest)
            print(f"Cover image extracted from {os.path.basename(audio_file_path)} using mutagen, processed, and saved as {COVER_FILENAME} in {directory}")
            return

def sanitize_filename(filename: str):
    return "".join(
        c if c.isalnum() or c in [".", "_", "-", " "] else "_" for c in filename
    )

def get_album_tag(file_path: str):
    try:
        if file_path.endswith(SUPPORTED_EXTENSIONS):
            album_tag = File(file_path, easy=True)["album"]
            return album_tag[0] if isinstance(album_tag, list) else album_tag
    except Exception:
        return None

def organize_music_files(root_dir: str):
    for filename in os.listdir(root_dir):
        file_path = os.path.join(root_dir, filename)
        if os.path.isfile(file_path) and file_path.endswith(SUPPORTED_EXTENSIONS):
            album_tag = get_album_tag(file_path)
            if album_tag:
                sanitized_album_tag = sanitize_filename(str(album_tag))
                album_folder = os.path.join(root_dir, sanitized_album_tag)
                os.makedirs(album_folder, exist_ok=True)
                try:
                    shutil.move(file_path, os.path.join(album_folder, filename))
                except Exception as e:
                    print(f"Error moving '{filename}': {e}")

def process_cover_image(image_path: str):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img = img.resize((300, 300))
            # Overwrite the original file in JPEG format
            img.save(image_path, "JPEG", quality=85, subsampling=0)
    except UnidentifiedImageError as e:
        print(f"Error processing '{os.path.basename(image_path)}': {str(e)}")

def process_images(root_dir: str):
    processed_folders = set()
    folders_processed = 0
    for root, dirs, _ in os.walk(root_dir):
        if ".rockbox" in dirs:
            dirs.remove(".rockbox")
        if root in processed_folders:
            continue
        cover_path = os.path.join(root, COVER_FILENAME)
        if os.path.exists(cover_path) and os.path.getsize(cover_path) > 0:
            process_cover_image(cover_path)
        else:
            handle_audio_files(root, os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME))
        folders_processed += 1
        processed_folders.add(root)
    if folders_processed > 0:
        print(f"\n{folders_processed} folder(s) processed.")

def clear_temp_directory():
    # Corrected to match the directory created in extract_art_mutagen
    temp_folder_to_clear = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME + "_extract")

    if os.path.exists(temp_folder_to_clear):
        try:
            shutil.rmtree(temp_folder_to_clear)
            print(f"Successfully cleared temporary directory: {temp_folder_to_clear}")
        except OSError as e:
            print(f"Error clearing temporary directory {temp_folder_to_clear}: {e}")
    # No need for an 'else' part, as it's not an error if the directory doesn't exist.

def main(root_directory: str) -> None:
    # I've removed the organize_music_files call as it seems out of scope
    # for a script focused on fixing album art, but you can add it back if needed.
    # organize_music_files(root_directory)
    try:
        process_images(root_directory)
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
    finally:
        # Ensure cleanup happens even if the script is interrupted
        clear_temp_directory()

if __name__ == "__main__":
    import typer
    typer.run(main)