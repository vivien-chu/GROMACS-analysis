# for extracting density for different temperatures
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import optimize
import random
import sys
import time
import os
import subprocess

def simulation_value(start_t, end_t, temp_step):
    ts = []
    ds = []
    for i in range(start_t, end_t + temp_step, temp_step):
        os.system(' echo 20 | gmx energy -f ' + str(i) + '.edr -s ' + str(i) + '.tpr -o energy.xvg')
        with open('energy.xvg', 'r') as f:
            lines = f.readlines()
        d = [float(line.split()[1]) for line in lines[30:]]
        ts.append(i)
        ds.append(reduce(lambda x, y: x + y, d) / len(d) / 1000)
        z = np.polyfit(ts, ds,1)
    with open('density.out', 'w') as out:
        out.write('#{:16.8f}{:16.8f}\n'.format(z[0], z[1]))
        out.write('#{:20.8f}\n'.format((z[0] - 5.26235681e-04) ** 2 + (z[1] - 1.09025142) ** 2))
        for i in range(len(ds)):
            out.write('{:10.3f}{:10.3f}\n'.format(ts[i], ds[i]))

simulation_value(370, 400, 2)
        
        
