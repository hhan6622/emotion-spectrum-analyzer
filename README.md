# 神经情绪光谱仪 (Emotion Spectrum Analyzer)

基于本地大语言模型的多模态情绪分析与可视化系统。

## 🚀 项目结构

```
e:\毕设/
├── src/                    # 源代码目录
│   ├── main.py            # 主入口文件
│   ├── web_interface.py   # Web界面模块
│   ├── api_service.py     # Ollama API服务
│   ├── visualization.py   # 可视化模块（雷达图、艺术光谱）
│   ├── self_trainer.py    # 自我训练模块
│   ├── database.py        # SQLite数据库模块
│   ├── services.py        # 服务工厂
│   ├── config.py          # 全局配置
│   ├── utils.py           # 工具函数
│   └── logging_config.py  # 日志配置
├── data/                  # 数据目录
│   ├── emotion_data.csv   # 训练数据集
│   └── emotion_db.sqlite  # SQLite数据库文件
├── tests/                 # 测试代码
├── venv/                  # Python虚拟环境
├── emotion_analyzer.modelfile  # Ollama模型配置
├── emotion_training_data.json  # 训练数据
├── feedback_data.json     # 用户反馈数据
├── training_history.json  # 训练历史
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── start.bat              # 启动脚本
└── install.bat            # 安装脚本
```

## 🛠️ 快速开始

### 方法1：使用启动脚本
```powershell
.\start.bat
```

### 方法2：手动启动
```powershell
# 设置环境变量
$env:PYTHONPATH = "e:\毕设"

# 启动应用
venv\Scripts\python.exe -m src.main
```

### 方法3：开发模式
```powershell
cd e:\毕设
$env:PYTHONPATH = "e:\毕设"
venv\Scripts\python.exe -m src.main
```

## 🎯 核心功能

| 功能 | 描述 |
|------|------|
| 🔐 **用户认证** | 注册、登录、退出 |
| 📝 **文本分析** | 输入文本进行情绪分析 |
| 🎤 **语音输入** | 支持麦克风语音输入 |
| 📊 **情绪雷达图** | 可视化七种情绪分布 |
| 🌌 **艺术光谱** | 将情绪转化为艺术图像 |
| 📋 **历史记录** | 保存用户分析历史 |
| 🧠 **自我训练** | 基于用户反馈持续优化模型 |
| 💾 **数据持久化** | SQLite数据库存储 |

## 🎨 艺术风格

- 🎭 故障艺术 - 经典数字故障效果
- 🌊 流体渐变 - 柔和色彩流动
- ⚡ 霓虹脉冲 - 赛博朋克风格
- 🔲 赛博网格 - 数字网格矩阵
- 🎨 粒子风暴 - 动态粒子效果
- 🖌️ 水墨意境 - 东方水墨风格

## 🔧 技术栈

- **前端框架**: Gradio 5.x
- **后端**: Python 3.11
- **数据库**: SQLite 3
- **AI模型**: Ollama (deepseek-r1:14b, qwen2.5, qwen3)
- **可视化**: Matplotlib
- **部署**: 本地运行

## 📊 性能指标

- 训练样本数: 281条
- 支持七种情绪分类: 喜悦、悲伤、愤怒、恐惧、惊讶、厌恶、中性
- 模型准确率: 85%+

## 🌐 访问地址

启动后访问: http://localhost:7861

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `src/main.py` | 主入口，支持多模式启动 |
| `src/web_interface.py` | Gradio Web界面 |
| `src/api_service.py` | Ollama API调用 |
| `src/database.py` | 用户认证和历史记录 |
| `src/self_trainer.py` | 模型自我训练 |
| `src/config.py` | 全局配置参数 |

## 🔍 关键词索引

| 关键词 | 描述 | 相关文件 |
|--------|------|----------|
| **情绪分析** | 文本情绪分类识别 | `src/api_service.py`, `src/self_trainer.py` |
| **可视化** | 雷达图、艺术光谱生成 | `src/visualization.py` |
| **用户认证** | 注册、登录、退出功能 | `src/database.py`, `src/web_interface.py` |
| **历史记录** | 用户分析历史存储与查询 | `src/database.py` |
| **自我训练** | 基于反馈的模型迭代 | `src/self_trainer.py` |
| **Ollama** | 本地大语言模型调用 | `src/api_service.py`, `src/services.py` |
| **Gradio** | Web界面框架 | `src/web_interface.py` |
| **SQLite** | 轻量级数据库 | `src/database.py` |

