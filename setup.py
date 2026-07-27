from pathlib import Path

ROOT = Path(__file__).parent

directories = [
    "src",
    "src/gui",
    "src/map",
    "src/map/web",
    "src/map/web/css",
    "src/map/web/js",
    "src/map/web/leaflet",
    "src/project",
    "src/importer",
    "src/exporter",
    "src/core",
    "src/widgets",
    "data",
    "projects",
    "tests",
]

files = {
    "README.md": "# TPF2 Map Studio\n",
    ".gitignore": """.venv/
__pycache__/
*.pyc
.vscode/
.idea/
""",
    "requirements.txt": """PySide6==6.7.2
requests==2.32.3
""",
}

init_files = [
    "src/__init__.py",
    "src/gui/__init__.py",
    "src/map/__init__.py",
    "src/project/__init__.py",
    "src/importer/__init__.py",
    "src/exporter/__init__.py",
    "src/core/__init__.py",
    "src/widgets/__init__.py",
]

for directory in directories:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

for filename, content in files.items():
    path = ROOT / filename
    if not path.exists():
        path.write_text(content, encoding="utf-8")

for filename in init_files:
    path = ROOT / filename
    if not path.exists():
        path.write_text("", encoding="utf-8")

print("✅ Projektstruktur erfolgreich erstellt.")