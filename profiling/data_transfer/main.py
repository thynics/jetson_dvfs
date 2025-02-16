from profiling.tegrastats_util import extract
from profiling.tegrastats_util import plot_figure
from profiling.tegrastats_util.extract_tegrastats import gpu_util_key, mem_freq_key, mem_band_key, gpu_freq_key
from profiling.tegrastats_util import available_gpu_frequencies

with open("./tegrastats_output.txt", "r") as f:
    content = [l for l in f]


dataAmountList = []
gpu_util_list = []
util = []
perf = []
gpu_data_cons = []

for f in available_gpu_frequencies:
    findStartLine = False
    startTime = .0
    endTime = .0
    dataAmount = 0
    util = 0
    count = 0
    gpu_util = 0
    gpu_data_c = 0
    for l in content:
        if f"GPU frequency {f} start" in l :
            findStartLine = True
            startTime = float(l.split(":")[1])
            continue
        if f"GPU frequency {f} end" in l :
            endTime = float(l.split(":")[1])
            break
        if findStartLine:
            m = extract(l.split("---")[1])
            count += 1
            dataAmount += m[mem_band_key] * m[mem_freq_key]
            gpu_util += m[gpu_util_key]
            gpu_data_c += m[gpu_util_key]*m[gpu_freq_key]
    dataAmountList.append(dataAmount/(endTime-startTime))
    gpu_util_list.append(gpu_util/(endTime-startTime))
    gpu_data_cons.append(gpu_data_c/(endTime-startTime))
    perf.append(1/(endTime - startTime))

plot_figure(gpu_data_cons, dataAmountList, "gpu_data", "mem_data", "data")

