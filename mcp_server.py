"""
MCP Server for Blog Publishing
让 AI 可以直接调用博客发布功能

使用方法：
1. 安装依赖: pip install mcp
2. 运行服务: python mcp_server.py
3. 在 Cherry Studio 中配置 MCP 服务器
"""

import os
import sys

# 确保能找到同目录下的 publish_blog 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
import publish_blog
import io

# 创建 MCP 服务器
mcp = FastMCP("BlogPublisher")


@mcp.tool()
def publish_article(note_filename: str) -> str:
    """
    博客发布工具 - 将 Obsidian 笔记发布到 Hugo 博客
    
    功能：
    - 自动提取笔记中的图片
    - 创建文章专属图片文件夹 (static/images/文章名/)
    - 转换 Obsidian 图片链接为 Hugo 格式
    - 自动推送到 GitHub
    
    参数:
        note_filename: 笔记文件名，例如 "test.md" 或 "C++内存池设计"
    
    返回:
        执行结果和详细日志
    """
    # 捕获 print 输出
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        success = publish_blog.publish_note(note_filename)
        output = new_stdout.getvalue()

        if success:
            return f"✅ 发布成功！\n\n详细日志：\n{output}"
        else:
            return f"⚠️ 执行完成但可能有问题，请检查日志：\n{output}"

    except Exception as e:
        return f"❌ 执行出错：{str(e)}"
    finally:
        sys.stdout = old_stdout


@mcp.tool()
def list_pending_notes() -> str:
    """
    列出 Obsidian 笔记目录中所有可发布的 Markdown 文件
    
    返回:
        文件列表
    """
    note_dir = publish_blog.OBSIDIAN_NOTE_DIR
    
    if not os.path.exists(note_dir):
        return f"❌ 笔记目录不存在：{note_dir}"
    
    md_files = [f for f in os.listdir(note_dir) if f.endswith('.md')]
    
    if not md_files:
        return "📭 笔记目录为空"
    
    result = f"📁 笔记目录：{note_dir}\n"
    result += f"📋 共 {len(md_files)} 个 Markdown 文件：\n\n"
    
    for i, f in enumerate(md_files, 1):
        result += f"  {i}. {f}\n"
    
    return result

if __name__ == "__main__":
    # 绝对不能在这里使用普通的 print！只能输出到标准错误流 (stderr)
    import sys
    sys.stderr.write("🚀 MCP Server 已启动，正在后台运行...\n")
    mcp.run(transport='stdio')
