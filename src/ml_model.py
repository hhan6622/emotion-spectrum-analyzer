"""
情绪光谱仪 - 机器学习模型模块

提供不依赖Ollama的本地情绪分类模型，使用scikit-learn实现。

使用方式：
    from src.ml_model import EmotionClassifier
    
    classifier = EmotionClassifier()
    result = classifier.predict("今天心情不错")
    # 返回: {'emotion': '喜悦', 'intensity': 0.85, 'confidence': 0.78}
"""

import json
import pickle
import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from src.config import EMOTIONS, DATA_DIR
from src.logging_config import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 情绪词典
EMOTION_WORDS = {
    '喜悦': ['开心', '快乐', '高兴', '幸福', '喜悦', '兴奋', '满足', '愉快', '欢乐', '欢喜', 
            '棒', '好', '赞', '爱', '乐', '欢', '笑', '喜', '甜', '美'],
    '悲伤': ['难过', '伤心', '悲伤', '失落', '沮丧', '痛苦', '悲哀', '哀伤', '哀愁', '忧郁',
            '悲', '苦', '哀', '泪', '痛', '惨', '愁', '闷', '郁'],
    '愤怒': ['生气', '愤怒', '恼火', '恼怒', '愤慨', '气愤', '暴怒', '怒', '火', '烦',
            '恼', '恨', '杀', '疯', '恶', '厌'],
    '恐惧': ['害怕', '恐惧', '担心', '担忧', '焦虑', '恐慌', '畏惧', '怕', '惊', '慌',
            '恐', '栗', '忧', '愁'],
    '惊讶': ['惊讶', '震惊', '惊奇', '意外', '居然', '竟然', '哇', '天呐', '没想到', '忽然',
            '突', '奇', '怪'],
    '厌恶': ['讨厌', '厌恶', '反感', '恶心', '嫌弃', '鄙视', '憎恶', '恶', '厌', '烦',
            '脏', '臭', '糟'],
    '中性': ['说', '想', '看', '听', '走', '来', '去', '有', '是', '在',
            '会', '能', '可以', '要', '知道', '觉得', '认为', '应该']
}

