import os

def generate_tree(startpath, exclude_dirs=None, max_depth=None):
    """
    生成项目的树状结构
    
    :param startpath: 起始路径
    :param exclude_dirs: 要排除的目录列表
    :param max_depth: 最大深度，None表示不限制
    :return: 树状结构字符串
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv', '.git', '.idea', '__pycache__']
    
    tree_str = []
    
    def add_tree_level(path, prefix='', depth=0):
        # 检查是否超过最大深度
        if max_depth is not None and depth > max_depth:
            return
        
        # 获取目录内容
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return
        
        # 处理文件和子目录
        for i, entry in enumerate(entries):
            # 跳过排除的目录
            if entry in exclude_dirs:
                continue
            
            full_path = os.path.join(path, entry)
            is_last = (i == len(entries) - 1)
            
            # 确定前缀
            if is_last:
                current_prefix = prefix + '└── '
                next_prefix = prefix + '    '
            else:
                current_prefix = prefix + '├── '
                next_prefix = prefix + '│   '
            
            # 添加当前项
            if os.path.isdir(full_path):
                tree_str.append(f"{current_prefix}{entry}/")
                add_tree_level(full_path, next_prefix, depth + 1)
            else:
                tree_str.append(f"{current_prefix}{entry}")
    
    # 添加根目录
    tree_str.append(os.path.basename(startpath) + '/')
    add_tree_level(startpath)
    
    return '\n'.join(tree_str)

def save_tree_to_markdown(tree_str, output_file='results/project_structure.md'):
    """
    将树状结构保存到Markdown文件
    
    :param tree_str: 树状结构字符串
    :param output_file: 输出文件名
    """
    markdown_content = f"## 项目结构\n\n```\n{tree_str}\n```"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"项目结构已保存到 {output_file}")

# 使用示例
if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成树状结构
    tree_structure = generate_tree(current_dir)
    
    # 打印到控制台
    print(tree_structure)
    
    # 保存到Markdown文件
    save_tree_to_markdown(tree_structure)