import os
import re

base_dir = "/home/darren/localdev/python/advent-of-code/src/AoC_2025"

def update_file(day_num):
    day_str = f"d{day_num:02d}"
    file_path = os.path.join(base_dir, day_str, f"{day_str}.py")
    
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} (not found)")
        return

    with open(file_path, 'r') as f:
        content = f.read()

    # Update YEAR
    content = re.sub(r'^YEAR = .*$', 'YEAR = 2025', content, flags=re.MULTILINE)
    
    # Update DAY
    content = re.sub(r'^DAY = .*$', f'DAY = {day_num}', content, flags=re.MULTILINE)
    
    # Update Docstring URL
    # Matches "Solving https://adventofcode.com/..." until end of line
    content = re.sub(r'Solving https://adventofcode\.com/.*$', f'Solving https://adventofcode.com/2025/day/{day_num}', content, flags=re.MULTILINE)

    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

def main():
    for i in range(1, 26):
        update_file(i)

if __name__ == "__main__":
    main()
