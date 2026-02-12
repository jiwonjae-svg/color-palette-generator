# Color Palette Generator v1.0.1

**Release Date:** February 12, 2026

## 🎯 Overview
Major code refactoring and optimization update. This release improves code quality, security, and UI responsiveness without changing user-facing features.

---

## ✨ What's New

### 🔧 Code Optimization
- **Merged icon modules**: Combined `embedded_icon.py` and `embedded_icons.py` into a single module for cleaner imports
- **Simplified main module**: Removed old tkinter-based `main.py`, renamed `main_ctk.py` → `main.py`
- **Removed duplicate code**: Eliminated ~32 duplicate dictionary keys in language manager
- **Cleaned unused code**: Removed unused methods (`get_luminance`, `_cleanup_stale_tooltips`) and imports
- **Fixed syntax errors**: Corrected double-comma syntax error in language_manager.py

### 🔒 Security Improvements
- **External encryption key**: Moved embedded Fernet encryption key to external `secret.key` file
- **Regenerated encryption key**: All data files re-encrypted with new secure key
- **Improved key management**: FileHandler now loads key from file instead of hardcoded value
- **Updated .gitignore**: Added `secret.key`, `embedded_icons.py`, and `assets/` to .gitignore

### 🐛 Bug Fixes
- **Fixed empty palette flicker**: New palette with 0 colors no longer flickers when adding first color
- **Fixed scrollbar color mismatch**: Color settings sidebar scrollbar now gray (was blue)
- **Fixed Korean text corruption**: Resolved `한국어` display issue in language settings
- **Fixed import warning**: Resolved Pylance `reportMissingImports` warning for `google.generativeai`

### 📝 Documentation
- **English comments**: Converted all Korean comments and docstrings to English across 6 files
- **Improved code readability**: Clearer function documentation and inline comments

---

## 🛠️ Technical Changes

### Modified Files
- `main.py` (renamed from main_ctk.py): Modern CustomTkinter UI (4593 lines)
- `file_handler.py`: External key loading, removed hardcoded EMBEDDED_KEY
- `embedded_icons.py`: Merged with embedded_icon.py (now includes ICO + PNG icons)
- `ai_color_recommender.py`: Fixed import, English comments
- `color_generator.py`: English comments, removed empty __init__
- `custom_harmony.py`: English comments
- `preset_generator.py`: English comments
- `language_manager.py`: Fixed duplicates, English section headers
- `.gitignore`: Added security and resource files

### Deleted Files
- `main_ctk.py` (renamed to main.py)
- `embedded_icon.py` (merged into embedded_icons.py)
- Old `main.py` (5232-line tkinter version)

### New Files
- `secret.key`: External Fernet encryption key (gitignored)

### Re-encrypted Data
- `data/config.dat`
- `data/custom_harmonies.dat`
- `data/palette_metadata.dat`
- `data/preset_palettes.dat`

---

## 📦 Installation & Upgrade

### New Installation
1. Download `ColorPaletteGenerator.exe` from Releases
2. Run the executable - no installation required
3. First launch will create `data/` folder and `secret.key`

### Upgrading from v1.0.0
⚠️ **IMPORTANT**: This version uses a new encryption key. Your existing settings and palettes will NOT be migrated automatically.

**To preserve your data:**
1. Export your palettes before upgrading (File → Export)
2. Note your settings
3. Install v1.0.1
4. Re-import palettes (File → Import)
5. Re-configure settings

Alternatively, continue using v1.0.0 if you have critical data that cannot be exported.

---

## 🔍 Performance

- **Startup time**: No change
- **UI responsiveness**: Improved (no flicker on empty palette)
- **Memory usage**: Slightly reduced (removed duplicate code)
- **Build size**: ~2% smaller (code optimization)

---

## 🌐 Compatibility

- **OS**: Windows 10/11 (x64)
- **Python**: 3.10+ (source code)
- **Dependencies**: No changes from v1.0.0

---

## 🐜 Known Issues

- Palette sharing module (`palette_sharing.py`) currently unused - will be activated in future release
- Preset browser service (`preset_browser.py`) unused - may be deprecated

---

## 📝 Changelog Summary

**Added:**
- External encryption key system
- English documentation across codebase

**Fixed:**
- Empty palette flicker bug
- Scrollbar color inconsistency
- Korean text encoding in settings
- Pylance import warnings
- Syntax error in language_manager.py

**Changed:**
- File structure (merged icon modules, renamed main.py)
- Encryption key (new secure key in external file)
- Code organization (removed duplicates, unused code)

**Removed:**
- Old tkinter UI (main.py)
- Embedded encryption key (now external)
- Duplicate code and unused methods
- 32 duplicate dictionary keys

---

## 🙏 Credits

**Developed by:** jiwonjae-svg

**Tools:**
- CustomTkinter (modern UI framework)
- Pillow (image processing)
- cryptography (Fernet encryption)
- google-generativeai (AI palette generation)

---

## 📄 License

This software is provided as-is for personal and educational use.

---

## 🔗 Links

- **GitHub Repository**: https://github.com/jiwonjae-svg/color_palette
- **Issue Tracker**: https://github.com/jiwonjae-svg/color_palette/issues
- **Previous Release (v1.0.0)**: https://github.com/jiwonjae-svg/color_palette/releases/tag/v1.0.0

---

**Full Diff:** [v1.0.0...v1.0.1](https://github.com/jiwonjae-svg/color_palette/compare/v1.0.0...v1.0.1)
