
if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  
  ulimit -c 0 # set the maximum size of the core files
  
  module load new gcc/6.3.0  
  module load python/3.7.1 mvapich2
  module load cmake/3.11.4
  #module load matlab/R2019b

fi
