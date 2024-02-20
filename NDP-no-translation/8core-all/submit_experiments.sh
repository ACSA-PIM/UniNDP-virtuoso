sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_8core_no_translation.cfg
trace_dir=/root/codes/Victima/traces


# List of directories
dirs=("bc" "bfs" "cc" "dlrm" "gc" "gen" "pr" "rnd" "sssp" "tc" "xs")

# Function to run the script and notify on completion
run_and_notify() {
    local dir=$1
    local trace=${trace_dir}/${dir}.sift
    (cd "$dir" && sbatch -n 4 --partition high_latency --nodelist kratos6 -J NDP_8core_no_translation_$dir /home/qjiang/codes/Victima/docker_wrapper.sh "podman run --rm -v /home/qjiang/:/root/ victima /root/codes/Victima/sniper/run-sniper -s stop-by-icount:500000000 --genstats --power -d ${PWD//\/home\/qjiang\//\/root\/} -c ${config} --traces=${trace},${trace},${trace},${trace},${trace},${trace},${trace},${trace}"  && echo "$dir completed") &
}

# Run test.sh in each directory in parallel and notify on completion
for dir in "${dirs[@]}"; do
    run_and_notify "$dir"
done

# Wait for all background processes to finish
wait
echo "All scripts have been submitted."
