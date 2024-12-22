import PyInstaller.__main__
import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 配置打包参数
options = [
    'ai_cluster_evaluator.py',  # 主程序文件
    '--name=AI集群评测系统',  # 程序名称
    '--noconsole',  # 不显示控制台窗口
    '--windowed',  # 使用窗口模式
    '--icon=icon.ico',  # 程序图标（如果你有的话）
    '--add-data=README.md;.',  # 添加README文件
    '--add-data=requirements.txt;.',  # 添加requirements文件
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=PySide6.QtGui',
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=openai',
    '--hidden-import=flask',
    '--hidden-import=requests',
    '--clean',  # 清理临时文件
    '--onefile',  # 打包成单个文件
]

# 执行打包命令
PyInstaller.__main__.run(options) 
