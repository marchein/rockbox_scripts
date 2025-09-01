import album_art_fix
import sysrsync
import typer


def sync_music(source_directory: str, target_directory: str) -> None:
    """
    Syncs a music library quickly by comparing file sizes, protecting generated
    cover art, and then fixes album art in the target directory.

    This script uses rsync with the --size-only flag for speed. It avoids the
    slow --checksum scan and relies on file size changes to detect differences.
    This prevents re-syncing files that have only had their metadata (like
    album art) updated on the target, as rsync will not overwrite a newer file
    with an older one by default.
    """
    print("Performing fast sync by comparing file sizes...")

    # rsync filter rules:
    # 1. 'P cover.jpg': Protect 'cover.jpg'. Any file matching this is exempt from deletion.
    # 2. '- .DS_Store': Exclude '.DS_Store'. Any file matching this is not copied.
    filter_rules = [
        "P cover.jpg",
        "- .DS_Store",
    ]

    rsync_options = [
        # Core options
        # -r: recursive, -t: preserve times
        # -vv: verbose, -h: human-readable, -P: --partial --progress
        "-rtvvhP",
        "--size-only",          # Base comparison on size only for speed
        "--delete",
        "--delete-excluded",
        "--inplace",
        "--modify-window=2",
        # Permissions
        "--no-g",
        "--no-o",
        "--no-p",
    ]

    # Add filter rules to the options
    for rule in filter_rules:
        rsync_options.append(f"--filter={rule}")

    sysrsync.run(
        source=source_directory,
        destination=target_directory,
        sync_source_contents=True,
        options=rsync_options,
    )

    print("\nFixing album art in the target directory...")
    # Call album_art_fix.main with a string path, not a list.
    album_art_fix.main(target_directory)

    print("\nMusic sync and album art fix complete.")


if __name__ == "__main__":
    typer.run(sync_music)