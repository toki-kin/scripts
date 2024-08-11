from rdkit import Chem

# 读取包含id的文本文件（例如output.txt）
with open('output.txt', 'r') as f:
    ids = f.read().splitlines()

# 从SDF文件（例如input.sdf）中提取包含相应id的小分子，并按照id的顺序重新排列
suppl = Chem.SDMolSupplier('input.sdf', removeHs=False, lazy = True)

# 使用一个字典来存储匹配的小分子，键是小分子的id，值是小分子对象
output_mols = {mol.GetProp('_Name'): mol for mol in suppl if mol is not None and mol.GetProp('_Name') in ids}

# 按照ids列表的顺序，将匹配的小分子添加到一个新的列表中
output_mols_ordered = [output_mols[id] for id in ids if id in output_mols]

# 将排列后的小分子保存到一个新的SDF文件（例如output.sdf）中
w = Chem.SDWriter('output.sdf')
for mol in output_mols_ordered:
    w.write(mol)
w.close()
