import album_art_fix
import sysrsync
import typer
from enum import Enum


class SyncMode(str, Enum):
    """
    Enum to define the synchronization mode.

    - 'dap': Digital Audio Player mode. Syncs only audio files and fixes album art.
    - 'nas': Network Attached Storage mode. Performs a full, unfiltered sync.
    """

    dap = "dap"
    nas = "nas"


def sync_music(
    source_directory: str,
    target_directory: str,
    mode: SyncMode = typer.Argument(
        ...,
        help="Sync mode: 'dap' for filtered audio sync to a DAP, or 'nas' for a full unfiltered copy to a NAS.",
    ),
) -> None:
    """
    Syncs a music library with options for a full unfiltered copy or a filtered copy for a DAP.

    - `dap` mode: Syncs only specific audio files based on modification time and size,
      protects generated cover art, cleans up macOS metadata, and fixes album art.
    - `nas` mode: Performs a direct, unfiltered sync of the entire directory,
      ensuring an exact copy on the destination.
    """
    rsync_options = [
        # Core options
        # -r: recursive, -t: preserve times, -v: verbose, -h: human-readable
        # -P: --partial --progress
        # -m: --prune-empty-dirs
        "-rtvhPm",
        # Sync based on mod-time & size (much faster than checksum).
        # --modify-window=2 helps with FAT/exFAT filesystem timestamp resolution.
        "--modify-window=2",
        "--delete",
        "--inplace",
        # Permissions
        "--no-g",
        "--no-o",
        "--no-p",
    ]

    if mode == SyncMode.dap:
        print(
            "Running in DAP mode: Syncing audio files and fixing album art (this may take a moment)..."
        )
        rsync_options.append("--delete-excluded")

        # Define which audio file extensions to include in the sync
        base_audio_extensions = [".mp3", ".m4a", ".flac", ".aac", ".ogg", ".wav"]
        # Create a case-insensitive list of extensions
        audio_extensions = []
        for ext in base_audio_extensions:
            audio_extensions.append(ext.lower())
            audio_extensions.append(ext.upper())

        # rsync filter rules for DAP mode:
        # 1. 'P cover.jpg': Protect 'cover.jpg' from deletion on the destination.
        # 2. '- .DS_Store', '- ._*': Exclude macOS metadata files.
        # 3. '+ */': IMPORTANT - Include all directories for traversal.
        # 4. '+ *.ext': Include specified audio files.
        # 5. '- *': Exclude all other files.
        filter_rules = [
            "P cover.jpg",
            "- .DS_Store",
            "- ._*",
            "+ */",  # Must come before the file include rules
        ]
        for ext in audio_extensions:
            filter_rules.append(f"+ *{ext}")
        filter_rules.append("- *")

        for rule in filter_rules:
            rsync_options.append(f"--filter={rule}")
        
        print(f"Syncing audio files (case-insensitive): {', '.join(base_audio_extensions)}")

    elif mode == SyncMode.nas:
        print("Running in NAS mode: Performing a full, unfiltered sync...")
        # For a NAS, checksumming can be more reliable if modification times
        # are not trusted across different systems.
        rsync_options.append("-c")


    # Run the sync operation
    sysrsync.run(
        source=source_directory,
        destination=target_directory,
        sync_source_contents=True,
        options=rsync_options,
    )

    if mode == SyncMode.dap:
        print("\nFixing album art in the target directory...")
        album_art_fix.main(target_directory)

    print(f"\nMusic sync in '{mode.value}' mode complete.")


if __name__ == "__main__":
    typer.run(sync_music)