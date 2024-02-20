sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_1core_no_translation.cfg
# trace=/root/codes/Victima/traces/xs.sift
trace=/root/codes/Victima/traces/xs.sift

$sniper -c $config --traces=$trace