class EmotionClassifier:
    """
    基于机器学习的情绪分类器
    
    使用TF-IDF特征提取 + 朴素贝叶斯分类器
    """
    
    def __init__(self):
        self.model_path = DATA_DIR / "emotion_model.pkl"
        self.vectorizer_path = DATA_DIR / "vectorizer.pkl"
        self.label_encoder_path = DATA_DIR / "label_encoder.pkl"
        
        self.pipeline = None
        self.label_encoder = None
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """加载已训练的模型或训练新模型"""
        try:
            if self.model_path.exists() and self.vectorizer_path.exists() and self.label_encoder_path.exists():
                # 加载已训练的模型
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                logger.info("✅ 机器学习模型加载成功")
            else:
                # 训练新模型
                self._train_model()
                logger.info("✅ 机器学习模型训练完成")
        except Exception as e:
            logger.error(f"加载模型失败，重新训练: {str(e)}")
            self._train_model()
    
    def _train_model(self):
        """训练情绪分类模型"""
        # 准备训练数据
        texts = []
        labels = []
        
        # 从情绪词典生成训练样本
        for emotion, words in EMOTION_WORDS.items():
            for word in words:
                texts.append(word)
                texts.append(f"我很{word}")
                texts.append(f"{word}的一天")
                texts.append(f"今天很{word}")
                labels.extend([emotion] * 4)
        
        # 添加更多训练样本
        additional_samples = [
            ("今天心情真不错", "喜悦"),
            ("我很难过", "悲伤"),
            ("太生气了", "愤怒"),
            ("好害怕", "恐惧"),
            ("哇！真的吗", "惊讶"),
            ("这个东西好恶心", "厌恶"),
            ("今天天气不错", "中性"),
            ("会议在下午三点", "中性"),
            ("我很高兴", "喜悦"),
            ("心里美滋滋的", "喜悦"),
            ("感到很沮丧", "悲伤"),
            ("心如刀割", "悲伤"),
            ("暴跳如雷", "愤怒"),
            ("怒火中烧", "愤怒"),
            ("担惊受怕", "恐惧"),
            ("感到紧张", "恐惧"),
            ("太意外了", "惊讶"),
            ("不可思议", "惊讶"),
            ("令人作呕", "厌恶"),
            ("令人反感", "厌恶"),
            ("今天天气晴朗", "中性"),
            ("我去吃饭", "中性"),
            ("开心极了", "喜悦"),
            ("伤心欲绝", "悲伤"),
            ("恨之入骨", "愤怒"),
            ("胆战心惊", "恐惧"),
            ("大吃一惊", "惊讶"),
            ("深恶痛绝", "厌恶"),
            ("明天会下雨", "中性"),
        ]
        
        for text, label in additional_samples:
            texts.append(text)
            labels.append(label)
        
        # 创建并训练模型
        self.vectorizer = TfidfVectorizer(max_features=1000, analyzer='char', ngram_range=(1, 3))
        self.label_encoder = LabelEncoder()
        
        X = self.vectorizer.fit_transform(texts)
        y = self.label_encoder.fit_transform(labels)
        
        self.pipeline = MultinomialNB(alpha=1.0)
        self.pipeline.fit(X, y)
        
        # 保存模型
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        with open(self.label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        logger.info(f"📊 训练样本数: {len(texts)}, 情绪类别: {len(self.label_encoder.classes_)}")
    
    def _calculate_intensity(self, text: str, emotion: str) -> float:
        """计算情绪强度"""
        text_lower = text.lower()
        emotion_words = EMOTION_WORDS.get(emotion, [])
        match_count = sum(1 for word in emotion_words if word in text_lower)
        
        # 基于感叹号和表情符号增强强度
        exclamation_count = text.count('!') + text.count('！')
        intensity = min(1.0, 0.3 + match_count * 0.2 + exclamation_count * 0.15)
        
        return round(intensity, 2)
    
    def predict(self, text: str) -> Dict:
        """
        预测文本情绪
        
        Args:
            text: 待分析的文本
            
        Returns:
            包含情绪、强度和置信度的字典
        """
        if not text or not text.strip():
            return {
                'emotion': '中性',
                'intensity': 0.0,
                'confidence': 0.5,
                'reason': '输入文本为空'
            }
        
        try:
            # 使用模型预测
            X = self.vectorizer.transform([text])
            probs = self.pipeline.predict_proba(X)[0]
            predicted_idx = np.argmax(probs)
            emotion = self.label_encoder.inverse_transform([predicted_idx])[0]
            confidence = round(float(probs[predicted_idx]), 2)
            intensity = self._calculate_intensity(text, emotion)
            
            return {
                'emotion': emotion,
                'intensity': intensity,
                'confidence': confidence,
                'reason': f"机器学习模型预测，置信度: {confidence}"
            }
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            return {
                'emotion': '中性',
                'intensity': 0.3,
                'confidence': 0.5,
                'reason': f"预测异常: {str(e)}"
            }

# 创建单例实例
_ml_classifier = None

def get_ml_classifier() -> EmotionClassifier:
    """获取机器学习分类器单例"""
    global _ml_classifier
    if _ml_classifier is None:
        _ml_classifier = EmotionClassifier()
    return _ml_classifier

if __name__ == "__main__":
    # 测试模型
    classifier = EmotionClassifier()
    test_texts = [
        "今天心情真不错！",
        "我很难过",
        "太生气了！",
        "好害怕",
        "哇！真的吗？",
        "这个东西好恶心",
        "今天天气不错"
    ]
    
    print("=== 机器学习模型测试 ===")
    for text in test_texts:
        result = classifier.predict(text)
        print(f"{text} -> {result}")
