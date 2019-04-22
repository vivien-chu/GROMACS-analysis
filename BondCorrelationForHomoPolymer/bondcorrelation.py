#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  residense_time.py
#
#  Copyright 2016 weiwei <weiwei@xps8700>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


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
    parser.add_argument('-t', dest='totaltime', default=100,help = 'Total time length in ns')
    parser.add_argument('-dt', dest='timestep', default=0.02, help = 'Timestep in ns')
    parser.add_argument('-dgrid', dest='gridsize',default=0.5, help = 'Grid size, default is 0.5')
    parser.add_argument('-o', dest='output', default = 'out.txt', help = 'The name of output file, default is out.txt')
    return parser

def convert_args(args):
    data_name = args.data_name
    totaltime = float(args.totaltime)
    timestep = float(args.timestep)
    gridsize = float(args.gridsize)
   # bondtype = int(args.bondtype)
    output = data_name +'_corrout.txt'
    return (data_name, totaltime, timestep, gridsize, output)


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
    (data_name, totaltime, timestep, gridsize, output)=convert_args(args)
    lines = []
    corr = []
    corgridt = []
    kk = 0
    temp = 0
    nf = 0

    #boxl = [16.68,10.84,11.45]
    with open(data_name,'r') as f:
        line = f.readline()
        #print line.split()[-3]
        boxx = float(line.split()[-3])
        ngrid = int(boxx/gridsize)
        corgrid = [0 for i in xrange(ngrid)]
        gridk = [0 for i in xrange(ngrid)]
        line = f.readline()
        while line.split()[0]!='frame':
            lines.append(line)
            line = f.readline()
        dic0 = {}
        for i in lines:
            (a,b) = (int(i.split()[0]),int(i.split()[1]))
            dic0[(a,b)] = [float(i.split()[2]),float(i.split()[3]),float(i.split()[4])]
        lines = []
        while line and nf < totaltime/timestep:
            nf += 1
            print nf
            line = f.readline()
            while line and line.split()[0]!='frame':
                lines.append(line)
                line = f.readline()
            for i in lines:
                (a,b) = (int(i.split()[0]),int(i.split()[1]))
                pos = int(float(i.split()[5])/gridsize)
                temp += np.dot([float(i.split()[2]),float(i.split()[3]),float(i.split()[4])], dic0[(a,b)])
                if pos>=0 and pos<ngrid:
                    gridk[pos] += 1
                    corgrid[pos] += np.dot([float(i.split()[2]),float(i.split()[3]),float(i.split()[4])], dic0[(a,b)])

                kk += 1
            for mmm in xrange(ngrid):
                if gridk[mmm] == 0:
                    corgrid[mmm] = 0
                else:
                    corgrid[mmm] /= gridk[mmm]
            temp /= kk
            corr.append(temp)
            #corgrid is the correlation function at certain time for the whole grid
            #corgridt is the total correlation function for all the time for all the position
            corgridt.append(corgrid)
            kk = 0
            temp = 0
            corgrid = [0 for i in xrange(ngrid)]
            gridk = [0 for i in xrange(ngrid)]
            lines = []
    t = np.arange(0, timestep*len(corr), timestep)
    x = np.arange(0, gridsize*ngrid, gridsize)
    corgridt = np.asarray(corgridt)
    cori = [0 for i in xrange(ngrid)]
    for i in xrange(ngrid):
		if corgridt[0][i] == 0:
			cori[i] = 0
		else:
			cori[i] = corgridt[-1][i]/corgridt[0][i]
    plt.plot(x, cori)
    plt.show()
    with open(output,'w') as out:
        for i in xrange(len(corr)):
            out.write('{0:10.3f}{1:10.3f}\n'.format(t[i], corr[i]/corr[0]))
    corgridt = np.asarray(corgridt)
    np.savetxt(output+"_grid", corgridt)


if __name__ == "__main__":
    main(sys.argv[1:])
