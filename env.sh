#!/bin/bash

# Define some basic environmental variables before launching the suite

# Load the analysis3 conda environment
module use /g/data/hh5/public/modules
module load conda/analysis3

# Root directory for this repo
export ROOT=/home/548/${USER}/code/nci_resource_tools
export MODULES=${ROOT}/nci_resource_tools

# Location of Scott Wale's tools
export TOOLS=/home/548/${USER}/code/nci-tools/src/ncitools

# Append to our python path
export PYTHONPATH=${MODULES}:${TOOLS}:${PYTHONPATH}
