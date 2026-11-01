"""
Automated File Organizer & Cleanup Utility
------------------------------------------
Sorts the files in a cluttered folder (default: ~/Downloads) into category
subfolders (Documents, Images, Videos, Archives, Code, ...).

- Extension -> category mapping dictionary (case-insensitive)
- os.scandir() to inspect the folder, shutil.move() to relocate files
- Category folders are created only when needed
- Naming collisions are resolved safely (report.pdf -> report_1.pdf)
- PermissionError / FileExistsError / OSError are caught per file
- Logging to console and 'organizer.log', plus a formatted summary

Usage:
    python organizer.py                  # organize ~/Downloads
    python organizer.py "C:/path/to/dir" # organize a specific folder
    python organizer.py --dry-run        # preview only, nothing is moved
"""

import argparse
import logging
import os
import shutil
from collections import Counter
from pathlib import Path

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
OTHERS = "Others"            # files with unknown extensions
LOG_NAME = "organizer.log"
EXT_TO_CATEGORY = {ext: cat for cat, exts in EXTENSION_MAP.items() for ext in exts}


def setup_logging(folder):
    """Log to both the console and a file inside the target folder."""
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    for handler in (logging.StreamHandler(), logging.FileHandler(folder / LOG_NAME, encoding="utf-8")):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


def category_for(path):
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHERS)


def unique_destination(dest_dir, name):
    """Return a destination path that does not exist yet (name_1.ext, name_2.ext...)."""
    candidate = dest_dir / name
    stem, suffix, n = Path(name).stem, Path(name).suffix, 1
    while candidate.exists():
        candidate = dest_dir / f"{stem}_{n}{suffix}"
        n += 1
    return candidate


def organize(folder, dry_run=False):
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Error: '{folder}' is not a directory.")

    log = setup_logging(folder)
    log.info("Organizing: %s%s", folder, "  [DRY RUN]" if dry_run else "")
    moved, errors, renamed = Counter(), 0, 0
    skip = {Path(__file__).name, LOG_NAME}

    with os.scandir(folder) as entries:
        files = [e for e in entries if e.is_file(follow_symlinks=False) and e.name not in skip]

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
                dest_dir.mkdir(exist_ok=True)
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
    line = "=" * 40
    print(f"\n{line}\n EXECUTION SUMMARY{' (dry run)' if dry_run else ''}\n{line}")
    for category, count in sorted(moved.items()):
        print(f" {category:<14}{count:>5} file(s)")
    print("-" * 40)
    print(f" {'Total relocated':<14}{sum(moved.values()):>5}")
    print(f" {'Renamed (collisions)':<20}{renamed:>3}")
    print(f" {'Errors':<20}{errors:>3}\n{line}")


def main():
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving files")
    args = parser.parse_args()
    organize(args.folder, args.dry_run)


if __name__ == "__main__":
    main()
