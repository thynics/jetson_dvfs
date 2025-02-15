import subprocess
import os
import signal
import threading
import time
import random
import asyncio
import fcntl

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
    1062400000,1331200000,
    1600000000,1866000000
]

process_tegrastats = None

EMC_UPDATE_FREQ="/sys/kernel/debug/bpmp/debug/clk/emc/rate"
EMC_FREQ_OVERRIDE="/sys/kernel/debug/bpmp/debug/clk/emc/mrq_rate_locked"
EMC_STATE="/sys/kernel/debug/bpmp/debug/clk/emc/state"

def set_frequency(f, min_path, max_path, available_frequencies):
    if f not in available_frequencies:
        raise ValueError(f"Frequency {f} is not supported.")
    with open(min_path, 'w') as min_f, open(max_path, 'w') as max_f:
        min_f.write(str(f))
        max_f.write(str(f))

def set_gpu_frequency(f):
    set_frequency(f, min_gpu_frequency_path, max_gpu_frequency_path, available_gpu_frequencies)

def set_memory_frequency(f):
    os.system(f'echo 1 >/sys/kernel/debug/bpmp/debug/clk/emc/mrq_rate_locked')
    os.system(f'echo {f} > /sys/kernel/debug/bpmp/debug/clk/emc/rate')
    os.system(f'echo 1 > /sys/kernel/debug/bpmp/debug/clk/emc/state')


# random change emc frequency
async def random_set_memory_frequency():
    while(True):
        set_memory_frequency(random.choice(available_memory_frequency))
        time.sleep(10)

tegrastats_command_thread = None
async def tegrastats_record():
    # 运行子进程，并捕获 stdout
    global tegrastats_command_thread
    tegrastats_command_thread = subprocess.Popen(["sudo tegrastats"], shell=True, stdout=subprocess.STDOUT, stderr=subprocess.PIPE)
    # 持续读取 stdout 并写入文件
    with open("./tegrastats_output.txt", "w") as tf:
        for line in iter(tegrastats_command_thread.stdout.readline, ''):
            decoded_line = line.decode("utf-8").strip()
            output_line = f"{time.time()}---{decoded_line}"
            fcntl.flock(tf, fcntl.LOCK_EX)
            tf.write(f'{output_line}\n')
            fcntl.flock(tf, fcntl.LOCK_UN)

def run_benchmarks():
    # run benchmark in different gpu frequency and then change emc frequency frequently
    for gpu_f in available_gpu_frequencies:
        set_gpu_frequency(gpu_f)
        time.sleep(10)
        with open("./tegrastats_output.txt", "w") as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.write(f'GPU frequency {gpu_f} start, time:{time.time()}\n')
            fcntl.flock(file, fcntl.LOCK_UN)
        thread_benchmark = subprocess.Popen([
        "sudo python3 ~/jetson_benchmarks/benchmark.py \
        --jetson_clocks --jetson_devkit tx2 --model_name vgg19\
         --csv_file_path ~/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv\
          --model_dir ~/jetson_benchmarks"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        thread_benchmark.wait()
        with open("./tegrastats_output.txt", "w") as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.write(f'GPU frequency {gpu_f} end, time:{time.time()}\n')
            fcntl.flock(file, fcntl.LOCK_UN)


async def main():
    memory_task = asyncio.create_task(random_set_memory_frequency())
    tegrastats_task = asyncio.create_task(tegrastats_record())
    benchmarks_task = asyncio.create_task(run_benchmarks())
    await benchmarks_task
    memory_task.cancel()
    tegrastats_task.cancel()
    tegrastats_command_thread.terminate()

asyncio.run(main())

