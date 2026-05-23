
## 模块说明

| 模块 | 并行方式 | 说明 |
|------|---------|------|
| `rename.py` | `ThreadPoolExecutor`（多线程） | 重命名是 I/O 密集型操作，适合多线程 |
| `resize.py` | `multiprocessing.Pool`（多进程） | 图片处理是 CPU 密集型操作，适合多进程 |

## 打包为 EXE
建议直接从Release下载zip文件，避免手动打包。

可使用 PyInstaller 将主程序打包为独立的 exe 文件：

```bash
pip install pyinstaller
pyinstaller --onefile --console main.py
```

生成的可执行文件位于 `dist/` 目录下。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。