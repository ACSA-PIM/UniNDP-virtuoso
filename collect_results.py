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
    'NDP-2MBpage/{}'.format(core_configuration),
    'NDP-2MBpage-no-translation/{}'.format(core_configuration),
]

output_file = 'output_{}.csv'.format(core_configuration)
frequency_ghz = 2.6

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Directory', 'File', 'Total Cycles', 'Average PTW Latency (Cycles)', 
                     'L1 Load Miss Rate', 'L1 Store Miss Rate', 'L1 Miss Rate Meta',
                     'L2 Load Miss Rate', 'L2 Store Miss Rate','L2 Miss Rate Meta', 
                     'LLC Load Miss Rate', 'LLC Store Miss Rate', 'LLC Miss Rate Meta', 
                     'pwc_L4 Miss Rate', 'pwc_L3 Miss Rate', 'pwc_L2 Miss Rate'])

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

def calculate_cache_miss_rate(data, directory, subdir):
    cache_level_mapping = {
        'L2': 'L1',
        'L3': 'L2',
        'nuca-cache': 'LLC',
        'cache-remote': 'cache-remote'
    }
    load_counts = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
    store_counts = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
    meta_data_accesses = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
    total_loads = 0
    total_stores = 0
    total_meta_accesses = 0

    for line in data.splitlines():
        key, value_str = line.split('=')
        is_meta_data = "page-table" in key
        cache_levels = ['L2', 'L3', 'nuca-cache', 'cache-remote', 'dram', '']
        if 'L1-D.loads-where' in key:
            first_value = float(value_str.split(',')[0].strip())
            for cache_level in cache_levels:
                if cache_level in key:
                    data_count_key = cache_level_mapping.get(cache_level, 'dram')
                    if is_meta_data:
                        meta_data_accesses[data_count_key] += first_value
                    else:
                        load_counts[data_count_key] += first_value
                    break
            if not is_meta_data:
                total_loads += first_value
            else:
                total_meta_accesses += first_value
        
        if 'L1-D.stores-where' in key:
            first_value = float(value_str.split(',')[0].strip())
            for cache_level in cache_levels:
                if cache_level in key:
                    data_count_key = cache_level_mapping.get(cache_level, 'dram')
                    store_counts[data_count_key] += first_value
                    break
            total_stores += first_value
    # print(directory, subdir, "total loads: ", total_loads, " total stores: ", total_stores, " total meata-data accesses: ", total_meta_accesses)        
    results = {}
    for cache_type in ['L1', 'L2', 'LLC']:
        if total_loads > 0:
            base_loads = total_loads - load_counts['L1'] if cache_type != 'L1' else total_loads
            load_miss_rate_normal = (base_loads - load_counts[cache_type]) / base_loads if base_loads > 0 else 0
            results['{}_load_miss_rate'.format(cache_type)] = '{:.4f}'.format(load_miss_rate_normal)
        else:
            results['{}_load_miss_rate'.format(cache_type)] = 'N/A'

        if total_stores > 0:
            base_stores = total_stores - store_counts['L1'] if cache_type != 'L1' else total_stores
            store_miss_rate_normal = (base_stores - store_counts[cache_type]) / base_stores if base_stores > 0 else 0
            results['{}_store_miss_rate'.format(cache_type)] = '{:.4f}'.format(store_miss_rate_normal)
        else:
            results['{}_store_miss_rate'.format(cache_type)] = 'N/A'
                
        if total_meta_accesses > 0:
            base_accesses = total_meta_accesses - meta_data_accesses['L1'] if cache_type != 'L1' else total_meta_accesses
            miss_rate_meta = (base_accesses - meta_data_accesses[cache_type]) / base_accesses if base_accesses > 0 else 0
            results['{}_miss_rate_meta_data'.format(cache_type)] = '{:.4f}'.format(miss_rate_meta)
        else:
            results['{}_miss_rate_meta_data'.format(cache_type)] = 'N/A'
    return results

def calculate_pwc_miss_rate(data, directory, subdir):
    access_counts = {'pwc_L2': 0, 'pwc_L3': 0, 'pwc_L4': 0}
    miss_counts = {'pwc_L2': 0, 'pwc_L3': 0, 'pwc_L4': 0}
    for line in data.splitlines():
        key, value_str = line.split('=')
        cache_levels = ['pwc_L2', 'pwc_L3', 'pwc_L4']
        first_value = float(value_str.split(',')[0].strip())
        for cache_level in cache_levels:
            if cache_level + '.access' in key:
                data_count_key = cache_level
                access_counts[data_count_key] += first_value
            if cache_level + '.miss' in key:
                data_count_key = cache_level
                miss_counts[data_count_key] += first_value
    results = {}
    for cache_type in ['pwc_L2', 'pwc_L3', 'pwc_L4']:
        if access_counts[cache_type] > 0:
            miss_rate_normal = miss_counts[cache_type] / access_counts[cache_type] if access_counts[cache_type] > 0 else 0
            results['{}_miss_rate'.format(cache_type)] = '{:.4f}'.format(miss_rate_normal)
        else:
            results['{}_miss_rate'.format(cache_type)] = 'N/A'
    return results

for directory in directories:
    for subdir in ['bc', 'bfs', 'cc', 'dlrm', 'gc', 'gen', 'pr', 'rnd', 'sssp', 'tc', 'xs']:
        out_path = os.path.join(directory, subdir, 'sim.stats')
        average_ptw_latency_cycles = 'N/A'
        cycles = 'N/A'
        cache_miss_rates = {}
        pwc_miss_rates = {}
        if os.path.exists(out_path):
            with open(out_path, 'r') as file:
                data = file.read()
                average_ptw_latency_cycles = calculate_average_ptw_latency(data, frequency_ghz)
                cache_miss_rates = calculate_cache_miss_rate(data, directory, subdir)
                pwc_miss_rates = calculate_pwc_miss_rate(data, directory, subdir)
                for line in data.splitlines():
                        if 'performance_model.cycle_count' in line:
                            cycles = line.split('=')[1].strip().split(',')[0].strip()

        with open(output_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([directory, subdir, cycles, average_ptw_latency_cycles,
                             cache_miss_rates.get('L1_load_miss_rate', 'N/A'),
                             cache_miss_rates.get('L1_store_miss_rate', 'N/A'),
                             cache_miss_rates.get('L1_miss_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('L2_load_miss_rate', 'N/A'),
                             cache_miss_rates.get('L2_store_miss_rate', 'N/A'),
                             cache_miss_rates.get('L2_miss_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('LLC_load_miss_rate', 'N/A'),
                             cache_miss_rates.get('LLC_store_miss_rate', 'N/A'),
                             cache_miss_rates.get('LLC_miss_rate_meta_data', 'N/A'),
                             pwc_miss_rates.get('pwc_L4_miss_rate', 'N/A'),
                             pwc_miss_rates.get('pwc_L3_miss_rate', 'N/A'),
                             pwc_miss_rates.get('pwc_L2_miss_rate', 'N/A')])
