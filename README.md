# Chromium Theme Studio v3

A desktop theme editor for Chromium-based browsers, built with PySide6. Create, preview, and export browser themes with a browser-style visual editor for Chrome, Brave, and Edge.

## What changed in v3

v3 focuses on stability, rendering correctness, image handling, and a more consistent editing experience.

### Preview and rendering
- Replaced the old multi-widget preview composition with a deterministic single-pass renderer.
- Fixed startup and refresh layer-order glitches.
- Browser chrome now consistently renders above the New Tab Page background.
- Improved browser-specific preview metrics for Chrome, Brave, and Edge.
- Improved text placement, alignment, and contrast in the preview.

### Images
- Supports PNG, JPEG, and WebP image selection and drag-and-drop.
- Image previews keep aspect ratio instead of stretching into the preview box.
- Large imports are safely reduced when the resize option is enabled.
- Image transforms use persistent scale/X/Y properties.
- Added proper render-cache invalidation when replacing or removing images.

### UI/UX
- Unified light and dark styling into one consistent design system.
- Standardized buttons, inputs, tabs, group boxes, spacing, and typography.
- Simplified the preview toolbar and resolution controls.
- Cleaner browser selector, Incognito control, and fullscreen workflow.

### Build and release
- Added `requirements.txt` for reproducible installs.
- Added a GitHub Actions workflow at `.github/workflows/build-windows.yml`.
- The workflow builds a Windows EXE package with PyInstaller.
- Manual builds are available from **Actions → Build Windows EXE → Run workflow**.
- Pushing a version tag such as `v3.0.0` also produces a GitHub Release attachment.

## Features

Live browser preview, Chrome/Brave/Edge skins, Incognito variants, color editing with RGBA and hex input, image overlays, drag-and-drop imports, presets, Undo/Redo, fullscreen preview, Spotlight FX, and ZIP/CRX-style theme packaging.

## Installation

Download the Windows build from the repository's **Actions** artifacts or a GitHub Release.

Run `ChromiumThemeStudio.exe` from the extracted build directory.

## Using the editor

Choose a browser from the preview header, select an editable property from the left panel, then adjust its controls on the right.

For images, select **Frame Image** or **NTP Image** and either choose **Select Image** or drop an image directly onto the preview canvas. Use Scale, X, and Y to position it.

Use the resolution buttons to switch between 16:9, 21:9, and a custom canvas size. F11 toggles fullscreen preview and Esc exits it.

## Exporting a theme

Open **Export**, enter the theme metadata, choose ZIP or CRX output, select a destination, and generate the package.

The exported theme uses Chromium Manifest V3 theme format.

## Development

### Requirements

- Windows 10/11 for the packaged application
- Python 3.10+ for development
- PySide6
- PyInstaller for packaging

### Run from source

```bash
git clone https://github.com/celestemadeline857-a11y/Chromium-Theme-Studio.git
cd Chromium-Theme-Studio
python -m pip install -r requirements.txt
python main.py
```

### Build locally

```bash
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --windowed --onedir --name ChromiumThemeStudio main.py
```

The packaged application will be in `dist/ChromiumThemeStudio/`.

## GitHub Actions build

Go to **Actions → Build Windows EXE → Run workflow**. The resulting `ChromiumThemeStudio-Windows.zip` is uploaded as a workflow artifact.

To create a release build, push a tag such as:

```bash
git tag v3.0.0
git push origin v3.0.0
```

The workflow then attaches the Windows ZIP to the generated GitHub Release.

## Versioning

Current version: **v3.0.0**

See [CHANGELOG.md](CHANGELOG.md) for the release history.

## License

See [LICENSE](LICENSE).
