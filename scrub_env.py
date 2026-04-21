import os
import re

workspace = r"f:\apptimus\envoy\agentic_coding"
exclude_dirs = {'node_modules', '.git', '.venv', 'venv', '__pycache__', '.next', 'dist', 'build'}

def scrub_line(line):
    # If the line is empty or a comment, return as is
    if not line.strip() or line.strip().startswith('#'):
        return line
    
    # Process KEY=VALUE lines
    if '=' in line:
        key, _ = line.split('=', 1)
        return f"{key}=\n"
        
    # Process YAML KEY: VALUE lines
    if ':' in line and not line.strip().startswith('apiVersion') and not line.strip().startswith('kind') and not line.strip().startswith('metadata') and not line.strip().startswith('name') and not line.strip().startswith('namespace') and not line.strip().startswith('data'):
        # Just find the first colon and replace everything after it
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0]
            # preserve original leading whitespace for yaml
            leading_space = len(line) - len(line.lstrip())
            return (" " * leading_space) + f"{key.strip()}: \"REDACTED\"\n"
            
    return line

for root, dirs, files in os.walk(workspace):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for file in files:
        if file.endswith('.example') or file.startswith('.env'):
            file_path = os.path.join(root, file)
            if '.env' in file:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = [scrub_line(line) for line in lines]
                        
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"Scrubbed: {file_path}")

print("Done scrubbing.")
