import multiprocessing
multiprocessing.freeze_support()  # 多进程打包必须

import os
import sys
import subprocess

# 关键：PyInstaller 打包后，所有模块都在 exe 内部，不需要再检查外部文件
# 所以我们直接导入，去掉“文件存在性检查”的逻辑
from resize import batch_scale_images, batch_scale_and_pad_images, single_scale_image, single_scale_and_pad_image
from exif_extract import extract_sd_parameters, format_sd_parameters, strip_exif

def clear_screen():
    """清空终端屏幕，适配不同系统"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """显示功能菜单"""
    clear_screen()
    print("=" * 40)
    print("         批量文件处理工具主程序")
    print("                     版本v1.2.3")
    print("=" * 40)
    print("【1】批量重命名文件（数字序号）")
    print("【2】批量缩放图片（等比例）")
    print("【3】批量缩放+补边（等比例放大 + 白边/透明背景填充）")
    print("【4】提取图片生成参数（SD 参数）")
    print("【0】退出程序")
    print("=" * 40)

def _is_file_path(text):
    """
    判断用户输入是否可能是一个文件路径
    检查路径分隔符、盘符、或文件实际存在
    """
    # 去掉首尾引号
    text = text.strip("\"'")
    # 包含路径分隔符
    if "\\" in text or "/" in text:
        return True
    # 以盘符开头（如 C:）
    if len(text) >= 2 and text[1] == ":":
        return True
    # 文件实际存在
    if os.path.isfile(text):
        return True
    return False

def main():
    """主程序逻辑"""
    # 如果命令行传入了图片文件路径，直接提取 SD 生成参数
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
        if os.path.isfile(image_path):
            params, fmt = extract_sd_parameters(image_path)
            print(format_sd_parameters(params, fmt))
            input("\n按回车键退出...")
            sys.exit(0)

    while True:
        show_menu()
        choice = input("请选择功能（输入数字0-4）：").strip()
        
        if choice == "1":
            # 批量重命名功能
            print("\n----- 批量重命名功能 -----")
            folder = input("请输入文件夹路径：").strip()
            if not os.path.isdir(folder):
                print("❌ 文件夹路径无效，请重新选择！")
                input("按回车键返回菜单...")
                continue
            
            try:
                start = input("起始编号（直接回车=1）：").strip()
                start_num = int(start) if start else 1
                workers = input("并行线程数（直接回车=8）：").strip()
                workers_num = int(workers) if workers else 8
                
                batch_rename(folder, start_num, workers_num)
            except ValueError:
                print("❌ 输入的数字格式无效！")
            input("\n重命名完成，按回车键返回菜单...")
        
        elif choice == "2":
            # 批量图片缩放功能
            print("\n----- 批量图片缩放功能 -----")
            path = input("请粘贴图片文件夹或图片文件完整路径：").strip().strip("\"'")
            if not os.path.exists(path):
                print("❌ 路径无效，请重新选择！")
                input("按回车键返回菜单...")
                continue
            
            try:
                width = int(input("请输入目标宽度：").strip())
                height = int(input("请输入目标高度：").strip())
                
                if os.path.isdir(path):
                    workers = input("并行进程数（直接回车=8）：").strip()
                    workers_num = int(workers) if workers else 8
                    batch_scale_images(path, width, height, workers_num)
                else:
                    single_scale_image(path, width, height)
            except ValueError:
                print("❌ 宽度/高度必须是数字！")
            input("\n缩放完成，按回车键返回菜单...")
        
        elif choice == "3":
            # 批量缩放+补边功能
            print("\n----- 批量缩放+补边功能 -----")
            path = input("请粘贴图片文件夹或图片文件完整路径：").strip().strip("\"'")
            if not os.path.exists(path):
                print("❌ 路径无效，请重新选择！")
                input("按回车键返回菜单...")
                continue
            
            try:
                width = int(input("请输入目标宽度：").strip())
                height = int(input("请输入目标高度：").strip())
                bg = input("背景颜色（直接回车=白色，输入t=透明）：").strip().lower()
                bg_color = "transparent" if bg == "t" else "white"
                
                if os.path.isdir(path):
                    workers = input("并行进程数（直接回车=8）：").strip()
                    workers_num = int(workers) if workers else 8
                    batch_scale_and_pad_images(path, width, height, bg_color, workers_num)
                else:
                    single_scale_and_pad_image(path, width, height, bg_color)
            except ValueError:
                print("❌ 宽度/高度必须是数字！")
            input("\n缩放补边完成，按回车键返回菜单...")

        elif choice == "4":
            # 提取 SD 生成参数
            print("\n----- 提取图片生成参数（SD 参数） -----")
            image_path = input("请粘贴图片文件完整路径：").strip()
            print()
            params, fmt = extract_sd_parameters(image_path)
            print(format_sd_parameters(params, fmt))
            input("\n按回车键返回菜单...")

        elif choice == "0":
            # 退出程序
            print("\n👋 感谢使用，程序已退出！")
            sys.exit(0)
        
        else:
            # 检查是否为图片文件路径
            raw_input = choice
            path = raw_input.strip("\"'")
            if _is_file_path(raw_input) and os.path.isfile(path):
                params, fmt = extract_sd_parameters(path)
                sd_text = format_sd_parameters(params, fmt)
                print(f"\n{sd_text}")
                # 子菜单：输出后的操作
                while True:
                    print("\n" + "-" * 30)
                    print("【1】返回主菜单")
                    print("【2】复制到剪贴板")
                    print("【3】保存为同名的 .txt 文件")
                    print("【4】复制文件并清除 EXIF")
                    print("-" * 30)
                    sub_choice = input("请选择操作：").strip()
                    if sub_choice == "1":
                        break
                    elif sub_choice == "2":
                        try:
                            subprocess.run(
                                ["powershell", "-command", "Set-Clipboard", "-Value", sd_text],
                                check=True
                            )
                            print("✅ 已复制到剪贴板！")
                        except Exception as e:
                            print(f"❌ 复制失败：{e}")
                    elif sub_choice == "3":
                        try:
                            txt_path = os.path.splitext(path)[0] + ".txt"
                            with open(txt_path, "w", encoding="utf-8") as f:
                                f.write(sd_text)
                            print(f"✅ 已保存到：{txt_path}")
                        except Exception as e:
                            print(f"❌ 保存失败：{e}")
                    elif sub_choice == "4":
                        # 复制文件并清除 EXIF
                        base, ext = os.path.splitext(path)
                        out_path = f"{base}_EXIFclr{ext}"
                        if strip_exif(path, out_path):
                            print(f"✅ 已生成（EXIF 已清除）：{out_path}")
                        else:
                            print("❌ 清除 EXIF 失败！")
                    else:
                        # 检查子菜单输入是否为图片文件路径
                        sub_path = sub_choice.strip("\"'")
                        if _is_file_path(sub_choice) and os.path.isfile(sub_path):
                            params, fmt = extract_sd_parameters(sub_path)
                            sd_text = format_sd_parameters(params, fmt)
                            print(f"\n{sd_text}")
                            path = sub_path  # 更新 path 供后续保存使用
                        else:
                            print(f"❌ 无效选择：{sub_choice}")
            else:
                print(f"\n❌ 无效选择：{raw_input}，请输入0-4之间的数字！")
                input("按回车键返回菜单...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被用户中断，已退出！")
        input("按回车键关闭窗口...")
    except Exception as e:
        print(f"\n\n❌ 程序出错：{str(e)}")
        input("按回车键关闭窗口...")