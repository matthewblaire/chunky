#!/usr/bin/env python3
"""
version.py - Single source of truth for the Chunky version number
"""

# Update this value when releasing a new version
VERSION = "1.1.1"

# Helper function to get the version string
def get_version():
    return VERSION

# Helper function to get the version tag (e.g., "v1.2.0")
def get_version_tag():
    return f"v{VERSION}"

if __name__ == "__main__":
    # When run directly, print the version
    print(VERSION)