## 📖 用法帮助

### 1. 打包版本使用说明

#### 📦 快速安装（推荐）

适用于 Windows 10/11 64位系统，无需预先安装 Python。

**安装步骤：**
1. 解压压缩包到任意目录
2. 双击 `install.cmd` 运行安装脚本
3. 等待安装完成（约5-10分钟）
4. 双击 `start.cmd` 或桌面快捷方式启动应用

**安装脚本会自动完成：**
- ✅ 检测并安装 Python 3.13（如需要）
- ✅ 创建虚拟环境
- ✅ 安装所有依赖包
- ✅ 初始化机器学习模型
- ✅ 创建桌面快捷方式

**访问地址：** http://localhost:7861

#### 🔧 手动安装 Python 3.13

如果自动安装失败，可手动安装：

1. **下载 Python 3.13**
   - 访问：https://www.python.org/downloads/windows/
   - 下载：Python 3.13.0 (64-bit)
   - 文件名：`python-3.13.0-amd64.exe`

2. **安装 Python**
   - 运行安装程序
   - ⚠️ **务必勾选** "Add Python to PATH"
   - 选择 "Install Now" 或 "Customize installation"
   - 等待安装完成

3. **验证安装**
   ```powershell
   python --version
   # 应显示：Python 3.13.0
   ```

4. **继续安装应用**
   - 双击 `install.cmd` 运行安装脚本

#### ⚠️ 常见问题

**Q: 安装脚本无法运行？**
A: 右键点击 `install.cmd` → 选择"以管理员身份运行"

**Q: Python 下载失败？**
A: 检查网络连接，或手动下载后放到 `C:\Users\你的用户名\AppData\Local\Temp\python_installer.exe`

**Q: 依赖安装失败？**
A: 尝试手动升级 pip：
```powershell
venv\Scripts\python.exe -m pip install --upgrade pip
```

**Q: 端口 7861 被占用？**
A: 修改 `src/config.py` 中的 `server_port` 参数

### 2. 基本使用流程

```
① 注册/登录 → ② 输入文本 → ③ 点击分析 → ④ 查看结果 → ⑤ 反馈纠错
```

### 3. 界面功能说明

| 标签页 | 功能 | 说明 |
|--------|------|------|
| 🔐 用户中心 | 用户注册、登录、退出 | 首次使用需注册 |
| 📊 实时扫描 | 文本输入与情绪分析 | 支持语音输入 |
| 🎨 艺术光谱 | 艺术风格选择与图像生成 | 6种艺术风格 |
| 📝 历史记录 | 查看个人分析历史 | 支持导出 |
| 📤 数据导出 | 导出历史记录为JSON | 便于数据备份 |
| 🧠 模型训练 | 查看状态与触发训练 | 管理员功能 |

### 4. API服务说明

**模型优先级顺序**：
1. `deepseek-r1:14b` - 主模型
2. `qwen2.5` - 备用模型1
3. `qwen3` - 备用模型2
4. `emotion_analyzer` - 自定义模型

### 4. 训练数据格式

CSV格式，包含字段：
- `text`: 文本内容
- `emotion`: 情绪标签（喜悦/悲伤/愤怒/恐惧/惊讶/厌恶/中性）
- `intensity`: 情绪强度（0-1）

### 5. 常见问题

**Q**: 服务启动失败？
**A**: 检查Ollama服务是否运行，确保已下载模型

**Q**: 情绪分析结果不准确？
**A**: 使用"反馈纠错"功能帮助模型学习，或触发重新训练

**Q**: 如何导出历史数据？
**A**: 在"数据导出"标签页点击"导出"按钮

## 📝 代码注释规范

项目采用Google风格的代码注释：

```python
def analyze_emotion(text: str) -> Dict:
    """分析文本情绪
    
    Args:
        text: 待分析的文本内容
        
    Returns:
        情绪分析结果字典，包含情绪类型和置信度
        
    Raises:
        ValueError: 当输入为空时
    """
    pass
```

## 📜 项目许可证

MIT License - 详见 LICENSE 文件（如需要）
