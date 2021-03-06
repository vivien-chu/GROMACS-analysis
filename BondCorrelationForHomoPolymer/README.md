These files are used to:
1. Get the bond information from GROMACS output angle gro file, you may need to change the atom name in the file to your own:
angle_to_bond.py.
2. Calculate the bond correlation function for the bond: bondcorrelation.py
3. Use Vogel-Fulcher-Tammann function to fit to the bond correlation function:
fit_vtf.py

Use python *.py -h to see available settings.

The angle file from GROMACS is generated using:
1. Generate the index file for all the angles: 
gmx mk_angndx -s *.tpr -n angle.ndx
2. Output the angles that includes the backbone atoms, you can set the
begin/end time and time step:
gmx trjconv -f *.xtc -o angle.gro -s *.tpr -n angle.ndx -dt 10
Sometimes, the file is very large, you may need to split it into several smaller
files by doing:
split -b 400m angle.gro bond/bond
This will give you several small files called *aa, *ab, etc al. You need to
manually make the start and end lines complete for each small file. 
