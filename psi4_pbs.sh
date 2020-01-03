#!/bin/sh
#
# Sample Torque job submition.

### Job name
#PBS -N noname
### Declare job non-rerunable
#PBS -r n
### Output files
#PBS -e test.err
#PBS -o test.log
### request 2 processors for this job (1 node and 2 processors per node)
#PBS -l nodes=1:ppn=2

# This job's working directory
echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR    

echo Running on host `hostname`
echo Time is `date`
echo Directory is `pwd`
echo This jobs runs on the following processors:
echo `cat $PBS_NODEFILE`
# Define number of processors
NPROCS=`wc -l < $PBS_NODEFILE`
echo This job has allocated $NPROCS nodes

# Run psi4 with scratch in a temporary directory
PSI4_SCRATCH=`mktemp -d /tmp/psi4__XXXXXX`

echo The psi4 scratch dir is $PSI4_SCRATCH

function finish {
  rm -rf "$PSI4_SCRATCH"
}
trap finish EXIT

export OMP_NUM_THREADS=$NPROCS
export MKL_NUM_THREADS=$NPROCS

# Run psi4
psi4 -s "$PSI4_SCRATCH" -n $NPROCS
