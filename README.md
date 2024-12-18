### BulkVMTool 说明文档

#### 概述
`BulkVMTool` 是一个用于简化和加速虚拟机批量部署过程的工具。它允许用户通过创建配置模板来定义虚拟机的参数，并可以一键执行部署，极大地提高了工作效率。该工具基于 Windows 平台运行，并依赖于 VMware 的 PowerCLI 来与 vSphere 环境进行交互。

#### 运行条件
- **操作系统**：Windows
- **依赖软件**：
  - **PowerCLI**：必须安装。`BulkVMTool` 可以自动检测是否安装了 PowerCLI；如果没有安装，程序会尝试自动完成安装。不过，推荐用户手动安装最新版本的 PowerCLI 以确保最佳兼容性和功能。
  
#### 脱机安装 （速度非常快）

- 如果需要[脱机](https://docs.vmware.com/en/VMware-PowerCLI/latest/powercli/GUID-3034A439-E9D7-4743-ABC0-EE38610E15F8.html "官方文档")安装 PowerCLI，请从 [PowerCLI](https://code.vmware.com/web/tool/vmware-powercli) 主页下载 [PowerCLI ZIP](https://developer.broadcom.com/tools/vmware-powercli/latest/ "新的下载网站") 文件，然后将 ZIP 文件传输到本地计算机。
- 使用以下命令检查 PowerShell 模块路径：`$env:PSModulePath`。
- 将 ZIP 文件的内容提取到其中一个列出的文件夹中。
- 使用命令 `cd <path_to_powershell_modules_folder>` 和 `Get-ChildItem * -Recurse | Unblock-File` 取消阻止这些文件。
- 可以使用 `Get-Module -Name VMware.PowerCLI -ListAvailable` 命令验证 PowerCLI 模块是否可用。

#### 功能特点
- **生成模板**：`BulkVMTool` 提供了一个功能，可以在程序所在的目录下生成一个配置模板文件。此模板文件包含了所有需要用户填写或调整的虚拟机配置信息。
- **导入模板**：用户可以将之前生成的或手工编辑的模板文件导入到 `BulkVMTool` 中。导入后，用户需要保存设置以使更改生效。
- **执行脚本**：当配置完成后，用户可以通过 `BulkVMTool` 调用 PowerShell 脚本（.ps1 文件）来批量部署虚拟机。这些脚本通常包含了根据模板中定义的参数自动化创建虚拟机的逻辑。

#### 使用步骤
1. **准备环境**：确保你的 Windows 系统满足运行条件，并根据推荐安装 PowerCLI。
2. **启动 BulkVMTool**：运行程序，它会自动检查并提示你是否需要安装 PowerCLI。
3. **生成配置模板**：使用 `BulkVMTool` 提供的功能生成一个新的配置模板。这将帮助你组织和管理虚拟机的部署参数。
4. **编辑模板**：打开生成的模板文件，按照需求填写或修改各项参数。请参考模板中的注释了解每个字段的具体含义。
5. **导入模板**：将编辑好的模板重新导入到 `BulkVMTool` 中。记得保存所做的任何更改，以便它们能够被应用。
6. **执行部署**：最后，选择调用相应的 PowerShell 脚本来开始批量部署过程。监控部署进度，并在必要时进行干预。

#### 注意事项
- 在执行批量部署前，请务必仔细检查所有配置参数，确保它们符合预期。
- 如果遇到问题或者不确定的地方，建议查阅 PowerCLI 的官方文档或联系技术支持。
- 自动安装 PowerCLI 的功能可能因网络状况、权限限制等因素而受到影响，因此推荐手动安装以避免潜在的问题。

#### 常见问题解答 (FAQ)
- **Q: 我应该在哪里下载 PowerCLI？**
  - A: 你可以从 VMware 的官方网站下载最新版本的 PowerCLI。
- **Q: 如果我有多个不同的虚拟机配置怎么办？**
  - A: 你可以为每种不同类型的虚拟机创建单独的模板文件，然后分别导入和部署。
- **Q: 部署过程中出现问题如何处理？**
  - A: 首先查看错误信息和日志文件，尝试理解问题所在。如果无法解决，可以寻求专业帮助或访问社区论坛获取支持。

#### 结语
`BulkVMTool` 是一款强大的工具，旨在让虚拟机的批量部署变得更加简单高效。希望这份文档能帮助你更好地理解和使用这个工具。如果你有任何疑问或建议，欢迎随时反馈。
