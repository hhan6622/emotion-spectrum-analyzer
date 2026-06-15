"""
情绪光谱仪 - API服务模块

负责处理情绪分析服务，支持两种模式：
1. 本地机器学习模型（优先）
2. Ollama大语言模型（备用）

采用统一的日志配置和工具函数
"""

import json
from typing import Dict, Optional
from time import sleep

import requests

from src.config import OLLAMA_CONFIG, EMOTIONS
from src.logging_config import get_logger
from src.utils import validate_emotion, validate_intensity
from src.ml_model import get_ml_classifier

# 获取日志记录器
logger = get_logger(__name__)

# 是否使用Ollama（设置为False则只使用本地ML模型）
USE_OLLAMA = False

class EmotionAnalysisService:
    """
    情绪分析服务类
    
    优先使用本地机器学习模型，不需要Ollama也能运行
    """
    
    def __init__(self):
        """初始化情绪分析服务"""
        self.ml_classifier = get_ml_classifier()
        self.use_ollama = USE_OLLAMA
        
        if self.use_ollama:
            self.base_url = OLLAMA_CONFIG['base_url']
            self.timeout = OLLAMA_CONFIG['timeout']
            self.max_retries = OLLAMA_CONFIG['max_retries']
            self.retry_delay = OLLAMA_CONFIG['retry_delay']
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        分析文本情绪
        
        Args:
            text: 待分析的文本
            
        Returns:
            情绪分析结果字典
        """
        if not text or not text.strip():
            logger.warning("空文本输入")
            return self._create_error_result("请输入有效文本")
        
        logger.info(f"开始分析情绪: {text[:50]}...")
        
        # 优先使用本地机器学习模型
        try:
            result = self.ml_classifier.predict(text)
            logger.info(f"ML模型分析结果: {result}")
            return {
                'success': True,
                'emotion': result['emotion'],
                'intensity': result['intensity'],
                'confidence': result['confidence'],
                'reason': result['reason'],
                'model': 'ml'
            }
        except Exception as ml_error:
            logger.warning(f"ML模型分析失败: {str(ml_error)}")
            
            # 如果启用了Ollama，尝试使用Ollama
            if self.use_ollama:
                return self._analyze_with_ollama(text)
            else:
                return self._create_error_result(f"分析失败: {str(ml_error)}")
    
    def _analyze_with_ollama(self, text: str) -> Dict:
        """使用Ollama分析情绪（备用方案）"""
        payload = {
            "model": "emotion_analyzer",
            "prompt": f"分析情绪：{text}",
            "stream": False
        }
        
        try:
            result = self._make_request("generate", payload)
            
            if result is None:
                return self._create_error_result("Ollama服务不可用")
            
            response_text = result.get("response", "{}")
            
            try:
                data = json.loads(response_text)
                return self._validate_result(data)
            except json.JSONDecodeError:
                logger.error(f"响应解析失败: {response_text}")
                return self._create_error_result(f"响应解析失败: {response_text[:50]}")
                    
        except Exception as e:
            logger.error(f"Ollama分析异常: {str(e)}", exc_info=True)
            return self._create_error_result(f"分析异常: {str(e)}")
    
    def _make_request(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        """发送HTTP请求到Ollama服务"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    sleep(self.retry_delay)
        
        logger.error(f"请求失败，已重试 {self.max_retries} 次")
        return None
    
    def _validate_result(self, data: Dict) -> Dict:
        """验证分析结果"""
        try:
            emotion = data.get('emotion', '中性')
            intensity = data.get('intensity', 0.5)
            confidence = data.get('confidence', 0.7)
            reason = data.get('reason', '分析完成')
            
            # 验证情绪值
            emotion = validate_emotion(emotion)
            intensity = validate_intensity(intensity)
            
            return {
                'success': True,
                'emotion': emotion,
                'intensity': intensity,
                'confidence': confidence,
                'reason': reason,
                'model': 'ollama'
            }
        except Exception as e:
            logger.error(f"结果验证失败: {str(e)}")
            return self._create_error_result(f"结果验证失败: {str(e)}")
    
    def _create_error_result(self, message: str) -> Dict:
        """创建错误结果"""
        return {
            'success': False,
            'emotion': '中性',
            'intensity': 0.0,
            'confidence': 0.0,
            'reason': message,
            'model': 'error'
        }

# 单例实例
_api_service = None

def get_api_service() -> EmotionAnalysisService:
    """获取情绪分析服务单例"""
    global _api_service
    if _api_service is None:
        _api_service = EmotionAnalysisService()
    return _api_service

def check_ollama_status() -> bool:
    """检查Ollama服务状态"""
    if not USE_OLLAMA:
        return True  # 不使用Ollama时返回True
    
    try:
        response = requests.get(f"{OLLAMA_CONFIG['base_url']}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    # 测试服务
    service = get_api_service()
    
    test_texts = [
        "今天心情真不错！",
        "我很难过",
        "太生气了！",
        "好害怕",
        "哇！真的吗？",
        "这个东西好恶心",
        "今天天气不错"
    ]
    
    print("=== 情绪分析服务测试 ===")
    for text in test_texts:
        result = service.analyze_emotion(text)
        print(f"{text} -> {result}")
