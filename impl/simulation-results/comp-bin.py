from compbindata import r1x, r1y, r2x, r2y
from itertools import product

import matplotlib.pyplot as plt


def visualize(dx, dy):
    hist, xedges, yedges, _ = plt.hist2d(dx, dy, bins=50, cmap='Reds')
    plt.colorbar(label='Frequency')
    plt.xlabel('n')
    plt.ylabel('m')

    for i, j in product(range(len(xedges) - 1), range(len(yedges) - 1)):
        n = hist[i, j]
        if n > 0:
            x = (xedges[i] + xedges[i + 1]) / 2
            y = (yedges[j] + yedges[j + 1]) / 2 - 0.03
            plt.text(x, y, str(int(n)), color='black', ha='left', va='top')

plt.subplot(2, 1, 1)
plt.title('10k runs: $n=bin(0.5, 7)$ $m=7-n$')
visualize(r1x, r1y)

plt.subplot(2, 1, 2)
plt.title('10k runs: n,m = H/T in 7 coin tosses')
visualize(r2x, r2y)

plt.tight_layout(pad=2)
plt.savefig('comp-bin.pdf')
