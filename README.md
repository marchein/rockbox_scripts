# Rockbox Scripts

A collection of Python scripts for managing and updating Rockbox firmware on Rockbox devices, along with tools for organizing, syncing, and exporting music and playlists.

---

## Table of Contents

- [Rockbox Scripts](#rockbox-scripts)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Scripts](#scripts)
    - [`app.py`](#apppy)
    - [`album_art_fix.py`](#album_art_fixpy)
    - [`mac_playlist_export.py`](#mac_playlist_exportpy)
    - [`sync_music.py`](#sync_musicpy)
    - [`update_rockbox.py`](#update_rockboxpy)
  - [Getting Started](#getting-started)
  - [Dependencies](#dependencies)
  - [Acknowledgments](#acknowledgments)

---

## Overview

This repository provides a suite of utilities to make life easier for Rockbox device users. Automate music synchronization, fix album artwork, export playlists from macOS Music, and keep your Rockbox firmware up to date—all with simple Python scripts.

---

## Scripts

### `app.py`

Unified entry point to perform multiple Rockbox-related tasks: music sync, playlist export, device updates, and more.

**Usage:**
```bash
python app.py --playlists-directory-name "Playlists" --music-directory-name "Music" /path/to/rockbox_mount /path/to/music
```
**Parameters:**
- `mount_point`: Mount point of the Rockbox device.
- `source_music_directory`: Directory containing music files to synchronize.
- `playlists_directory_name` (optional): Directory to export playlists (default: "Playlists").
- `music_directory_name` (optional): Directory on device for music sync (default: "Music").

---

### `album_art_fix.py`

Organizes music files and extracts/normalizes cover images (album art) from audio files for consistent format and device compatibility.

**Usage:**
```bash
python album_art_fix.py /path/to/music_directory
```

---

### `mac_playlist_export.py`

Exports all user playlists from the macOS Music app to a specified directory as `.m3u` files.

**Usage:**
```bash
python mac_playlist_export.py /path/to/store_playlists
```

---

### `sync_music.py`

Synchronizes music between a source and a target directory using `rsync`. Supports two modes:

- `dap`: Syncs only audio files (filters by extension), preserves album art, and cleans up metadata.
- `nas`: Performs a full, unfiltered sync for backup to a NAS.

Also integrates album art fixing after sync.

**Usage:**
```bash
python sync_music.py /path/to/source_directory /path/to/target_directory --mode dap
```
or
```bash
python sync_music.py /path/to/source_directory /path/to/target_directory --mode nas
```

---

### `update_rockbox.py`

Updates the Rockbox firmware on your device. Auto-detects the current device and revision, downloads, and installs the latest daily build if needed.

**Usage:**
```bash
python update_rockbox.py /path/to/rockbox_mount_point
```

---

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rockbox_scripts.git
   cd rockbox_scripts
   ```

2. **Install dependencies**
   ```bash
   pip install -U -r requirements.txt
   ```

3. **Run the scripts as shown in the [Scripts](#scripts) section.**

---

## Dependencies

- Python 3.8+
- [typer](https://typer.tiangolo.com/)
- [mutagen](https://mutagen.readthedocs.io/)
- [Pillow (PIL)](https://pillow.readthedocs.io/)
- [sysrsync](https://pypi.org/project/sysrsync/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
- [requests](https://requests.readthedocs.io/)

Install all dependencies using:
```bash
pip install -U -r requirements.txt
```

---

## Acknowledgments

- [@SupItsZaire](https://github.com/SupItsZaire) for their [Rockbox Cover Art Fixer](https://github.com/SupItsZaire/rockbox-cover-art-fixer) script

---

Happy Rockboxing!
