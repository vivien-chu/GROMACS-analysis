#!/usr/bin/env python


import sys
import math
import pylab
import matplotlib.pyplot as plt
import numpy as np
import sys,argparse
import string

def create_parser():
    parser = argparse.ArgumentParser(description = "Calculate bond correlation function")
    parser.add_argument('data_name', help = "Path and name of bond vector file")
    parser.add_argument('-t', dest='totaltime', default=20,help = 'Total time length in ns')
    parser.add_argument('-dt', dest='timestep', default=0.02, help = 'Timestep in ns')
    parser.add_argument('-niter', dest='niteration', default=2, help = 'Number of iteration')
    parser.add_argument('-dgrid', dest='gridsize',default=0.5, help = 'Grid size, default is 0.5')
    parser.add_argument('-o', dest='output', default = 'out.txt', help = 'The name of output file, default is out.txt')
    return parser

def convert_args(args):
    data_name = args.data_name
    totaltime = float(args.totaltime)
    timestep = float(args.timestep)
    gridsize = float(args.gridsize)
    niteration = int(args.niteration)
   # bondtype = int(args.bondtype)
    output = data_name +'_corrout.txt'
    return (data_name, totaltime, niteration, timestep, gridsize, output)


def dist(a,b,boxl):
    d = 0
    for i in xrange(3):
        m = abs(b[i]-a[i])
        if m > 0.5*boxl[i]:
            m -= boxl[i]
        d += m*m
    return math.sqrt(d)

def main(argv):
    parser = create_parser()
    args = parser.parse_args()
    (data_name, totaltime, niteration, timestep, gridsize, output)=convert_args(args)
    lines = []
    corr = []
    corn = []
    kk = 0
    temp = 0
    nf = 0

    #boxl = [16.68,10.84,11.45]
    with open(data_name,'r') as f:
        lines = f.readlines()
    for i in range(1, len(lines)):
       # print lines[i]
        if lines[i].split()[0] == 'frame':
            nbond = i
            break
    first = True
    print nbond
    for m in range(niteration):
        print "iter", m
        dic0 = {}
        nf = 0
        j = nbond * m
        if j + nbond <= len(lines):
            for k in range(j + 1, nbond + j):
                (a,b) = (int(lines[k].split()[0]),int(lines[k].split()[1]))
                dic0[(a,b)] = [float(lines[k].split()[2]),float(lines[k].split()[3]),float(lines[k].split()[4])]
            nf = 0
            while j + (1 + nf) * nbond <= len(lines):
                nf += 1
               # print "iter", m, "frame", nf
                for i in lines[j + nf * nbond + 1: j + (nf + 1) * nbond]:
                    (a,b) = (int(i.split()[0]),int(i.split()[1]))
                    temp += np.dot([float(i.split()[2]),float(i.split()[3]),float(i.split()[4])], dic0[(a,b)])
                    kk += 1
                if first:
                    if kk != 0:
                        corr.append(temp)
                        corn.append(kk)
                   # print corn
                else:
                    corr[nf - 1] += temp
                    corn[nf - 1] += kk
                
                
                kk = 0
                temp = 0
            if first:
                first = False
    #print corn
    for i in range(len(corr)):
        corr[i] = corr[i] * 1.0/ corn[i]            
    t = np.arange(0, timestep*len(corr), timestep)
   
    with open(output,'w') as out:
        for i in xrange(len(corr)):
            out.write('{0:10.3f}{1:10.3f}\n'.format(t[i], corr[i]/corr[0]))
   

if __name__ == "__main__":
    main(sys.argv[1:])
