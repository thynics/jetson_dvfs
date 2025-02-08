# Smapling rate of tegrastats remain constant
# -> count sampling point = relative perf
# Filter: Remove points where utilization of GPU is 0.
# 1. Freq - Perf
# 2. Perf - Bandwidth Util
# 3. Freq - Energy Consumption
import os

# deal by frequncy
# perf - number of points
# energy consumption - sum of vdd_gpu

import matplotlib.pyplot as plt

mem_band_key = "EMC_FREQ"
gpu_util_key = "GR3D_FREQ"
gpu_power_key = "VDD_SYS_GPU"
cpu_power_key = "VDD_SYS_CPU"
tegrastats_keys = [mem_band_key, gpu_util_key, gpu_power_key, cpu_power_key]

# return dict{str:float}
def extract(p:str):
    # extract from 
    s = p.split(" ")
    last = ""
    tmp = {}
    for v in s:
        if v in tegrastats_keys:
            last = v
        else:
            if last != "":
                tmp[last]=v
                last = ""
    return {
        mem_band_key: int(tmp[mem_band_key].split("%")[0]),
        gpu_util_key: int(tmp[gpu_util_key].split("%")[0]),
        gpu_power_key: int(tmp[gpu_power_key].split("/")[0]),
        cpu_power_key: int(tmp[cpu_power_key].split("/")[0]),
    }

available_frequencies = [114750000, 216750000, 318750000,
                        420750000, 522750000, 624750000,
                        726750000, 854250000, 930750000,
                        1032750000, 1122000000, 1236750000,
                        1300500000]

perf_list = []
mem_util_list = []
energy_list = []
energy_effciency_list = []
edp_list = []

for freq in available_frequencies:
    # read 2 kind of files
    with open(f'./vgg_tegrastats_output/tegrastats_{freq}.txt', "r") as tg_f, open(f'./vgg_benchmarks_output/benchmark_{freq}.txt', "r") as b_f:
        tg_list = [line for line in tg_f]
        b_list = [line for line in b_f]
        # filter tg and calculate: avg band util, energy consumption
        i = len(tg_list)-1
        tail = -1
        while i>=0:
            if extract(tg_list[i])[gpu_util_key] != 0:
                tail = i
                break
            i -= 1
        tg_list = tg_list[:tail+1]

        time = float(b_list[10].split(":")[1][1:])
        perf = 1/time
        start = False
        total_util = 0
        total_power = 0
        for l in tg_list:
            total_util += extract(l)[mem_band_key]
            total_power += extract(l)[gpu_power_key]
        avg_util = total_util/len(tg_list)
        avg_power = total_power/len(tg_list)

        perf_list.append(perf)
        mem_util_list.append(avg_util)
        energy_list.append(avg_power * time)
        energy_effciency_list.append(perf/avg_power/time)
        edp_list.append(avg_power * time * time)


def plot_figure(x, y, x_name, y_name, module_name, title):
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.title(title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.grid(True)
    plt.savefig(f'./{module_name}_plot/{title}.png')

module_name = "vgg"
plot_figure(available_frequencies, perf_list, "freq", "perf", module_name, "freq_vs_perf")
plot_figure(available_frequencies, energy_list, "freq", "energy", module_name, "freq_vs_energy")
plot_figure(mem_util_list, perf_list, "util", "perf", module_name, "util_vs_perf")