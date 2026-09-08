with open('scripts/build_advanced_technical_html.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = -1
end_line = -1

for i, line in enumerate(lines):
    if 'BUY RADAR & AUTOMATED SIGNAL PROGRESS TRACKER ENGINE' in line:
        start_line = i
        break

for i in range(start_line, len(lines)):
    if 'function applyLiveQuotes(quotes)' in lines[i]:
        end_line = i
        break

print(f"Found radar block: lines {start_line+1} to {end_line}")

new_lines = lines[:start_line] + [
    "\n    // =========================================================================\n",
    "    // MODULAR INSTITUTIONAL BUY RADAR ENGINE (PARTS 1, 2, 3)\n",
    "    // =========================================================================\n",
    "__RADAR_MODULES_INJECTION__\n\n"
] + lines[end_line:]

with open('scripts/build_advanced_technical_html.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Replaced inline radar block with __RADAR_MODULES_INJECTION__ placeholder successfully!")
