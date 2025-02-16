import matplotlib.pyplot as plt

def plot_figure(x, y, x_name, y_name, module_name):
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.title(f"{x_name}_vs{y_name}")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.grid(True)
    plt.savefig(f'./{x_name}_vs{y_name}.png')