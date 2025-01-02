import os
import shutil
from pathlib import Path

def organize_downloads():
    downloads = Path.home() / "Downloads"
    extensions = {
        'images': {'.jpg', '.png', '.gif', '.svg'},
        'documents': {'.pdf', '.docx', '.txt', '.xlsx'},
        'videos': {'.mp4', '.avi', '.mkv'},
        'archives': {'.zip', '.rar', '.tar.gz'}
    }
    
    for file in downloads.iterdir():
        if file.is_file():
            for folder, exts in extensions.items():
                if file.suffix.lower() in exts:
                    (downloads / folder).mkdir(exist_ok=True)
                    shutil.move(str(file), downloads / folder / file.name)
                    break