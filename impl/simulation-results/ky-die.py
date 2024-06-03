from kydata import r1, r2

from matplotlib import pyplot as plt


def visual(data):
    counts, _, patches = plt.hist(data, bins=20, edgecolor='black', alpha=0.7)

    for count, patch in zip(counts, patches):
        if count == 0: continue
        height = patch.get_height()
        s = str(int(count))
        plt.text(patch.get_x() + patch.get_width() / 2, height * 0.9, s)


plt.title('Knuth-Yao Dice: 10k simulation runs')
plt.ylabel('frequency')
plt.xlabel('dice value')
visual(r1)

# plt.subplot(2, 1, 2)
# plt.title('Knuth Yao program 2: 10k simulation runs')
# plt.ylabel('frequency')
# plt.xlabel('dice value')
# visual(r2)

plt.tight_layout()
plt.savefig('ky-die-bars.pdf')
