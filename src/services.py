"""
情绪光谱仪 - 服务工厂模块

提供统一的服务管理入口，实现：
- 单例模式管理服务实例
- 服务依赖注入
- 统一的服务初始化和销毁

使用方式：
    from src.services import ServiceFactory
    
    # 获取服务
    api_service = ServiceFactory.get_api_service()
    visualizer = ServiceFactory.get_visualizer()
    trainer = ServiceFactory.get_self_trainer()
    
    # 检查服务状态
    status = ServiceFactory.check_all_services()
"""

from typing import Optional, Dict, Any
from pathlib import Path

from src.config import PROJECT_ROOT
from src.logging_config import get_logger
from src.api_service import EmotionAnalysisService
from src.visualization import EmotionVisualizer
from src.self_trainer import SelfTrainer

# 获取日志记录器
logger = get_logger(__name__)


class ServiceFactory:
    """
    服务工厂类 - 统一管理所有服务实例
    
    采用单例模式，确保每个服务在应用生命周期内只有一个实例
    """
    
    # 服务实例缓存
    _services: Dict[str, Any] = {}
    
    # 服务状态
    _initialized: bool = False
    
    @classmethod
    def _init_services(cls):
        """初始化所有服务（仅执行一次）"""
        if cls._initialized:
            return
        
        logger.info("🚀 初始化服务工厂...")
        
        # 确保必要的目录存在
        for dir_name in ["data", "models", "temp", "model_backups"]:
            dir_path = PROJECT_ROOT / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        cls._initialized = True
        logger.info("✅ 服务工厂初始化完成")
    
    @classmethod
    def get_api_service(cls) -> EmotionAnalysisService:
        """
        获取情绪分析服务实例
        
        Returns:
            EmotionAnalysisService实例
        """
        cls._init_services()
        
        if 'api_service' not in cls._services:
            logger.debug("创建 EmotionAnalysisService 实例...")
            cls._services['api_service'] = EmotionAnalysisService()
        
        return cls._services['api_service']
    
    @classmethod
    def get_visualizer(cls) -> EmotionVisualizer:
        """
        获取情绪可视化器实例
        
        Returns:
            EmotionVisualizer实例
        """
        cls._init_services()
        
        if 'visualizer' not in cls._services:
            logger.debug("创建 EmotionVisualizer 实例...")
            cls._services['visualizer'] = EmotionVisualizer()
        
        return cls._services['visualizer']
    
    @classmethod
    def get_self_trainer(cls) -> SelfTrainer:
        """
        获取自我训练器实例
        
        Returns:
            SelfTrainer实例
        """
        cls._init_services()
        
        if 'self_trainer' not in cls._services:
            logger.debug("创建 SelfTrainer 实例...")
            cls._services['self_trainer'] = SelfTrainer()
        
        return cls._services['self_trainer']
    
    @classmethod
    def check_all_services(cls) -> Dict[str, bool]:
        """
        检查所有服务的状态
        
        Returns:
            服务状态字典，key为服务名称，value为是否正常
        """
        status = {}
        
        try:
            api_service = cls.get_api_service()
            status['emotion_analysis'] = True
        except Exception as e:
            logger.error(f"检查情绪分析服务失败: {str(e)}")
            status['emotion_analysis'] = False
        
        try:
            visualizer = cls.get_visualizer()
            status['visualizer'] = True
        except Exception as e:
            logger.error(f"检查可视化服务失败: {str(e)}")
            status['visualizer'] = False
        
        try:
            trainer = cls.get_self_trainer()
            status['self_trainer'] = True
        except Exception as e:
            logger.error(f"检查自我训练器失败: {str(e)}")
            status['self_trainer'] = False
        
        return status
    
    @classmethod
    def get_service_status_summary(cls) -> str:
        """
        获取服务状态摘要（用于控制台输出）
        
        Returns:
            格式化的状态摘要字符串
        """
        status = cls.check_all_services()
        
        summary = "\n📊 服务状态检查:\n"
        summary += f"  {'🟢' if status.get('emotion_analysis', False) else '🔴'} 情绪分析服务: {'运行中' if status.get('emotion_analysis', False) else '未就绪'}\n"
        summary += f"  {'🟢' if status.get('visualizer', False) else '🔴'} 可视化服务: {'运行中' if status.get('visualizer', False) else '未就绪'}\n"
        summary += f"  {'🟢' if status.get('self_trainer', False) else '🔴'} 训练器服务: {'运行中' if status.get('self_trainer', False) else '未就绪'}\n"
        
        return summary
    
    @classmethod
    def reset_all_services(cls):
        """重置所有服务实例"""
        cls._services = {}
        cls._initialized = False
        logger.info("🔄 所有服务已重置")
    
    @classmethod
    def get_service_count(cls) -> int:
        """获取已创建的服务实例数量"""
        return len(cls._services)


# ==================== 便捷函数 ====================

def get_api_service() -> EmotionAnalysisService:
    """便捷函数：获取情绪分析服务"""
    return ServiceFactory.get_api_service()


def get_visualizer() -> EmotionVisualizer:
    """便捷函数：获取可视化器"""
    return ServiceFactory.get_visualizer()


def get_self_trainer() -> SelfTrainer:
    """便捷函数：获取自我训练器"""
    return ServiceFactory.get_self_trainer()


def check_services() -> Dict[str, bool]:
    """便捷函数：检查所有服务状态"""
    return ServiceFactory.check_all_services()


def get_service_status() -> str:
    """便捷函数：获取服务状态摘要"""
    return ServiceFactory.get_service_status_summary()


# ==================== 示例用法 ====================
if __name__ == "__main__":
    # 检查服务状态
    print(get_service_status())
    
    # 使用服务
    api = get_api_service()
    visualizer = get_visualizer()
    trainer = get_self_trainer()
    
    print(f"\n已创建服务实例: {ServiceFactory.get_service_count()} 个")
    
    # 测试API服务
    print("\n📝 测试情绪分析...")
    result = api.analyze_emotion("今天心情很好")
    print(f"结果: {result}")
