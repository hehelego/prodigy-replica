from kydata import r1, r2

from matplotlib import pyplot as plt


def visual(data):
    counts, _, patches = plt.hist(data, bins=20, edgecolor='black', alpha=0.7)

    for count, patch in zip(counts, patches):
        height = patch.get_height()
        plt.text(patch.get_x() + patch.get_width() / 2,
                 height,
                 count,
                 ha='center',
                 va='bottom')


plt.subplot(2, 1, 1)
plt.title('Knuth Yao program 1: 10k simulation runs')
plt.ylabel('frequency')
plt.xlabel('dice value')
visual(r1)

plt.subplot(2, 1, 2)
plt.title('Knuth Yao program 2: 10k simulation runs')
plt.ylabel('frequency')
plt.xlabel('dice value')
visual(r2)

plt.tight_layout()
plt.savefig('ky-die-sim.pdf')
