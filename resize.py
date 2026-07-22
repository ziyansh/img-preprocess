import os
from PIL import Image
from multiprocessing import Pool

def _single_proc(args):
    file_path, output_dir, target_width, target_height = args
    try:
        img = Image.open(file_path)
        w, h = img.size

        # 计算等比例缩放后的大小（不超过目标尺寸）
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        filename = os.path.basename(file_path)
        save_path = os.path.join(output_dir, filename)
        img_resized.save(save_path)
        print(f"已处理：{filename} ({w}x{h} -> {new_w}x{new_h})")
    except Exception as e:
        print(f"处理失败 {file_path}：{e}")

def batch_scale_images(input_dir=".", target_width=512, target_height=512, process_num=4):
    # 在输入目录下创建输出子目录
    output_dir = os.path.join(input_dir, f"resized_{target_width}x{target_height}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_list = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]

    tasks = [(f, output_dir, target_width, target_height) for f in file_list]

    with Pool(processes=process_num) as pool:
        pool.map(_single_proc, tasks)

    print(f"\n全部处理完成！输出目录：{output_dir}")

def _single_proc_pad(args):
    file_path, output_dir, target_width, target_height, bg_color = args
    try:
        img = Image.open(file_path)
        # 统一转为RGBA，便于透明通道处理
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size

        # 先等比例放大/缩小到目标尺寸内（尽量撑满）
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        paste_x = (target_width - new_w) // 2
        paste_y = (target_height - new_h) // 2

        if bg_color == "white":
            # 白色背景：在RGBA空间合成，再转RGB输出
            canvas = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 255))
            canvas.paste(img_resized, (paste_x, paste_y), img_resized)
            final = Image.new("RGB", (target_width, target_height), (255, 255, 255))
            final.paste(canvas, (0, 0), canvas)
        else:
            # 透明背景：直接使用RGBA输出
            canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
            canvas.paste(img_resized, (paste_x, paste_y), img_resized)
            final = canvas

        filename = os.path.basename(file_path)
        # 透明背景必须用PNG保留alpha通道
        if bg_color == "transparent":
            name, _ = os.path.splitext(filename)
            save_path = os.path.join(output_dir, f"{name}.png")
        else:
            save_path = os.path.join(output_dir, filename)
        final.save(save_path)
        print(f"已处理：{filename} ({w}x{h} -> {new_w}x{new_h} -> {target_width}x{target_height})")
    except Exception as e:
        print(f"处理失败 {file_path}：{e}")


def batch_scale_and_pad_images(input_dir=".", target_width=512, target_height=512,
                                bg_color="white", process_num=4):
    bg_label = "白底" if bg_color == "white" else "透明底"
    output_dir = os.path.join(input_dir, f"padded_{target_width}x{target_height}_{bg_label}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_list = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]

    tasks = [(f, output_dir, target_width, target_height, bg_color) for f in file_list]

    with Pool(processes=process_num) as pool:
        pool.map(_single_proc_pad, tasks)

    print(f"\n全部处理完成！输出目录：{output_dir}")


def single_scale_image(file_path, target_width=512, target_height=512):
    """
    处理单张图片的等比例缩放

    参数:
        file_path: 图片文件路径
        target_width: 目标宽度
        target_height: 目标高度
    """
    file_dir = os.path.dirname(file_path)
    if not file_dir:
        file_dir = "."
    output_dir = os.path.join(file_dir, f"resized_{target_width}x{target_height}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    _single_proc((file_path, output_dir, target_width, target_height))
    print(f"\n处理完成！输出目录：{output_dir}")


def single_scale_and_pad_image(file_path, target_width=512, target_height=512, bg_color="white"):
    """
    处理单张图片的等比例缩放+补边

    参数:
        file_path: 图片文件路径
        target_width: 目标宽度
        target_height: 目标高度
        bg_color: 背景颜色 ("white" 或 "transparent")
    """
    file_dir = os.path.dirname(file_path)
    if not file_dir:
        file_dir = "."
    bg_label = "白底" if bg_color == "white" else "透明底"
    output_dir = os.path.join(file_dir, f"padded_{target_width}x{target_height}_{bg_label}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    _single_proc_pad((file_path, output_dir, target_width, target_height, bg_color))
    print(f"\n处理完成！输出目录：{output_dir}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        batch_scale_images(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    else:
        batch_scale_images()
    input("按回车退出")