#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从source目录下提取Rust代码中的函数、结构体、枚举、常量等，
生成训练数据集
"""

import os
import json
from pathlib import Path
from typing import List, Dict


class RustCodeExtractor:
    """Rust代码提取器 - 使用简单的行扫描方法"""
    
    def __init__(self, source_dir: str = "source"):
        self.source_dir = source_dir
        self.dataset = []
        
    def find_rust_files(self) -> List[Path]:
        """递归查找所有.rs文件"""
        rust_files = []
        for root, dirs, files in os.walk(self.source_dir):
            # 跳过target目录
            if 'target' in dirs:
                dirs.remove('target')
            for file in files:
                if file.endswith('.rs'):
                    rust_files.append(Path(root) / file)
        return rust_files
    
    def read_file_content(self, file_path: Path) -> List[str]:
        """读取文件内容并返回行列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"  ⚠ 读取失败: {e}")
            return []
    
    def count_braces(self, line: str) -> int:
        """计算行中的大括号平衡数"""
        # 简单计数，忽略字符串和注释中的括号
        in_string = False
        in_char = False
        escape = False
        count = 0
        
        for i, ch in enumerate(line):
            if escape:
                escape = False
                continue
            
            if ch == '\\':
                escape = True
                continue
            
            if ch == '"' and not in_char:
                in_string = not in_string
            elif ch == "'" and not in_string:
                in_char = not in_char
            elif not in_string and not in_char:
                if ch == '{':
                    count += 1
                elif ch == '}':
                    count -= 1
        
        return count
    
    def extract_code_block(self, lines: List[str], start_idx: int, keyword: str) -> tuple:
        """
        从指定位置提取代码块
        返回: (代码文本, 结束行索引)
        注意: 返回的结束索引保证 >= start_idx
        """
        # 向前查找注释和属性（限制最多向前50行）
        block_start = start_idx
        lookback = 0
        while block_start > 0 and lookback < 50:
            prev_line = lines[block_start - 1].strip()
            if prev_line.startswith('///') or prev_line.startswith('#[') or prev_line.startswith('//!'):
                block_start -= 1
                lookback += 1
            elif prev_line == '' or prev_line.startswith('//'):
                block_start -= 1
                lookback += 1
            else:
                break
        
        # 查找代码块的结束（从start_idx开始，不是block_start）
        code_lines = []
        # 先添加前面的注释部分
        for j in range(block_start, start_idx):
            code_lines.append(lines[j].rstrip())
        
        brace_count = 0
        found_open_brace = False
        i = start_idx
        max_lines = 2000  # 限制单个代码块最大行数
        
        while i < len(lines) and (i - start_idx) < max_lines:
            line = lines[i]
            code_lines.append(line.rstrip())
            
            # 检查是否有分号结尾（如 struct Foo;）
            if keyword in ['struct', 'type'] and ';' in line and not found_open_brace:
                return ('\n'.join(code_lines), i)
            
            # 计算括号
            brace_delta = self.count_braces(line)
            brace_count += brace_delta
            
            if brace_delta > 0:
                found_open_brace = True
            
            # 如果找到了开括号且括号平衡，结束
            if found_open_brace and brace_count == 0:
                return ('\n'.join(code_lines), i)
            
            i += 1
        
        # 超出限制或到达文件末尾
        if (i - start_idx) >= max_lines:
            print(f"        ⚠ 代码块超过 {max_lines} 行，截断")
        
        # 确保返回的索引 >= start_idx
        end_idx = max(i - 1, start_idx)
        return ('\n'.join(code_lines), end_idx)

    def is_in_range(self, idx: int, ranges: List[tuple]) -> bool:
        """检查索引是否在某个范围内"""
        return any(start <= idx <= end for start, end in ranges)
    
    def extract_macros(self, lines: List[str]) -> List[Dict]:
        """提取宏定义"""
        macros = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 查找 macro_rules! 关键字
            if 'macro_rules!' in line:
                # 提取宏名称
                parts = line.split('macro_rules!')
                if len(parts) > 1:
                    macro_name = parts[1].strip().split()[0].strip('{').strip()
                    print(f"    → 提取宏: {macro_name} (行 {i+1})")
                    
                    # 收集前面的注释和属性
                    macro_start = i
                    lookback = 0
                    while macro_start > 0 and lookback < 50:
                        prev = lines[macro_start - 1].strip()
                        if prev.startswith('///') or prev.startswith('#['):
                            macro_start -= 1
                            lookback += 1
                        else:
                            break
                    
                    # 收集宏定义（查找匹配的大括号）
                    macro_lines = []
                    for j in range(macro_start, i + 1):
                        macro_lines.append(lines[j].rstrip())
                    
                    brace_count = self.count_braces(lines[i])
                    found_open = brace_count > 0
                    
                    if found_open:
                        for j in range(i + 1, min(i + 1000, len(lines))):
                            macro_lines.append(lines[j].rstrip())
                            brace_count += self.count_braces(lines[j])
                            if brace_count == 0:
                                macro_code = '\n'.join(macro_lines).strip()
                                if macro_code:
                                    macros.append({
                                        'name': macro_name,
                                        'code': macro_code,
                                        'type': 'macro'
                                    })
                                    print(f"      ✓ 完成 (结束行 {j+1})")
                                i = max(j, i + 1)
                                break
                        else:
                            print(f"      ✗ 未找到宏结束")
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return macros
    
    def extract_items(self, lines: List[str], keyword: str, item_type: str) -> List[Dict]:
        """提取指定关键字的代码项"""
        items = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过注释行
            if line.startswith('//'):
                i += 1
                continue
            
            # 查找关键字
            if f' {keyword} ' in f' {line} ' or line.startswith(f'{keyword} '):
                # 提取名称
                parts = line.split()
                name_idx = -1
                for j, part in enumerate(parts):
                    if part == keyword and j + 1 < len(parts):
                        name_idx = j + 1
                        break
                
                if name_idx == -1:
                    i += 1
                    continue
                
                # 获取名称（去除泛型和其他符号）
                name = parts[name_idx].split('<')[0].split('(')[0].split('{')[0].split(':')[0]
                print(f"    → 提取 {item_type}: {name} (行 {i+1})")
                
                # 提取代码块
                code, end_idx = self.extract_code_block(lines, i, keyword)
                
                if code.strip():
                    items.append({
                        'name': name,
                        'code': code.strip(),
                        'type': item_type
                    })
                    print(f"      ✓ 完成 (结束行 {end_idx+1})")
                else:
                    print(f"      ✗ 代码为空")
                
                # 确保向前移动
                i = max(end_idx + 1, i + 1)
            else:
                i += 1
        
        return items
    
    def extract_impl_methods(self, lines: List[str]) -> List[Dict]:
        """提取impl块中的方法"""
        methods = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 查找impl关键字
            if line.startswith('impl ') or ' impl ' in line:
                print(f"    → 发现 impl 块 (行 {i+1})")
                
                # 提取类型名
                parts = line.replace('<', ' ').replace('>', ' ').split()
                type_name = None
                for j, part in enumerate(parts):
                    if part == 'impl' and j + 1 < len(parts):
                        type_name = parts[j + 1]
                        break
                    elif part == 'for' and j + 1 < len(parts):
                        type_name = parts[j + 1]
                        break
                
                if not type_name:
                    print(f"      ✗ 无法提取类型名")
                    i += 1
                    continue
                
                print(f"      类型: {type_name}")
                
                # 找到impl块的范围
                impl_start = i
                brace_count = 0
                found_open = False
                impl_end = i
                
                for j in range(i, min(i + 5000, len(lines))):  # 限制搜索范围
                    brace_count += self.count_braces(lines[j])
                    if self.count_braces(lines[j]) > 0:
                        found_open = True
                    if found_open and brace_count == 0:
                        impl_end = j
                        break
                
                print(f"      impl块范围: {impl_start+1} - {impl_end+1}")
                
                # 在impl块中查找方法
                for j in range(impl_start + 1, impl_end):
                    method_line = lines[j].strip()
                    if method_line.startswith('fn ') or ' fn ' in method_line:
                        # 提取方法名
                        fn_parts = method_line.split()
                        method_name = None
                        for k, part in enumerate(fn_parts):
                            if part == 'fn' and k + 1 < len(fn_parts):
                                method_name = fn_parts[k + 1].split('(')[0].split('<')[0]
                                break
                        
                        if method_name:
                            print(f"      → 提取方法: {type_name}::{method_name} (行 {j+1})")
                            # 提取方法代码
                            code, end_idx = self.extract_code_block(lines, j, 'fn')
                            if code.strip():
                                methods.append({
                                    'name': f"{type_name}::{method_name}",
                                    'code': code.strip(),
                                    'type': 'method',
                                    'parent': type_name
                                })
                                print(f"        ✓ 完成")
                            else:
                                print(f"        ✗ 代码为空")
                
                i = impl_end + 1
            else:
                i += 1
        
        return methods

    def extract_functions(self, lines: List[str]) -> List[Dict]:
        """提取独立函数（排除impl块中的）"""
        print(f"    → 查找 impl 块范围...")
        # 先找出所有impl块的范围
        impl_ranges = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('impl ') or ' impl ' in line:
                impl_start = i
                brace_count = 0
                found_open = False
                # 限制搜索范围，防止无限循环
                for j in range(i, min(i + 5000, len(lines))):
                    brace_count += self.count_braces(lines[j])
                    if self.count_braces(lines[j]) > 0:
                        found_open = True
                    if found_open and brace_count == 0:
                        impl_ranges.append((impl_start, j))
                        print(f"      impl 块: {impl_start+1} - {j+1}")
                        i = j
                        break
                else:
                    # 如果没找到结束，跳过这个impl
                    print(f"      ⚠ impl 块未找到结束 (行 {impl_start+1})")
                    i += 1
            i += 1
        
        print(f"    → 找到 {len(impl_ranges)} 个 impl 块")
        print(f"    → 提取独立函数...")
        
        # 提取不在impl块中的函数
        functions = []
        i = 0
        checked = 0
        while i < len(lines):
            checked += 1
            if checked % 1000 == 0:
                print(f"      已检查 {checked}/{len(lines)} 行...")
            
            # 跳过impl块
            if self.is_in_range(i, impl_ranges):
                i += 1
                continue
            
            line = lines[i].strip()
            if line.startswith('fn ') or ' fn ' in line:
                # 提取函数名
                parts = line.split()
                func_name = None
                for j, part in enumerate(parts):
                    if part == 'fn' and j + 1 < len(parts):
                        func_name = parts[j + 1].split('(')[0].split('<')[0]
                        break
                
                if func_name:
                    print(f"      → 提取函数: {func_name} (行 {i+1})")
                    code, end_idx = self.extract_code_block(lines, i, 'fn')
                    if code.strip():
                        functions.append({
                            'name': func_name,
                            'code': code.strip(),
                            'type': 'function'
                        })
                        print(f"        ✓ 完成 (结束行 {end_idx+1})")
                    else:
                        print(f"        ✗ 代码为空")
                    # 确保向前移动，防止无限循环
                    i = max(end_idx + 1, i + 1)
                else:
                    i += 1
            else:
                i += 1
        
        print(f"    → 提取了 {len(functions)} 个独立函数")
        return functions
    
    def create_dataset_entry(self, item: Dict[str, str]) -> Dict[str, str]:
        """创建数据集条目"""
        item_type = item['type']
        item_name = item['name']
        item_code = item['code']
        
        # 根据类型生成问题
        type_map = {
            'struct': '结构体',
            'enum': '枚举',
            'function': '函数',
            'method': '方法',
            'const': '常量',
            'trait': 'trait',
            'type': '类型别名',
            'macro': '宏'
        }
        
        type_name = type_map.get(item_type, item_type)
        question = f"{item_name}{type_name}的源码是怎么实现的？"
        
        # 生成答案（肯定句形式 + 源码）
        answer = f"{item_name}{type_name}的源码实现如下：\n\n```rust\n{item_code}\n```"
        
        return {
            "instruction": question,
            "input": "",
            "output": answer,
            "system": ""
        }
    
    def process_file(self, file_path: Path):
        """处理单个Rust文件"""
        lines = self.read_file_content(file_path)
        if not lines:
            return
        
        try:
            print(f"  文件行数: {len(lines)}")
            
            # 提取各种代码元素
            print(f"  [1/8] 提取 struct...")
            structs = self.extract_items(lines, 'struct', 'struct')
            
            print(f"  [2/8] 提取 enum...")
            enums = self.extract_items(lines, 'enum', 'enum')
            
            print(f"  [3/8] 提取 trait...")
            traits = self.extract_items(lines, 'trait', 'trait')
            
            print(f"  [4/8] 提取 type...")
            type_aliases = self.extract_items(lines, 'type', 'type')
            
            print(f"  [5/8] 提取 const...")
            constants = self.extract_items(lines, 'const', 'const')
            
            print(f"  [6/8] 提取 macro...")
            macros = self.extract_macros(lines)
            
            # 提取方法和函数
            print(f"  [7/8] 提取 impl 方法...")
            methods = self.extract_impl_methods(lines)
            
            print(f"  [8/8] 提取独立函数...")
            functions = self.extract_functions(lines)
            
            # 合并所有提取的项
            all_items = structs + enums + traits + type_aliases + constants + macros + methods + functions
            
            # 为每个项创建数据集条目
            for item in all_items:
                entry = self.create_dataset_entry(item)
                self.dataset.append(entry)
            
            print(f"  ✓ 提取了 {len(all_items)} 个代码元素 (struct:{len(structs)}, enum:{len(enums)}, trait:{len(traits)}, type:{len(type_aliases)}, const:{len(constants)}, macro:{len(macros)}, method:{len(methods)}, fn:{len(functions)})")
        except Exception as e:
            import traceback
            print(f"  ✗ 处理出错: {e}")
            print(f"  错误详情:\n{traceback.format_exc()}")

    def extract_all(self):
        """提取所有Rust文件中的代码"""
        rust_files = self.find_rust_files()
        total = len(rust_files)
        print(f"找到 {total} 个Rust文件\n")
        
        for idx, file_path in enumerate(rust_files, 1):
            print(f"[{idx}/{total}] {file_path}")
            self.process_file(file_path)
        
        print(f"\n总共提取了 {len(self.dataset)} 个数据集条目")
    
    def save_dataset(self, output_path: str = "./dataset/dataset.json"):
        """保存数据集到JSON文件"""
        # 创建输出目录
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建目录: {output_dir}")
        
        # 保存JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, ensure_ascii=False, indent=2)
        
        print(f"\n数据集已保存到: {output_path}")
        print(f"数据集大小: {len(self.dataset)} 条")


def main():
    """主函数"""
    print("=" * 60)
    print("Rust代码提取器 - 生成训练数据集")
    print("=" * 60)
    print()
    
    # 创建提取器
    extractor = RustCodeExtractor(source_dir="source")
    
    # 提取所有代码
    extractor.extract_all()
    
    # 保存数据集
    extractor.save_dataset("./dataset/dataset.json")
    
    print()
    print("=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
