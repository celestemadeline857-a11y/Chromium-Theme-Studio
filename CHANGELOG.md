# Changelog

All notable changes to Chromium Theme Studio are documented here.

## [v3.0.0] - 2026-09-03

### Fixed
- Fixed first-launch and refresh-time preview layering glitches.
- Fixed browser chrome being rendered behind or inconsistently with background imagery.
- Fixed text positioning and clipping in the browser preview.
- Fixed image cache behavior when replacing/removing images.
- Fixed image preview stretching in the editor.
- Fixed several light/dark UI inconsistencies.
- Fixed preview-target synchronization so the editor and settings page use the same browser selection.

### Improved
- Replaced the multi-layer QLabel preview composition with a deterministic single-pass compositor.
- Added browser-specific preview metrics for Chrome, Brave, and Edge.
- Improved RGBA/hex input handling and color synchronization.
- Improved canvas resizing and fullscreen restoration.
- Improved image import validation and added WebP support.
- Added safer large-image downscaling.
- Consolidated light and dark UI styling into one design system.
- Improved editor spacing, controls, labels, and resolution controls.

### Build
- Added `requirements.txt` with pinned major-version ranges for PySide6 and PyInstaller.
- Added `.github/workflows/build-windows.yml` for Windows EXE builds.
- Manual workflow runs are available from GitHub Actions.
- Version tags (`v*`) create release assets automatically.

### Documentation
- Rewritten README with installation, development, build, export, and Actions instructions.

## [v2.3.8] - 2025-12-25

### Fixed
- Final v2.3.8 bug-fix release.

## [v2.3.7] - 2025-12-24

### Added
- Spotlight FX with magnetic targets, shape morphing, and re-ignition behavior.
- Settings tabs for General, Appearance, and Advanced.
- Spotlight customization for radius, strength, opacity, and light/dark colors.

### Improved
- Gradient slider reliability.
- Button sizing and navigation controls.
- Light/dark text contrast and settings backgrounds.

## [v2.2.0] - 2025-12-23

### Added
- True fullscreen preview.
- NTP background and Omnibox customization.
- Incognito defaults.
- Updated preset collection.
- First-launch welcome message.

## [v2.1.0] - 2025-12-22

### Added
- Undo/Redo history.
- Centralized application styling.

## [v2.0.0] - 2025-12-20

### Major release
- Rewritten in PySide6.
- Modularized into UI, rendering, logic, and utility packages.
- Added live browser preview and drag-and-drop image support.
