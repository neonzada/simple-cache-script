#!/usr/bin/env python3

import matplotlib.pyplot as plt
import csv
import numpy as np

configs = []
i_missrate = []
d_missrate = []

with open('results/missrates.csv', newline='') as csvfile:
  reader = csv.reader(csvfile)
  for row in reader:
    configs.append(row[0])
    i_missrate.append(float(row[1]))
    d_missrate.append(float(row[2]))

width = 0.35

bar1 = np.arange(len(configs))
bar2 = [i+width for i in bar1]

plt.figure(figsize=(10,6))
plt.bar(bar1, i_missrate, width, label='IL1 Miss Rate', color='skyblue')
plt.bar(bar2, d_missrate, width, label='DL1 Miss Rate', color='red')

plt.xlabel("Cache Configuration")
plt.ylabel("Miss Rate")
plt.title("L1 Cache Miss Rate per Configuration")
plt.xticks((bar1+bar2)/2, configs, ha="center")
plt.legend()

plt.ylim(0, 1)
plt.tight_layout()
plt.savefig("results/results.png", dpi=150)