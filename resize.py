import os
from PIL import Image
from multiprocessing import Pool

def _single_proc(args):
    file_path, output_dir, target_width, target_height = args
    try:
        img = Image.open(file_path)
        w, h = img.size

        # 计算等比例缩放后的大小（不超过目标尺寸）
        scale = min(target_width / w, target_height / h, 1.0)
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        batch_scale_images(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    else:
        batch_scale_images()
    input("按回车退出")