#!/usr/bin/python3
import os
import sys
import csv

if len(sys.argv) < 2:
    sys.exit(1)

core_configuration = sys.argv[1]

directories = [
    'CPU/{}'.format(core_configuration),
    'NDP/{}'.format(core_configuration),
    'CPU-no-translation/{}'.format(core_configuration),
    'NDP-no-translation/{}'.format(core_configuration),
]

output_file = 'output_{}.csv'.format(core_configuration)
frequency_ghz = 2.6

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Directory', 'File', 'Total Cycles', 'Average PTW Latency (Cycles)', 
                     'L1 Miss Rate Normal Data', 'L1 Miss Rate Meta Data',
                     'L2 Miss Rate Normal Data', 'L2 Miss Rate Meta Data', 
                     'LLC Miss Rate Normal Data', 'LLC Miss Rate Meta Data'])

def calculate_average_ptw_latency(data, frequency_ghz):
    ptw_latency_fs = 0
    ptw_walks = 0
    for line in data.splitlines():
        if line.startswith('ptw_radix_0.page_level_latency'):
            ptw_latency_fs += float(line.split('=')[1].split(',')[0].strip())
        elif line.startswith('PTW_0.page_walks'):
            ptw_walks = float(line.split('=')[1].split(',')[0].strip())

    if ptw_walks != 0:
        average_ptw_latency_cycles = (ptw_latency_fs / ptw_walks) * (frequency_ghz / 1e6)
        average_ptw_latency_cycles = round(average_ptw_latency_cycles, 2)
    else:
        average_ptw_latency_cycles = 'N/A'
    return average_ptw_latency_cycles

def calculate_cache_miss_rate(data, subdir):
    normal_data_counts = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
    meta_data_counts = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
    total_normal_accesses = 0
    total_meta_accesses = 0

    for line in data.splitlines():
        key, value_str = line.split('=')
        is_meta_data = "page-table" in key
        cache_levels = ['L2', 'L3', 'nuca-cache', 'cache-remote', 'dram']
        if 'L1-D.loads-where' in key:
            first_value = float(value_str.split(',')[0].strip())
            for cache_level in cache_levels:
                if cache_level in key:
                    if cache_level == 'L2':
                        data_count_key = 'L1'
                    elif cache_level == 'L3':
                        data_count_key = 'L2'
                    elif cache_level == 'nuca-cache':
                        data_count_key = 'LLC'
                    elif cache_level == 'cache-remote':
                        data_count_key = 'cache-remote'
                    else:
                        data_count_key = 'dram'

                    if is_meta_data:
                        meta_data_counts[data_count_key] += first_value
                    else:
                        normal_data_counts[data_count_key] += first_value
                    break

            if not is_meta_data:
                total_normal_accesses += first_value
            else:
                total_meta_accesses += first_value

    results = {}
    for cache_type in ['L1', 'L2', 'LLC']:
        if total_normal_accesses > 0:
            base_accesses = total_normal_accesses - normal_data_counts['L1'] if cache_type != 'L1' else total_normal_accesses
            miss_rate_normal = (base_accesses - normal_data_counts[cache_type]) / base_accesses if base_accesses > 0 else 0
            results['{}_misses_rate_normal_data'.format(cache_type)] = '{:.4f}'.format(miss_rate_normal)
        else:
            results['{}_misses_rate_normal_data'.format(cache_type)] = 'N/A'
        
        if total_meta_accesses > 0:
            base_accesses = total_meta_accesses - meta_data_counts['L1'] if cache_type != 'L1' else total_meta_accesses
            miss_rate_meta = (base_accesses - meta_data_counts[cache_type]) / base_accesses if base_accesses > 0 else 0
            results['{}_misses_rate_meta_data'.format(cache_type)] = '{:.4f}'.format(miss_rate_meta)
        else:
            results['{}_misses_rate_meta_data'.format(cache_type)] = 'N/A'
    return results

for directory in directories:
    for subdir in ['bc', 'bfs', 'cc', 'dlrm', 'gc', 'gen', 'pr', 'rnd', 'sssp', 'tc', 'xs']:
        out_path = os.path.join(directory, subdir, 'sim.stats')
        sim_out_path = os.path.join(directory, subdir, 'sim.out')
        average_ptw_latency_cycles = 'N/A'
        cycles = 'N/A'
        cache_miss_rates = {}

        if os.path.exists(out_path):
            with open(out_path, 'r') as file:
                data = file.read()
                average_ptw_latency_cycles = calculate_average_ptw_latency(data, frequency_ghz)
                cache_miss_rates = calculate_cache_miss_rate(data, subdir)

        if os.path.exists(sim_out_path):
            with open(sim_out_path, 'r') as file:
                data = file.read()
                for line in data.splitlines():
                    if 'Cycles' in line:
                        cycles = line.split('|')[1].strip()

        with open(output_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([directory, subdir, cycles, average_ptw_latency_cycles,
                             cache_miss_rates.get('L1_misses_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('L1_misses_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('L2_misses_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('L2_misses_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('LLC_misses_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('LLC_misses_rate_meta_data', 'N/A')])
