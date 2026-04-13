from __future__ import annotations

import shutil
from pathlib import Path
from typing import TypedDict

from .utils import Constants


class ArtTypeInfo(TypedDict):
    destination_folder: Path
    files_moved: int


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"}


def _unique_destination(destination: Path, source_file: Path) -> Path:
    candidate = destination / source_file.name
    counter = 1

    while candidate.exists():
        candidate = destination / f"{source_file.stem}_{counter}{source_file.suffix}"
        counter += 1

    return candidate


def _move_image_files(source_dir: Path, destination: Path) -> int:
    moved_files = 0

    for file_path in source_dir.iterdir():
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        target = _unique_destination(destination, file_path)
        shutil.move(str(file_path), str(target))
        moved_files += 1

    return moved_files


def organize_art(base_dir: Path | None = None) -> None:
    base_dir = base_dir or Constants.DEFAULT_PATH
    base_dir.mkdir(parents=True, exist_ok=True)

    art_types: dict[str, ArtTypeInfo] = {}
    art_dirs = [
        path
        for pattern in ("arte_*", "set_*")
        for path in base_dir.glob(pattern)
        if path.is_dir()
    ]

    for art_dir in art_dirs:
        for subdir in art_dir.iterdir():
            if not subdir.is_dir():
                continue

            art_types.setdefault(
                subdir.name,
                {
                    "destination_folder": base_dir / subdir.name,
                    "files_moved": 0,
                },
            )

    for info in art_types.values():
        info["destination_folder"].mkdir(parents=True, exist_ok=True)

    for art_dir in art_dirs:
        for type_dir in art_dir.iterdir():
            if not type_dir.is_dir() or type_dir.name not in art_types:
                continue

            art_type = type_dir.name
            destination = art_types[art_type]["destination_folder"]
            moved = _move_image_files(type_dir, destination)
            art_types[art_type]["files_moved"] += moved

            try:
                type_dir.rmdir()
            except OSError:
                pass

        try:
            art_dir.rmdir()
        except OSError:
            pass

    misc_folder = base_dir / "misc"
    misc_folder.mkdir(parents=True, exist_ok=True)

    moved_misc = 0
    for file_path in base_dir.iterdir():
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        target = _unique_destination(misc_folder, file_path)
        shutil.move(str(file_path), str(target))
        moved_misc += 1

    print("\nOrganization completed!")
    print("\nSummary:")
    print("-" * 50)

    if not art_types:
        print("No legacy art folders were found.")
    else:
        for art_type, info in art_types.items():
            print(f"Art type: {art_type}")
            print(f"  - Files moved: {info['files_moved']}")
            print(f"  - Location: {info['destination_folder']}")
            print("-" * 50)

    if moved_misc == 0:
        print("No loose image files were found.")
    else:
        print(f"\nLoose files moved to: {misc_folder}")


if __name__ == "__main__":
    print("Starting art file organization...")
    organize_art()
