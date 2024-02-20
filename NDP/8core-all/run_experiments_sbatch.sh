#!/bin/bash

# # Original script
# original_script="bc/test.sh"

# # List of new directories
# new_dirs=("bfs" "cc" "dlrm" "gc" "gen" "rnd" "sssp" "tc" "xs")

# # Copy original script and update the trace path in each new directory
# for dir in "${new_dirs[@]}"; do
#     # Create directory if it doesn't exist
#     mkdir -p "$dir"

#     # Copy the original script to the new directory
#     cp "$original_script" "$dir/"

#     # Construct the new trace path
#     new_trace_path="/root/codes/Victima/traces/$dir.sift"
    
#     # Update the trace path in the script
#     sed -i "s|trace=.*|trace=$new_trace_path|" "$dir/test.sh"
# done

# echo "Directories created, scripts copied and updated."

sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_8core.cfg
trace_dir=/root/codes/Victima/traces
num_instructions=1000000000


# List of directories
dirs=("bc" "bfs" "cc" "dlrm" "gc" "gen" "pr" "rnd" "sssp" "tc" "xs")
# dirs=("bfs" "cc" "dlrm" "gc" "gen" "pr" "rnd" "sssp")

# Function to run the script and notify on completion
run_and_notify() {
    local dir=$1
    local trace=${trace_dir}/${dir}.sift
    (cd "$dir" && sbatch --partition high_latency \
    --exclude kratos1,kratos3 -J NDP_8core_$dir \
    --output=./std.out --error=./std.err \
    /home/qjiang/codes/Victima/docker_wrapper.sh \
    "podman run --rm -v /mnt/panzer/qjiang/:/root/ victima $sniper \
    --genstats --power -d ${PWD//\/home\/qjiang\//\/root\/} -c ${config} \
    --traces=${trace},${trace},${trace},${trace},${trace},${trace},${trace},${trace}"  && echo "$dir completed") &
}

# Run test.sh in each directory in parallel and notify on completion
for dir in "${dirs[@]}"; do
    run_and_notify "$dir"
done

# Wait for all background processes to finish
wait
echo "All scripts have been executed."
