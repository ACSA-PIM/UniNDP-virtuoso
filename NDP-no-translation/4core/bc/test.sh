sniper=/root/codes/Victima/sniper/run-sniper
config=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_1core_no_translation.cfg
# trace=/root/codes/Victima/traces_small/GraphBIG_PageRank_amazon0302.sift
trace=/root/codes/Victima/traces/bc.sift

$sniper -c $config --traces=$trace
