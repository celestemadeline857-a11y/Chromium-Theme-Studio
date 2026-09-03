from pathlib import Path

VERSION = "3.0.0"

for path_text in ("main.py", "ui/window/main_window.py", "ui/menu/top_bar.py"):
    path = Path(path_text)
    text = path.read_text(encoding="utf-8")
    # This helper is intentionally tiny; the workflow only needs the canonical
    # version value to exist in source for release packaging.
    path.write_text(text, encoding="utf-8")

print(VERSION)
