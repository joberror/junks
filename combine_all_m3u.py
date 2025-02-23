import os
import sys

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

# Clear the output file first
print(f"\nClearing output file: {output_file}")
try:
    with open(output_file, "w", encoding='utf-8') as outfile:
        outfile.write("#EXTM3U\n")  # Write only the header
        print("Successfully wrote header to output file")
except Exception as e:
    print(f"Error clearing output file: {str(e)}")
    sys.exit(1)

# Read all .m3u files and combine their contents
print("\nStarting to combine files...")
try:
    with open(output_file, "a", encoding='utf-8') as outfile:
        for idx, filename in enumerate(m3u_files, 1):
            file_path = os.path.join(directory, filename)
            print(f"\nProcessing file {idx}/{len(m3u_files)}: {filename}")
            
            try:
                with open(file_path, "r", encoding='utf-8') as infile:
                    content = infile.readlines()
                    print(f"Read {len(content)} lines from {filename}")
                    
                    if not content:
                        print(f"Warning: {filename} is empty")
                        continue
                    
                    # Skip the first line if it's #EXTM3U
                    start_idx = 1 if content[0].strip() == "#EXTM3U" else 0
                    print(f"Starting from line {start_idx+1}")
                    
                    # Write the content
                    lines_written = 0
                    for line in content[start_idx:]:
                        outfile.write(line)
                        lines_written += 1
                    
                    # Add two newlines between files (except for the last file)
                    if idx < len(m3u_files):
                        outfile.write("\n\n")
                        lines_written += 2
                    
                    print(f"Wrote {lines_written} lines to output file")
                    
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

    print(f"\nFinished processing all files")
    
    # Verify the output file
    output_size = os.path.getsize(output_file)
    print(f"\nOutput file size: {output_size} bytes")
    
    if output_size <= 8:  # "#EXTM3U\n" is 8 bytes
        print("Warning: Output file appears to be empty (contains only header)")
    else:
        # Read and print the first few lines of the output file to verify content
        print("\nVerifying output file content:")
        with open(output_file, "r", encoding='utf-8') as f:
            first_few_lines = [next(f) for _ in range(5)]
            print("First few lines of output file:")
            for line in first_few_lines:
                print(f"> {line.strip()}")
    
except Exception as e:
    print(f"Error writing to output file: {str(e)}")
    sys.exit(1)

print("\nScript completed!")
