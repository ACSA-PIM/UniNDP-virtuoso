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
    '../NDP/{}'.format(core_configuration),
    '../CPU-no-translation/{}'.format(core_configuration),
    '../NDP-no-translation/{}'.format(core_configuration),
    '../CPU-2MBpage/{}'.format(core_configuration),
    '../NDP-2MBpage/{}'.format(core_configuration),
    '../CPU-cuckoo/{}'.format(core_configuration),
    '../NDP-cuckoo/{}'.format(core_configuration),
    '../CPU-potm/{}'.format(core_configuration),
    '../NDP-potm/{}'.format(core_configuration)
]

output_file = 'output_{}.csv'.format(core_configuration)
frequency_ghz = 2.6

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Directory', 'File', 'Total Cycles', 'Average PTW Latency (Cycles)', 
                     'L1 Miss Rate Normal', 'L1 Miss Rate Meta',
                     'L2 Miss Rate Normal', 'L2 Miss Rate Meta', 
                     'LLC Miss Rate Normal', 'LLC Miss Rate Meta', 
                     'pwc_L4 Miss Rate', 'pwc_L3 Miss Rate', 'pwc_L2 Miss Rate',
                     'DRAM Rank Total Time CoV', 'DRAM BG Total Time CoV', 'DRAM Rank Total Time MAX', 'DRAM BG Total Time MAX',
                     'DRAM Rank Request CoV', 'DRAM BG Request CoV', 'DRAM Rank Request MAX', 'DRAM BG Request MAX',
                     'DRAM Rank Delay CoV', 'DRAM BG Delay CoV', 'DRAM Rank Delay MAX', 'DRAM BG Delay MAX',
                     'Uncore-request',
                     'STLB miss rate'])

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

def calculate_STLB_miss_rate(data):
    for line in data.splitlines():
        if line.startswith('stlb.access'):
            access_time = int(line.split('=')[1].split(',')[0].strip())
        if line.startswith('stlb.miss'):
            miss_time = int(line.split('=')[1].split(',')[0].strip())
    if access_time == 0:
        return 'N/A'
    return miss_time / access_time

def calculate_STLB_MPKI(data):
    for line in data.splitlines():
        if line.startswith('stlb.access'):
            access_time = int(line.split('=')[1].split(',')[0].strip())
        if line.startswith('stlb.miss'):
            miss_time = int(line.split('=')[1].split(',')[0].strip())
    if access_time == 0:
        return 'N/A'
    return miss_time / 500000000

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
    normal_data_accesses = {'L1': 0, 'L2': 0, 'LLC': 0, 'cache-remote': 0, 'dram':0}
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
    for key in load_counts:
        normal_data_accesses[key] = load_counts[key] + store_counts[key]
    total_normal_accesses = total_loads + total_stores
    results = {}
    for cache_type in ['L1', 'L2', 'LLC']:
        if total_normal_accesses > 0:
            base_accesses = total_normal_accesses - normal_data_accesses['L1'] if cache_type != 'L1' else total_normal_accesses
            miss_rate_normal = (base_accesses - normal_data_accesses[cache_type]) / base_accesses if base_accesses > 0 else 0
            results['{}_miss_rate_normal_data'.format(cache_type)] = '{:.4f}'.format(miss_rate_normal)
        else:
            results['{}_miss_rate_normal_data'.format(cache_type)] = 'N/A'                
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

def get_dram_coefficient_of_variation(sim_stats_path):
    # Call the external script and parse its output
    result = subprocess.run(["./calculate_dram_time_coefficient_of_variance.sh", sim_stats_path], capture_output=True, text=True)
    output = result.stdout.strip()
    lines = output.split('\n')
    dram_rank_total_time_cv =  lines[0].split(': ')[1].rstrip('%')
    dram_bg_total_time_cv =  lines[1].split(': ')[1].rstrip('%')
    dram_rank_total_time_max =  lines[2].split(': ')[1].rstrip('%')
    dram_bg_total_time_max =  lines[3].split(': ')[1].rstrip('%')      
    dram_rank_request_cv =  lines[4].split(': ')[1].rstrip('%')
    dram_bg_request_cv =  lines[5].split(': ')[1].rstrip('%')
    dram_rank_request_max =  lines[6].split(': ')[1].rstrip('%')
    dram_bg_request_max =  lines[7].split(': ')[1].rstrip('%')
    dram_rank_delay_cv =  lines[8].split(': ')[1].rstrip('%')
    dram_bg_delay_cv =  lines[9].split(': ')[1].rstrip('%')
    dram_rank_delay_max =  lines[10].split(': ')[1].rstrip('%')
    dram_bg_delay_max =  lines[11].split(': ')[1].rstrip('%')    
    return dram_rank_total_time_cv, dram_bg_total_time_cv, dram_rank_total_time_max, dram_bg_total_time_max, dram_rank_request_cv, dram_bg_request_cv, dram_rank_request_max, dram_bg_request_max, dram_rank_delay_cv, dram_bg_delay_cv, dram_rank_delay_max, dram_bg_delay_max, llc_uncore_requests

