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
    parser = argparse.ArgumentParser(description = "Read from angle file and write out bond information")
    parser.add_argument('data_name', help = "Path and name of ion trajectory file, default is bond/bond")
    parser.add_argument('-o', dest='output', default = 'out.txt', help = 'The name of output file, default is out.txt')
    return parser

def convert_args(args):
    data_name = args.data_name
    output = args.output
    return (data_name,output)


def dist(a,b,boxl):
    d = 0
    for i in xrange(3):
        m = abs(b[i]-a[i])
        if m > 0.5*boxl[i]:
            m -= boxl[i]
        d += m*m
    return math.sqrt(d)
    
def vectorb(a,b,boxl):
    c = []
    for i in xrange(3):
        x = b[i]-a[i]
        if x>0.5*boxl[i]:
            x-= boxl[i]
        if x<-0.5*boxl[i]:
            x+=boxl[i]
        c.append(x)
    return c
        

def main(argv):
    parser = create_parser()
    args = parser.parse_args()
    (data_name, output)=convert_args(args)
    fl = ['aa','ab','ac','ad','ae','af','ag','ah','ai','aj','ak','al','am','an']#,'ao','ap','aq','ar','as','at','au','av', 'aw', 'ax', 'ay', 'az', 'ba', 'bb', 'bc', 'bd', 'be', 'bf']
    psl = []
    p2vpl = []
    outs = open('bond'+output,'w')
    kk = 0
    natoms = 0
    lines = []
    count = 0
    #boxl = [16.68,10.84,11.45]
    for fk in fl:
        with open(data_name+fk,'r') as f:
            line = f.readline()
            lines.append(line)
            count += 1
            if fk == 'aa':               
                #lines.append(line)
                time = int(float(line.split()[-1]))
                print "line 92: time", time
            print fk
            while line:
                if fk == 'aa' and natoms == 0:
                    line = f.readline()
                    lines.append(line)
                    count += 1
                    natoms = int(line.split()[0])
                    print "natoms", natoms
                #print len(lines)
                if len(lines)==(natoms+3):
                    #line = f.readline()
                    time = float(lines[0].split()[-1])
                    #print 'line 104: time', time
                    #print lines[-1]
                    boxl = map(lambda x: float(x), lines[-1].split())
                    outs.write('frame '+str(kk)+'   '+str(time)+'   '+line)
                    lines = lines[2:]
                    for i in xrange(natoms/3):
                        li1 = lines[i*3]
                        li2 = lines[i*3+1]
                        li3 = lines[i*3+2]
                        p1 = np.asarray(map(lambda x: float(x), li1.split()[-3:]))
                        p2 = np.asarray(map(lambda x: float(x), li2.split()[-3:]))
                        n1 = int(li1[15:20])
                        n2 = int(li2[15:20])
                        p2 = vectorb(p1,p2,boxl)
                        outs.write('{0:8d}{1:8d}{2:10.3f}{3:10.3f}{4:10.3f}{5:10.3f}\n'.format(n1, n2, p2[0], p2[1], p2[2], p1[0]))
                    lines = []
                    kk += 1
                    print kk
                    
                if len(lines) < natoms+3:
                    line = f.readline()
                    if line:
                        lines.append(line)
                    
                   


    outs.close()







if __name__ == "__main__":
    main(sys.argv[1:])
