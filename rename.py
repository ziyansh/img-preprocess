import os
from concurrent.futures import ThreadPoolExecutor

# ====================== 批量重命名（一行调用版） ======================
def batch_rename(folder_path: str, start_num: int = 1, workers: int = 8) -> None:
    def _process(file_data):
        filename, num = file_data
        try:
            name, ext = os.path.splitext(filename)
            new_name = f"{num:03d}{ext}"
            old = os.path.join(folder_path, filename)
            new = os.path.join(folder_path, new_name)
            if os.path.exists(new):
                return f"⏭️ 跳过 {filename} → {new_name}（已存在）"
            os.rename(old, new)
            return f"✅ {filename} → {new_name}"
        except Exception as e:
            return f"❌ {filename} 失败：{str(e)}"

    if not os.path.isdir(folder_path):
        print("文件夹路径无效")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    tasks = list(zip(files, range(start_num, start_num + len(files))))

    print(f"共找到 {len(files)} 个文件，开始重命名")
    with ThreadPoolExecutor(workers) as executor:
        for msg in executor.map(_process, tasks):
            print(msg)
    print("重命名处理完毕")

# ====================== 独立运行 ======================
if __name__ == "__main__":
    folder = input("请输入文件夹路径：").strip()
    start = int(input("起始编号（直接回车=1）：") or 1)
    batch_rename(folder, start)