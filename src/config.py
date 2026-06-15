"""
情绪光谱仪 - 全局配置模块

集中管理项目所有配置参数，包括：
- 情绪相关配置
- Ollama服务配置
- UI界面配置
- 可视化配置
- 训练参数配置
"""

import os
from pathlib import Path

# ==================== 项目路径配置 ====================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
BACKUP_DIR = PROJECT_ROOT / "model_backups"
TEMP_DIR = PROJECT_ROOT / "temp"

# 确保目录存在
for dir_path in [DATA_DIR, MODEL_DIR, BACKUP_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==================== 情绪配置 ====================
# 七种基本情绪
EMOTIONS = ['喜悦', '悲伤', '愤怒', '恐惧', '惊讶', '厌恶', '中性']

# 情绪颜色映射 - 赛博朋克风格
EMOTION_COLORS = {
    '喜悦': '#FF00FF',      # 霓虹粉
    '悲伤': '#00FFFF',      # 冰晶蓝
    '愤怒': '#FF3131',      # 极客红
    '恐惧': '#7D2AE8',      # 幻影紫
    '惊讶': '#39FF14',      # 荧光绿
    '厌恶': '#FFD700',      # 闪耀金
    '中性': '#E0E0E0'       # 珍珠白
}

# 情绪强度标签
INTENSITY_LABELS = ['极低', '低', '中等', '高', '极高']

# 情绪词典
EMOTION_LEXICON = {
    '喜悦': ['开心', '快乐', '棒', '好', '喜', '乐', '欢', '爱', '赞', '喜悦', '兴奋', '满足'],
    '悲伤': ['难过', '伤心', '悲', '苦', '哀', '泪', '痛', '惨', '忧伤', '郁闷', '失落'],
    '愤怒': ['生气', '愤怒', '气', '恼', '怒', '恨', '杀', '疯', '恼火', '可恶', '不满'],
    '恐惧': ['害怕', '恐惧', '惊', '恐', '怕', '栗', '慌', '担惊受怕', '紧张'],
    '惊讶': ['惊讶', '震惊', '哇', '居然', '竟然', '吓', '奇迹', '意外'],
    '厌恶': ['讨厌', '恶心', '厌', '呸', '脏', '臭', '反感', '鄙视'],
    '中性': ['一般', '还行', '普通', '正常', '平常', '还好']
}

# ==================== Ollama服务配置 ====================
OLLAMA_CONFIG = {
    'host': 'localhost',
    'port': 11434,
    'base_url': 'http://localhost:11434/api',
    'model_name': 'emotion_analyzer',
    'timeout': 60,
    'max_retries': 3,
    'retry_delay': 2
}

# ==================== 可视化配置 ====================
VISUALIZATION_CONFIG = {
    'dpi': 150,
    'figsize_radar': (8, 8),
    'figsize_art': (7, 7),
    'figsize_timeseries': (12, 6),
    'font_family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
    'background_color': '#0a0a0a',
    'grid_color': '#333333',
    'edge_color': '#00FFFF'
}

# 艺术风格配置
ART_STYLES = [
    ("故障艺术", "glitch"),
    ("粒子风暴", "particles"),
    ("流体渐变", "fluid"),
    ("霓虹脉冲", "neon"),
    ("赛博网格", "cyber"),
    ("水墨意境", "ink")
]

# ==================== 自我训练配置 ====================
TRAINING_CONFIG = {
    'min_feedback_threshold': 10,
    'performance_threshold': 0.85,
    'max_feedback_to_keep': 20,
    'max_correct_samples': 5,
    'backup_enabled': True,
    'auto_train_enabled': True
}

# ==================== 数据文件路径 ====================
DATA_PATHS = {
    'training_data': PROJECT_ROOT / "emotion_training_data.json",
    'feedback_data': PROJECT_ROOT / "feedback_data.json",
    'training_history': PROJECT_ROOT / "training_history.json",
    'modelfile': PROJECT_ROOT / "emotion_analyzer.modelfile",
    'emotion_data': DATA_DIR / "emotion_data.csv"
}

# ==================== UI配置 ====================
UI_CONFIG = {
    'title': '神经情绪光谱仪 v1.2',
    'subtitle': '多模态情绪分析系统',
    'server_port': 7861,
    'server_name': '0.0.0.0',
    'max_history': 100,
    'max_input_length': 5000
}

# ==================== 日志配置 ====================
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': PROJECT_ROOT / "app.log"
}

# ==================== 渐变背景配置 ====================
UI_GRADIENTS = {
    'primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'secondary': 'linear-gradient(to right, #ff7e5f, #feb47b)',
    'accent': 'linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)',
    'cyber': 'linear-gradient(90deg, #00fff0, #ff00ff, #00fff0)'
}

# ==================== 版本信息 ====================
VERSION_INFO = {
    'version': '1.2.0',
    'build_date': '2026-06-14',
    'description': '情绪光谱仪 - 多模态情绪分析系统'
}