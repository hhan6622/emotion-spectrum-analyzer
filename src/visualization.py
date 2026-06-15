"""
情绪光谱仪 - 可视化模块

负责生成各种可视化图表，包括：
- 情绪雷达图
- 艺术光谱图
- 情绪时序图

支持多种艺术风格和自定义配置
"""

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib
import numpy as np
import random
from typing import Dict, Optional, List

from src.config import EMOTION_COLORS, EMOTIONS, VISUALIZATION_CONFIG
from src.logging_config import get_logger
from src.utils import hex_to_rgb_array, normalize_dict_values

# 获取日志记录器
logger = get_logger(__name__)

# 配置matplotlib
matplotlib.rcParams['font.sans-serif'] = VISUALIZATION_CONFIG['font_family']
matplotlib.rcParams['axes.unicode_minus'] = False


class EmotionVisualizer:
    """
    情绪可视化器类
    
    提供情绪数据的可视化功能，支持多种图表类型和艺术风格
    """
    
    def __init__(self):
        """初始化可视化器"""
        self.colors = EMOTION_COLORS
        self.emotions = EMOTIONS
        self.config = VISUALIZATION_CONFIG
        plt.style.use('dark_background')
        
    def _get_dominant_color(self, emotion_data: Dict[str, float]) -> np.ndarray:
        """
        获取主导情绪颜色
        
        Args:
            emotion_data: 情绪数据字典
            
        Returns:
            RGB颜色数组
        """
        dominant_emotion = max(emotion_data, key=emotion_data.get)
        color_hex = self.colors.get(dominant_emotion, '#FF00FF')
        return hex_to_rgb_array(color_hex)
    
    def create_radar_chart(self, emotion_data: Dict[str, float]) -> plt.Figure:
        """
        创建情绪雷达图
        
        Args:
            emotion_data: 情绪数据字典，包含七种情绪的概率值
            
        Returns:
            matplotlib Figure对象
        """
        expanded_data = self._expand_emotion_scores(emotion_data)
        normalized_data = normalize_dict_values(expanded_data)
        
        labels = self.emotions
        values = [normalized_data.get(e, 0) for e in labels]
        
        # 准备极坐标数据
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        # 创建图表
        fig, ax = plt.subplots(
            figsize=self.config['figsize_radar'],
            dpi=self.config['dpi'],
            subplot_kw=dict(polar=True)
        )
        
        # 绘制多层填充区域
        ax.fill(angles, values, color='#FF00FF', alpha=0.35)
        ax.fill(angles, [v * 0.7 for v in values], color='#00FFFF', alpha=0.25)
        ax.fill(angles, [v * 0.5 for v in values], color='#7D2AE8', alpha=0.15)
        
        # 绘制轮廓线
        ax.plot(angles, values, color='#39FF14', linewidth=4, 
                path_effects=[path_effects.withStroke(linewidth=12, foreground='#39FF14', alpha=0.5)],
                alpha=0.95)
        ax.plot(angles, [v * 0.7 for v in values], color='#00FFFF', linewidth=2, 
                path_effects=[path_effects.withStroke(linewidth=6, foreground='#00FFFF', alpha=0.3)],
                alpha=0.7)
        
        # 添加数据点和标签
        for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
            if value > 0.05:
                color_rgb = hex_to_rgb_array(self.colors.get(labels[i], '#FF00FF'))
                ax.scatter([angle], [value], color=color_rgb, s=120, zorder=5,
                          edgecolors='white', linewidths=3, alpha=0.9)
                ax.text(angle, value + 0.05, f'{value * 100:.0f}%', 
                        ha='center', va='center', fontsize=9, fontweight='bold',
                        color='#FFFFFF')
        
        # 配置坐标轴
        ax.set_ylim(0, 1.2)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], 
                          fontsize=10, color='#AAAAAA', fontweight='bold')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=14, fontweight='bold', color='#FFFFFF')
        
        # 配置网格和背景
        ax.grid(color=self.config['grid_color'], linestyle='-', alpha=0.8, linewidth=1.5)
        ax.set_facecolor(self.config['background_color'])
        ax.spines['polar'].set_color(self.config['edge_color'])
        ax.spines['polar'].set_linewidth(3)
        
        # 添加标题和主导情绪
        plt.title("情绪多维光谱分析", size=22, color='#00FFFF', fontweight='bold', y=1.12)
        max_emotion = labels[values[:-1].index(max(values[:-1]))]
        max_value = max(values[:-1])
        ax.text(0.5, -0.14, f'主导情绪: {max_emotion} ({max_value * 100:.0f}%)', 
                transform=ax.transAxes, ha='center', fontsize=14, color='#39FF14', fontweight='bold')
        
        fig.set_facecolor(self.config['background_color'])
        return fig
    
    def create_time_series(self, history_data: List[Dict]) -> Optional[plt.Figure]:
        """
        创建情绪时序图
        
        Args:
            history_data: 历史记录列表
            
        Returns:
            matplotlib Figure对象或None
        """
        if not history_data:
            logger.warning("历史数据为空，无法生成时序图")
            return None
            
        fig, ax = plt.subplots(
            figsize=self.config['figsize_timeseries'],
            dpi=self.config['dpi']
        )
        
        timestamps = [d['timestamp'] for d in history_data]
        valences = [d.get('valence', 0.5) for d in history_data]
        arousals = [d.get('arousal', 0.5) for d in history_data]
        
        ax.plot(timestamps, valences, label='愉悦度', marker='o', color='#FF00FF', linewidth=3,
                path_effects=[path_effects.withStroke(linewidth=5, foreground='#FF00FF', alpha=0.2)])
        ax.plot(timestamps, arousals, label='唤醒度', marker='s', color='#00FFFF', linewidth=3,
                path_effects=[path_effects.withStroke(linewidth=5, foreground='#00FFFF', alpha=0.2)])
        
        ax.fill_between(timestamps, valences, alpha=0.15, color='#FF00FF')
        ax.fill_between(timestamps, arousals, alpha=0.15, color='#00FFFF')
        
        ax.set_ylim(-1.2, 1.2)
        ax.axhline(0, color='#555555', linewidth=2, linestyle='--')
        ax.set_title("情感流转时序图", fontsize=18, color='#E0E0E0', fontweight='bold')
        ax.legend(facecolor='#1a1a1a', edgecolor='#444444')
        
        plt.xticks(rotation=45, fontsize=10)
        plt.tight_layout()
        
        return fig
    
    def generate_art_spectrum(self, emotion_score: Dict[str, float], style: str = "glitch") -> plt.Figure:
        """
        生成艺术光谱图
        
        Args:
            emotion_score: 情绪分数字典
            style: 艺术风格（glitch/particles/fluid/neon/cyber/ink）
            
        Returns:
            matplotlib Figure对象
        """
        width, height = 500, 500
        image = np.zeros((height, width, 3))
        
        dominant_color = self._get_dominant_color(emotion_score)
        
        # 创建基础渐变
        for y in range(height):
            image[y, :] = dominant_color * (y / height) * 0.5
        
        # 添加噪声
        noise = np.random.normal(0, 0.04, (height, width, 3))
        image = np.clip(image + noise, 0, 1)
        
        # 添加随机色块
        for _ in range(50):
            x = np.random.randint(0, width)
            w = np.random.randint(1, 25)
            rand_color = self._get_random_color()
            blend = np.random.uniform(0.35, 0.75)
            image[:, x:x+w] = image[:, x:x+w] * (1 - blend) + rand_color * blend
        
        # 应用艺术风格
        style_methods = {
            "glitch": self._apply_glitch_style,
            "particles": self._apply_particles_style,
            "fluid": self._apply_fluid_style,
            "neon": self._apply_neon_style,
            "cyber": self._apply_cyber_style,
            "ink": self._apply_ink_style
        }
        
        if style in style_methods:
            image = style_methods[style](image, height, width, dominant_color)
        else:
            logger.warning(f"未知艺术风格: {style}，使用默认风格")
        
        # 创建最终图像
        fig, ax = plt.subplots(figsize=self.config['figsize_art'], dpi=self.config['dpi'])
        ax.imshow(image)
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        return fig
    
    def _expand_emotion_scores(self, emotion_data: Dict[str, float]) -> Dict[str, float]:
        """
        根据情绪关联关系扩展情绪分数
        
        Args:
            emotion_data: 原始情绪数据
            
        Returns:
            扩展后的情绪数据
        """
        emotion_relations = {
            '喜悦': {'喜悦': 1.0, '惊讶': 0.3, '中性': 0.15, '悲伤': 0.05, '恐惧': 0.05, '愤怒': 0.02, '厌恶': 0.02},
            '悲伤': {'悲伤': 1.0, '恐惧': 0.35, '愤怒': 0.2, '厌恶': 0.15, '中性': 0.1, '惊讶': 0.05, '喜悦': 0.02},
            '愤怒': {'愤怒': 1.0, '厌恶': 0.4, '悲伤': 0.25, '恐惧': 0.15, '惊讶': 0.1, '中性': 0.05, '喜悦': 0.02},
            '恐惧': {'恐惧': 1.0, '悲伤': 0.3, '惊讶': 0.25, '愤怒': 0.15, '厌恶': 0.1, '中性': 0.08, '喜悦': 0.02},
            '惊讶': {'惊讶': 1.0, '喜悦': 0.35, '恐惧': 0.2, '中性': 0.15, '愤怒': 0.1, '悲伤': 0.08, '厌恶': 0.05},
            '厌恶': {'厌恶': 1.0, '愤怒': 0.45, '悲伤': 0.2, '恐惧': 0.12, '中性': 0.1, '惊讶': 0.05, '喜悦': 0.02},
            '中性': {'中性': 1.0, '喜悦': 0.12, '悲伤': 0.12, '惊讶': 0.1, '恐惧': 0.08, '愤怒': 0.06, '厌恶': 0.05}
        }
        
        expanded = {}
        for emotion, score in emotion_data.items():
            if emotion in emotion_relations and score > 0:
                relations = emotion_relations[emotion]
                for related_emotion, relation_weight in relations.items():
                    current = expanded.get(related_emotion, 0)
                    expanded[related_emotion] = current + score * relation_weight
            else:
                expanded[emotion] = max(expanded.get(emotion, 0), score)
        return expanded
    
    def _get_random_color(self) -> np.ndarray:
        """获取随机情绪颜色"""
        color_hex = random.choice(list(self.colors.values()))
        return hex_to_rgb_array(color_hex)
    
    def _apply_glitch_style(self, image: np.ndarray, height: int, width: int, *args) -> np.ndarray:
        """应用故障艺术风格"""
        for _ in range(30):
            y = np.random.randint(0, height)
            h = np.random.randint(1, 6)
            shift = np.random.randint(-40, 40)
            channel = np.random.randint(0, 3)
            image[y:y+h, :, channel] = np.roll(image[y:y+h, :, channel], shift, axis=1)
        
        for _ in range(20):
            x_start = np.random.randint(0, width - 80)
            x_end = x_start + np.random.randint(15, 80)
            y_pos = np.random.randint(0, height)
            image[y_pos, x_start:x_end] = image[y_pos, x_start:x_end][::-1]
        
        return image
    
    def _apply_particles_style(self, image: np.ndarray, height: int, width: int, dominant_color: np.ndarray) -> np.ndarray:
        """应用粒子风暴风格"""
        num_particles = 250
        for _ in range(num_particles):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            radius = np.random.randint(1, 6)
            intensity = np.random.uniform(0.4, 1.0)
            
            y_grid, x_grid = np.ogrid[:height, :width]
            dist_sq = (y_grid - y)**2 + (x_grid - x)**2
            mask = dist_sq <= radius**2
            image[mask] = image[mask] * (1 - intensity) + dominant_color * intensity
        
        return image
    
    def _apply_fluid_style(self, image: np.ndarray, height: int, width: int, dominant_color: np.ndarray) -> np.ndarray:
        """应用流体渐变风格"""
        Y, X = np.ogrid[:height, :width]
        
        for i in range(3):
            wave = np.sin(X * 0.015 + i) * np.sin(Y * 0.015 + i * 1.3)
            wave += np.sin(X * 0.008 + Y * 0.008 * i) * 0.4
            image[..., i] = image[..., i] * 0.5 + dominant_color[i] * (wave * 0.35 + 0.5)
        
        return image
    
    def _apply_neon_style(self, image: np.ndarray, height: int, width: int, *args) -> np.ndarray:
        """应用霓虹脉冲风格"""
        for _ in range(35):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            
            for dx in range(-6, 7):
                for dy in range(-6, 7):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        dist = np.sqrt(dx**2 + dy**2)
                        if dist <= 6:
                            neon_color = random.choice([
                                np.array([1, 0, 1]),
                                np.array([0, 1, 1]),
                                np.array([0.22, 1, 0.08]),
                                np.array([1, 0.2, 0.2])
                            ])
                            intensity = 1 - dist / 6
                            image[ny, nx] = image[ny, nx] * (1 - intensity * 0.7) + neon_color * intensity * 0.7
        
        return image
    
    def _apply_cyber_style(self, image: np.ndarray, height: int, width: int, *args) -> np.ndarray:
        """应用赛博网格风格"""
        grid_size = 25
        
        for x in range(0, width, grid_size):
            image[:, x:x+2] = np.array([0, 0.6, 1]) * 0.4
        
        for y in range(0, height, grid_size):
            image[y:y+2, :] = np.array([0, 0.6, 1]) * 0.4
        
        for _ in range(12):
            x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
            x2, y2 = np.random.randint(0, width), np.random.randint(0, height)
            
            num_points = 60
            xs = np.linspace(x1, x2, num_points).astype(int)
            ys = np.linspace(y1, y2, num_points).astype(int)
            
            for i in range(num_points):
                if 0 <= xs[i] < width and 0 <= ys[i] < height:
                    image[ys[i], xs[i]] = np.array([0, 1, 0.5]) * 0.7
        
        return image
    
    def _apply_ink_style(self, image: np.ndarray, height: int, width: int, dominant_color: np.ndarray) -> np.ndarray:
        """应用水墨意境风格"""
        ink_intensity = np.zeros((height, width))
        
        for _ in range(60):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            radius = np.random.randint(15, 80)
            
            Y, X = np.ogrid[:height, :width]
            dist = np.sqrt((X - x)**2 + (Y - y)**2)
            ink_intensity += np.exp(-dist / radius) * np.random.uniform(0.35, 0.85)
        
        ink_intensity = np.clip(ink_intensity, 0, 1)
        
        for i in range(3):
            image[..., i] = image[..., i] * (1 - ink_intensity) + dominant_color[i] * ink_intensity * 0.65
        
        noise = np.random.normal(0, 0.025, (height, width))
        image = image * (1 + noise[:, :, np.newaxis])
        
        return np.clip(image, 0, 1)
