#!/usr/bin/env python3
"""
update_version.py - Helper script to update Chunky version
This script handles updating the version.py file and can verify all files are in sync.
"""

import os
import sys
import re
from pathlib import Path

def get_current_version():
    """Read the current version from version.py"""
    try:
        # Try to import it directly
        from version import VERSION
        return VERSION
    except ImportError:
        # If that fails, try to parse the file
        try:
            with open("version.py", "r") as f:
                content = f.read()
                match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
        except:
            pass
    
    # Default if all else fails
    return "unknown"

def update_version(new_version):
    """Update the version in version.py"""
    try:
        with open("version.py", "r") as f:
            content = f.read()
        
        # Replace the version
        new_content = re.sub(
            r'(VERSION\s*=\s*")[^"]+(")' , 
            rf'\g<1>{new_version}\g<2>', 
            content
        )
        
        with open("version.py", "w") as f:
            f.write(new_content)
            
        print(f"✅ Updated version.py to version {new_version}")
        return True
    except Exception as e:
        print(f"❌ Failed to update version.py: {e}")
        return False

def update_readme(new_version):
    """Update version references in README.md"""
    try:
        if not os.path.exists("README.md"):
            print("❌ README.md not found")
            return False
            
        with open("README.md", "r") as f:
            content = f.read()
        
        # Update download links
        new_content = re.sub(
            r'chunky-(windows|mac|linux)-\d+\.\d+\.\d+', 
            rf'chunky-\1-{new_version}', 
            content
        )
        
        # Update version text
        new_content = re.sub(
            r'Chunky version \d+\.\d+\.\d+', 
            f'Chunky version {new_version}', 
            new_content
        )
        
        with open("README.md", "w") as f:
            f.write(new_content)
            
        print(f"✅ Updated README.md to version {new_version}")
        return True
    except Exception as e:
        print(f"❌ Failed to update README.md: {e}")
        return False

def check_version_consistency():
    """Check if all files reference the same version"""
    try:
        # Get the version from version.py
        current_version = get_current_version()
        if current_version == "unknown":
            print("❌ Could not determine current version from version.py")
            return False
        
        print(f"Current version in version.py: {current_version}")
        issues = []
        
        # Check chunky.py
        try:
            # First try importing to see if it's using the correct import
            import chunky
            if hasattr(chunky, "VERSION") and chunky.VERSION != current_version:
                issues.append(f"chunky.py has version {chunky.VERSION} (should be {current_version})")
        except:
            # If that fails, check the file directly
            if os.path.exists("chunky.py"):
                with open("chunky.py", "r") as f:
                    content = f.read()
                match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
                if match and match.group(1) != current_version:
                    issues.append(f"chunky.py has hardcoded version {match.group(1)} (should be {current_version})")
                elif not re.search(r'from version import VERSION', content):
                    issues.append("chunky.py is not importing VERSION from version.py")
        
        # Check install.py
        if os.path.exists("install.py"):
            with open("install.py", "r") as f:
                content = f.read()
            if not re.search(r'from version import VERSION', content):
                match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
                if match and match.group(1) != current_version:
                    issues.append(f"install.py has hardcoded version {match.group(1)} (should be {current_version})")
        
        # Check README.md for version references
        if os.path.exists("README.md"):
            with open("README.md", "r") as f:
                content = f.read()
            readme_versions = re.findall(r'chunky-(?:windows|mac|linux)-(\d+\.\d+\.\d+)', content)
            for v in readme_versions:
                if v != current_version:
                    issues.append(f"README.md references version {v} (should be {current_version})")
            
            # Check for other version references
            if f"Chunky version {current_version}" not in content:
                issues.append(f"README.md contains wrong version number in text")
        
        # Check pyproject.toml
        if os.path.exists("pyproject.toml"):
            with open("pyproject.toml", "r") as f:
                content = f.read()
            if 'dynamic = ["version"]' not in content and 'version = {attr = "version.VERSION"}' not in content:
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match and match.group(1) != current_version:
                    issues.append(f"pyproject.toml has hardcoded version {match.group(1)} (should be {current_version})")
        
        if issues:
            print("\n❌ Version inconsistencies found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("\n✅ All files are consistent with version", current_version)
            return True
            
    except Exception as e:
        print(f"❌ Error checking version consistency: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Chunky Version Manager")
        print(f"Current version: {get_current_version()}")
        print("\nUsage:")
        print("  python update_version.py check          # Check version consistency")
        print("  python update_version.py update X.Y.Z   # Update to version X.Y.Z")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        check_version_consistency()
    elif command == "update" and len(sys.argv) > 2:
        new_version = sys.argv[2]
        if not re.match(r'^\d+\.\d+\.\d+$', new_version):
            print("❌ Invalid version format. Please use X.Y.Z (e.g., 1.2.0)")
            return
        
        current = get_current_version()
        print(f"Updating version: {current} -> {new_version}")
        
        if update_version(new_version):
            # Also update README.md
            update_readme(new_version)
            
            print("\nRemember to:")
            print("1. Commit the changes to version.py and README.md")
            print("2. Tag the release: git tag v" + new_version)
            print("3. Push the tag: git push origin v" + new_version)
    else:
        print("❌ Unknown command. Use 'check' or 'update X.Y.Z'")

if __name__ == "__main__":
    main()