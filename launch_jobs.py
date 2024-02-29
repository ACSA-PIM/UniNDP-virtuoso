
import os
import argparse
import sys

# I need the user to provide an argument --native or --slurm to specify the execution mode

parser = argparse.ArgumentParser(
    description="Script creats experiments run in native or SLURM mode.")
parser.add_argument("--native", action="store_true",
                    help="Run in native mode.")
parser.add_argument("--slurm", action="store_true", help="Run in SLURM mode.")
parser.add_argument("path", help="Path to the file or directory.")
parser.add_argument("--excluded_nodes", nargs='?', default=None,
                    help="Comma-separated list of excluded nodes.")

args = parser.parse_args()

if args.native and args.slurm:
    print("Error: Cannot specify both --native and --slurm. Choose one execution mode.")
    exit(1)

slurm = False
native = False
if args.native:
    native = True
elif args.slurm:
    slurm = True
else:
    print("Error: Please specify either --native or --slurm to choose the execution mode.")
    exit(1)

trace_path = "/home/qjiang/codes/Victima"

traces = [("bc", "bc.sift"),
          ("bfs", "bfs.sift"),
          ("cc", "cc.sift"),
          ("tc", "tc.sift"),
          ("gc", "gc.sift"),
          ("pr", "pr.sift"),
          ("sssp", "sssp.sift"),
          ("rnd", "rnd.sift"),
          ("xs", "xs.sift"),
          ("dlrm", "dlrm.sift"),
          ("gen", "gen.sift")
          ]


# Docker command to run the binary inside the container
docker_command = "docker run --rm -v "+args.path + \
    ":/app/ docker.io/kanell21/artifact_evaluation:victima"

NDP_4core = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_4core.cfg'
NDP_4core_no_translation = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_4core_no_translation.cfg'
CPU_4core = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_4core.cfg'
CPU_4core_no_translation = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_4core_no_translation.cfg'

NDP_8core = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_8core.cfg'
NDP_8core_no_translation = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/NDP/baseline_NDP_8core_no_translation.cfg'
CPU_8core = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_8core.cfg'
CPU_8core_no_translation = '-c /home/qjiang/codes/Victima/sniper/config/UniNDP/CPU/baseline_CPU_8core_no_translation.cfg'

baseline = " -c /app/sniper/config/virtual_memory_configs/radix.cfg "


configs = [
    ("NDP_4core", NDP_4core),
    ("NDP_4core_no_translation", NDP_4core_no_translation),
    ("CPU_4core", CPU_4core),
    ("CPU_4core_no_translation", CPU_4core_no_translation),
    ("NDP_8core", NDP_8core),
    ("NDP_8core_no_translation", NDP_8core_no_translation),
    ("CPU_8core", CPU_8core),
    ("CPU_8core_no_translation", CPU_8core_no_translation)
]


sniper_parameters = "/app/sniper/run-sniper -s stop-by-icount:500000000 --genstats --power"

# # # Create the jobfile: a bash script that runs all the binaries with all the configurations
with open("./jobfile", "w") as jobfile:
    jobfile.write("#!/bin/bash\n")

    for (trace_name, trace) in traces:

        for (config_name, configuration_string) in configs:

            trace_command = "--traces={}".format(trace_path+trace)

            output_command = "-d /app/results/{}_{}".format(
                config_name, trace_name)

            if (slurm):
                # SLURM parameters are overprovisioned just in case the simulation takes longer than expected
                if args.excluded_nodes is not None:
                    execution_command = "sbatch --exclude="+args.excluded_nodes+"  -J {}_{} --output=./results/{}_{}.out --error=./results/{}_{}.err docker_wrapper.sh ".format(
                        config_name, trace_name, config_name, trace_name, config_name, trace_name)
                else:
                    execution_command = "sbatch   -J {}_{} --output=./results/{}_{}.out --error=./results/{}_{}.err docker_wrapper.sh ".format(
                        config_name, trace_name, config_name, trace_name, config_name, trace_name)
                command = execution_command + "\"" + docker_command + " " + sniper_parameters + \
                    " " + output_command+" "+configuration_string+" "+trace_command+"\""
            elif (native):
                command = docker_command + " " + sniper_parameters + " " + output_command+" " + \
                    configuration_string+" "+trace_command + \
                    " > ./results/"+config_name+"_"+trace_name+".out  &"
            # command = docker_command + " " + sniper_parameters + " " + output_command+" "+configuration_string+" "+trace_command

            jobfile.write(command)
            jobfile.write("\n")
