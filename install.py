#!/usr/bin/env python3
"""
Chunky Installer Script
-----------------------
This script automatically downloads and installs the appropriate
version of Chunky for your operating system.
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
import zipfile
import tarfile
import urllib.request
import hashlib

# Import version from version.py
try:
    from version import VERSION, get_version_tag
    RELEASE_TAG = get_version_tag()
except ImportError:
    # Fallback in case version.py is not accessible
    VERSION = "1.2.0"
    RELEASE_TAG = f"v{VERSION}"

GITHUB_RELEASES_URL = "https://github.com/matthewblaire/chunky/releases/download"

def get_platform():
    """Determine the current platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        print(f"Error: Unsupported platform: {system}")
        sys.exit(1)

def get_binary_url(platform_name):
    """Generate the URL for the appropriate binary."""
    if platform_name == "windows":
        filename = f"chunky-windows-{VERSION}.zip"
    elif platform_name == "mac":
        filename = f"chunky-mac-{VERSION}.tar.gz"
    elif platform_name == "linux":
        filename = f"chunky-linux-{VERSION}.tar.gz"
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")
    
    return f"{GITHUB_RELEASES_URL}/{RELEASE_TAG}/{filename}", filename

def download_file(url, filename):
    """Download a file with progress indicator."""
    print(f"Downloading {filename}...")
    try:
        with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
            file_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 8192
            
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                
                downloaded += len(buffer)
                out_file.write(buffer)
                
                # Update progress
                progress = int(50 * downloaded / file_size) if file_size > 0 else 0
                sys.stdout.write(f"\r[{'#' * progress}{'.' * (50 - progress)}] {downloaded}/{file_size} bytes")
                sys.stdout.flush()
        
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nError downloading file: {e}")
        return False

def verify_checksum(filename, expected_checksum=None):
    """Verify the file checksum if provided."""
    if not expected_checksum:
        return True  # Skip verification if no checksum provided
    
    print("Verifying file integrity...")
    sha256_hash = hashlib.sha256()
    
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    calculated_hash = sha256_hash.hexdigest()
    
    if calculated_hash == expected_checksum:
        print("Checksum verified!")
        return True
    else:
        print(f"Checksum verification failed! Expected: {expected_checksum}, Got: {calculated_hash}")
        return False

def extract_archive(filename, dest_dir):
    """Extract the downloaded archive."""
    print(f"Extracting {filename}...")
    
    try:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
        elif filename.endswith('.tar.gz'):
            with tarfile.open(filename, 'r:gz') as tar_ref:
                tar_ref.extractall(dest_dir)
        else:
            print(f"Unsupported archive format: {filename}")
            return False
        
        print("Extraction complete!")
        return True
    except Exception as e:
        print(f"Error extracting archive: {e}")
        return False

def get_binary_path(extract_dir, platform_name):
    """Find the binary in the extracted directory."""
    if platform_name == "windows":
        binary_path = next(Path(extract_dir).glob("**/chunky*.exe"), None)
    else:
        binary_path = next(Path(extract_dir).glob("**/chunky*"), None)
    
    if not binary_path:
        print(f"Error: Could not find chunky binary in {extract_dir}")
        return None
    
    return binary_path

def install_binary(binary_path, platform_name):
    """Install the binary to the appropriate location."""
    if platform_name == "windows":
        # On Windows, we'll use %LOCALAPPDATA%\Programs\Chunky
        install_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Programs', 'Chunky')
        binary_dest = os.path.join(install_dir, 'chunky.exe')
    else:
        # On Unix-like systems, we'll use ~/.local/bin
        install_dir = os.path.expanduser('~/.local/bin')
        binary_dest = os.path.join(install_dir, 'chunky')
    
    # Create the install directory if it doesn't exist
    os.makedirs(install_dir, exist_ok=True)
    
    # Copy the binary
    print(f"Installing Chunky to {binary_dest}...")
    shutil.copy2(binary_path, binary_dest)
    
    # Make the binary executable on Unix-like systems
    if platform_name != "windows":
        os.chmod(binary_dest, 0o755)
    
    return install_dir, binary_dest

