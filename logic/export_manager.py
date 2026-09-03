from __future__ import annotations

import json
import os
import tempfile
import zipfile

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QMessageBox


class ExportManager:
    @staticmethod
    def run_export_process(parent_window, theme_data, export_data, p_settings, renderer, is_log_enabled):
        dest_path = export_data["dest_path"]
        fmt = export_data["format"]
        try:
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            with tempfile.TemporaryDirectory() as tmp_dir:
                images_dir = os.path.join(tmp_dir, "images")
                os.makedirs(images_dir, exist_ok=True)
                version = ExportManager._normalize_version(export_data.get("meta_version", "3.0.0"))
                if p_settings.get_auto_increment():
                    parts = version.split(".")
                    parts[-1] = str(int(parts[-1]) + 1)
                    version = ".".join(parts)

                transparent = QPixmap(1, 1)
                transparent.fill(Qt.transparent)
                overlay = os.path.join(images_dir, "theme_frame_overlay.png")
                transparent.save(overlay, "PNG")

                colors = {
                    "frame": ExportManager._hex_to_rgb_list(theme_data.get("frame", "#CC0000FF")),
                    "toolbar": ExportManager._hex_to_rgb_list(theme_data.get("toolbar", "#FFFFFFFF")),
                    "tab_text": ExportManager._hex_to_rgb_list(theme_data.get("tab_text", "#000000FF")),
                    "tab_background_text": ExportManager._hex_to_rgb_list(theme_data.get("inactive_tab_text", "#555555FF")),
                    "tab_background": ExportManager._hex_to_rgb_list(theme_data.get("inactive_tab", "#E68A8AFF")),
                    "bookmark_text": ExportManager._hex_to_rgb_list(theme_data.get("bookmark_text", "#555555FF")),
                    "ntp_text": ExportManager._hex_to_rgb_list(theme_data.get("toolbar_text", "#333333FF")),
                    "button_background": [0, 0, 0, 0],
                    "omnibox_background": ExportManager._hex_to_rgb_list(theme_data.get("omnibox_background", "#F0F0F0FF")),
                    "omnibox_text": ExportManager._hex_to_rgb_list(theme_data.get("omnibox_text", "#000000FF")),
                    "ntp_background": ExportManager._hex_to_rgb_list(theme_data.get("ntp_background", "#FFFFFFFF")),
                }
                if theme_data.get("frame_incognito"):
                    colors["frame_incognito"] = ExportManager._hex_to_rgb_list(theme_data["frame_incognito"])
                if theme_data.get("frame_incognito_inactive"):
                    colors["frame_incognito_inactive"] = ExportManager._hex_to_rgb_list(theme_data["frame_incognito_inactive"])

                images = {
                    "theme_frame_overlay": "images/theme_frame_overlay.png",
                    "theme_window_control_background": "images/theme_frame_overlay.png",
                }
                ExportManager._add_image(theme_data, renderer, "frame_image", images_dir, images, "theme_frame.png")
                ExportManager._add_image(theme_data, renderer, "ntp_image", images_dir, images, "theme_ntp_background.png")
                ExportManager._add_image(theme_data, renderer, "frame_image_incognito", images_dir, images, "theme_frame_incognito.png")

                manifest = {
                    "manifest_version": 3,
                    "version": version,
                    "name": export_data.get("meta_name") or "Untitled Theme",
                    "description": export_data.get("meta_desc") or "Chromium Theme Studio theme",
                    "theme": {"colors": colors, "images": images},
                }
                if "theme_ntp_background" in images:
                    manifest["theme"]["properties"] = {"ntp_background_alignment": "center", "ntp_background_repeat": "no-repeat"}

                with open(os.path.join(tmp_dir, "manifest.json"), "w", encoding="utf-8") as fh:
                    json.dump(manifest, fh, indent=None if is_log_enabled else 4)

                temp_zip = dest_path if fmt == "zip" else os.path.splitext(dest_path)[0] + ".zip"
                with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as archive:
                    for root, _, files in os.walk(tmp_dir):
                        for filename in files:
                            path = os.path.join(root, filename)
                            archive.write(path, os.path.relpath(path, tmp_dir))

                if fmt == "crx":
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    os.replace(temp_zip, dest_path)
                message = "CRX" if fmt == "crx" else "ZIP"
                QMessageBox.information(parent_window, f"{message} generated", f"Theme package saved to:\n{dest_path}")
                if os.name == "nt" and p_settings.get_val("open_after_export", "true") in (True, "true"):
                    os.startfile(os.path.dirname(os.path.abspath(dest_path)))
        except Exception as exc:
            QMessageBox.critical(parent_window, "Export failed", f"An error occurred while exporting:\n{exc}")

    @staticmethod
    def _add_image(theme_data, renderer, key, images_dir, images, output_name):
        if not theme_data.get(key):
            return
        pix = renderer.get_processed_pixmap(key)
        if pix and not pix.isNull():
            output = os.path.join(images_dir, output_name)
            pix.save(output, "PNG")
            manifest_key = {
                "frame_image": "theme_frame",
                "ntp_image": "theme_ntp_background",
                "frame_image_incognito": "theme_frame_incognito",
            }[key]
            images[manifest_key] = f"images/{output_name}"
            if key.startswith("frame_image"):
                inactive_key = "theme_frame_incognito_inactive" if key == "frame_image_incognito" else "theme_frame_inactive"
                images[inactive_key] = f"images/{output_name}"

    @staticmethod
    def _normalize_version(version):
        raw = str(version).strip().lstrip("v")
        parts = raw.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            return "3.0.0"
        return ".".join(str(int(part)) for part in parts)

    @staticmethod
    def _hex_to_rgb_list(hex_str):
        c = ExportManager.color_from_rgba_hex(hex_str)
        return [c.red(), c.green(), c.blue()]

    @staticmethod
    def color_from_rgba_hex(text):
        if not isinstance(text, str) or not text.startswith("#"):
            return QColor(255, 255, 255, 255)
        if len(text) == 7:
            text += "FF"
        if len(text) != 9:
            return QColor(255, 255, 255, 255)
        try:
            return QColor(int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16), int(text[7:9], 16))
        except ValueError:
            return QColor(255, 255, 255, 255)
