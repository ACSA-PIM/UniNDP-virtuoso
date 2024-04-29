#!/usr/bin/python3
import os
import sys
import csv
import subprocess

if len(sys.argv) < 2:
    sys.exit(1)

core_configuration = sys.argv[1]

directories = [
    '../CPU/{}'.format(core_configuration),
    # '../NDP/{}'.format(core_configuration),
    # '../CPU-no-translation/{}'.format(core_configuration),
    # '../NDP-no-translation/{}'.format(core_configuration),
    # '../CPU-2MBpage/{}'.format(core_configuration),
    # '../NDP-2MBpage/{}'.format(core_configuration),
    # '../CPU-cuckoo/{}'.format(core_configuration),
    # '../NDP-cuckoo/{}'.format(core_configuration),
    # '../CPU-potm/{}'.format(core_configuration),
    # '../NDP-potm/{}'.format(core_configuration),
    # '../NDP-cuckoo-potm-normal/{}'.format(core_configuration),
    # '../NDP-cuckoo-potm-bank/{}'.format(core_configuration),
    # '../NDP-cuckoo-potm-channel/{}'.format(core_configuration)
]

output_file = 'occupany_{}.csv'.format(core_configuration)

def extract_and_save_data(data):
    
    lines = data.splitlines()
    last_200_lines = lines[-200:]
    extracted_data = []

    for line in last_200_lines:
        if 'occupancy rate' in line or 'Number of tables' in line:
            line = line.rstrip(';')
            parts = line.split('; ')
            for part in parts:
                key, value = part.split(':')
                key = key.strip()
                value = value.strip().rstrip(';')
                if key in ['PL4 occupancy rate', 'PL3 occupancy rate', 'PL2 occupancy rate', 'PL1 occupancy rate', 'Overall PL4/PL3 occupancy rate'] or key.startswith('Number of tables with occupancy'):
                    extracted_data.append(value)
        if 'Number of PL3' in line:
            extracted_data.append(line.split('=')[1])
    return extracted_data
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['App', 'PL4 occupancy rate', 'PL3 occupancy rate', 'PL2 occupancy rate', 'PL1 occupancy rate', 'Overall PL4/PL3 occupancy rate', 'Number of PL3', 'Number of tables with occupancy < 0.5', 'Number of tables with occupancy < 0.4', 'Number of tables with occupancy < 0.3', 'Number of tables with occupancy < 0.2', 'Number of tables with occupancy < 0.1', 'Number of tables with occupancy < 0.05'])
for directory in directories:
    for subdir in ['bc', 'bfs', 'cc', 'dlrm', 'gc', 'gen', 'pr', 'rnd', 'sssp', 'tc', 'xs']:
        out_path = os.path.join(directory, subdir, 'sim.stdout')
        if os.path.exists(out_path):
            with open(out_path, 'r') as file:
                data = file.read()
                extracted_data = extract_and_save_data(data)
            with open(output_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([subdir] + extracted_data)