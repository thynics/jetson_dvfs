import subprocess
import os
import time
import random
import asyncio

gpu_dir = '/sys/devices/gpu.0/devfreq/17000000.gp10b/'
available_gpu_frequencies = [114750000, 216750000, 318750000,
                             420750000, 522750000, 624750000,
                             726750000, 854250000, 930750000,
                             1032750000, 1122000000, 1236750000,
                             1300500000]

min_gpu_frequency_path = gpu_dir + 'min_freq'
max_gpu_frequency_path = gpu_dir + 'max_freq'

mem_dir = '/sys/kernel/debug/bpmp/debug/clk/emc/'
available_memory_frequency = [1062400000, 1331200000, 1600000000, 1866000000]

def set_gpu_frequency(f):
    with open(min_gpu_frequency_path, 'w') as min_f, open(max_gpu_frequency_path, 'w') as max_f:
        min_f.write(str(f))
        max_f.write(str(f))

def set_memory_frequency(f):
    os.system(f'echo 1 >/sys/kernel/debug/bpmp/debug/clk/emc/mrq_rate_locked')
    os.system(f'echo {f} > /sys/kernel/debug/bpmp/debug/clk/emc/rate')
    os.system(f'echo 1 > /sys/kernel/debug/bpmp/debug/clk/emc/state')


async def random_set_memory_frequency():
    while True:
        set_memory_frequency(random.choice(available_memory_frequency))
        await asyncio.sleep(10)

tegrastats_command_thread = None

async def tegrastats_record():
    global tegrastats_command_thread
    tegrastats_command_thread = await asyncio.create_subprocess_shell(
        "sudo tegrastats",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    print("create tegrastats success")

    with open("./tegrastats_output.txt", "a") as tf:
        while True:
            line = await tegrastats_command_thread.stdout.readline()
            if not line:
                break
            output_line = f"{time.time()}---{line.decode('utf-8').strip()}"
            tf.write(f'{output_line}\n')
            tf.flush()

benchmark_dir = "/media/work_data/long/jetson_benchmarks"

def get_benchmark_command(benchmark_name):
    return f"sudo python3 {benchmark_dir}/benchmark.py \
            --jetson_clocks --jetson_devkit tx2 --model_name {benchmark_name}\
            --csv_file_path {benchmark_dir}/benchmark_csv/tx2-nano-benchmarks.csv\
            --model_dir {benchmark_dir}"

benchmark_list = ["inception_v4", "vgg19", "super_resolution", "unet", "pose_estimation", "tiny-yolov3", "resnet", "ssd-mobilenet-v1", "ssd-resnet34"]

async def run_benchmarks():
    for bm in benchmark_list:
        for gpu_f in available_gpu_frequencies:
            set_gpu_frequency(gpu_f)
            await asyncio.sleep(10)
            process = await asyncio.create_subprocess_shell(
                get_benchmark_command(f"bm > {bm}_output.txt"),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            await process.wait()

async def main():
    memory_task = asyncio.create_task(random_set_memory_frequency())
    tegrastats_task = asyncio.create_task(tegrastats_record())
    benchmarks_task = asyncio.create_task(run_benchmarks())

    print("all task start")

    await benchmarks_task
    memory_task.cancel()
    tegrastats_task.cancel()

    if tegrastats_command_thread:
        tegrastats_command_thread.terminate()

asyncio.run(main())
