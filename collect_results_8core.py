#!/usr/bin/python3
import os
import csv

directories = ['CPU/8core', 'NDP/8core', 'CPU-no-translation/8core', 'NDP-no-translation/8core']
output_file = 'output_8core.csv'
frequency_ghz = 2.6

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Directory', 'File', 'Total Cycles', 'MMU Latency (Cycles)'])

for directory in directories:
    for subdir in ['bc', 'bfs', 'cc', 'dlrm', 'gc', 'gen', 'pr', 'rnd', 'sssp', 'tc', 'xs']:
        out_path = os.path.join(directory, subdir, 'out')
        sim_out_path = os.path.join(directory, subdir, 'sim.out')
        mmu_latency_ps = 'N/A'
        mmu_latency_cycles = 'N/A'
        cycles = 'N/A'

        # if os.path.exists(out_path):
        #     with open(out_path, 'r') as file:
        #         data = file.read()
        #         for line in data.splitlines():
        #             if line.startswith('mmu.total_latency'):
        #                 mmu_latency_ps = float(line.split('=')[1].strip())
        #                 mmu_latency_cycles = mmu_latency_ps * (frequency_ghz / 1000000)

        if os.path.exists(sim_out_path):
            with open(sim_out_path, 'r') as file:
                data = file.read()
                for line in data.splitlines():
                    if 'Cycles' in line:
                        cycles = line.split('|')[1].strip()

        with open(output_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([directory, subdir, cycles, mmu_latency_cycles])

print("Data extraction complete, results saved in", output_file)
