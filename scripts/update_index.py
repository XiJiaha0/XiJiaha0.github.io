# .github/scripts/update_index.py
import os
import json
from datetime import datetime

def scan_repository():
    """扫描仓库中的文件夹和HTML文件"""
    structure = {}
    
    for root, dirs, files in os.walk('.'):
        # 忽略.git和其他隐藏文件夹
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.github']
        
        # 获取相对路径
        rel_path = os.path.relpath(root, '.')
        
        # 过滤HTML文件（排除index.html）
        html_files = [
            {
                'name': f,
                'path': os.path.join(rel_path, f),
                'size': os.path.getsize(os.path.join(root, f)),
                'modified': datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(root, f))
                ).strftime('%Y-%m-%d %H:%M')
            }
            for f in files 
            if f.endswith('.html') and f != 'index.html'
        ]
        
        if html_files:
            folder_name = rel_path if rel_path != '.' else '根目录'
            structure[folder_name] = {
                'path': rel_path,
                'files': html_files
            }
    
    return structure

def generate_folder_section(folder_name, folder_data):
    """生成文件夹部分的HTML"""
    files_html = ''
    for file_info in folder_data['files']:
        files_html += f'''
            <div class="project-card">
                <div class="project-icon">
                    <i class="fas fa-file-code"></i>
                </div>
                <h3 class="project-title">{file_info["name"]}</h3>
                <p class="project-description">
                    路径: {file_info["path"]}<br>
                    大小: {file_info["size"]} bytes<br>
                    修改时间: {file_info["modified"]}
                </p>
                <div class="project-tags">
                    <span class="tag">{folder_name}</span>
                    <span class="tag">HTML文档</span>
                </div>
                <a href="{file_info['path']}" class="project-link" target="_blank">
                    查看文档
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        '''
    
    return f'''
    <div class="folder-section">
        <h3 class="folder-title" style="color: var(--text-primary); margin: 40px 0 20px 0; font-size: 1.5rem; border-left: 4px solid #667eea; padding-left: 15px;">
            <i class="fas fa-folder" style="margin-right: 10px; color: #667eea;"></i>
            {folder_name}
        </h3>
        <div class="projects-grid">
            {files_html}
        </div>
    </div>
    '''

def update_index_html(structure):
    """更新index.html文件"""
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成所有文件夹的HTML
    folders_html = ''
    for folder_name, folder_data in structure.items():
        folders_html += generate_folder_section(folder_name, folder_data)
    
    # 如果没有找到文件，显示提示信息
    if not structure:
        folders_html = '''
        <div class="project-card" style="text-align: center; padding: 60px 30px;">
            <div class="project-icon" style="margin: 0 auto 20px auto;">
                <i class="fas fa-folder-open"></i>
            </div>
            <h3 class="project-title">暂无文档</h3>
            <p class="project-description">
                仓库中尚未添加HTML文档<br>
                请上传HTML文件到相应文件夹
            </p>
            <div class="project-tags">
                <span class="tag">提示</span>
            </div>
        </div>
        '''
    
    # 替换项目部分的内容
    start_marker = '<!-- AUTO-GENERATED-PROJECTS-START -->'
    end_marker = '<!-- AUTO-GENERATED-PROJECTS-END -->'
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    
    if start_index != -1 and end_index != -1:
        new_content = (
            content[:start_index + len(start_marker)] +
            f'\n{folders_html}\n        ' +
            content[end_index:]
        )
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"成功更新 index.html，找到 {len(structure)} 个文件夹")
    else:
        print("错误：未找到替换标记")

def main():
    print("开始扫描仓库结构...")
    structure = scan_repository()
    
    print(f"找到 {len(structure)} 个包含HTML文件的文件夹:")
    for folder_name in structure.keys():
        file_count = len(structure[folder_name]['files'])
        print(f"  - {folder_name} ({file_count} 个文件)")
    
    print("更新 index.html...")
    update_index_html(structure)
    print("完成!")

if __name__ == '__main__':
    main()
