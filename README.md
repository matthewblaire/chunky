# Chunky - Simple File Chunking Tool

![GitHub release (latest by date)](https://img.shields.io/github/v/release/matthewblaire/chunky)
![GitHub all releases](https://img.shields.io/github/downloads/matthewblaire/chunky/total)
![License](https://img.shields.io/github/license/matthewblaire/chunky)

Chunky is a command-line tool that divides files in a folder into chunks without splitting file contents. This is useful for processing large collections of files in parallel or for fitting files into size constraints.

## Features

- Divides files across multiple output chunks without breaking up individual files
- Recursive directory traversal
- Supports ignoring files with `.chunkyignore` (GitIgnore-style patterns) in any directory
- Each `.chunkyignore` file only affects its directory and subdirectories
- Automatically ignores Chunky-related files and folders
- Automatically opens the output folder after completion
- Cross-platform: works on Windows, macOS, and Linux
- Simple installation process

## Installation

### Quick Install (Recommended)

**One-line install:**

```bash
# For macOS/Linux
curl -sSL https://raw.githubusercontent.com/matthewblaire/chunky/master/install.py | python3

# For Windows (PowerShell)
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/matthewblaire/chunky/master/install.py -UseBasicParsing).Content | python
```

### Manual Install Steps

1. Download the installer script:
   ```bash
   # For macOS/Linux
   curl -O https://raw.githubusercontent.com/matthewblaire/chunky/master/install.py
   
   # For Windows (PowerShell)
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/matthewblaire/chunky/master/install.py -OutFile install.py
   ```

2. Run the installer:
   ```bash
   python3 install.py  # Use 'python' on Windows
   ```

3. Verify installation:
   ```bash
   chunky --version
   ```

   > **Note**: You may need to restart your terminal or command prompt before the `chunky` command is available in your PATH.
   > 
   > If the command isn't found, either restart your terminal session or use the full path to the executable:
   > - Windows: `%LOCALAPPDATA%\Programs\Chunky\chunky.exe --version`
   > - macOS/Linux: `~/.local/bin/chunky --version`

If you see `Chunky version 1.1.1` (or similar), the installation was successful!

### Direct Download Option

If you prefer to download the binaries directly:

1. Visit the [releases page](https://github.com/matthewblaire/chunky/releases)
2. Download the appropriate file for your system:
   - Windows: `chunky-windows-1.1.1.zip`
   - macOS: `chunky-mac-1.1.1.tar.gz`
   - Linux: `chunky-linux-1.1.1.tar.gz`
3. Extract the file and place the executable in your PATH

## Usage

Basic usage:

```bash
chunky path/to/folder --chunks 5
```

This command will:
1. Find all files in the specified folder (recursively)
2. Divide them into 5 chunks
3. Create a `chunkies` subfolder with the chunked files
4. Automatically open the folder with the chunk files

### Options

```
chunky --help
```

Available options:
- `--chunks`, `-c`: Number of output chunks (default: 2)
- `--output-prefix`: Prefix for output files (default: "chunk")
- `--version`, `-v`: Show version and exit

### Ignoring Files

Create a `.chunkyignore` file in any directory to exclude files using gitignore-style patterns. Each `.chunkyignore` file affects only its own directory and subdirectories:

```
# Ignore all log files
*.log

# Ignore the node_modules directory
node_modules/

# Ignore specific files
secrets.txt
```

Note: Chunky automatically ignores the `.chunkyignore` file itself and anything in the `chunkies` folder.

## Examples

```bash
# Split a project into 3 chunks
chunky my_project --chunks 3

# Split with custom output file naming
chunky documents --chunks 4 --output-prefix document_set

# Check version
chunky --version
```

## How It Works

Chunky uses a round-robin algorithm to distribute files across chunks, ensuring that:

1. Files are never split across chunks (each file remains whole)
2. Files are distributed as evenly as possible among chunks
3. Each chunk contains the complete file contents with metadata tags

## Building from Source

To build from source:

```bash
# Clone the repository
git clone https://github.com/matthewblaire/chunky.git
cd chunky

# Install dependencies
pip install -r requirements.txt

# Run the script directly
python chunky.py path/to/folder --chunks 3

# Or build binaries with PyInstaller
pip install pyinstaller
pyinstaller --onefile --name chunky chunky.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see the LICENSE file for details.