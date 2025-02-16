from profiling.tegrastats_util import extract
from profiling.tegrastats_util import plot_figure
from profiling.tegrastats_util.extract_tegrastats import gpu_util_key, mem_freq_key, mem_band_key, gpu_freq_key
from profiling.tegrastats_util import available_gpu_frequencies

with open("./tegrastats_output.txt", "r") as f:
    content = [l for l in f]


def analysis_benchmark(bm):
    data_amount_list = []
    perf_list = []

    full = 100 * 1866

    for f  in available_gpu_frequencies:
        if bm == "super_resolution" and f == 1300500000:
            break
        with open(f'{bm}_{f}_output.txt', 'r') as fi:
            bf = [l for l in fi]
        start = float(bf[0].split(': ')[1])
        end = float(bf[3].split(': ')[1])
        with open("./tegrastats_output.txt", "r") as fi:
            tf = [l for l in fi]
        data_amount = 0
        count = 0
        for l in tf:
            if start <= float(l.split('---')[0]) <= end:
                m = extract(l.split("---")[1])
                data_amount += (m[mem_band_key]*m[mem_freq_key]/full)
                count += 1
            if float(l.split('---')[0]) > end:
                break
        data_amount_list.append(data_amount/count*100)
        perf_list.append(1000/(end-start))
    print(available_gpu_frequencies[perf_list.index(max(perf_list))])
    plot_figure(data_amount_list, perf_list, f"{bm}_data", "perf", bm)

for bm in ["inception_v4", "super_resolution", "vgg19"]:
    analysis_benchmark(bm)
