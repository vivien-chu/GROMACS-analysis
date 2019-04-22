#!bin/bash

pre=400
for i in {start_temp..end_temp..temp_step}; do
   t=$(((400-$i)*100))
   bt=$(($t-10))
   echo 0 | gmx trjconv -f cooling.xtc -o ${i}.gro -s cooling.tpr -b ${bt} -dump ${t} -pbc\
   whole
   sed -i "s/${pre}/${i}/g" simulation_ana.mdp
   sed -i "s/${pre}/${i}/g" job_temp
   grompp -f simulation_ana.mdp -c ${i}.gro -o ${i}.tpr -p chains.top
   sbatch job_temp
   pre=${i}
done
