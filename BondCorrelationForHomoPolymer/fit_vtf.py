#!/home/mwebb/anaconda/bin/python

#==================================================================
#  IMPORT MODULES
#==================================================================
from math import *
import sys,argparse
from numpy import *
import glob
import numpy as np
from scipy.optimize import curve_fit

#==================================================================
#  AUX: create_parser
#==================================================================
def create_parser():

  parser = argparse.ArgumentParser(description='Computes time constants and Kohlrausch-William-Watts (kww) fits with stretching coefficients from autocorrelation decays.')
  

  # DO REQUIRED POSITIONAL ARGUMENTS
  parser.add_argument('data_name',help = 'Name of file containing data. First column should be time variable, and \
        subsequent columns should contain the ACF data for given Rouse modes.')

  # OPTIONAL ARGUMENTS
  parser.add_argument('-tcut'     ,dest='tcut',default=1.0e8,
                      help = 'Time cutoff to use for fitting data. This can be set to avoid fitting \
                              difficult long-time tails, for example. (default = 1e8)')

  parser.add_argument('-maxtau'     ,dest='tau_max',default=1.0e8,
                      help = 'Specification for constraint on optimization of time constants. \
                              If time constants beyond this value are encountered, a hyperbolic penalty is imposed. (default = 1e8)')

  parser.add_argument('-penalty'     ,dest='pen_params',default="1000 1",
                      help = 'Specification of parameters for imposing hyperbolic penalty function of the form: \
                              C{1+exp[-2k(x-xmax)]}^(-1) \
                              Should be supplied as a quoted pair value as "C k". (default = "1000 1") ')

  return parser

#==================================================================
#  AUX: convert_args
#==================================================================
def convert_args(args):
  data_name       = args.data_name
  tcut            = float(args.tcut)
  maxtau          = float(args.tau_max)
  penalty         = [float(i) for i in args.pen_params.split()]
  return(data_name,tcut,maxtau,penalty)

#==================================================================
#  AUX: is_number
#==================================================================
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#==================================================================
#  AUX: process_data
#==================================================================
def process_data(file):
  fid = open(file,"r")
  lines = [line.strip() for line in fid]
  lines = [line.split() for line in lines]
  lines = [line for line in lines if is_number(line[0]) ]  # SKIP HEADER LINES
  fid.close()
  x     = [float(line[0]) for line in lines if float(line[0]) > 0.0]
  y     = [[float(i) for i in line[1:]] for line in lines if float(line[0]) > 0.0]

  return (array(x),np.log(array(y)).transpose())

#==================================================================
#  AUX: rouse_fun
#==================================================================
def vtf_fun(t,A, B, C):
   penalty = -100000 * C
   
   return B/(t - C) + A + penalty
   #return A / (t - B) + C


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#  MAIN: _main
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def main(argv):
  # CREATE THE ARGUMENT PARSER
  parser = create_parser()

  # PARSE ARGUMENTS
  args               = parser.parse_args()
  (data_name,tcut,taumax,Cpen) \
                     = convert_args(args)

  # PROCESS FILE 
  (t,ACF) = process_data(data_name)   # extracts data in aggregate
  N = ACF.shape[0]                    # number of data sets to be fit
  ind = t <= tcut                     # yields index reference that satisfy time cutoff
  
  # CREATE ANONYMOUS FUNCTIONS THAT IMPOSE PENALTIES
  vtf_con_fun = lambda t,A, B, C     : vtf_fun(t,A, B, C)
 
  # COMPUTE RELAXATION TIMES AND STRETCHING COEFFICIENTS
  # Fit to a functional form of the kind KWW = exp[-(t/tau)^beta]
  # and to a the rouse expected from of  R   = exp[-(t/tau)]
  A = [0.0]*N
  B   = [0.0]*N
  C  = [0.0]*N
  ACF_vtf   = zeros(ACF.shape)
  #dt = t[1] - t[0]
  #nt = np.arange(0, 2, dt)
 # ACF_vtf   = zeros([ACF.shape[0], len(nt)])
  for p,ACFp in enumerate(ACF):
    # PERFORM THE OPTIMIZATION AND CONSTRUCT FITS
    # ROUSE:
    params_vtf   = curve_fit(vtf_con_fun,t[ind],ACFp[ind],p0=[1.0, 1.0, 0.3],maxfev=30000)
    [A[p], B[p], C[p]] = params_vtf[0]
    ACF_vtf[p,:] = vtf_fun(t,A[p], B[p], C[p])
   
   

  # WRITE OUT FITS
  with open(data_name + ".fit.vtf","w") as fid:
    fid.write("#{:<6s}".format("t"))
    for p in range(N):
      fid.write("p={:<8d}".format(p))
    fid.write("\n")
    for i,ti in enumerate(t):
      fid.write("{:>7.3f}".format(ti))
      for p in range(N):
        fid.write("{:>10.5f}".format(np.exp(ACF_vtf[p,i])))
      fid.write("\n")

  with open(data_name + ".taus","w") as fid:
    fid.write("{:<15s}{:^15s}{:^15s}{:^15s}\n".format("#p","A","B","C"))
    for p,(tr,tkww,bff) in enumerate(zip(A,B,C)):
      fid.write("{:<15d}{:>15.5f}{:>15.5f}{:>15.5f}\n".format(p,tr,tkww,bff))
  
  
#==================================================================
#  RUN PROGRAM
#==================================================================
if __name__ == "__main__":
  main(sys.argv[1:])
                          
