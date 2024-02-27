sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_1core.cfg
# trace=/root/codes/Victima/traces/bfs.sift
trace=/root/codes/Victima/traces/bfs.sift

$sniper -c $config --traces=$trace
