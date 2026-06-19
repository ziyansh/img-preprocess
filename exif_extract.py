"""
Stable Diffusion 图片生成参数提取模块
- PNG：读取 tEXt 块中的 parameters 键
- JPEG：读取 EXIF UserComment 字段 (tag 0x9286)
"""

import os
import sys
import shutil
from PIL import Image
from PIL.ExifTags import TAGS as EXIF_TAGS

# EXIF UserComment 对应的 tag ID
TAG_USER_COMMENT = 0x9286


def extract_sd_parameters(image_path):
    """
    提取 Stable Diffusion 图片的生成参数

    PNG → tEXt 块 key="parameters"
    JPEG → EXIF UserComment 字段

    参数:
        image_path: 图片文件路径

    返回:
        (参数文本, 格式标识) 元组。
        参数文本：提取到的参数字符串，未找到则返回 None
        格式标识："png" 或 "jpeg"
    """
    if not os.path.isfile(image_path):
        return None, None

    ext = os.path.splitext(image_path)[1].lower()

    try:
        img = Image.open(image_path)

        if ext == ".png":
            # PNG：读取 tEXt 文本块中的 parameters
            text_chunks = getattr(img, "text", {}) or getattr(img, "info", {})
            params = text_chunks.get("parameters")
            if params:
                return params, "png"
            return None, "png"

        elif ext in (".jpg", ".jpeg"):
            # JPEG：读取 EXIF UserComment
            exif = img.getexif()
            raw = exif.get(TAG_USER_COMMENT)
            if raw is None:
                return None, "jpeg"
            # UserComment 通常是 bytes，尝试解码
            if isinstance(raw, bytes):
                try:
                    return raw.decode("utf-8", errors="replace"), "jpeg"
                except Exception:
                    return repr(raw), "jpeg"
            return str(raw), "jpeg"

        else:
            return None, ext

    except Exception:
        return None, None


def format_sd_parameters(params, fmt):
    """将 SD 参数格式化为友好的显示文本"""
    if params is None:
        return "未找到 Stable Diffusion 生成参数。"

    if fmt == "png":
        source = "PNG tEXt (parameters)"
    elif fmt == "jpeg":
        source = "JPEG EXIF (UserComment)"
    else:
        source = fmt

    lines = []
    lines.append("=" * 50)
    lines.append("Stable Diffusion 生成参数")
    lines.append(f"来源：{source}")
    lines.append("=" * 50)
    lines.append(params)
    lines.append("=" * 50)
    return "\n".join(lines)


def strip_exif(image_path, output_path):
    """
    复制图片并清除所有 EXIF / 文本元数据

    参数:
        image_path: 源图片路径
        output_path: 输出的新文件路径

    返回:
        True 成功 / False 失败
    """
    try:
        # 先复制文件
        shutil.copy2(image_path, output_path)
        # 打开副本重新保存以剥离元数据
        img = Image.open(output_path)
        ext = os.path.splitext(output_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            img.save(output_path, exif=b"")
        else:
            img.save(output_path)
        return True
    except Exception:
        return False


def main_cli():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python exif_extract.py <图片文件路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    params, fmt = extract_sd_parameters(image_path)
    print(format_sd_parameters(params, fmt))


if __name__ == "__main__":
    main_cli()