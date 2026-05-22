import multiprocessing
multiprocessing.freeze_support()  # 多进程打包必须

import os
import sys

# 关键：PyInstaller 打包后，所有模块都在 exe 内部，不需要再检查外部文件
# 所以我们直接导入，去掉“文件存在性检查”的逻辑
from rename import batch_rename
from resize import batch_scale_images

def clear_screen():
    """清空终端屏幕，适配不同系统"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """显示功能菜单"""
    clear_screen()
    print("=" * 40)
    print("         批量文件处理工具主程序")
    print("=" * 40)
    print("【1】批量重命名文件（数字序号）")
    print("【2】批量缩放图片（等比例）")
    print("【0】退出程序")
    print("=" * 40)

def main():
    """主程序逻辑"""
    while True:
        show_menu()
        choice = input("请选择功能（输入数字0-2）：").strip()
        
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
            folder = input("请粘贴图片文件夹完整路径：").strip()
            if not os.path.isdir(folder):
                print("❌ 文件夹路径无效，请重新选择！")
                input("按回车键返回菜单...")
                continue
            
            try:
                width = int(input("请输入目标宽度：").strip())
                height = int(input("请输入目标高度：").strip())
                workers = input("并行进程数（直接回车=8）：").strip()
                workers_num = int(workers) if workers else 8
                
                batch_scale_images(folder, width, height, workers_num)
            except ValueError:
                print("❌ 宽度/高度/进程数必须是数字！")
            input("\n缩放完成，按回车键返回菜单...")
        
        elif choice == "0":
            # 退出程序
            print("\n👋 感谢使用，程序已退出！")
            sys.exit(0)
        
        else:
            # 无效选择
            print(f"\n❌ 无效选择：{choice}，请输入0-2之间的数字！")
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