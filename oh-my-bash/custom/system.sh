
if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  ulimit -c 0 # set the maximum size of the core files
  echo "Load modules..."
#  . /cluster/apps/local/env2lmod.sh
#  module load gcc/8.2.0  python/3.6.4  cmake/3.9.4 openmpi/4.0.2
  
  module load new gcc/6.3.0  
  module load python/3.7.1
  module load mvapich2
  module load cmake/3.11.4
  echo "Done loading modules."
fi

if [[ $HOST_NAME == *"panda.ethz.ch"* ]]; then
  module load gnu/9.1.0
  module load mpich
  module load python
  module load gsl
fi

if [[ $HOST_NAME == *"barry.ethz.ch"* ]]; then
  module load python
  module load gnu
fi
