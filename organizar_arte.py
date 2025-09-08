import os
import shutil
from pathlib import Path


def organize_art():
    # Base path where art folders are located
    base_dir = Path(__file__).parent / "output"

    # Create a dictionary to track found art types
    art_types = {}

    # First, identify all unique art types
    for art_dir in base_dir.glob("arte_*"):
        if art_dir.is_dir():
            for subdir in art_dir.iterdir():
                if subdir.is_dir():
                    art_type = subdir.name
                    if art_type not in art_types:
                        art_types[art_type] = {
                            "destination_folder": base_dir / art_type,
                            "files_moved": 0,
                        }

    # Create folders for each art type if they don't exist
    for art_type in art_types:
        art_types[art_type]["destination_folder"].mkdir(exist_ok=True)

    # Move files to their respective folders
    for art_dir in base_dir.glob("arte_*"):
        if art_dir.is_dir():
            for type_dir in art_dir.iterdir():
                if type_dir.is_dir() and type_dir.name in art_types:
                    art_type = type_dir.name
                    destination = art_types[art_type]["destination_folder"]

                    # Move each file
                    for file in type_dir.glob("*"):
                        if file.is_file():
                            # Check if the file already exists in the destination
                            counter = 1
                            file_name = file.name
                            new_name = file_name

                            while (destination / new_name).exists():
                                # If the file already exists, add a numeric suffix
                                parts = os.path.splitext(file_name)
                                new_name = f"{parts[0]}_{counter}{parts[1]}"
                                counter += 1

                            # Move the file
                            shutil.move(str(file), str(destination / new_name))
                            art_types[art_type]["files_moved"] += 1

                    # Remove the art type directory if it's empty
                    try:
                        type_dir.rmdir()
                    except OSError:
                        pass  # The directory is not empty or cannot be removed

            # Try to remove the art directory if it's empty
            try:
                art_dir.rmdir()
            except OSError:
                pass  # The directory is not empty or cannot be removed

    # Move loose files to a "misc" folder
    misc_folder = base_dir / "misc"
    misc_folder.mkdir(exist_ok=True)

    for file in base_dir.glob("*.*"):
        if file.is_file() and file.suffix.lower() in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
        ]:
            # Check if the file already exists in the destination
            counter = 1
            file_name = file.name
            new_name = file_name

            while (misc_folder / new_name).exists():
                # If the file already exists, add a numeric suffix
                parts = os.path.splitext(file_name)
                new_name = f"{parts[0]}_{counter}{parts[1]}"
                counter += 1

            # Move the file
            shutil.move(str(file), str(misc_folder / new_name))

    # Show summary
    print("\nOrganization completed!")
    print("\nSummary:")
    print("-" * 50)

    for art_type, info in art_types.items():
        print(f"Art type: {art_type}")
        print(f"  - Files moved: {info['files_moved']}")
        print(f"  - Location: {info['destination_folder']}")
        print("-" * 50)

    print(f"\nLoose files moved to: {misc_folder}")


if __name__ == "__main__":
    print("Starting art file organization...")
    organize_art()
