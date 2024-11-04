def modify_gcode(input_file, output_file, multiplier):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Ensure the file has enough lines to process
    if len(lines) <= 9:
        raise ValueError("The file does not have enough lines to process according to the given criteria.")

    # Copy the first 3 lines and last 6 lines
    header = lines[:3]
    footer = lines[-6:]
    content = lines[3:-6]

    modified_lines = []

    for line in content:
        if line.startswith('G1'):
            parts = line.split()
            new_parts = []
            for part in parts:
                if part.startswith('X'):
                    x_value = float(part[1:]) * multiplier
                    new_parts.append(f'X{x_value:.4f}')
                elif part.startswith('Y'):
                    y_value = float(part[1:]) * multiplier
                    new_parts.append(f'Y{y_value:.4f}')
                elif part.startswith('Z'):
                    z_value = float(part[1:]) * multiplier
                    new_parts.append(f'Z{z_value:.4f}')
                elif part.startswith('A'):
                    # Skip the 'A' value
                    continue
                else:
                    new_parts.append(part)
            modified_line = ' '.join(new_parts)
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line.strip())

    # Combine all parts into final content
    final_content = header + [line + '\n' for line in modified_lines] + footer

    with open(output_file, 'w') as file:
        file.writelines(final_content)

# Example usage
input_file = 'abc.gcode'
output_file = 'abd.gcode'
multiplier = 5.0  # Adjust the multiplier as needed
modify_gcode(input_file, output_file, multiplier)
