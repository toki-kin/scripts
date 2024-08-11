import os
import sys
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import SDWriter

#a和b是要进行对比的文件，使用方法是命令行输入python compare_sdfs.py 对比文件1 对比文件2
a = sys.argv[1]
b = sys.argv[2]

c = a.replace('_sp_5000.sdf','')
d = b.replace('_sp_5000.sdf','')

a = sys.argv[1]
b = sys.argv[2]
# 读取sdf文件
suppl = Chem.SDMolSupplier(a)

# 创建输出的sdf文件
writer = Chem.SDWriter("{}.sdf".format(c))

# 遍历分子并提取属性
for mol in suppl:
    if mol is None:
        continue

    # 获取分子名称
    mol_name = mol.GetProp('_Name')

    # 获取属性
    docking_score = mol.GetProp('r_i_docking_score')
    glide_gscore = mol.GetProp('r_i_glide_gscore')

    # 创建新的分子
    new_mol = Chem.MolFromSmiles(Chem.MolToSmiles(mol))
    new_mol.SetProp('r_i_docking_score', docking_score)
    new_mol.SetProp('r_i_glide_gscore', glide_gscore)
    new_mol.SetProp('_Name', mol_name)

    # 计算分子的描述符
    AllChem.Compute2DCoords(new_mol)

    # 写入输出的sdf文件
    writer.write(new_mol)

# 关闭输出的sdf文件
writer.close()


# 读取sdf文件
suppl = Chem.SDMolSupplier(b)

# 创建输出的sdf文件
writer = Chem.SDWriter("{}.sdf".format(d))

# 遍历分子并提取属性
for mol in suppl:
    if mol is None:
        continue

    # 获取分子名称
    mol_name = mol.GetProp('_Name')

    # 获取属性
    docking_score = mol.GetProp('r_i_docking_score')
    glide_gscore = mol.GetProp('r_i_glide_gscore')

    # 创建新的分子
    new_mol = Chem.MolFromSmiles(Chem.MolToSmiles(mol))
    new_mol.SetProp('r_i_docking_score', docking_score)
    new_mol.SetProp('r_i_glide_gscore', glide_gscore)
    new_mol.SetProp('_Name', mol_name)

    # 计算分子的描述符
    AllChem.Compute2DCoords(new_mol)

    # 写入输出的sdf文件
    writer.write(new_mol)

# 关闭输出的sdf文件
writer.close()

def compare_sdf_files(sdf_file_1, sdf_file_2, output_file):
    # 读取第一个sdf文件
    suppl_1 = Chem.SDMolSupplier(sdf_file_1)
    mols_1 = [mol for mol in suppl_1 if mol is not None]
    # 读取第二个sdf文件
    suppl_2 = Chem.SDMolSupplier(sdf_file_2)
    mols_2 = [mol for mol in suppl_2 if mol is not None]

    # 将第二个sdf文件的小分子以字典形式存储，键为化合物名称，值为化合物对象
    mols_2_dict = {mol.GetProp("_Name"): mol for mol in mols_2}

    # 创建一个SDWriter对象，用于将匹配的小分子输出到sdf文件中
    writer = SDWriter(output_file)

    # 遍历第一个sdf文件中的小分子，查找是否在第二个sdf文件中存在相同的小分子
    for mol_1 in mols_1:
        name = mol_1.GetProp("_Name")
        if name in mols_2_dict:
            mol_2 = mols_2_dict[name]
            # 将两个分子的docking_score和glide_gscore写入新的sdf文件中
            writer.write(mol_1)

    writer.close()

compare_sdf_files("{}.sdf".format(c), "{}.sdf".format(d), "{}_output.sdf".format(c))
compare_sdf_files("{}.sdf".format(d), "{}_output.sdf".format(c), "{}_output.sdf".format(d))
#删除临时文件
os.remove("{}.sdf".format(c))
os.remove("{}.sdf".format(d))