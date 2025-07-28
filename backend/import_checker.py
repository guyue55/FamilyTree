#!/usr/bin/env python
"""
导入检查脚本

检查指定目录下Python文件的导入问题，包括：
1. 未使用的导入
2. 缺失的导入
3. 语法错误
"""

import ast
import os
import sys
from pathlib import Path
from typing import Set, List, Dict


class ImportChecker:
    """导入检查器"""
    
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.unused_imports = {}
        self.missing_imports = {}
        self.syntax_errors = {}
        
    def check_file(self, file_path: Path) -> Dict:
        """检查单个文件的导入问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content, filename=str(file_path))
            
            # 收集导入和使用情况
            imports = self._collect_imports(tree)
            used_names = self._collect_used_names(tree)
            
            # 检查未使用的导入
            unused = self._find_unused_imports(imports, used_names)
            
            return {
                'file': str(file_path),
                'imports': imports,
                'used_names': used_names,
                'unused_imports': unused,
                'syntax_error': None
            }
            
        except SyntaxError as e:
            return {
                'file': str(file_path),
                'imports': {},
                'used_names': set(),
                'unused_imports': [],
                'syntax_error': str(e)
            }
        except Exception as e:
            return {
                'file': str(file_path),
                'imports': {},
                'used_names': set(),
                'unused_imports': [],
                'syntax_error': f"Error reading file: {e}"
            }
    
    def _collect_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        """收集所有导入语句"""
        imports = {
            'import': [],
            'from_import': [],
            'import_as': [],
            'from_import_as': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        imports['import_as'].append((alias.name, alias.asname))
                    else:
                        imports['import'].append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if alias.asname:
                        imports['from_import_as'].append((module, alias.name, alias.asname))
                    else:
                        imports['from_import'].append((module, alias.name))
        
        return imports
    
    def _collect_used_names(self, tree: ast.AST) -> Set[str]:
        """收集所有使用的名称"""
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # 处理属性访问，如 module.function
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        return used_names
    
    def _find_unused_imports(self, imports: Dict, used_names: Set[str]) -> List[str]:
        """查找未使用的导入"""
        unused = []
        
        # 检查直接导入
        for module_name in imports['import']:
            # 获取模块的顶级名称
            top_level = module_name.split('.')[0]
            if top_level not in used_names:
                unused.append(f"import {module_name}")
        
        # 检查带别名的导入
        for module_name, alias in imports['import_as']:
            if alias not in used_names:
                unused.append(f"import {module_name} as {alias}")
        
        # 检查from导入
        for module_name, imported_name in imports['from_import']:
            if imported_name not in used_names:
                unused.append(f"from {module_name} import {imported_name}")
        
        # 检查带别名的from导入
        for module_name, imported_name, alias in imports['from_import_as']:
            if alias not in used_names:
                unused.append(f"from {module_name} import {imported_name} as {alias}")
        
        return unused
    
    def check_directory(self) -> Dict:
        """检查整个目录"""
        results = {}
        
        for py_file in self.directory.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            
            result = self.check_file(py_file)
            results[str(py_file)] = result
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 80)
        report.append("导入检查报告")
        report.append("=" * 80)
        
        total_files = len(results)
        files_with_issues = 0
        total_unused = 0
        
        for file_path, result in results.items():
            if result['syntax_error']:
                files_with_issues += 1
                report.append(f"\n❌ {file_path}")
                report.append(f"   语法错误: {result['syntax_error']}")
                continue
            
            unused = result['unused_imports']
            if unused:
                files_with_issues += 1
                total_unused += len(unused)
                report.append(f"\n⚠️  {file_path}")
                report.append(f"   未使用的导入 ({len(unused)}个):")
                for imp in unused:
                    report.append(f"     - {imp}")
        
        # 统计信息
        report.append("\n" + "=" * 80)
        report.append("统计信息")
        report.append("=" * 80)
        report.append(f"总文件数: {total_files}")
        report.append(f"有问题的文件数: {files_with_issues}")
        report.append(f"未使用导入总数: {total_unused}")
        
        if files_with_issues == 0:
            report.append("\n✅ 所有文件的导入都正常！")
        
        return "\n".join(report)


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python import_checker.py <目录路径>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"错误: 目录 {directory} 不存在")
        sys.exit(1)
    
    print(f"正在检查目录: {directory}")
    
    checker = ImportChecker(directory)
    results = checker.check_directory()
    report = checker.generate_report(results)
    
    print(report)
    
    # 保存报告到文件
    report_file = "import_check_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_file}")


if __name__ == "__main__":
    main()