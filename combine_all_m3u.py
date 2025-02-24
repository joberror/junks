import os
import sys
import re

def extract_group_title(line):
    """Extract group-title from EXTINF line."""
    match = re.search(r'group-title="([^"]+)"', line)
    return match.group(1) if match else ""

def sort_playlist_entries(content):
    """Sort playlist entries by group-title."""
    if not content:
        return []
    
    # Initialize variables
    entries = []
    current_entry = []
    
    # Group lines into entries (EXTINF line + URL line)
    for line in content:
        current_entry.append(line)
        if len(current_entry) == 2:  # We have a complete entry
            entries.append(current_entry)
            current_entry = []
    
    # If there's a leftover line, add it
    if current_entry:
        entries.append(current_entry)
    
    # Sort entries based on group-title
    entries.sort(key=lambda x: extract_group_title(x[0]))
    
    # Flatten the entries back into lines
    sorted_content = []
    for entry in entries:
        sorted_content.extend(entry)
    
    return sorted_content

directory = "m3u"  # Directory containing .m3u files
output_file = "all.m3u"  # Output file name

print(f"\nStarting script...")
print(f"Looking for .m3u files in directory: {os.path.abspath(directory)}")

# Check if directory exists
if not os.path.exists(directory):
    print(f"Error: Directory '{directory}' does not exist")
    sys.exit(1)

# Get list of .m3u files, excluding the output file
m3u_files = [f for f in os.listdir(directory) if f.endswith('.m3u') and f != output_file]

if not m3u_files:
    print(f"Error: No .m3u files found in directory '{directory}'")
    sys.exit(1)

print(f"\nFound {len(m3u_files)} .m3u files:")
for file in m3u_files:
    print(f"- {file}")

# Collect all content first
all_content = []
print("\nReading all files...")
for idx, filename in enumerate(m3u_files, 1):
    file_path = os.path.join(directory, filename)
    print(f"\nProcessing file {idx}/{len(m3u_files)}: {filename}")
    
    try:
        with open(file_path, "r", encoding='utf-8') as infile:
            # Read all lines and filter out empty ones and #EXTM3U
            content = [line.strip() + '\n' for line in infile.readlines() 
                      if line.strip() and line.strip() != "#EXTM3U"]
            print(f"Read {len(content)} non-empty lines from {filename}")
            
            if content:
                all_content.extend(content)
            else:
                print(f"Warning: {filename} is empty or contains only empty lines")
                
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        continue

# Sort all content
print("\nSorting playlist entries...")
sorted_content = sort_playlist_entries(all_content)

# Write sorted content to output file
print(f"\nWriting sorted content to {output_file}")
try:
    with open(output_file, "w", encoding='utf-8') as outfile:
        # Write header
        outfile.write("#EXTM3U\n")
        
        # Write sorted content
        for line in sorted_content:
            outfile.write(line)
    
    # Verify the output file
    output_size = os.path.getsize(output_file)
    print(f"\nOutput file size: {output_size} bytes")
    
    if output_size <= 8:  # "#EXTM3U\n" is 8 bytes
        print("Warning: Output file appears to be empty (contains only header)")
    else:
        # Read and print the first few lines of the output file to verify content
        print("\nVerifying output file content:")
        with open(output_file, "r", encoding='utf-8') as f:
            first_few_lines = [next(f) for _ in range(min(10, len(sorted_content) + 1))]
            print("First few lines of output file:")
            for line in first_few_lines:
                print(f"> {line.strip()}")
    
except Exception as e:
    print(f"Error writing to output file: {str(e)}")
    sys.exit(1)

print("\nScript completed!")
