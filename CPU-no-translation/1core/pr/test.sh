sniper=/root/codes/Victima/sniper/run-sniper
# config=/root/codes/Victima/sniper/config/virtual_memory_configs_multicore/radix.cfg
config=/root/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_1core.cfg
# trace=/root/codes/Victima/traces_small/GraphBIG_PageRank_amazon0302.sift
trace=/root/codes/Victima/traces/pr.sift

$sniper -c $config --traces=$trace
