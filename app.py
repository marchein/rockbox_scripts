import os
import os.path
import platform
import typer

import mac_playlist_export
import sync_music
import update_rockbox

def main(
    mount_point: str,
    source_music_directory: str,
    playlists_directory_name: str = "Playlists",
    music_directory_name: str = "Music",
    sync_mode: sync_music.SyncMode = typer.Option(
        sync_music.SyncMode.dap,
        help="Sync mode for music transfer: 'dap' for filtered audio sync to a DAP, or 'nas' for a full unfiltered copy to a NAS.",
    ),
):
    """
    Unified entry point to export playlists, sync music, and update Rockbox firmware.

    Args:
        mount_point (str): Path to the Rockbox device mount point.
        source_music_directory (str): Directory containing music to sync.
        playlists_directory_name (str, optional): Directory to export playlists. Defaults to "Playlists".
        music_directory_name (str, optional): Directory on Rockbox device for music. Defaults to "Music".
        sync_mode (SyncMode, optional): Sync mode for music transfer. Defaults to 'dap'.
    """
    if platform.system() == "Darwin":
        print("Detected macOS, exporting playlists...")
        playlists_dir = os.path.join(mount_point, playlists_directory_name)
        os.makedirs(playlists_dir, exist_ok=True)
        mac_playlist_export.export_playlists(playlists_dir)
    else:
        print("Non-macOS system detected, skipping playlist export.")

    music_target_dir = os.path.join(mount_point, music_directory_name)
    os.makedirs(music_target_dir, exist_ok=True)

    print(f"Syncing music from '{source_music_directory}' to '{music_target_dir}' in '{sync_mode.value}' mode...")
    sync_music.sync_music(
        source_music_directory, music_target_dir, mode=sync_mode
    )

    print("Updating Rockbox firmware if needed...")
    update_rockbox.update_rockbox(mount_point)

    print("Done.")

if __name__ == "__main__":
    typer.run(main)
