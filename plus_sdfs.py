from rdkit import Chem
import sys
# 使用方法python plus_sdfs.py sdf文件1 sdf文件2
a = sys.argv[1]
b = sys.argv[2]

# 读取第一个sdf文件并记录其docking score
docking_scores1 = {}
suppl1 = Chem.SDMolSupplier(a)
for mol in suppl1:
    if mol is not None:
        id = mol.GetProp("_Name")
        score = mol.GetDoubleProp("r_i_docking_score")
        docking_scores1[id] = score

# 读取第二个sdf文件并记录其docking score
docking_scores2 = {}
suppl2 = Chem.SDMolSupplier(b)
for mol in suppl2:
    if mol is not None:
        id = mol.GetProp("_Name")
        score = mol.GetDoubleProp("r_i_docking_score")
        docking_scores2[id] = score

# 找到相同的分子并计算其docking score总和
common_mols = set(docking_scores1.keys()) & set(docking_scores2.keys())
total_score = 0.0
with open("output.txt", "w") as f:
    for id in common_mols:
        score1 = docking_scores1[id]
        score2 = docking_scores2[id]
        total_score += score1 + score2
        f.write(f"{id}\n{score1} + {score2} = {score1 + score2}\n\n")
