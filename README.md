<div align="center">

# 🎨 Color Palette Generator

**Your Professional Color Palette Creation Suite**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue.svg)](https://www.microsoft.com/windows)

*Create, manage, and export beautiful color palettes with AI-powered intelligence and professional tools.*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Building](#-building)

---

</div>

## 🎯 What is Color Palette Generator?

Color Palette Generator is a **powerful, feature-rich desktop application** for creating and managing color palettes with professional-grade tools. Extract colors from images, generate harmonious schemes based on color theory, or let AI create palettes from your descriptions.

Perfect for:
- 🎨 **Designers & Artists** crafting cohesive color schemes
- 💼 **Brand Strategists** developing visual identities
- 🖥️ **Developers** needing consistent UI color systems
- 📸 **Photographers** extracting dominant image colors

## ✨ Features

- **10+ Color Harmony Schemes**: Complementary, Analogous, Triadic, and more
- **AI-Powered Generation**: Google Gemini integration for creative palettes
- **Image Color Extraction**: K-means clustering for dominant colors
- **Custom Harmony Editor**: Create your own color rules with HSV offsets
- **Smart Palette Management**: Track, preview, and organize all your palettes
- **Multiple Export Formats**: PNG, TXT, and encrypted MPS files
- **Multi-Language**: Full Korean/English support
- **Modern UI**: CustomTkinter dark mode interface

## 📦 Installation

Download ColorPaletteGenerator.exe from [Releases](../../releases) or run from source:

```powershell
pip install -r requirements.txt
python main.py
```

## 🚀 Quick Start

1. Launch the application
2. Choose input method (HEX, Color Picker, or Image)
3. Select harmony type
4. Click **Generate Palette**
5. Save, export, or recolor images!

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       UI Layer (CustomTkinter)          │
├─────────────────────────────────────────┤
│    Generator Layer (Color Logic)        │
├─────────────────────────────────────────┤
│   Services Layer (AI, Image, Export)    │
├─────────────────────────────────────────┤
│      Storage Layer (Encrypted)          │
└─────────────────────────────────────────┘
```

## 🔒 Security

- **Fernet Encryption**: All data files encrypted with AES-128
- **External Key**: Machine-specific secret.key (gitignored)
- **API Protection**: Gemini API keys never stored in plaintext

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Color Palette Generator** - Where Creativity Meets Technology 🎨

Made with ❤️ by jiwonjae-svg

</div>
