from PIL import Image
import os
from concurrent.futures import ProcessPoolExecutor

def batch_scale_images(folder_path: str, target_w: int, target_h: int, workers: int = 8) -> None:
    """
    一行调用批量等比例缩放图片，无裁剪、覆盖原图、不遍历子目录、多进程加速
    :param folder_path: 图片文件夹路径
    :param target_w: 目标宽度
    :param target_h: 目标高度
    :param workers: 并行进程数
    """
    def _single_proc(file_path):
        try:
            with Image.open(file_path) as img:
                ow, oh = img.size
                scale = min(target_w / ow, target_h / oh)
                nw, nh = int(ow * scale), int(oh * scale)
                new_img = img.resize((nw, nh), Image.LANCZOS)
                new_img.save(file_path, quality=95)
            return f"✅ {os.path.basename(file_path)} {ow}x{oh}→{nw}x{nh}"
        except Exception as e:
            return f"❌ {os.path.basename(file_path)}：{str(e)}"

    if not os.path.isdir(folder_path):
        print("文件夹路径无效")
        return
    suffix = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff")
    img_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(suffix)]
    print(f"共检测到{len(img_list)}张图片，开始处理")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for info in pool.map(_single_proc, img_list):
            print(info)
    print("图片缩放处理完毕")


# ====================== 直接运行时启用 ======================
if __name__ == "__main__":
    # 直接运行此文件时，手动输入路径 + 自动缩放
    folder = input("请粘贴图片文件夹完整路径：").strip()
    width = int(input("请输入目标宽度："))
    height = int(input("请输入目标高度："))
    
    # 调用核心功能
    batch_scale_images(folder, width, height)