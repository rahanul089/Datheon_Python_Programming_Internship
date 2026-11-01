
import argparse
import logging
import os
import shutil
from collections import Counter
from pathlib import Path

# Which extensions go into which category folder
EXTENSION_MAP = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".csv", ".ppt", ".pptx", ".md"},
    "Images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"},
    "Videos":    {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio":     {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"},
    "Archives":  {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code":      {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".json",
                  ".xml", ".sql", ".sh", ".ts"},
}

OTHERS = "Others"      # category for unknown file types
LOG_NAME = "organizer.log"

# Build a flat lookup: extension -> category (e.g. ".pdf" -> "Documents")
EXT_TO_CATEGORY = {ext: cat for cat, exts in EXTENSION_MAP.items() for ext in exts}


def setup_logging(folder):
    """Log messages to both the console and a log file in the target folder."""
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    for handler in (logging.StreamHandler(),
                    logging.FileHandler(folder / LOG_NAME, encoding="utf-8")):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


def category_for(path):
    """Look up which category folder a file belongs to."""
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHERS)


def unique_destination(dest_dir, name):
    """Avoid overwriting: turn 'report.pdf' into 'report_1.pdf', 'report_2.pdf', ..."""
    candidate = dest_dir / name
    stem, suffix, n = Path(name).stem, Path(name).suffix, 1
    while candidate.exists():
        candidate = dest_dir / f"{stem}_{n}{suffix}"
        n += 1
    return candidate


def organize(folder, dry_run=False):
    """Move every file in `folder` into its category subfolder."""
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Error: '{folder}' is not a directory.")

    log = setup_logging(folder)
    log.info("Organizing: %s%s", folder, "  [DRY RUN]" if dry_run else "")

    moved = Counter()          # how many files went into each category
    errors = 0                 # how many files could not be moved
    renamed = 0                # how many names had to be changed

    # Don't touch the script itself or its own log file
    skip = {Path(__file__).name, LOG_NAME}

    # Grab all files in the folder (ignore subfolders)
    with os.scandir(folder) as entries:
        files = [e for e in entries
                 if e.is_file(follow_symlinks=False) and e.name not in skip]

    # Process files one by one, alphabetically
    for entry in sorted(files, key=lambda e: e.name.lower()):
        src = Path(entry.path)
        category = category_for(src)
        dest_dir = folder / category

        try:
            dest = unique_destination(dest_dir, src.name)

            if dest.name != src.name:
                renamed += 1
                log.warning("Name collision: %s -> %s", src.name, dest.name)

            if dry_run:
                log.info("[dry-run] %s -> %s/%s", src.name, category, dest.name)
            else:
                dest_dir.mkdir(exist_ok=True)      # create category folder if needed
                shutil.move(str(src), str(dest))
                log.info("Moved %s -> %s/%s", src.name, category, dest.name)

            moved[category] += 1

        except PermissionError:
            errors += 1
            log.error("Permission denied: %s", src.name)
        except FileExistsError:
            errors += 1
            log.error("Destination already exists: %s", src.name)
        except OSError as exc:
            errors += 1
            log.error("Could not move %s: %s", src.name, exc)

    print_summary(moved, renamed, errors, dry_run)
    return moved


def print_summary(moved, renamed, errors, dry_run):
    """Print a small report of what happened."""
    line = "=" * 40
    print(f"\n{line}\n EXECUTION SUMMARY{' (dry run)' if dry_run else ''}\n{line}")

    for category, count in sorted(moved.items()):
        print(f" {category:<14}{count:>5} file(s)")

    print("-" * 40)
    print(f" {'Total relocated':<14}{sum(moved.values()):>5}")
    print(f" {'Renamed (collisions)':<20}{renamed:>3}")
    print(f" {'Errors':<20}{errors:>3}\n{line}")


def main():
    """Read command-line options and start organizing."""
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("folder", nargs="?",
                        default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="preview without moving files")
    args = parser.parse_args()
    organize(args.folder, args.dry_run)


if __name__ == "__main__":
    main()