def update_path(install_dir, platform_name):
    """Update the PATH environment variable if needed."""
    path_updated = False
    refresh_needed = False
    
    if platform_name == "windows":
        # Check if the directory is in the user's PATH
        path_var = os.environ.get('PATH', '')
        if install_dir.lower() not in [p.lower() for p in path_var.split(os.pathsep)]:
            try:
                # Use PowerShell to update the PATH permanently
                ps_command = f'[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{install_dir}", "User")'
                subprocess.run(["powershell", "-Command", ps_command], check=True)
                print(f"Added {install_dir} to your PATH")
                
                # Try to refresh the current session's PATH
                try:
                    # Update the current process environment
                    os.environ['PATH'] = f"{os.environ['PATH']}{os.pathsep}{install_dir}"
                    print("PATH refreshed for current session")
                    path_updated = True
                except Exception:
                    refresh_needed = True
                    
                return True, refresh_needed
            except Exception as e:
                print(f"Warning: Could not add directory to PATH: {e}")
                print(f"Please manually add {install_dir} to your PATH")
                return False, True
    else:
        # For Unix-like systems, check if ~/.local/bin is in PATH
        path_var = os.environ.get('PATH', '')
        if install_dir not in path_var.split(os.pathsep):
            # For bash/zsh users
            shell = os.environ.get('SHELL', '')
            if 'bash' in shell:
                rc_file = os.path.expanduser('~/.bashrc')
            elif 'zsh' in shell:
                rc_file = os.path.expanduser('~/.zshrc')
            else:
                print(f"Warning: Unsupported shell {shell}. Please manually add {install_dir} to your PATH")
                return False, True
            
            # Append to shell rc file
            try:
                with open(rc_file, 'a') as f:
                    f.write(f'\n# Added by Chunky installer\nexport PATH="$PATH:{install_dir}"\n')
                print(f"Added {install_dir} to your PATH in {rc_file}")
                
                # Try to update current session PATH
                os.environ['PATH'] = f"{os.environ['PATH']}{os.pathsep}{install_dir}"
                
                # Still need to source the rc file for a complete refresh
                print(f"To use chunky immediately, run: source {rc_file}")
                refresh_needed = True
                
                return True, refresh_needed
            except Exception as e:
                print(f"Warning: Could not update {rc_file}: {e}")
                print(f"Please manually add {install_dir} to your PATH")
                return False, True
    
    return True, False  # Already in PATH

def check_installation(binary_path, platform_name):
    """Verify the installation by running the version command."""
    try:
        result = subprocess.run([binary_path, "--version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        print(f"Installation successful! {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"Installation verification failed: {e}")
        if platform_name != "windows":
            print("Try running: chmod +x " + binary_path)
        
        # Add additional troubleshooting note
        print("\nIf you see 'command not found' errors when trying to run 'chunky',")
        print("this is likely because your PATH environment hasn't been updated in this session.")
        print("You can always run Chunky using the full path:")
        if platform_name == "windows":
            print(f"  {binary_path}")
        else:
            print(f"  {binary_path}")
        
        return False

def main():
    print("=== Chunky Installer ===")
    print(f"Installing Chunky version {VERSION}")
    
    # Determine platform
    platform_name = get_platform()
    print(f"Detected platform: {platform_name}")
    
    # Get the appropriate download URL
    download_url, filename = get_binary_url(platform_name)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the binary
        local_file = os.path.join(temp_dir, filename)
        if not download_file(download_url, local_file):
            sys.exit(1)
        
        # Extract the archive
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        if not extract_archive(local_file, extract_dir):
            sys.exit(1)
        
        # Get the binary path
        binary_path = get_binary_path(extract_dir, platform_name)
        if not binary_path:
            sys.exit(1)
        
        # Install the binary
        install_dir, binary_dest = install_binary(binary_path, platform_name)
        
        # Update PATH if needed
        _, refresh_needed = update_path(install_dir, platform_name)
        
        # Verify installation
        check_result = check_installation(binary_dest, platform_name)
        
        print("\nYou now have chunky!")
        
        if refresh_needed:
            print("\nIMPORTANT: You may need to restart your terminal or command prompt")
            print("before the 'chunky' command is available in your PATH.")
            print("\nAlternatively, you can run chunky directly using the full path:")
            print(f"  {binary_dest}")
        else:
            print("\nCheck installation by running: chunky --version")

if __name__ == "__main__":
    main()