#!/bin/bash
# SPDX-License-Identifier: MIT
# Draft values: size these to the specified workload before submission.
#SBATCH --job-name=cpu-job
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --no-requeue

set -euo pipefail

# Add the required explicit module or virtual environment setup here.
# Submit from an environment without credentials or sensitive variables.

# A draft must fail instead of accidentally running an unspecified workload.
# Replace this guard with the approved command, for example:
# exec /absolute/path/to/srun /absolute/path/to/program argument
printf '%s\n' 'Draft job: configure the approved command and environment first.' >&2
exit 64
