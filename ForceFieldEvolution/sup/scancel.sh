#!/bin/sh
squeue -u weiweichu -o "%.9i %.9P %.25j %.4u %.2t %.10M %.5D     %R" | awk '{print $1}' >> tocancel
while read line; do
  echo $line
  scancel $line
done < tocancel
