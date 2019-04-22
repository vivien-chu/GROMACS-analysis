# This is used to do parameter sweaping with evolutionary algorithm for GROMACS forcefield for butyl rubber.

In this case, we are sweaping for sigma and epsilon in the Lennard-Jones potential to match the experimental value of density. The idea is to generate N children for each iteration. The N children will have randomized value of sigma and epsilon. We equilibrate and then cool down the system. From the density-temperature curve, we calculate the slope and intercept and match them to the experiment value. We will choose the child/children with the smallest error and use them as the center to generate the next generation. After several iteration, we should get the parameters with enough precision.

