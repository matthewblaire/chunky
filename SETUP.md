# Chunky Developer Setup

This document provides instructions for setting up the Chunky development environment and preparing it for distribution.

## Project Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/matthewblaire/chunky.git
   cd chunky
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller build twine pytest
   ```

## Building Executables Locally

To build the executable on your local machine:

```bash
pyinstaller --onefile --name chunky chunky.py
```

The executable will be created in the `dist` directory.

## Creating a Release

1. Update version numbers in:
   - `chunky.py` (VERSION constant)
   - `install.py` (VERSION constant)
   - `pyproject.toml`

2. Commit your changes:
   ```bash
   git add .
   git commit -m "Prepare release v1.0.0"
   ```

3. Tag the release:
   ```bash
   git tag v1.0.0
   git push origin main v1.0.0
   ```

4. GitHub Actions will automatically build the executables for all platforms.

5. Go to GitHub releases, create a new release from the tag, and add release notes.

## Publishing to PyPI (Optional)

If you want to make Chunky installable via pip:

```bash
python -m build
python -m twine upload dist/*
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Updating the Installer

If you change the release structure or file naming, make sure to update:

1. The installer script (`install.py`)
2. The GitHub workflow file (`.github/workflows/build.yml`)

## Troubleshooting Common Issues

### Missing Dependencies in PyInstaller Builds

If PyInstaller fails to include dependencies, use the `--hidden-import` flag:

```bash
pyinstaller --onefile --name chunky --hidden-import pathspec chunky.py
```

### Cross-Platform Path Issues

Always use `Path` from `pathlib` for cross-platform path handling. Avoid using string concatenation for paths.

### GitHub Actions Failures

If GitHub Actions fail to build the executables:

1. Check the workflow logs
2. Verify the Python version and dependencies
3. Make sure the repository has the correct secrets set up for GitHub releases