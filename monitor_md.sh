#!/bin/bash

set -euo pipefail

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

GMX_CMD="gmx_mpi"
NTOMP=16
GPU_IDS="0,1"

cd "${SCRIPT_DIR}/md" || exit 1

log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1" >> monitor.log
}

log_message "监控脚本启动"

while true; do
    current_time=$(date '+%Y-%m-%d %H:%M:%S')
    if ! pgrep -f "gmx_mpi" > /dev/null; then
        LATEST_LOG=$(ls -t md.part*.log 2>/dev/null | head -n1)
        if [ -z "$LATEST_LOG" ]; then
            log_message "[${current_time}] 未找到log文件，等待..."
            sleep 60
            continue
        fi
        
        if ! grep -q "Finished mdrun" "$LATEST_LOG"; then
            log_message "[${current_time}] MD似乎异常终止,尝试重启..."
               nohup $GMX_CMD mdrun -ntmpi 2 -noappend -cpi md -v -deffnm md -s md.tpr -ntomp $((NTOMP/2)) -pin on -pinoffset 0 -gpu_id $GPU_IDS > md.out 2>&1 &
        else
            log_message "[${current_time}] MD已正常完成"
            break
        fi
    fi
    sleep 300
done