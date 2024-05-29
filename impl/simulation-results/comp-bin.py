from compbindata import r1x, r1y, r2x, r2y
from itertools import product

import matplotlib.pyplot as plt


def visualize(dx, dy):
    hist, xedges, yedges, _ = plt.hist2d(dx, dy, bins=50, cmap='Reds')
    plt.colorbar(label='Frequency')
    plt.xlabel('n')
    plt.ylabel('m')

    for i, j in product(range(len(xedges) - 1), range(len(yedges) - 1)):
        bin_count = hist[i, j]
        if bin_count > 0:
            x = (xedges[i] + xedges[i + 1]) / 2
            y = (yedges[j] + yedges[j + 1]) / 2
            plt.text(x, y, bin_count, color='black', ha='center', va='center')


plt.subplot(1, 2, 1)
plt.title('10k runs: $n=bin(0.5, 7)$ and $m=7-n$')
visualize(r1x, r1y)

plt.subplot(1, 2, 2)
plt.title('10k runs: n,m = H/T in 7 coin tosses')
visualize(r2x, r2y)

plt.tight_layout()
plt.savefig('comp-bin.pdf')
