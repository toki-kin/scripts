#!/bin/bash

conda activate martinize

# 在当前目录查找PDB文件
pdb_file=$(ls *.pdb | grep -v "_cg.pdb" | head -n 1)

if [ -z "$pdb_file" ]; then
    echo "错误：未找到PDB文件"
    exit 1
fi

# 获取不带扩展名的文件名
base_name="${pdb_file%.pdb}"

# 运行martinize2，输出带_cg后缀的PDB文件
martinize2 -f "$pdb_file" -o "${base_name}.top" -x "${base_name}_cg.pdb" -dssp dssp -p backbone -ff martini3001 -elastic -ef 700.0 -el 0.5 -eu 0.9 -ea 0 -ep 0 -scfix -cys auto -maxwarn 99

# 检查是否成功创建CG PDB文件
if [ ! -f "${base_name}_cg.pdb" ]; then
    echo "错误：未能创建 ${base_name}_cg.pdb"
    exit 1
fi

insane     -o system.gro -p topol.top     -pbc cubic -box 15,15,12     -l POPC -sol W     -f "${base_name}_cg.pdb" -center    -salt 0.15 -charge 0

# 检查输入文件
if [ ! -f "topol.top" ]; then
    echo "错误: topol.top 文件不存在"
    exit 1
fi

# 创建备份
cp topol.top topol_bak.top
echo "已创建备份文件: topol_bak.top"

# 创建临时文件
temp_file=$(mktemp)

# 写入新的include语句
cat > "$temp_file" << 'EOF'
#include "../itp/martini_v3.0.0.itp"

#include "../itp/martini_v3.0.0_phospholipids_v1.itp"

#include "../itp/martini_v3.0.0_ions_v1.itp"

#include "../itp/martini_v3.0.0_solvents_v1.itp"

#include "../molecule_0.itp"
EOF

# 将原文件中非include部分追加到临时文件，同时进行替换
sed '/^#include/d' topol.top | \
    sed 's/Protein          1/molecule_0       2/g' | \
    sed 's/NA+/NA /g' | \
    sed 's/CL-/CL /g' >> "$temp_file"

# 将临时文件移动回原文件
mv "$temp_file" topol.top

echo "替换完成"

# 检查system.gro文件
if [ ! -f "system.gro" ]; then
    echo "错误: system.gro 文件不存在"
    exit 1
fi

# 创建system.gro备份
cp system.gro system_bak.gro
echo "已创建备份文件: system_bak.gro"

# 替换system.gro中的内容
sed -i 's/NA+/NA /g' system.gro
sed -i 's/CL-/CL /g' system.gro

echo "system.gro 文件替换完成"