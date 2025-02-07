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

process_tegrastats = None

def set_gpu_frequency(f):
    if f not in available_frequencies:
        raise ValueError(f"Frequency {f} is not supported.")
    
    with open(min_frequency_path, "w") as min_f_file, open(max_frequency_path, "w") as max_f_file:
        min_f_file.write(str(f) + "\n")
        max_f_file.write(str(f) + "\n")

def run_command(command, output_file, is_command_t=False):
    global process_tegrastats
    with open(output_file, "w") as f:
        process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, shell=True)
        if is_command_t:
            process.wait()
            if process_tegrastats:
                os.killpg(os.getpgid(process_tegrastats.pid), signal.SIGTERM)
        else:
            process_tegrastats = process

for f in available_frequencies:
    print("Setting Frequency...")
    set_gpu_frequency(f)
    print("Frequency Set", f)

    print("Running in", f)
    
    thread_benchmark = threading.Thread(
        target=run_command,
        args=(["sudo python3 ~/jetson_benchmarks/benchmark.py --jetson_clocks --model_name vgg19 --csv_file_path ~/jetson_benchmarks/benchmark_csv/nx-benchmarks.csv --model_dir ~/jetson_benchmarks"], f"benchmark_{f}.txt")
    )

    thread_tegrastats = threading.Thread(
        target=run_command,
        args=(["sudo tegrastats"], f"tegrastats_{f}.txt", True)
    )

    thread_benchmark.start()
    thread_tegrastats.start()

    thread_benchmark.join()
    thread_tegrastats.join()
