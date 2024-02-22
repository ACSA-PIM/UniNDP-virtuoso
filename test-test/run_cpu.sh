sniper=/root/codes/Victima/sniper/run-sniper
# trace=/root/codes/Victima/traces_small/GraphBIG_BFS_amazon0302.sift
trace=/root/codes/Victima/traces_small/bigJump.sift
config_cpu=/root/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_1core_test.cfg
config_ndp=/root/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_1core_test.cfg

cd /root/codes/UniNDP-virtuoso/test-test/CPU
$sniper -c $config_cpu --traces=$trace &
pid_ndp=$!

# cd /root/codes/UniNDP-virtuoso/test-test/NDP
# $sniper -c $config_cpu --traces=$trace &
# pid_cpu=$!

wait $pid_ndp
cd /root/codes/UniNDP-virtuoso/test-test/CPU
dumpstats.py > out

# wait $pid_cpu
# cd /root/codes/UniNDP-virtuoso/test-test/NDP
# dumpstats.py > out
