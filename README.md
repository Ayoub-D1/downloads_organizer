# 📁 Downloads Organizer

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

A smart, lightweight Python script that automatically organizes your cluttered Downloads folder by sorting files into categorized subdirectories based on their file extensions.

## ✨ Features

- 🎯 **Smart Categorization**: Automatically sorts files by type (images, documents, videos, archives)
- 🚀 **One-Click Organization**: Run once and watch your Downloads folder transform
- 🔧 **Easily Customizable**: Add new file types and categories with minimal code changes
- 💻 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🛡️ **Safe Operations**: Uses `shutil.move()` for reliable file handling
- 📦 **Zero Dependencies**: Uses only Python standard library

## 🚀 Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/Ayoub-D1/downloads_organizer.git
   cd downloads_organizer
   ```

2. **Run the organizer**
   ```bash
   python organize_downloads.py
   ```

That's it! Your Downloads folder is now organized! 🎉

## 📂 File Organization Structure

```
Downloads/
├── images/          # .jpg, .png, .gif, .svg, .webp
├── documents/       # .pdf, .docx, .txt, .xlsx, .pptx
├── videos/          # .mp4, .avi, .mkv, .mov, .wmv
├── archives/        # .zip, .rar, .tar.gz, .7z
├── audio/           # .mp3, .wav, .flac, .aac
└── code/            # .py, .js, .html, .css, .json
```

## 🔧 Customization

Want to add more file types? Simply edit the `extensions` dictionary:

```python
extensions = {
    'images': {'.jpg', '.png', '.gif', '.svg', '.webp'},
    'documents': {'.pdf', '.docx', '.txt', '.xlsx', '.pptx'},
    'videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv'},
    'archives': {'.zip', '.rar', '.tar.gz', '.7z'},
    'audio': {'.mp3', '.wav', '.flac', '.aac'},
    'code': {'.py', '.js', '.html', '.css', '.json'},
    'your_category': {'.ext1', '.ext2'}  # Add your own!
}
```

## 💡 Use Cases

- 🎓 **Students**: Organize downloaded course materials and assignments
- 💼 **Professionals**: Keep work documents and resources sorted
- 🎮 **Gamers**: Separate game files, mods, and screenshots
- 📸 **Content Creators**: Automatically sort media assets

## ⚠️ Important Notes

- The script operates on your actual Downloads folder
- Files are **moved**, not copied (original location changes)
- Always backup important files before running organizational scripts
- The script creates folders automatically if they don't exist

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- Add support for more file types
- Implement duplicate file detection
- Add configuration file support
- Create a GUI version
- Add scheduling/automation features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If this project helped you organize your digital life, please consider giving it a ⭐!

---

<div align="center">
  <strong>Made with ❤️ by <a href="https://github.com/Ayoub-D1">Ayoub-D1</a></strong>
</div>
