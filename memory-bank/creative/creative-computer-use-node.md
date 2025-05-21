# Computer Use节点创意设计

## 任务概述
本文档为Computer Use节点的创意设计方案，该节点将使DeerFlow系统能够通过访问和控制电脑、登录网站等操作与外部环境进行交互，从而增强系统的自主性和功能范围。

## 设计理念
Computer Use节点的设计遵循以下核心理念：

1. **安全第一**: 所有操作都必须经过严格的安全验证和用户确认，确保系统不会执行危险操作。
2. **最小权限**: 节点默认以最小必要权限运行，只请求完成任务所需的最低权限级别。
3. **透明可审计**: 所有操作都有详细记录，便于审计和回溯，确保操作可追踪。
4. **优雅降级**: 在遇到错误或权限不足时能够优雅地降级，提供替代解决方案。
5. **用户中心**: 将用户作为最终决策者，所有重要操作都需要用户明确批准。

## 功能模块设计
Computer Use节点将包含以下核心功能模块：

### 1. 浏览器交互模块
浏览器交互模块负责与网页浏览器的交互，包括打开URL、生成登录指导等功能。

#### 功能点：
- **URL打开功能**: 通过Python标准库webbrowser模块在默认浏览器中打开指定URL。
- **登录指导生成**: 生成结构化的网站登录步骤指南，包括字段识别和操作顺序。
- **页面元素查找指导**: 提供查找特定页面元素的方法指导，如通过ID、类名、XPath等。
- **网页内容提取指导**: 提供从网页中提取内容的方法指导，包括文本、链接和图像。

#### 设计示例：
```python
@tool
def open_browser(url: Annotated[str, "URL to open in the browser."]):
    """Open a URL in the default web browser."""
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Log the action
        logger.info(f"Opening URL in browser: {url}")

        # Open the URL
        webbrowser.open(url)
        return f"Successfully opened {url} in your default browser."
    except Exception as e:
        error_msg = f"Error opening {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg
```

### 2. 终端交互模块
终端交互模块负责与操作系统的终端/命令行进行交互，以执行系统级操作。所有命令都有严格的安全检查和用户确认机制。

#### 功能点：
- **命令执行**：执行用户批准的系统命令，获取输出结果。
- **安全检查**：对命令进行安全性评估，拦截潜在危险命令。
- **命令建议**：针对用户的高级需求，转换为安全的命令序列。
- **结果解析**：分析命令执行结果，提供人类可读的解释。

#### 创新安全机制：
终端交互模块将实现以下创新安全机制：

1. **多层级安全评估**
   - 静态危险关键词检查（如 'rm -rf /'）
   - 上下文敏感分析（检查命令的上下文适宜性）
   - 权限级别评估（执行命令所需的权限级别）

2. **可视化命令解析**
   - 向用户展示命令的每个部分和它们的含义
   - 高亮显示可能有风险的操作
   - 预测命令执行的可能结果

3. **沙箱运行评估**
   - 对于支持的命令，在沙箱环境中预执行并评估结果
   - 检测文件系统修改范围
   - 评估资源使用情况

#### 设计示例：
```python
@tool
def execute_terminal_command(
    command: Annotated[str, "Command to execute in the terminal."],
    working_directory: Annotated[str, "Working directory for the command."] = None,
    timeout: Annotated[int, "Timeout in seconds (0 for no timeout)."] = 30,
):
    """Execute a terminal command through the AI assistant with safety checks."""
    # Safety check for potentially dangerous commands
    dangerous_keywords = ["rm -rf", "dd if=", "mkfs", "> /dev/", ":(){ :|:& };:"]
    for keyword in dangerous_keywords:
        if keyword in command:
            return f"⚠️ Safety Alert: This command contains potentially dangerous operation: '{keyword}'. Please use a safer alternative."

    # Generate command analysis for user confirmation
    command_analysis = {
        "command": command,
        "working_directory": working_directory or "current directory",
        "explanation": "Command prepared for execution (will be executed after user approval)",
        "safety_level": "standard"  # Could be low, standard, or high risk
    }

    # Return command analysis for user confirmation
    # Actual execution will be performed by the computer_use_node after user approval
    return json.dumps(command_analysis, indent=2)
```

### 3. 系统信息模块
系统信息模块负责收集和提供系统相关信息，帮助用户了解当前计算机环境的状态，便于更好地执行后续操作。

#### 功能点：
- **获取基本系统信息**：操作系统类型、版本、架构等基本信息。
- **检测Python环境**：检测可用的Python版本和安装的关键包。
- **网络状态检查**：检查网络连接状态和配置。
- **文件系统信息**：获取可用空间和挂载点信息。

#### 设计示例：
```python
@tool
def system_info():
    """Get basic information about the operating system."""
    try:
        # Collect basic system information
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }

        # Add system-specific information
        if platform.system() == "Darwin":
            info["mac_version"] = platform.mac_ver()[0]
        elif platform.system() == "Windows":
            info["win_edition"] = platform.win32_edition()
            info["win_version"] = platform.win32_ver()
        elif platform.system() == "Linux":
            info["linux_distro"] = platform.freedesktop_os_release().get("PRETTY_NAME", "Unknown")

        return json.dumps(info, indent=2)
    except Exception as e:
        error_msg = f"Error getting system info: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
```
