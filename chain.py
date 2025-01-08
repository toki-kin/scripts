import argparse
import string
from typing import Generator

class ChainLimitExceeded(Exception):
    """自定义异常类，用于处理链编号超出限制的情况"""
    pass

class PDBChainProcessor:
    """PDB文件处理器类，用于处理PDB文件中的链标识符
    
    主要功能：
    - 为PDB文件中的分子添加链标识符
    - 处理氨基酸、脂质和溶剂分子的链分配
    - 在适当位置插入TER记录
    """
    def __init__(self):
        # 初始化链编号列表(A-Z)
        self.chain_ids = list(string.ascii_uppercase)
        # 定义标准氨基酸集合
        self.amino_acids = {
            'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY',
            'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER',
            'THR', 'TRP', 'TYR', 'VAL'
        }
        # 定义脂质分子集合
        self.lipids = {'POPC'}

    def check_chain_limit(self, current_chain_index: int) -> None:
        """检查链编号是否超出限制(A-Z 26个字母)
        
        Args:
            current_chain_index: 当前链的索引值
        Raises:
            ChainLimitExceeded: 当链编号超过26时抛出异常
        """
        if current_chain_index >= len(self.chain_ids):
            raise ChainLimitExceeded("链编号超出限制！超过26个链（A-Z）")

    def should_change_chain(self, current_resName: str, resName: str) -> bool:
        """判断是否需要更换链编号
        
        在以下情况下需要更换链编号：
        1. 从脂质变为溶剂分子
        2. 从氨基酸变为非氨基酸
        3. 从非氨基酸变为氨基酸
        
        Args:
            current_resName: 当前残基名称
            resName: 新的残基名称
        Returns:
            bool: 是否需要更换链编号
        """
        return ((current_resName in self.lipids and resName == 'SOL') or
                (current_resName in self.amino_acids and resName not in self.amino_acids) or
                (current_resName not in self.amino_acids and resName in self.amino_acids))

    def write_ter_line(self, fout, i: int, resName: str, chain_id: str) -> None:
        """写入TER终止记录行
        
        Args:
            fout: 输出文件对象
            i: 行号
            resName: 残基名称
            chain_id: 链标识符
        """
        fout.write(f"TER   {i+1:>5}      {resName} {chain_id}\n")

    def process_line(self, line: str, chain_id: str) -> str:
        """处理PDB文件中的单行数据
        
        将链标识符插入到正确的位置，并保持格式对齐
        
        Args:
            line: 原始PDB文件行
            chain_id: 要插入的链标识符
        Returns:
            str: 处理后的PDB文件行
        """
        return (line[:21] + chain_id + line[22:26].rjust(4) + line[26:])

    def process_pdb(self, input_pdb: str, output_pdb: str) -> None:
        """处理整个PDB文件
        
        Args:
            input_pdb: 输入PDB文件路径
            output_pdb: 输出PDB文件路径
        """
        # 初始化链编号索引
        current_chain_index = 0
        # 初始化残基序号
        current_resSeq = -1
        # 初始化残基名称
        current_resName = ""
        # 标记是否已处理第一条链
        first_chain_handled = False

        with open(input_pdb, "r") as fin, open(output_pdb, "w") as fout:
            for i, line in enumerate(fin):
                if not (line.startswith("ATOM") or line.startswith("HETATM")):
                    continue

                resSeq = int(line[22:26].strip())
                resName = line[16:21].strip()

                if not first_chain_handled:
                    first_chain_handled = True
                elif resName != current_resName and self.should_change_chain(current_resName, resName):
                    self.write_ter_line(fout, i, current_resName, self.chain_ids[current_chain_index])
                    current_chain_index += 1
                    self.check_chain_limit(current_chain_index)

                if resSeq == 0 and resSeq != current_resSeq and current_resSeq != -1:
                    self.write_ter_line(fout, i, current_resName, self.chain_ids[current_chain_index])
                    current_chain_index += 1
                    self.check_chain_limit(current_chain_index)

                current_resName = resName
                current_resSeq = resSeq
                
                processed_line = self.process_line(line, self.chain_ids[current_chain_index])
                fout.write(processed_line)

            # 写入最后一条链的TER记录
            self.write_ter_line(fout, i+1, current_resName, self.chain_ids[current_chain_index])

def main():
    parser = argparse.ArgumentParser(description="处理PDB文件并插入链标识符")
    parser.add_argument("-f", "--file", required=True, help="输入PDB文件")
    parser.add_argument("-o", "--output", required=True, help="输出带链标识符的PDB文件")
    args = parser.parse_args()

    processor = PDBChainProcessor()
    try:
        processor.process_pdb(args.file, args.output)
    except ChainLimitExceeded as e:
        print(f"错误: {e}")
        exit(1)

if __name__ == "__main__":
    main()