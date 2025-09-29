#!/bin/bash

# Define some basic environmental variables before launching the suite
 
# Load the analysis3 conda environment
module use /g/data/xp65/public/modules
module load conda/analysis3

# Load a virtual python environment built on xp65 - this includes 
# 'pymunge' library used by Scott Wales' nci tools repo
source /g/data/gb02/public/venvs/xp65_extras/bin/activate

# Root directory for this repo
export ROOT=/g/data/gb02/public/code/nci_resource_tools
export MODULES=${ROOT}/nci_resource_tools

# Location of Scott Wales' tools
export TOOLS=/g/data/gb02/public/code/nci-tools/src/ncitools

# Append to our python path
export PYTHONPATH=${MODULES}:${TOOLS}:${PYTHONPATH}

# Add quarto to our path
export PATH=${PATH}:/g/data/gb02/pag548/quarto-1.7.29/bin/

echo " INFO : PYTHONPATH=${PYTHONPATH}"
echo " INFO : PATH=${PATH}"