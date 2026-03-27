import os
import shutil
import re
import subprocess

# ================= 配置区 =================
# 你的 Obsidian 源文件路径
OBSIDIAN_NOTE_DIR = r"F:\Obsidian\repository\Note"
OBSIDIAN_IMG_DIR = r"F:\Obsidian\repository\Note\images" # 根据你之前的配置确认

# 你的 Hugo 博客实体路径
HUGO_ROOT = r"E:\Github_blog\Sakurarry_blog"
HUGO_POST_DIR = os.path.join(HUGO_ROOT, "content", "posts")
HUGO_IMG_DIR = os.path.join(HUGO_ROOT, "static", "images")
# ==========================================

def publish_note(note_filename):
    """
    核心发布函数：将指定的 Markdown 笔记连同图片复制到 Hugo 并推送到 GitHub
    note_filename: 笔记名称，例如 "具身智能基础.md"
    """
    if not note_filename.endswith('.md'):
        note_filename += '.md'

    src_md = os.path.join(OBSIDIAN_NOTE_DIR, note_filename)
    dest_md = os.path.join(HUGO_POST_DIR, note_filename)

    if not os.path.exists(src_md):
        print(f"❌ 找不到笔记：{src_md}")
        return

    print(f"🚀 开始处理笔记：{note_filename} ...")

    # 1. 读取内容并提取图片链接
    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则匹配 Markdown 图片语法: ![alt](图片路径)
    # 因为你改成了绝对路径，图片名通常在最后一部分
    images = re.findall(r'!\[.*?\]\((.*?)\)', content)
    
    img_count = 0
    for img_path in images:
        img_name = os.path.basename(img_path)
        src_img = os.path.join(OBSIDIAN_IMG_DIR, img_name)
        dest_img = os.path.join(HUGO_IMG_DIR, img_name)
        
        # 2. 复制图片到 static/images
        if os.path.exists(src_img):
            shutil.copy2(src_img, dest_img)
            img_count += 1
            print(f"  - 成功搬运图片：{img_name}")

    # 3. 复制 Markdown 文件到 content/posts
    shutil.copy2(src_md, dest_md)
    print(f"✅ 笔记已搬运至 E 盘！(包含 {img_count} 张图片)")

    # 4. 执行 Git 提交并推送
    print("☁️ 正在将代码推送到 GitHub...")
    try:
        os.chdir(HUGO_ROOT)
        subprocess.run(["git", "add", "."], check=True)
        # 如果没有改动，commit 会报错，所以这里忽略 commit 的报错
        subprocess.run(["git", "commit", "-m", f"Auto-publish: {note_filename}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=True)
        print("🎉 自动发布成功！GitHub Actions 正在云端为你编译网页。")
    except Exception as e:
        print(f"❌ 推送失败，请检查 Git 配置或网络: {e}")

# 测试代码：手动运行这个脚本时，修改这里的笔记名来测试
if __name__ == "__main__":
    # 请把下面的名字换成你 Obsidian 里真实存在的一篇测试笔记的名字
    publish_note("test.md")
