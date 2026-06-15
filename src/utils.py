"""
情绪光谱仪 - 工具函数模块

提供项目通用的工具函数，包括：
- 文件操作工具
- 数据处理工具
- 颜色转换工具
- 时间处理工具
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np


# ==================== 文件操作工具 ====================

def load_json(file_path: Path) -> Any:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        JSON数据，如果文件不存在或解析失败返回空列表
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        return []


def save_json(file_path: Path, data: Any, ensure_ascii: bool = False, indent: int = 2) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
        ensure_ascii: 是否确保ASCII编码
        indent: 缩进空格数
        
    Returns:
        是否保存成功
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        return True
    except Exception:
        return False


def ensure_dir_exists(dir_path: Path) -> None:
    """
    确保目录存在，不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    dir_path.mkdir(parents=True, exist_ok=True)


def backup_file(source_path: Path, backup_dir: Path) -> Optional[Path]:
    """
    备份文件
    
    Args:
        source_path: 源文件路径
        backup_dir: 备份目录
        
    Returns:
        备份文件路径，如果失败返回None
    """
    try:
        ensure_dir_exists(backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = backup_dir / file_name
        shutil.copy(source_path, backup_path)
        return backup_path
    except Exception:
        return None


# ==================== 颜色转换工具 ====================

def hex_to_rgb(hex_color: str) -> tuple:
    """
    将十六进制颜色转换为RGB元组（0-1范围）
    
    Args:
        hex_color: 十六进制颜色字符串，如 '#FF00FF'
        
    Returns:
        RGB元组 (r, g, b)
    """
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))


def hex_to_rgb_array(hex_color: str) -> np.ndarray:
    """
    将十六进制颜色转换为RGB数组
    
    Args:
        hex_color: 十六进制颜色字符串
        
    Returns:
        RGB数组 [r, g, b]
    """
    return np.array([int(hex_color[i:i+2], 16) for i in (1, 3, 5)]) / 255.0


def rgb_to_hex(rgb: tuple) -> str:
    """
    将RGB元组转换为十六进制颜色字符串
    
    Args:
        rgb: RGB元组 (0-1范围)
        
    Returns:
        十六进制颜色字符串
    """
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255)
    )


# ==================== 数据处理工具 ====================

def normalize_dict_values(data: Dict[str, float]) -> Dict[str, float]:
    """
    归一化字典值，使总和为1
    
    Args:
        data: 待归一化的字典
        
    Returns:
        归一化后的字典
    """
    total = sum(data.values())
    if total == 0:
        return {k: 0.0 for k in data}
    return {k: v / total for k, v in data.items()}


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    将值限制在指定范围内
    
    Args:
        value: 输入值
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_val, min(max_val, value))


def sample_dict_keys(data: Dict, count: int) -> List:
    """
    从字典中随机采样指定数量的键
    
    Args:
        data: 字典
        count: 采样数量
        
    Returns:
        采样的键列表
    """
    keys = list(data.keys())
    sample_size = min(count, len(keys))
    return np.random.choice(keys, sample_size, replace=False).tolist()


# ==================== 时间处理工具 ====================

def get_current_timestamp() -> str:
    """
    获取当前时间戳（ISO格式）
    
    Returns:
        ISO格式时间戳字符串
    """
    return datetime.now().isoformat()


def get_current_time_str(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    获取当前时间字符串
    
    Args:
        format_str: 时间格式字符串
        
    Returns:
        格式化的时间字符串
    """
    return datetime.now().strftime(format_str)


def format_duration(seconds: float) -> str:
    """
    格式化时间间隔
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串，如 "1小时23分45秒"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


# ==================== 情绪数据工具 ====================

def validate_emotion(emotion: str, valid_emotions: List[str]) -> str:
    """
    验证情绪值是否有效
    
    Args:
        emotion: 待验证的情绪值
        valid_emotions: 有效情绪列表
        
    Returns:
        验证后的情绪值（无效则返回默认值）
    """
    if emotion in valid_emotions:
        return emotion
    return "中性"


def validate_intensity(intensity: float) -> float:
    """
    验证情绪强度值
    
    Args:
        intensity: 待验证的强度值
        
    Returns:
        验证后的强度值（0-100范围）
    """
    try:
        return clamp(float(intensity), 0, 100)
    except (ValueError, TypeError):
        return 50.0


def get_emotion_intensity_label(intensity: float) -> str:
    """
    根据强度值获取标签
    
    Args:
        intensity: 强度值（0-100）
        
    Returns:
        强度标签
    """
    if intensity < 20:
        return "极低"
    elif intensity < 40:
        return "低"
    elif intensity < 60:
        return "中等"
    elif intensity < 80:
        return "高"
    else:
        return "极高"


# ==================== 字符串处理工具 ====================

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def generate_filename(prefix: str, suffix: str = ".png") -> str:
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        suffix: 文件后缀
        
    Returns:
        生成的文件名
    """
    return f"{prefix}_{get_current_time_str()}{suffix}"