def get_llc_uncore_requests_first_value(data):
    for line in data.splitlines():
        if line.startswith('LLC.uncore-requests'):
            first_value = line.split('=')[1].split(',')[0].strip()
            return first_value
    return 'N/A'

for directory in directories:
    for subdir in ['bc', 'bfs', 'cc', 'dlrm', 'gc', 'gen', 'pr', 'rnd', 'sssp', 'tc', 'xs']:
        out_path = os.path.join(directory, subdir, 'sim.stats')
        average_ptw_latency_cycles = 'N/A'
        cycles = 'N/A'
        cache_miss_rates = {}
        pwc_miss_rates = {}
        dram_rank_total_time_cv = 'N/A'
        dram_bg_total_time_cv = 'N/A'
        dram_rank_total_time_max = 'N/A'
        dram_bg_total_time_max = 'N/A'      
        dram_rank_request_cv = 'N/A'
        dram_bg_request_cv = 'N/A'
        dram_rank_request_max = 'N/A'
        dram_bg_request_max = 'N/A'  
        dram_rank_delay_cv = 'N/A'
        dram_bg_delay_cv = 'N/A'
        dram_rank_delay_max = 'N/A'
        dram_bg_delay_max = 'N/A'    
        llc_uncore_requests = 'N/A'
        stlb_miss_rate = 'N/A'
        stlb_miss = 'N/A'
        if os.path.exists(out_path):
            with open(out_path, 'r') as file:
                data = file.read()
                average_ptw_latency_cycles = calculate_average_ptw_latency(data, frequency_ghz)
                cache_miss_rates = calculate_cache_miss_rate(data, directory, subdir)
                pwc_miss_rates = calculate_pwc_miss_rate(data, directory, subdir)
                dram_rank_total_time_cv, dram_bg_total_time_cv, dram_rank_total_time_max, dram_bg_total_time_max, dram_rank_request_cv, dram_bg_request_cv, dram_rank_request_max, dram_bg_request_max, dram_rank_delay_cv, dram_bg_delay_cv, dram_rank_delay_max, dram_bg_delay_max, llc_uncore_requests = get_dram_coefficient_of_variation(out_path)
                llc_uncore_requests = get_llc_uncore_requests_first_value(data)
                stlb_miss_rate = calculate_STLB_miss_rate(data)
                stlb_MPKI = calculate_STLB_MPKI(data)
                for line in data.splitlines():
                        if 'performance_model.cycle_count' in line:
                            cycles = line.split('=')[1].strip().split(',')[0].strip()

        with open(output_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([directory, subdir, cycles, average_ptw_latency_cycles,
                             cache_miss_rates.get('L1_miss_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('L1_miss_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('L2_miss_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('L2_miss_rate_meta_data', 'N/A'),
                             cache_miss_rates.get('LLC_miss_rate_normal_data', 'N/A'),
                             cache_miss_rates.get('LLC_miss_rate_meta_data', 'N/A'),
                             pwc_miss_rates.get('pwc_L4_miss_rate', 'N/A'),
                             pwc_miss_rates.get('pwc_L3_miss_rate', 'N/A'),
                             pwc_miss_rates.get('pwc_L2_miss_rate', 'N/A'),
                             dram_rank_total_time_cv, dram_bg_total_time_cv, dram_rank_total_time_max, dram_bg_total_time_max, dram_rank_request_cv, dram_bg_request_cv, dram_rank_request_max, dram_bg_request_max, dram_rank_delay_cv, dram_bg_delay_cv, dram_rank_delay_max, dram_bg_delay_max,
                             llc_uncore_requests,
                             stlb_miss_rate,
                             stlb_MPKI
                             ])
