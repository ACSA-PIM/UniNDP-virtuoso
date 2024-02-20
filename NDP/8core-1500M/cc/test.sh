sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_1core.cfg
# trace=/root/codes/Victima/traces/cc.sift
trace=/root/codes/Victima/traces/cc.sift

$sniper -c $config --traces=$trace
