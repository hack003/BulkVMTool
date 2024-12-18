import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import subprocess
import os
import sys
import csv
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk VM Deployment Tool")
        self.is_checking_or_installing = False  # 新增标志变量
        # Set window size to 680x720
        self.root.geometry("680x600")
        # Initialize connection status and connect/disconnect button
        self.connection_status = False
        self.connect_disconnect_button = None
        
        # Initialize settings variables with default values
        self.vc_host_var = tk.StringVar(value="192.168.1.100")
        self.user_var = tk.StringVar(value="administrator@vsphere.local")
        self.pw_var = tk.StringVar(value="")
        self.gateway_var = tk.StringVar(value="192.168.1.1")
        self.vm_file_path = ""  # Variable to store the path of the selected CSV file
        self.vm_file_name = ""  # Variable to store the name of the selected CSV file
        
        # Initialize PowerShell process variable
        self.ps_process = None
        
        # Setup GUI components
        self.setup_gui()
    
    def setup_gui(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Top Section for Settings and Buttons
        left_top_frame = ttk.Frame(frame, height=260)
        left_top_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Settings section
        settings_frame = ttk.LabelFrame(left_top_frame, text="设置")
        settings_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        ttk.Label(settings_frame, text="VC 地址:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.vc_host_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="用户名:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.user_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="密码:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(settings_frame, show="*", textvariable=self.pw_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="目标虚拟机网关:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.gateway_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # First row of buttons: Save Settings, Connect, Disconnect
        first_buttons_frame = ttk.Frame(settings_frame)
        first_buttons_frame.grid(row=4, columnspan=2, padx=5, pady=10, sticky=tk.NSEW)
        
        save_button = ttk.Button(first_buttons_frame, text="保存设置", command=self.save_settings)
        save_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Connect/Disconnect button
        self.connect_disconnect_button = ttk.Button(first_buttons_frame, text="开始连接", command=self.toggle_connection)
        self.connect_disconnect_button.grid(row=0, column=1, padx=5, pady=5)

        disconnect_button = ttk.Button(first_buttons_frame, text="虚拟机模板", command=lambda: self.execute_ps_command("Get-template -Name * | Format-Table Name, Description"))
        disconnect_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Second row of buttons: View Storage, View Network, View Virtual Machines
        second_buttons_frame = ttk.Frame(settings_frame)
        second_buttons_frame.grid(row=5, columnspan=2, padx=5, pady=10, sticky=tk.NSEW)
        
        view_storage_button = ttk.Button(second_buttons_frame, text="查看存储", command=lambda: self.execute_ps_command("Get-Datastore | Format-Table Name,CapacityGB,FreeSpaceGB"))
        view_storage_button.grid(row=0, column=0, padx=5, pady=5)
        
        view_network_button = ttk.Button(second_buttons_frame, text="查看网络", command=lambda: self.execute_ps_command("Get-VirtualNetwork "))
        view_network_button.grid(row=0, column=1, padx=5, pady=5)
        
        view_vm_button = ttk.Button(second_buttons_frame, text="查看虚拟机", command=lambda: self.execute_ps_command("Get-VM | Format-Table Name, PowerState, numCPU, MemoryGB -AutoSize "))
        view_vm_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Right Top Section for Additional Actions
        right_top_frame = ttk.Frame(frame, height=260)
        right_top_frame.grid(row=0, column=1, sticky=tk.NSEW)
        
        # Additional Buttons Frame in two columns
        additional_buttons_frame = ttk.LabelFrame(right_top_frame, text="操作")
        additional_buttons_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Column 1
        col1_frame = ttk.Frame(additional_buttons_frame)
        col1_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NS)
        
        generate_csv_button = ttk.Button(col1_frame, text="生成模板", command=self.generate_csv_template)
        generate_csv_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W+tk.E)

        import_csv_button = ttk.Button(col1_frame, text="导入模板", command=self.import_csv)
        import_csv_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W+tk.E)

        show_csv_button = ttk.Button(col1_frame, text="显示模板", command=self.show_csv_in_log)
        show_csv_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        check_powercli_button = ttk.Button(col1_frame, text="检测环境", command=self.check_powercli)
        check_powercli_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
                               
        # Column 2
        col2_frame = ttk.Frame(additional_buttons_frame)
        col2_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NS)

        execute_button = ttk.Button(col2_frame, text="执行脚本", command=self.execute_script_in_new_window)
        execute_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        show_settings_button = ttk.Button(col2_frame, text="显示设置", command=self.show_settings_in_log)
        show_settings_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W+tk.E)        
        
        about_button = ttk.Button(col2_frame, text="关于", command=self.show_about)
        about_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        exit_button = ttk.Button(col2_frame, text="退出", command=self.root.quit)
        exit_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Output Text Widget in the middle area
        self.output_text = tk.Text(frame, height=15, width=80)
        self.output_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Command Input Entry and Execute Button in the bottom area
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        
        self.command_entry = ttk.Entry(input_frame, width=70)
        self.command_entry.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        
        execute_cmd_button = ttk.Button(input_frame, text="执行命令", command=self.execute_custom_command)
        execute_cmd_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Allow frames to be resizable
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
    def get_resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def save_settings(self):
        vc_host = self.vc_host_var.get()
        user = self.user_var.get()
        pw = self.pw_var.get()
        gateway = self.gateway_var.get()
        
        if not all([vc_host, user, pw, gateway]):
            messagebox.showwarning("警告", "请填写所有字段")
            return
        
        try:
            ps1_file_path = self.get_resource_path("DeployVM.ps1")
            with open(ps1_file_path, "r", encoding="utf-8") as file:
                script_content = file.read()
            
            script_content = re.sub(r'\$vc\s*=\s*".*?"', f'$vc = "{vc_host}"', script_content)
            script_content = re.sub(r'\$user\s*=\s*".*?"', f'$user = "{user}"', script_content)
            script_content = re.sub(r'\$password\s*=\s*".*?"', f'$password = "{pw}"', script_content)
            script_content = re.sub(r'\$Gateway\s*=\s*".*?"', f'$Gateway = "{gateway}"', script_content)
            
            # Add $vm_file variable
            vm_file_full_path = os.path.join(self.vm_file_path, self.vm_file_name) if self.vm_file_path and self.vm_file_name else os.path.dirname(os.path.abspath(sys.executable))
            vm_file_full_path = vm_file_full_path.replace("\\", "\\\\")
            script_content = re.sub(r'^\s*\$vm_file\s*=\s*".*?"', f'$vm_file = "{vm_file_full_path}"', script_content, flags=re.MULTILINE)
            if '$vm_file =' not in script_content:
                script_content += f"\n$vm_file = \"{vm_file_full_path}\""
            
            # Replace 'D:\\DeployVM.csv' with '$vm_file'
            script_content = re.sub(r'\$vm_file\s*=\s*".*?"', f'$vm_file = "{vm_file_full_path}"', script_content)
            
            # Write the updated content back to DeployVM.ps1
            with open(ps1_file_path, "w", encoding="utf-8") as file:
                file.write(script_content)
            
            self.log_message("成功", "设置已保存")
        except FileNotFoundError:
            self.log_message("错误", "DeployVM.ps1 文件未找到")
        except Exception as e:
            self.log_message("错误", str(e))
    
    def generate_csv_template(self):
        template_content = (
            "Name,IP,CPU,Memory,Template,Vlan,Description,Host,DiskCapacityGB,Datastore,Rule\n"
            "ceshi20241116,192.168.18.249,8,32,RHEL7.9-VH17Ver2,VM Network,10678,192.168.18.111,400,fc_disks_data3,Linux\n"
        )
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        template_path = os.path.join(exe_dir, "DeployVM_Template.csv")
        
        try:
            with open(template_path, "w", encoding="utf-8") as file:
                file.write(template_content)
            self.log_message("成功", f"CSV 模板已生成并保存在: {template_path}")
        except Exception as e:
            self.log_message("错误", f"无法生成 CSV 模板: {str(e)}")
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="选择 CSV 模板文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.vm_file_path = os.path.dirname(file_path)
            self.vm_file_name = os.path.basename(file_path)
            self.log_message("成功", f"CSV 模板路径已设置为: {os.path.join(self.vm_file_path, self.vm_file_name)}")
            messagebox.showinfo("提示", "模板已导入，点击保存设置后生效！")
    def view_script(self):
        file_path = self.get_resource_path("DeployVM.ps1")
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.log_message("错误", "脚本文件不存在")

    def execute_script_in_new_window(self):
        try:
            ps1_file_path = self.get_resource_path("DeployVM.ps1")
            subprocess.Popen(
                ["cmd.exe", "/K", "powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", f"& '{ps1_file_path}'"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception as e:
            self.log_message("错误", f"无法执行 PowerShell 脚本: {str(e)}")
    def check_powercli(self):
        if self.is_checking_or_installing:
            self.log_message("警告", "检测或安装正在进行中，请稍后重试")
            return
        
        self.is_checking_or_installing = True
        self.log_message("检测开始", "正在检测 PowerCLI...")
        
        try:
            # 启动PowerShell进程并捕获输出以检查是否已安装 PowerCLI
            ps_check_process = subprocess.Popen(
                ["powershell.exe", "-Command", "(Get-Module -ListAvailable VMware.PowerCLI)"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏PowerShell窗口
            )
            
            # 读取检查结果
            check_output = ps_check_process.stdout.read()
            if "VMware.PowerCLI" in check_output:
                self.log_message("检测结果", "PowerCLI 已安装")
            else:
                self.log_message("检测结果", "PowerCLI 未安装")
                self.log_message("安装开始", "正在安装 PowerCLI...")
                
                # 启动PowerShell进程并捕获输出以安装 PowerCLI
                ps_install_process = subprocess.Popen(
                    ["powershell.exe", "-Command", "Install-Module -Name VMware.PowerCLI -Scope CurrentUser -Force"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏PowerShell窗口
                )
                
                # 启动一个线程来读取PowerShell进程的输出
                threading.Thread(target=self.read_ps_output, args=(ps_install_process,), daemon=True).start()
        except Exception as e:
            self.log_message("错误", f"检测或安装过程中出错: {str(e)}")
        finally:
            self.is_checking_or_installing = False

    def read_ps_output(self, process):
        for line in process.stdout:
            self.log_message("输出", line.strip())
        process.wait()
        if process.returncode == 0:
            self.log_message("成功", "操作完成")
        else:
            self.log_message("失败", "操作失败")
    def show_csv_in_log(self):
        file_path = os.path.join(self.vm_file_path, self.vm_file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_content = file.read()
            self.log_message("CSV 内容", csv_content)
        except FileNotFoundError:
            self.log_message("错误", "CSV 文件未找到")
        except Exception as e:
            self.log_message("错误", str(e))
    def toggle_connection(self):
        if not self.connection_status:
            # 检查所有字段是否已填写
            vc_host = self.vc_host_var.get()
            user = self.user_var.get()
            pw = self.pw_var.get()
            gateway = self.gateway_var.get()
            
            if not all([vc_host, user, pw, gateway]):
                messagebox.showwarning("警告", "请填写所有字段")
                return
            
            self.connect_to_vc()
            self.connect_disconnect_button.config(text="断开连接")
            self.log_message("稍等", "正在连接到VC")
        else:
            self.disconnect_from_vc()
            self.connect_disconnect_button.config(text="连接")
            self.log_message("断开连接", "已断开连接")
    def connect_to_vc(self):
        vc_host = self.vc_host_var.get()
        user = self.user_var.get()
        pw = self.pw_var.get()
        gateway = self.gateway_var.get()
        
        if not all([vc_host, user, pw]):
            messagebox.showwarning("警告", "请填写所有字段")
            return
        ps_command = f'Set-PowerCLIConfiguration -ParticipateInCEIP $false -ParticipateInStagingCEIP $false -InvalidCertificateAction Ignore -Confirm:$false'
        ps_command = f'Connect-VIServer -Protocol https -User \'{user}\' -Password \'{pw}\' -Server {vc_host}'
        
        try:
            if self.ps_process is not None:
                self.ps_process.terminate()
                self.ps_process.wait()
                self.ps_process = None
            
            self.ps_process = subprocess.Popen(
                ["powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide the PowerShell window
            )
            
            # Start a thread to read the output from the PowerShell process
            import threading
            threading.Thread(target=self.read_ps_output, args=(self.ps_process,), daemon=True).start()
            
            self.log_message("稍等", "正在连接 vCenter Server")
        except Exception as e:
            self.log_message("错误", f"无法连接到 VC: {str(e)}")
        self.connection_status = True
    def disconnect_from_vc(self):
        try:
            if self.ps_process is not None:
                self.ps_process.communicate(input='Disconnect-VIServer -Confirm:$false\r\nexit\r\n')
                self.ps_process = None
                self.log_message("成功", "已断开连接")
            else:
                self.log_message("警告", "尚未连接到 vCenter Server")
        except Exception as e:
            self.log_message("错误", f"无法断开连接: {str(e)}")
        self.connection_status = False
    def execute_ps_command(self, command):
        try:
            if self.ps_process is None:
                self.log_message("警告", "请先连接到 vCenter Server")
                return
            
            self.ps_process.stdin.write(command + '\r\n')
            self.ps_process.stdin.flush()
        except Exception as e:
            self.log_message("错误", f"无法执行命令: {str(e)}")
    
    def execute_custom_command(self):
        custom_command = self.command_entry.get().strip()
        if custom_command:
            self.execute_ps_command(custom_command)
        else:
            self.log_message("警告", "请输入有效的命令")
    
    def read_ps_output(self, process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)
    
    def log_message(self, level, message):
        log_entry = f"[{level}] {message}\n"
        self.output_text.insert(tk.END, log_entry)
        self.output_text.see(tk.END)
    
    def show_about(self):
        about_info = (
            "版本: 1.2\n"
            "说明: 批量部署虚拟机工具\n"
            "作者: xugh\n"
            "联系邮箱: hack003@163.com"
        )
        self.log_message("关于", about_info)
    
    def show_settings_in_log(self):
        settings_info = (
            f"VC 地址: {self.vc_host_var.get()}\n"
            f"用户名: {self.user_var.get()}\n"
            f"密码: {'*' * len(self.pw_var.get())}\n"
            f"目标虚拟机网关: {self.gateway_var.get()}\n"
            f"CSV 文件路径: {os.path.join(self.vm_file_path, self.vm_file_name)}"
        )
        self.log_message("当前设置", settings_info)

def main():
    app = App(root=tk.Tk())
    app.root.mainloop()

if __name__ == "__main__":
    main()



