# run benchmark under different frequency.
# collect data printed by tegrastats

import subprocess
import os
import signal
import threading

dir = '/sys/devices/gpu.0/devfreq/17000000.gp10b'

available_frequencies = [114750000, 216750000, 318750000, 
                        420750000, 522750000, 624750000,
                        726750000, 854250000, 930750000,
                        1032750000, 1122000000, 1236750000,
                        1300500000]

min_frequency_path = dir + '/min_freq'
max_frequency_path = dir + '/max_freq'

def set_gpu_frequency(f):
    with open(min_frequency_path, "w") as min_f_file, open(max_frequency_path, "w") as max_f_file:
        min_f_file.write(str(f))
        max_f_file.write(str(f))


# run benchmark in all frequency


process_tegrastats = None

def run_command(command, output_file, is_command_t=False):
    global process_b
    with open(output_file, "w") as f:
        process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT)
        if is_command_t:
            process.wait()
            if process_tegrastats:
                os.killpg(os.getpgid(process_b.pid), signal.SIGTERM)
        else:
            process_tegrastats = process

for f in available_frequencies:
    set_gpu_frequency(f) # set frequency first
    # EMC is max default, no need to reset
    # run the benchmark in one process.
    thread_benchmark = threading.Thread(target=run_command, args=(["cd ../../jetson_benchmarks && sudo python3 benchmark.py --jetson_clocks --model_name vgg19 --csv_file_path ./benchmark_csv/nx-benchmarks.csv --model_dir ~/jetson_benchmarks"], f"benchmark_{f}"))
    # start tegrastats and output to result
    thread_benchmark = threading.Thread(target=run_command, args=(["sudo tegrastats"], f"tegrastats{f}", True))
