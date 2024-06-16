#!/bin/bash

calculate_cv() {
    local -n nums=$1
    local sum=0
    local sumsq=0
    local n=0

    for num in "${nums[@]}"; do
        sum=$(echo "$sum + $num" | bc)
        sumsq=$(echo "$sumsq + ($num * $num)" | bc)
        ((n++))
    done

    local mean=$(echo "scale=5; $sum / $n" | bc)
    local variance=$(echo "scale=5; ($sumsq / $n) - ($mean * $mean)" | bc)
    local stddev=$(echo "scale=5; sqrt($variance)" | bc)
    local cv=$(echo "scale=5; ($stddev / $mean) * 100" | bc)
    echo $cv
}

calculate_max() {
    local -n nums=$1
    local max=0

    for num in "${nums[@]}"; do
        if (( $(echo "$num > $max" | bc -l) )); then
            max=$num
        fi
    done

    echo $max
}

inputfile="sim.stats"
if [ $# -gt 0 ]; then
    inputfile=$1
fi

if [ ! -f "$inputfile" ]; then
    echo "File not found: $inputfile"
    exit 1
fi

declare -a rank_times
declare -a group_times
declare -a rank_requests
declare -a group_requests
declare -a rank_queue_delays
declare -a group_queue_delays

rank_numbers=$(grep -oP 'dram-rank-\K\d+' "$inputfile" | sort -nu)
for i in $rank_numbers; do
    rank_time=$(grep -oP "dram-rank-$i.total-time-used = \K\d+" "$inputfile")
    rank_request=$(grep -oP "dram-rank-$i.num-requests = \K\d+" "$inputfile")
    rank_queue_delay=$(grep -oP "dram-rank-$i.total-queue-delay = \K\d+" "$inputfile")
    if [ ! -z "$rank_time" ]; then
        rank_times+=($rank_time)
    fi
    if [ ! -z "$rank_request" ]; then
        rank_requests+=($rank_request)
    fi
    if [ ! -z "$rank_queue_delay" ]; then
        rank_queue_delays+=($rank_queue_delay)
    fi
done

group_numbers=$(grep -oP 'dram-bank-group-\K\d+' "$inputfile" | sort -nu)
for i in $group_numbers; do
    group_time=$(grep -oP "dram-bank-group-$i.total-time-used = \K\d+" "$inputfile")
    group_request=$(grep -oP "dram-bank-group-$i.num-requests = \K\d+" "$inputfile")
    group_queue_delay=$(grep -oP "dram-bank-group-$i.total-queue-delay = \K\d+" "$inputfile")
    if [ ! -z "$group_time" ]; then
        group_times+=($group_time)
    fi
    if [ ! -z "$group_request" ]; then
        group_requests+=($group_request)
    fi
    if [ ! -z "$group_queue_delay" ]; then
        group_queue_delays+=($group_queue_delay)
    fi
done

rank_cv=$(calculate_cv rank_times)
group_cv=$(calculate_cv group_times)
rank_max=$(calculate_max rank_times)
group_max=$(calculate_max group_times)

rank_request_cv=$(calculate_cv rank_requests)
group_request_cv=$(calculate_cv group_requests)
rank_request_max=$(calculate_max rank_requests)
group_request_max=$(calculate_max group_requests)

rank_queue_delay_cv=$(calculate_cv rank_queue_delays)
group_queue_delay_cv=$(calculate_cv group_queue_delays)
rank_queue_delay_max=$(calculate_max rank_queue_delays)
group_queue_delay_max=$(calculate_max group_queue_delays)

echo "DRAM Rank Total Time Used Coefficient of Variation: $rank_cv%"
echo "DRAM Bank Group Total Time Used Coefficient of Variation: $group_cv%"
echo "DRAM Rank Total Time Used Maximum: $rank_max"
echo "DRAM Bank Group Total Time Used Maximum: $group_max"
echo "DRAM Rank Num Requests Coefficient of Variation: $rank_request_cv%"
echo "DRAM Bank Group Num Requests Coefficient of Variation: $group_request_cv%"
echo "DRAM Rank Num Requests Maximum: $rank_request_max"
echo "DRAM Bank Group Num Requests Maximum: $group_request_max"
echo "DRAM Rank Total Queue Delay Coefficient of Variation: $rank_queue_delay_cv%"
echo "DRAM Bank Group Total Queue Delay Coefficient of Variation: $group_queue_delay_cv%"
echo "DRAM Rank Total Queue Delay Maximum: $rank_queue_delay_max"
echo "DRAM Bank Group Total Queue Delay Maximum: $group_queue_delay_max"
