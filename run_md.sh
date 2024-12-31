#!/bin/bash

set -euo pipefail

GMX_CMD="gmx_mpi"
NTOMP=16
GPU_IDS="0,1"

run_em() {
    cd em || exit 1
    
    [ -f "topol.top" ] || exit 1
    [ -f "em.mdp" ] || exit 1
    [ -f "system.gro" ] || exit 1
    
    $GMX_CMD grompp -p topol.top -f em.mdp -c system.gro -o em.tpr -maxwarn 1 || exit 1
    $GMX_CMD mdrun -v -deffnm em || exit 1
    
    [ -f "em.gro" ] || exit 1
    cd ..
}

run_eq() {
    cd eq || exit 1
    
    cp ../em/em.gro ./
    $GMX_CMD grompp -p topol.top -f eq.mdp -c em.gro -r em.gro -o eq.tpr -maxwarn 1 || exit 1
    $GMX_CMD mdrun -v -deffnm eq -ntomp $NTOMP -nb gpu || exit 1
    
    [ -f "eq.gro" ] || exit 1
    cd ..
}

run_md_background() {
    cd md || exit 1
    
    cp ../eq/eq.gro ./
    $GMX_CMD grompp -p topol.top -f md.mdp -c eq.gro -o md.tpr -maxwarn 1 || exit 1
    nohup mpirun -np 2 $GMX_CMD mdrun -noappend -cpi md -v -deffnm md -s md.tpr -ntomp $NTOMP -pin on -pinoffset 0 -gpu_id $GPU_IDS > md.out 2>&1 &
    
    # 启动监控脚本
    chmod +x ../monitor_md.sh
    nohup ../monitor_md.sh > monitor.out 2>&1 &
    
    cd ..
}

main() {
    [ -d "em" ] || exit 1
    [ -d "eq" ] || exit 1
    [ -d "md" ] || exit 1
    
    run_em
    run_eq
    run_md_background
    
    echo "MD started in background"
}

main
