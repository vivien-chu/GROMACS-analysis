import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import optimize
import random
import sys
import time
import os
import subprocess
import pdb

# need to set proper parameters for mdp file
# put scancel.sh into sup
sigma = 0.9
epsi = 0.98
step = 0.1
step_change_rate = 0.1
key_word = "round8"
job_num_base = 0
precision = 1e-8
max_iter = 10000
generation = 15
exp_slope = -5.26235681e-04
exp_inter = 1.09025142e+00
start_t = 370
end_t = 400
temp_step = 2
sleep_time = 60

# return the slope and intercect from simulation for temperature range
def simulation_value(num):
    ts = []
    ds = []
    for i in range(start_t, end_t, temp_step):
        os.system('cd ' + str(num) + ' && echo 20 | gmx energy -f ' + str(i) + '.edr -s ' + str(i) + '.tpr -o energy.xvg')
        with open(str(num) + '/energy.xvg', 'r') as f:
            lines = f.readlines()
        d = [float(line.split()[1]) for line in lines[30:]]
        ts.append(i)
        ds.append(reduce(lambda x, y: x + y, d) / len(d) / 1000)
        z = np.polyfit(ts, ds,1)
    return z
        
        

def set_param(sigma_c, epsi_c):
    sigma_scale = sigma_c
    epsi_scale = epsi_c
    nfiles = len(sigma_scale)

    for i in range(nfiles):
        os.system("mkdir " + str(i))
        os.system("cp -a sup/* " + str(i))
        with open(str(i) + "/oplsaa.ff/ffnonbonded.itp", 'r') as f:
            lines = f.readlines()
        with open(str(i) + "/oplsaa.ff/ffnonbonded_new.itp", 'w') as out:
            for line in lines:
                if "opls" in line[:5]:
                    temp = line.split()
                    sigma_old = temp[6]
                    epsi_old = temp[7]
                    sigma_new = str(float(sigma_old) * sigma_scale[i])
                    epsi_new = str(float(epsi_old) *  epsi_scale[i])
                    line = line.replace(sigma_old, sigma_new)
                    line = line.replace(epsi_old, epsi_new)
                out.write(line)
        os.system("mv " + str(i) + "/oplsaa.ff/ffnonbonded_new.itp " +                  str(i) + "/oplsaa.ff/ffnonbonded.itp")
        os.system('sed -i "s/rubbersw/equirubber' + str(i) + key_word + '/g" ' + str(i) +'/job')
        os.system('sed -i "s/start_temp/' + str(start_t)  + '/g" ' + str(i)
                +'/set1.sh')
        os.system('sed -i "s/end_temp/' + str(end_t)  + '/g" ' + str(i)
                +'/set1.sh')
        os.system('sed -i "s/temp_step/' + str(temp_step)  + '/g" ' + str(i)
                +'/set1.sh')
        os.system('sed -i "s/rubbersw/dumprubber' + str(i) + key_word + '/g" ' +
                str(i) +'/job_temp')
        os.system('sed -i "s/rubbersw/coolrubber' + str(i) + key_word + '/g" ' + str(i)
                +'/job_cooling')
        #print 'sed -i "s/rubbersw/rubber' + str(i) + '/g" ' + str(i) +'/job'
        os.system("cd " + str(i) + "&& sbatch job")


error = 100000
with open("error.out", 'w') as out:
    out.write("# iteration    error    stepsize\n ")
with open("rst.out", "w") as rstout:
    rstout.write("{:16s}{:16s}{:16s}{:16s}\n".format("num", "sigma", "epsi", "error"))
for i in range(max_iter):
    with open("rst.out", "a") as rstout:
        rstout.write("{:10d}{:10s}\n".format(i, "th iteration"))
    sigma_c = []
    epsi_c = []
    # 10 generation every step
    # equilibrating with new sigma and epsi value
    for j in range(generation):
        sigma_c.append(sigma + step * (random.random() * 2 - 1))
        epsi_c.append(epsi + step * (random.random() * 2 - 1))
        print j, sigma_c, epsi_c
    set_param(sigma_c, epsi_c)
    showjob = 'squeue -u msx626 -o "%.9i %.9P %.25j %.4u %.2t %.10M %.5D %R"'
    cmd = showjob + " > jobs"
    os.system(cmd)
    print "Systems are equlibrating to new sigma and epsi"
    while True:
        with open("jobs", 'r') as f:
            lines = f.readlines()
        lines = [line for line in lines if key_word in line]
        print "number of jobs", len(lines)
        num_jobs = len(lines)
       # os.system("rm -rf jobs")
        if num_jobs <= job_num_base:
            break
        os.system(cmd)
        print lines
        print "number of jobs remaining for equilibrating", num_jobs
        time.sleep(sleep_time)
    pdb.set_trace()
    # cooling down
    for j in range(generation):
        os.system("cd " + str(j) + " && sbatch job_cooling")
    print "Systems are cooling down"

    os.system(cmd)
    while True:
        with open("jobs", 'r') as f:
            lines = f.readlines()
        lines = [line for line in lines if key_word in line]
        num_jobs = len(lines)
        os.system("rm -rf jobs")
        if num_jobs <= job_num_base:
            break
        os.system(cmd)
        print "number of jobs remaining for cooling", num_jobs
        time.sleep(sleep_time)
    print "Extracting snapshots for temperature range"
    for j in range(generation):
        os.system("cd " + str(j) + " && bash set1.sh")
     
    os.system(cmd)
    while True:
        with open("jobs", 'r') as f:
            lines = f.readlines()
        lines = [line for line in lines if key_word in line]
        num_jobs = len(lines)
        if num_jobs <= job_num_base:
            os.system("rm -rf jobs")
            break
        os.system(cmd)
        print "number of jobs remaining for dump snapshots", num_jobs
        time.sleep(sleep_time)
    for j in range(generation):
        sim_value = simulation_value(j)
        new_error = (sim_value[0] - exp_slope) ** 2 + (sim_value[1] - exp_inter) ** 2
        with open("rst.out", "a") as rstout:
            rstout.write("{:16d}{:16.4f}{:16.4f}{:16.5f}\n".format(j, sigma_c[j],
                epsi_c[j], new_error))
        os.system("mv " + str(j) + " iter" + str(i) + "_" + str(j))
        if new_error < error:
            sigma = sigma_c[j]
            epsi = epsi_c[j]
            error = new_error
    step *= step_change_rate
    with open("error.out", 'a') as out:
        out.write('{:10d}{:16.5f}{:16.5f}\n'.format(i, error, step))
    if error < precision:
        break
