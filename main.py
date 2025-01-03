#!/usr/bin/env python3
"""
Enhanced Downloads Organizer
A robust, cross-platform file organizer with concurrent processing and comprehensive error handling.
"""

import os
import shutil
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
from datetime import datetime
import platform
import time
from typing import Dict, Set, List, Tuple, Optional


class DownloadsOrganizer:
    """Enhanced downloads folder organizer with concurrent processing and robust error handling."""
    
    def __init__(self, downloads_path: Optional[Path] = None, max_workers: int = 4):
        """
        Initialize the organizer.
        
        Args:
            downloads_path: Custom downloads path (auto-detected if None)
            max_workers: Maximum number of concurrent threads
        """
        self.downloads_path = downloads_path or self._get_downloads_path()
        self.max_workers = max_workers
        self.results = {
            'moved': defaultdict(list),
            'errors': [],
            'skipped': [],
            'stats': Counter()
        }
        
        # Enhanced file type mappings
        self.extensions = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', 
                      '.tiff', '.ico', '.heic', '.raw', '.cr2', '.nef'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
                         '.xlsx', '.xls', '.csv', '.pptx', '.ppt', '.odp', '.keynote'},
            'videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', 
                      '.m4v', '.3gp', '.mpg', '.mpeg', '.ogv'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', 
                     '.opus', '.aiff', '.alac'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz', '.tar.bz2',
                        '.bz2', '.xz', '.tar.xz', '.dmg', '.pkg', '.deb', '.rpm'},
            'code': {'.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml',
                    '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift'},
            'executables': {'.exe', '.msi', '.app', '.deb', '.rpm', '.dmg', '.pkg',
                           '.run', '.appimage', '.flatpak', '.snap'},
            'fonts': {'.ttf', '.otf', '.woff', '.woff2', '.eot'},
            'ebooks': {'.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit'},
            'cad': {'.dwg', '.dxf', '.step', '.iges', '.stl', '.obj', '.blend'},
        }
        
        self._setup_logging()
    
    def _get_downloads_path(self) -> Path:
        """Auto-detect downloads folder based on operating system."""
        system = platform.system().lower()
        home = Path.home()
        
        if system == "windows":
            # Try Windows-specific paths
            downloads_paths = [
                home / "Downloads",
                home / "Desktop",
                Path(os.environ.get("USERPROFILE", "")) / "Downloads"
            ]
        elif system == "darwin":  # macOS
            downloads_paths = [
                home / "Downloads",
                home / "Desktop"
            ]
        else:  # Linux and others
            downloads_paths = [
                home / "Downloads",
                home / "downloads",
                home / "Desktop"
            ]
        
        # Return first existing path
        for path in downloads_paths:
            if path.exists() and path.is_dir():
                return path
        
        # Fallback to home directory
        logging.warning(f"Could not find Downloads folder, using {home}")
        return home
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('downloads_organizer.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_file_category(self, file_path: Path) -> Optional[str]:
        """Determine file category based on extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.extensions.items():
            if extension in extensions:
                return category
        
        return None
    
    def _create_category_folder(self, category: str) -> Path:
        """Create category folder if it doesn't exist."""
        folder_path = self.downloads_path / category
        try:
            folder_path.mkdir(exist_ok=True)
            return folder_path
        except OSError as e:
            self.logger.error(f"Failed to create folder {folder_path}: {e}")
            raise
    
    def _move_file_safely(self, source: Path, destination: Path) -> bool:
        """
        Safely move a file with conflict resolution.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle filename conflicts
            if destination.exists():
                counter = 1
                stem = destination.stem
                suffix = destination.suffix
                
                while destination.exists():
                    new_name = f"{stem}_{counter}{suffix}"
                    destination = destination.parent / new_name
                    counter += 1
            
            # Perform the move
            shutil.move(str(source), str(destination))
            return True
            
        except (OSError, shutil.Error) as e:
            self.logger.error(f"Failed to move {source} to {destination}: {e}")
            return False
    
    def _process_file(self, file_path: Path) -> Tuple[str, str, Optional[str]]:
        """
        Process a single file.
        
        Returns:
            Tuple of (status, file_name, error_message)
            status: 'moved', 'skipped', 'error'
        """
        try:
            # Skip if not a file
            if not file_path.is_file():
                return 'skipped', file_path.name, 'Not a regular file'
            
            # Skip hidden files and system files
            if file_path.name.startswith('.') or file_path.name.startswith('~'):
                return 'skipped', file_path.name, 'Hidden or temporary file'
            
            # Skip files that are currently being downloaded (common extensions)
            if file_path.suffix.lower() in {'.crdownload', '.part', '.tmp'}:
                return 'skipped', file_path.name, 'File currently downloading'
            
            # Skip very large files that might be in use
            try:
                if file_path.stat().st_size > 10 * 1024 * 1024 * 1024:  # 10GB
                    return 'skipped', file_path.name, 'File too large (>10GB)'
            except OSError:
                pass
            
            # Determine category
            category = self._get_file_category(file_path)
            if not category:
                return 'skipped', file_path.name, 'Unknown file type'
            
            # Create destination folder
            category_folder = self._create_category_folder(category)
            destination = category_folder / file_path.name
            
            # Move file
            if self._move_file_safely(file_path, destination):
                return 'moved', file_path.name, None
            else:
                return 'error', file_path.name, 'Move operation failed'
                
        except Exception as e:
            return 'error', file_path.name, str(e)
    
    def organize(self) -> Dict:
        """
        Organize the downloads folder with concurrent processing.
        
        Returns:
            Dict with organization results and statistics
        """
        start_time = time.time()
        
        self.logger.info(f"Starting organization of {self.downloads_path}")
        
        # Get all files to process
        try:
            all_files = [f for f in self.downloads_path.iterdir() if f.is_file()]
        except OSError as e:
            self.logger.error(f"Cannot access downloads folder: {e}")
            return {'error': f"Cannot access downloads folder: {e}"}
        
        if not all_files:
            self.logger.info("No files found to organize")
            return {'message': 'No files found to organize'}
        
        self.logger.info(f"Found {len(all_files)} files to process")
        
        # Process files concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_file, file_path): file_path 
                for file_path in all_files
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    status, filename, error_msg = future.result()
                    
                    if status == 'moved':
                        category = self._get_file_category(file_path)
                        self.results['moved'][category].append(filename)
                        self.results['stats']['moved'] += 1
                    elif status == 'skipped':
                        self.results['skipped'].append((filename, error_msg))
                        self.results['stats']['skipped'] += 1
                    elif status == 'error':
                        self.results['errors'].append((filename, error_msg))
                        self.results['stats']['errors'] += 1
                        
                except Exception as e:
                    self.results['errors'].append((file_path.name, str(e)))
                    self.results['stats']['errors'] += 1
        
        # Calculate execution time
        execution_time = time.time() - start_time
        self.results['stats']['execution_time'] = round(execution_time, 2)
        self.results['stats']['total_files'] = len(all_files)
        
        self._log_results()
        return self.results
    
    def _log_results(self):
        """Log detailed results of the organization process."""
        stats = self.results['stats']
        
        print("\n" + "="*60)
        print("🗂️  DOWNLOADS ORGANIZATION COMPLETE")
        print("="*60)
        
        print(f"📊 SUMMARY:")
        print(f"   Total files processed: {stats['total_files']}")
        print(f"   ✅ Successfully moved: {stats['moved']}")
        print(f"   ⏭️  Skipped: {stats['skipped']}")
        print(f"   ❌ Errors: {stats['errors']}")
        print(f"   ⏱️  Execution time: {stats['execution_time']} seconds")
        
        if self.results['moved']:
            print(f"\n📁 FILES ORGANIZED BY CATEGORY:")
            for category, files in self.results['moved'].items():
                print(f"   {category.upper()}: {len(files)} files")
                if len(files) <= 5:  # Show all files if 5 or fewer
                    for file in files:
                        print(f"      • {file}")
                else:  # Show first 3 and count
                    for file in files[:3]:
                        print(f"      • {file}")
                    print(f"      ... and {len(files) - 3} more")
        
        if self.results['skipped']:
            print(f"\n⏭️  SKIPPED FILES:")
            for filename, reason in self.results['skipped'][:5]:  # Show first 5
                print(f"   • {filename}: {reason}")
            if len(self.results['skipped']) > 5:
                print(f"   ... and {len(self.results['skipped']) - 5} more")
        
        if self.results['errors']:
            print(f"\n❌ ERRORS:")
            for filename, error in self.results['errors'][:5]:  # Show first 5
                print(f"   • {filename}: {error}")
            if len(self.results['errors']) > 5:
                print(f"   ... and {len(self.results['errors']) - 5} more")
        
        print(f"\n📂 Organized files location: {self.downloads_path}")
        print("="*60)


def main():
    """Main function to run the downloads organizer."""
    try:
        # Create organizer instance
        organizer = DownloadsOrganizer(max_workers=6)
        
        # Run organization
        results = organizer.organize()
        
        # Handle any critical errors
        if 'error' in results:
            print(f"❌ Critical error: {results['error']}")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Organization cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Unexpected error occurred")
        return 1


if __name__ == "__main__":
    exit(main())