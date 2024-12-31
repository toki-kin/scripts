#!/bin/bash

set -euo pipefail

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

GMX_CMD="gmx_mpi"
NTOMP=16
GPU_IDS="0,1"

cd "${SCRIPT_DIR}/md" || exit 1

while true; do
    if ! pgrep -f "gmx_mpi.*mdrun" > /dev/null; then
        LATEST_LOG=$(ls -t md.part*.log 2>/dev/null | head -n1)
        if [ -z "$LATEST_LOG" ]; then
            echo "未找到log文件，等待..." >> monitor.log
            sleep 60
            continue
        fi
        
        if ! grep -q "Finished mdrun" "$LATEST_LOG"; then
            echo "MD似乎异常终止,尝试重启..." >> monitor.log
            nohup mpirun -np 2 $GMX_CMD mdrun -noappend -cpi md -v -deffnm md -s md.tpr -ntomp $NTOMP -pin on -pinoffset 0 -gpu_id $GPU_IDS > md.out 2>&1 &
        else
            echo "MD已正常完成" >> monitor.log
            break
        fi
    fi
    sleep 300
done