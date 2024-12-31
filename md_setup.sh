#!/bin/bash

# 设置严格模式
set -euo pipefail

# 定义变量
WORK_DIR=$(pwd)
ITP_SOURCE_DIR=~/itp
LOG_FILE="${WORK_DIR}/md_prep.log"
DIRS=("em" "eq" "md")
MDP_DIR="$HOME/mdp"

# 创建日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1" | tee -a "${LOG_FILE}"
}

# 错误处理函数
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 检查必要文件是否存在
[ -d "${ITP_SOURCE_DIR}" ] || error_exit "itp source directory not found"
[ -f "topol.top" ] || error_exit "topol.top not found"
[ -f "system.gro" ] || error_exit "system.gro not found"
[[ -d $MDP_DIR ]] || error_exit "mdp 目录不存在: $MDP_DIR"

# 开始处理
log "Starting MD preparation..."

# 复制itp文件
log "Copying itp files..."
cp -r "${ITP_SOURCE_DIR}" . || error_exit "Failed to copy itp directory"

# 创建目录
log "Creating directories..."
for dir in "${DIRS[@]}"; do
    mkdir -p "$dir" || error_exit "Failed to create $dir directory"
    log "Created directory: $dir"
done

# 复制topol.top到各个目录
log "Copying topol.top to directories..."
for dir in "${DIRS[@]}"; do
    cp topol.top "$dir/" || error_exit "Failed to copy topol.top to $dir"
    log "Copied topol.top to $dir"
done

# 复制system.gro到em目录
log "Copying system.gro to em directory..."
cp system.gro em/ || error_exit "Failed to copy system.gro to em directory"

# 复制 mdp 文件到对应目录
log "Copying mdp files to directories..."
cp -f "$MDP_DIR/em.mdp" "em/" || error_exit "复制 em.mdp 失败"
cp -f "$MDP_DIR/eq.mdp" "eq/" || error_exit "复制 eq.mdp 失败"
cp -f "$MDP_DIR/md.mdp" "md/" || error_exit "复制 md.mdp 失败"

log "MD preparation completed successfully"
