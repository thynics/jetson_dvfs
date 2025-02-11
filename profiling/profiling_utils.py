import subprocess
import os
import signal
import threading
import time

# we will try to change gpu frequency and memory frequency randomly
# to see performance in different utilization and memory frequency

gpu_dir = '/sys/devices/gpu.0/devfreq/17000000.gp10b/'

available_gpu_frequencies = [114750000, 216750000, 318750000,
                        420750000, 522750000, 624750000,
                        726750000, 854250000, 930750000,
                        1032750000, 1122000000, 1236750000,
                        1300500000]

min_gpu_frequency_path = gpu_dir + 'min_freq'
max_gpu_frequency_path = gpu_dir + 'max_freq'

mem_dir = '/sys/kernel/debug/bpmp/debug/clk/emc/'

min_mem_frequency_path = mem_dir + "min_rate"
max_mem_frequency_path = mem_dir + "max_rate"

available_memory_frequency = [
    204000000,408000000,665600000,
    800000000,1062400000,1331200000,
    1600000000,1866000000,1331200000,
    1866000000
]

process_tegrastats = None

def set_frequency(f, min_path, max_path, available_frequencies):
    if f not in available_frequencies:
        raise ValueError(f"Frequency {f} is not supported.")
    with open(min_path, 'w') as min_f, open(max_path, 'w') as max_f:
        min_f.write(str(f))
        max_f.write(str(f))

def set_gpu_frequency(f):
    set_frequency(f, min_gpu_frequency_path, max_gpu_frequency_path, available_gpu_frequencies)

def set_memory_frequency(f):
    set_frequency(f, min_mem_frequency_path, max_mem_frequency_path, available_memory_frequency)

for f in available_memory_frequency:
    set_memory_frequency(f)
    time.sleep(5)


exit(0)
thread_benchmark = subprocess.Popen([
    "sudo python3 ~/jetson_benchmarks/benchmark.py \
    --jetson_clocks --jetson_devkit tx2 --model_name vgg19\
     --csv_file_path ~/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv\
      --model_dir ~/jetson_benchmarks"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
