import argparse
import string

def process_pdb(input_pdb, output_pdb):
    # 定义链编号列表，A-Z共26个链编号
    chain_ids = list(string.ascii_uppercase)

    # 初始化
    current_chain_index = 0  # 确保从A开始
    current_resSeq = -1
    current_resName = ""
    first_chain_handled = False  # 用于标记是否处理过第一条链

    # 定义氨基酸列表
    amino_acids = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY',
        'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER',
        'THR', 'TRP', 'TYR', 'VAL'
    }

    # 定义脂质名称列表
    lipids = {'POPC'}

    with open(input_pdb, "r") as f:
        lines = f.readlines()

    with open(output_pdb, "w") as f:
        for i, line in enumerate(lines):
            if line.startswith("ATOM") or line.startswith("HETATM"):
                # 提取当前行的resSeq（分子序号）和resName（成分名称）
                resSeq = int(line[22:26].strip())
                resName = line[16:21].strip()

                if not first_chain_handled:
                    # 确保第一条链从A开始
                    current_chain_index = 0
                    first_chain_handled = True
                else:
                    # 检查成分名称是否改变
                    if resName != current_resName:
                        # 如果从脂质变为溶剂，或者氨基酸变为其他成分，重新分配链编号
                        if (current_resName in lipids and resName == 'SOL') or \
                        (current_resName in amino_acids and resName not in amino_acids) or \
                        (current_resName not in amino_acids and resName in amino_acids):
                            f.write(f"TER   {i+1:>5}      {current_resName} {chain_ids[current_chain_index]}\n")
                            current_chain_index += 1
                            if current_chain_index >= len(chain_ids):
                                raise ValueError("链编号超出限制！超过26个链（A-Z）")

                # 更新当前的resName
                current_resName = resName

                # 如果resSeq从0开始，并且当前分子序号与之前的不同，则切换到下一个链编号
                if resSeq == 1 and resSeq != current_resSeq:
                    if current_resSeq != -1:  # 仅在不是第一个链时增加链编号
                        f.write(f"TER   {i+1:>5}      {current_resName} {chain_ids[current_chain_index]}\n")
                        current_chain_index += 1
                        if current_chain_index >= len(chain_ids):
                            raise ValueError("链编号超出限制！超过26个链（A-Z）")

                # 更新当前的resSeq
                current_resSeq = resSeq

                # 按照PDB文件格式规范，确保每个字段正确对齐
                line = (
                    line[:21] + chain_ids[current_chain_index] +   # 插入链编号
                    line[22:26].rjust(4) + line[26:]  # 调整对齐
                )

                f.write(line)
        
        # 最后一条链结束时添加TER
        f.write(f"TER   {len(lines)+1:>5}      {current_resName} {chain_ids[current_chain_index]}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a PDB file and insert chain identifiers.")
    #用法：python insert.py -f input.pdb -o output_with_chain.pdb
    parser.add_argument("-f", "--file", required=True, help="Input PDB file")
    parser.add_argument("-o", "--output", required=True, help="Output PDB file with chain identifiers")

    args = parser.parse_args()

    process_pdb(args.file, args.output)
