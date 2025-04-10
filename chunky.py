#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

try:
    import pathspec
except ImportError:
    print("The pathspec module is not installed. Run 'pip install pathspec'")
    sys.exit(1)


def load_ignore_spec(folder: Path, ignore_filename=".chunkyignore"):
    """
    Load ignore patterns from the ignore file (if present) and compile them using pathspec.

    Args:
        folder (Path): The folder to look for the ignore file.
        ignore_filename (str): The name of the ignore file.
        
    Returns:
        A compiled pathspec object for matching ignored files.
    """
    ignore_file = folder / ignore_filename
    if not ignore_file.exists():
        return None

    with ignore_file.open("r") as f:
        lines = f.read().splitlines()

    # Compile patterns using GitIgnorePattern (see pathspec docs for more information)
    spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return spec


def list_files(folder: Path, ignore_spec):
    """
    Recursively list all files in folder (as Path objects) that are not matched by the ignore spec.
    
    Args:
        folder (Path): The root folder to search.
        ignore_spec: A compiled pathspec object for filtering out ignored files, or None.
    
    Returns:
        A list of Path objects representing files to be chunked.
    """
    all_files = []
    # Use rglob to search recursively for files
    for file in folder.rglob("*"):
        if file.is_file():
            # Create the path relative to the folder root (so that ignore patterns work correctly)
            rel_path = file.relative_to(folder)
            # If we have an ignore spec, check if the file should be ignored
            if ignore_spec and ignore_spec.match_file(str(rel_path)):
                continue
            all_files.append(file)
    # Optionally sort the files; here we sort by relative path
    return sorted(all_files, key=lambda p: str(p))


def chunk_files(files, n_chunks):
    """
    Divide the list of file paths into n_chunks groups. Files are NOT split in half; each file's
    entire content remains intact.
    
    This function partitions the file list into as equal slices as possible.
    
    Args:
        files (list): List of file paths to be chunked.
        n_chunks (int): Number of output chunks.
        
    Returns:
        A list of lists, where each sublist is a group of file paths.
    """
    chunks = [[] for _ in range(n_chunks)]
    # Simple round-robin assignment ensures files are not split across chunks.
    for index, file in enumerate(files):
        chunks[index % n_chunks].append(file)
    return chunks


def write_chunk(chunk, output_path, folder_root: Path):
    """
    Write one output chunk file which contains the data of all files in that chunk.
    Before and after each file's content, insert tags with the file's relative path info.
    
    Args:
        chunk (list): List of Path objects (files) belonging to this chunk.
        output_path (Path): The file path to write the chunk data.
        folder_root (Path): The original root folder for proper relative tagging.
    """
    with output_path.open("w", encoding="utf-8") as out_f:
        for file_path in chunk:
            # Get file's relative path from the folder root
            rel_file_path = file_path.relative_to(folder_root)
            # Write pre-file tag (you can change the tag format if desired)
            out_f.write(f"<<<START: {rel_file_path}>>>\n")
            try:
                with file_path.open("r", encoding="utf-8") as in_f:
                    content = in_f.read()
                out_f.write(content)
            except Exception as e:
                # It is useful to log errors if a file could not be read
                out_f.write(f"[Error reading file: {e}]\n")
            # Write post-file tag
            out_f.write(f"\n<<<END: {rel_file_path}>>>\n\n")
            

def parse_arguments():
    """
    Parse command-line arguments: the number of chunks and folder path.
    """
    parser = argparse.ArgumentParser(description="Chunkifier: divide files in a folder into chunks without splitting file contents.")
    parser.add_argument("chunks", type=int, help="Number of output text files (chunks)")
    parser.add_argument("folder", type=str, help="Path to the folder to be chunked")
    parser.add_argument("--output-prefix", type=str, default="chunk", help="Prefix for output files (default 'chunk')")
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    folder_path = Path(args.folder)
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: The folder path '{folder_path}' does not exist or is not a directory.")
        sys.exit(1)

    # Load ignore spec from .chunkyignore if it exists in the root folder
    ignore_spec = load_ignore_spec(folder_path)

    # List all non-ignored files in the folder (recursively)
    files = list_files(folder_path, ignore_spec)
    if not files:
        print("No files found for chunking after applying ignore rules.")
        sys.exit(0)

    # Divide files into specified number of chunks
    n_chunks = args.chunks
    chunks = chunk_files(files, n_chunks)

    # Write out each chunk to a separate text file
    output_dir = folder_path / "chunks"
    output_dir.mkdir(exist_ok=True)  # Create the 'chunks' directory if it doesn't exist

    for i, chunk in enumerate(chunks, start=1):
        output_filename = f"{args.output_prefix}_{i}.txt"
        output_path = output_dir / output_filename
        write_chunk(chunk, output_path, folder_path)
        print(f"Wrote {len(chunk)} files to {output_path}")

        
if __name__ == "__main__":
    main()
