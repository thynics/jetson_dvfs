import subprocess
import os
import signal
import threading
import time


# different memory frequency

dir = '/sys/devices/gpu.0/devfreq/17000000.gp10b'

available_frequencies = [114750000, 216750000, 318750000, 
                        420750000, 522750000, 624750000,
                        726750000, 854250000, 930750000,
                        1032750000, 1122000000, 1236750000,
                        1300500000]

min_frequency_path = dir + '/min_freq'
max_frequency_path = dir + '/max_freq'

process_tegrastats = None

def set_gpu_frequency(f):
    if f not in available_frequencies:
        raise ValueError(f"Frequency {f} is not supported.")
    
    with open(min_frequency_path, "w") as min_f_file, open(max_frequency_path, "w") as max_f_file:
        min_f_file.write(str(f) + "\n")
        max_f_file.write(str(f) + "\n")

for freq in available_frequencies:
    print("Setting Frequency...")
    set_gpu_frequency(freq)
    print("Frequency Set", freq)

    print("Running in", freq)
    
    thread_benchmark = None
    thread_tegrastats = None

    with open(f"benchmark_{freq}.txt", "w") as f:
        thread_benchmark = subprocess.Popen(["sudo python3 ~/jetson_benchmarks/benchmark.py --jetson_clocks --jetson_devkit tx2 --model_name vgg19 --csv_file_path ~/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv --model_dir ~/jetson_benchmarks"], stdout=f, stderr=subprocess.STDOUT, shell=True)

    with open(f"tegrastats_{freq}.txt", "w") as f:
        thread_tegrastats = subprocess.Popen(["sudo tegrastats"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in thread_tegrastats.stdout:
            f.write(f'{time.time()}---{line}\n')
            f.flush()
    thread_benchmark.wait()
    thread_tegrastats.terminate()
    thread_tegrastats.wait()
    print(f"{freq} Finished")
