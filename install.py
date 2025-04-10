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

VERSION = "1.0.0"
GITHUB_RELEASES_URL = "https://github.com/matthewblaire/chunky/releases/download"
RELEASE_TAG = f"v{VERSION}"

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
    if platform_name == "windows":
        # Check if the directory is in the user's PATH
        path_var = os.environ.get('PATH', '')
        if install_dir.lower() not in [p.lower() for p in path_var.split(os.pathsep)]:
            try:
                # Use PowerShell to update the PATH permanently
                ps_command = f'[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{install_dir}", "User")'
                subprocess.run(["powershell", "-Command", ps_command], check=True)
                print(f"Added {install_dir} to your PATH")
                return True
            except Exception as e:
                print(f"Warning: Could not add directory to PATH: {e}")
                print(f"Please manually add {install_dir} to your PATH")
                return False
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
                return False
            
            # Append to shell rc file
            try:
                with open(rc_file, 'a') as f:
                    f.write(f'\n# Added by Chunky installer\nexport PATH="$PATH:{install_dir}"\n')
                print(f"Added {install_dir} to your PATH in {rc_file}")
                print("Please restart your terminal or run 'source ~/.bashrc' to use chunky")
                return True
            except Exception as e:
                print(f"Warning: Could not update {rc_file}: {e}")
                print(f"Please manually add {install_dir} to your PATH")
                return False
    
    return True  # Already in PATH

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
        return False

def main():
    print("=== Chunky Installer ===")
    
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
        update_path(install_dir, platform_name)
        
        # Verify installation
        check_installation(binary_dest, platform_name)
        
        print("\nYou now have chunky! Check installation by running: chunky --version")

if __name__ == "__main__":
    main()