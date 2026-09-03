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
- Image transforms use persistent scale/X/Y properties.
- Added render-cache invalidation when replacing or removing images.

### UI/UX
- Unified light and dark styling into one consistent design system.
- Standardized buttons, inputs, tabs, group boxes, spacing, and typography.
- Added a reusable custom-resolution dialog.
- Simplified the preview toolbar and resolution controls.
- Cleaner browser selector, Incognito control, and fullscreen workflow.

### Build and release
- Added `requirements.txt` for reproducible installs.
- Added a GitHub Actions workflow at `.github/workflows/build-windows.yml`.
- The workflow compiles the Python sources, runs regression tests, then builds a single-file `ChromiumThemeStudio.exe`.
- Manual builds are available from **Actions → Build Windows EXE → Run workflow**.
- Pushing a version tag such as `v3.0.0` also uploads the build to a GitHub Release.

## Features

Live browser preview, Chrome/Brave/Edge skins, Incognito variants, color editing with RGBA and hex input, image overlays, drag-and-drop imports, presets, Undo/Redo, fullscreen preview, Spotlight FX, custom resolution, and ZIP/CRX-style theme packaging.

## Installation

Download `ChromiumThemeStudio-Windows.zip` from a GitHub Actions run or release, extract it, and run `ChromiumThemeStudio.exe`.

## Using the editor

Choose a browser from the preview header, select an editable property from the left panel, then adjust its controls on the right.

For images, select **Frame Image** or **NTP Image** and either choose **Select Image** or drop an image directly onto the preview canvas. Use Scale, X, and Y to position it without stretching the source.

Use the resolution buttons for 16:9, 21:9, or **Custom**. F11 toggles fullscreen preview and Esc exits it.

## Exporting a theme

Open **Export**, enter the theme metadata, choose ZIP or CRX output, select a destination, and generate the package.

The exported package uses Chromium Manifest V3 theme format. The CRX option currently produces the packaged theme archive using the application's existing ZIP-based export path; browser-specific CRX signing/packing is not performed by the editor.

## Development

### Requirements

- Python 3.10+
- PySide6
- PyInstaller
- pytest

### Run from source

```bash
git clone https://github.com/celestemadeline857-a11y/Chromium-Theme-Studio.git
cd Chromium-Theme-Studio
python -m pip install -r requirements.txt
python main.py
```

### Run tests

```bash
python -m pytest -q
```

### Build locally

```bash
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --onefile --windowed --name ChromiumThemeStudio main.py
```

The executable will be written to `dist/ChromiumThemeStudio.exe`.

## GitHub Actions build

Go to **Actions → Build Windows EXE → Run workflow**. The workflow will compile the sources, run the regression tests, build the single-file Windows executable, and upload `ChromiumThemeStudio-Windows.zip` as an artifact.

To trigger the release step, push a version tag such as:

```bash
git tag v3.0.0
git push origin v3.0.0
```

The tagged workflow attaches the Windows ZIP to the GitHub Release.

## Versioning

Current version: **v3.0.0**

See [CHANGELOG.md](CHANGELOG.md) for the complete release history.

## Repository security

The current connected GitHub integration does not provide repository-visibility, collaborator, or branch-protection/ruleset write operations. Those settings must therefore be applied in GitHub's repository settings by an account with the required administrative permissions.

For the strongest setup after merging v3, make the repository **Private**, then protect `main` with required pull requests/reviews and disable direct pushes for everyone except your chosen administrators.

## License

See [LICENSE](LICENSE).
