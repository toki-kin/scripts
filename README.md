# Molecular Dynamics & File Processing Scripts Collection

A comprehensive collection of scripts for molecular dynamics simulation setup, monitoring, and molecular file processing. These tools are designed to streamline the workflow of molecular dynamics research and handle various molecular file formats.

## Overview

This toolkit consists of two main components:

### 1. File Processing Tools
- Molecular file format handling (SDF, PDB)
- Chain ID manipulation
- Data extraction and comparison
- File sorting and merging

### 2. Molecular Dynamics Tools
- Automated MD simulation setup
- Coarse-grained simulation preparation
- Simulation monitoring and crash recovery
- Multi-step workflow (EM -> EQ -> MD)

## Purpose of the scripts

### File Processing Tools

check_boost.cpp: Check the version of boost library

sort_sdf.py: Sort molecules in SDF file based on given ID list

compare_sdf.py: Compare and extract information of identical molecules from two SDF files

plus_sdfs.py: Calculate sum of docking scores for identical molecules from two SDF files

key.py: Extract rows from CSV file based on keywords in a keyword file

extract_output.sh: Calculate binding time for specific molecules

insert.py: Add chain numbers to PDB files

chain.py: Process chain identifiers in PDB files, adding chain IDs to molecules

### Molecular Dynamics Tools

prepare_cg_sim.sh: Prepare files for coarse-grained molecular dynamics simulation

md_setup.sh: Set up directory structure and files for MD simulation

run_md.sh: Run energy minimization (EM), equilibration (EQ) and molecular dynamics (MD) simulation

monitor_md.sh: Monitor MD simulation status and auto-restart on abnormal termination

## Usage Instructions

### Prerequisites
- Python 3.6+
- GROMACS
- Boost library

### File Processing Scripts
```bash
# Compare two SDF files
python compare_sdfs.py file1.sdf file2.sdf

# Sum docking scores
python plus_sdfs.py file1.sdf file2.sdf

# Extract CSV rows by keywords
python key.py -i input.csv -k keywords.txt -o output.csv

# Add chain IDs to PDB
python insert.py -f input.pdb -o output_with_chain.pdb
python chain.py -f input.pdb -o output.pdb
