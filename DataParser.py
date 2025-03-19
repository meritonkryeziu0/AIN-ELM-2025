import json
import re

def parse_dzn(file_path):
    with open(file_path, 'r') as file:
        data = file.read()

    parsed_data = {}

    pattern = r'(\w+)\s*=\s*(\[[^\]]*\]|\d+);'
    matches = re.findall(pattern, data, re.DOTALL)

    for key, value in matches:
        if value.startswith('['):  # Handling lists
            value = value.replace('|', '').replace('\n', ' ').strip('[]')  # Remove | and newlines
            parsed_data[key] = list(map(int, re.findall(r'\d+', value)))  # Extract numbers safely
        else:
            parsed_data[key] = int(value)  # Convert to integer

    supply_cost_match = re.search(r'SupplyCost\s*=\s*\[\|(.*?)\|\];', data, re.DOTALL)
    if supply_cost_match:
        supply_cost_str = supply_cost_match.group(1).strip().replace('\n', ' ')
        parsed_data["SupplyCost"] = [list(map(int, re.findall(r'\d+', row))) for row in supply_cost_str.split('|')]

    incompatible_match = re.search(r'IncompatiblePairs\s*=\s*\[\|(.*?)\|\];', data, re.DOTALL)
    if incompatible_match:
        incompatible_str = incompatible_match.group(1).strip().replace('\n', ' ')
        parsed_data["IncompatiblePairs"] = [list(map(int, re.findall(r'\d+', row))) for row in incompatible_str.split('|')]

    return parsed_data

# Convert to JSON
dzn_file = "toy.dzn"
json_output = parse_dzn(dzn_file)

# Save as JSON file
with open("output.json", "w") as json_file:
    json.dump(json_output, json_file, indent=2)

print(json.dumps(json_output, indent=2))
