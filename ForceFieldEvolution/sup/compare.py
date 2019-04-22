import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import optimize

sim_file = sys.argv[1]
#rubber tg
with open(sim_file, 'r') as f:
        lines = f.readlines()[1:]
d = [float(line.split()[1]) for line in lines]
t = [float(line.split()[0]) for line in lines]
z = np.polyfit(t, d,1)
print 'simulation', z
p = np.poly1d(z)
xnew = np.linspace(370, 400, num=100, endpoint=True)
plt.plot(xnew, p(xnew), '--', color = 'black')
with open('/project/depablo/weiwei/from_meng/evolution/rubber/round7/sup/rubber.dat', 'r') as f:
    lines = f.readlines()
de = [float(line.split()[1]) for line in lines]
te = [float(line.split()[0]) for line in lines]
ze = np.polyfit(te, de,1)
print 'experiment', ze
pe = np.poly1d(ze)
xnewe = np.linspace(240, 400, num=100, endpoint=True)
plt.plot(xnewe, pe(xnewe), '--', color = 'black')

plt.scatter(t, d, label = 'simulation')
plt.scatter(te, de, label = 'experiment')
plt.legend(loc='lower left')

plt.xlabel("T/K")
plt.ylabel("density/" + "$kg/m^{3}$")


plt.show()

