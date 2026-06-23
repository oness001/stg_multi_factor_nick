import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import tempfile


class Py2PydGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python转Pyd工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # 核心变量
        self.py_file_path = tk.StringVar()  # 选中的py文件路径
        self.module_name = tk.StringVar()  # 生成的模块名
        self.use_numpy = tk.BooleanVar(value=True)  # 是否启用numpy支持
        self.py_file_path.trace("w", self._auto_fill_module_name)  # 选文件后自动填充模块名

        # 初始化样式（提前配置ttk样式）
        self._init_style()
        # 布局搭建
        self._create_widgets()

    def _init_style(self):
        """初始化ttk样式"""
        style = ttk.Style()
        # 主按钮样式
        style.configure("Accent.TButton", font=("微软雅黑", 10, "bold"), padding=5)
        # 灰色提示文字样式
        style.configure("Gray.TLabel", font=("微软雅黑", 9), foreground="gray")

    def _create_widgets(self):
        """创建GUI组件"""
        # ========== 第一行：选择PY文件 ==========
        frame1 = ttk.Frame(self.root, padding="10 10 10 5")
        frame1.pack(fill=tk.X)

        ttk.Label(frame1, text="选择Python文件：").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(frame1, textvariable=self.py_file_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(frame1, text="浏览", command=self._select_py_file).grid(row=0, column=2, padx=5)

        # ========== 第二行：模块名配置 ==========
        frame2 = ttk.Frame(self.root, padding="10 5 10 5")
        frame2.pack(fill=tk.X)

        ttk.Label(frame2, text="生成模块名：").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(frame2, textvariable=self.module_name, width=60).grid(row=0, column=1, padx=5)
        # 修正：使用自定义灰色样式，移除grid里的fg参数
        ttk.Label(frame2, text="(默认与文件名一致，无需后缀)", style="Gray.TLabel").grid(row=0, column=2, padx=5)

        # ========== 第三行：编译参数 ==========
        frame3 = ttk.Frame(self.root, padding="10 5 10 10")
        frame3.pack(fill=tk.X)

        ttk.Checkbutton(frame3, text="启用NumPy支持（代码用到numpy时勾选）", variable=self.use_numpy).grid(row=0,
                                                                                                         column=0,
                                                                                                         sticky=tk.W,
                                                                                                         padx=5)

        # ========== 第四行：编译按钮 ==========
        frame4 = ttk.Frame(self.root, padding="10 5 10 10")
        frame4.pack(fill=tk.X)

        ttk.Button(frame4, text="开始编译生成.pyd", command=self._compile_to_pyd, style="Accent.TButton").pack()

        # ========== 第五行：日志输出 ==========
        frame5 = ttk.Frame(self.root, padding="10 5 10 10")
        frame5.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame5, text="编译日志：").pack(anchor=tk.W)
        self.log_text = tk.Text(frame5, width=95, height=25, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame5, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _select_py_file(self):
        """选择.py文件"""
        file_path = filedialog.askopenfilename(
            title="选择Python文件",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if file_path:
            self.py_file_path.set(file_path)

    def _auto_fill_module_name(self, *args):
        """选文件后自动填充模块名（去掉路径和后缀）"""
        file_path = self.py_file_path.get()
        if file_path and not self.module_name.get():
            file_name = os.path.basename(file_path)
            module_name = os.path.splitext(file_name)[0]
            self.module_name.set(module_name)

    def _log(self, msg, is_error=False):
        """日志输出"""
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.root.update()
        if is_error:
            self.log_text.tag_add("error", "end-2l", "end-1l")
            self.log_text.tag_config("error", foreground="red")

    def _compile_to_pyd(self):
        """核心编译逻辑"""
        # 1. 参数校验
        py_file = self.py_file_path.get().strip()
        module_name = self.module_name.get().strip()
        if not py_file:
            messagebox.warning("警告", "请先选择要编译的.py文件！")
            return
        if not os.path.exists(py_file):
            messagebox.error("错误", f"文件不存在：{py_file}")
            return
        if not module_name:
            messagebox.warning("警告", "请输入生成的模块名！")
            return

        # 2. 清空日志
        self.log_text.delete(1.0, tk.END)
        self._log("===== 开始编译 =====")
        self._log(f"源文件：{py_file}")
        self._log(f"模块名：{module_name}")
        self._log(f"NumPy支持：{'开启' if self.use_numpy.get() else '关闭'}")

        # 3. 生成临时setup.py文件
        try:
            # 复制原py文件为pyx（Cython源文件）
            pyx_file = os.path.join(os.path.dirname(py_file), f"{module_name}.pyx")
            with open(py_file, "r", encoding="utf-8") as f_src, open(pyx_file, "w", encoding="utf-8") as f_dst:
                f_dst.write(f_src.read())
            self._log(f"已生成Cython源文件：{pyx_file}")

            # 修复：提前定义numpy相关代码，避免f-string里的反斜杠
            numpy_code = ""
            if self.use_numpy.get():
                numpy_code = "import numpy as np\nextensions[0].include_dirs = [np.get_include()]"

            # 修复：将pyx路径转为正斜杠，避免反斜杠问题
            pyx_file_normalized = pyx_file.replace("\\", "/")

            # 生成setup.py内容（拆分f-string，避免反斜杠）
            setup_content = f"""
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import sys

# 编译配置
extensions = [
    Extension(
        name="{module_name}",
        sources=["{pyx_file_normalized}"],
        extra_compile_args=["/O2"],  # 编译优化
        language="c"
    )
]

# 加入NumPy支持
{numpy_code}

# 执行编译
setup(
    name="{module_name}",
    ext_modules=cythonize(extensions, language_level=sys.version_info[0])
)
"""
            # 写入临时setup.py
            setup_file = os.path.join(os.path.dirname(py_file), "setup_temp.py")
            with open(setup_file, "w", encoding="utf-8") as f:
                f.write(setup_content)
            self._log(f"已生成编译配置文件：{setup_file}")

            # 4. 执行编译命令
            self._log("===== 执行编译命令 =====")
            compile_cmd = [sys.executable, setup_file, "build_ext", "--inplace"]
            process = subprocess.Popen(
                compile_cmd,
                cwd=os.path.dirname(py_file),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="ignore"
            )

            # 实时输出日志
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    self._log(output.strip())

            # 5. 检查编译结果
            return_code = process.poll()
            if return_code == 0:
                # 查找生成的.pyd文件
                pyd_files = [f for f in os.listdir(os.path.dirname(py_file))
                             if f.startswith(module_name) and f.endswith(".pyd")]
                if pyd_files:
                    pyd_path = os.path.join(os.path.dirname(py_file), pyd_files[0])
                    self._log(f"\n===== 编译成功 =====")
                    self._log(f"生成的.pyd文件：{pyd_path}")
                    messagebox.showinfo("成功", f"Pyd文件生成完成！\n路径：{pyd_path}")
                else:
                    self._log("\n===== 编译异常 =====", is_error=True)
                    self._log("未找到生成的.pyd文件，请检查日志！", is_error=True)
            else:
                self._log("\n===== 编译失败 =====", is_error=True)
                self._log(f"返回码：{return_code}", is_error=True)
                messagebox.showerror("失败", "编译出错，请查看日志详情！")

        except Exception as e:
            self._log(f"\n===== 运行时错误 =====", is_error=True)
            self._log(f"错误信息：{str(e)}", is_error=True)
            messagebox.showerror("错误", f"运行出错：{str(e)}")

        finally:
            # 清理临时文件（可选）
            try:
                if os.path.exists(pyx_file):
                    os.remove(pyx_file)
                if os.path.exists(setup_file):
                    os.remove(setup_file)
                # 清理Cython生成的.c文件
                c_file = os.path.join(os.path.dirname(py_file), f"{module_name}.c")
                if os.path.exists(c_file):
                    os.remove(c_file)
                self._log("已清理临时文件")
            except:
                pass


if __name__ == "__main__":
    # 前置检查：是否安装Cython
    try:
        import Cython
    except ImportError:
        messagebox.warning("警告", "未检测到Cython！请先执行：pip install cython")
        sys.exit(1)

    # 启动GUI
    root = tk.Tk()
    app = Py2PydGUI(root)
    root.mainloop()

