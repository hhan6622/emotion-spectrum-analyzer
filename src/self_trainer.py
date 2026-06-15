"""
情绪光谱仪 - 自我训练迭代系统

该模块实现了一个能够持续自我训练和自我迭代的情绪分析模型：
1. 自动收集用户反馈数据
2. 定期进行增量训练
3. 评估模型性能并自动迭代优化
4. 记录训练历史和效果追踪
"""

import json
import random
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

from src.config import DATA_PATHS, TRAINING_CONFIG
from src.logging_config import get_logger
from src.utils import load_json, save_json, backup_file, ensure_dir_exists

# 获取日志记录器
logger = get_logger(__name__)


class SelfTrainer:
    """
    自我训练器类 - 实现持续自我训练和迭代功能
    """
    
    def __init__(self, 
                 model_name: str = "emotion_analyzer",
                 min_feedback_threshold: int = None,
                 performance_threshold: float = None):
        """
        初始化自我训练器
        
        Args:
            model_name: Ollama模型名称
            min_feedback_threshold: 触发训练的最小反馈数量
            performance_threshold: 性能阈值，低于此值触发迭代
        """
        # 使用配置参数
        self.model_name = model_name
        self.min_feedback_threshold = min_feedback_threshold or TRAINING_CONFIG['min_feedback_threshold']
        self.performance_threshold = performance_threshold or TRAINING_CONFIG['performance_threshold']
        
        # 数据路径（使用绝对路径）
        self.training_data_path = DATA_PATHS['training_data']
        self.modelfile_path = DATA_PATHS['modelfile']
        self.feedback_data_path = DATA_PATHS['feedback_data']
        self.training_history_path = DATA_PATHS['training_history']
        
        # 确保目录存在
        ensure_dir_exists(self.training_data_path.parent)
        ensure_dir_exists(self.feedback_data_path.parent)
        ensure_dir_exists(self.training_history_path.parent)
        
        # 加载数据
        self.training_data = self._load_training_data()
        self.feedback_data = self._load_feedback_data()
        self.training_history = self._load_training_history()
        
        # 性能指标
        self.current_performance = self._calculate_performance()
        
        logger.info(f"✅ 自我训练器初始化完成")
        logger.info(f"   - 训练样本数: {len(self.training_data)}")
        logger.info(f"   - 待处理反馈: {len(self.feedback_data)}")
        logger.info(f"   - 当前性能: {self.current_performance:.2%}")
    
    def _load_training_data(self) -> List[Dict]:
        """加载训练数据"""
        data = load_json(self.training_data_path)
        if not data:
            logger.warning(f"训练数据文件不存在或为空: {self.training_data_path}")
        return data if isinstance(data, list) else []
    
    def _load_feedback_data(self) -> List[Dict]:
        """加载反馈数据"""
        data = load_json(self.feedback_data_path)
        if not data:
            logger.warning(f"反馈数据文件不存在或为空: {self.feedback_data_path}")
        return data if isinstance(data, list) else []
    
    def _load_training_history(self) -> List[Dict]:
        """加载训练历史"""
        data = load_json(self.training_history_path)
        if not data:
            logger.warning(f"训练历史文件不存在或为空: {self.training_history_path}")
        return data if isinstance(data, list) else []
    
    def _calculate_performance(self) -> float:
        """计算当前模型性能"""
        if not self.feedback_data:
            return 0.0
        
        try:
            correct = sum(1 for f in self.feedback_data if f.get('is_correct', False))
            performance = correct / len(self.feedback_data)
            logger.debug(f"性能计算: {correct}/{len(self.feedback_data)} = {performance:.2%}")
            return performance
        except Exception as e:
            logger.error(f"计算性能失败: {str(e)}", exc_info=True)
            return 0.0
    
    def add_feedback(self, 
                     input_text: str, 
                     predicted_emotion: str, 
                     predicted_intensity: float,
                     actual_emotion: str, 
                     actual_intensity: Optional[float] = None,
                     is_correct: bool = True,
                     user_comment: str = "") -> None:
        """
        添加用户反馈
        
        Args:
            input_text: 用户输入的文本
            predicted_emotion: 模型预测的情绪
            predicted_intensity: 模型预测的强度
            actual_emotion: 用户反馈的实际情绪
            actual_intensity: 用户反馈的实际强度
            is_correct: 是否预测正确
            user_comment: 用户备注
        """
        try:
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "input_text": input_text,
                "predicted": {
                    "emotion": predicted_emotion,
                    "intensity": predicted_intensity
                },
                "actual": {
                    "emotion": actual_emotion,
                    "intensity": actual_intensity
                },
                "is_correct": is_correct,
                "user_comment": user_comment
            }
            
            self.feedback_data.append(feedback)
            save_json(self.feedback_data_path, self.feedback_data)
            
            # 更新性能
            self.current_performance = self._calculate_performance()
            
            logger.info(f"📝 新增反馈: {'正确' if is_correct else '错误'} - {predicted_emotion} → {actual_emotion}")
            
            # 检查是否需要触发训练
            self._check_and_train()
            
        except Exception as e:
            logger.error(f"添加反馈失败: {str(e)}", exc_info=True)
    
    def _check_and_train(self) -> bool:
        """检查是否需要触发训练并执行"""
        try:
            # 检查反馈数量是否达到阈值
            if len(self.feedback_data) >= self.min_feedback_threshold:
                # 检查性能是否低于阈值
                if self.current_performance < self.performance_threshold:
                    logger.warning(f"🚨 性能 {self.current_performance:.2%} 低于阈值 {self.performance_threshold:.2%}，触发迭代训练...")
                    return self._perform_training()
                else:
                    logger.info(f"✅ 性能 {self.current_performance:.2%} 高于阈值，暂不训练")
                    # 即使性能高，也定期进行增量训练
                    if len(self.feedback_data) >= self.min_feedback_threshold * 5:
                        logger.info("📈 反馈数据充足，执行增量训练...")
                        return self._perform_training(incremental=True)
            return False
        except Exception as e:
            logger.error(f"检查训练条件失败: {str(e)}", exc_info=True)
            return False
    
    def _perform_training(self, incremental: bool = False) -> bool:
        """
        执行模型训练
        
        Args:
            incremental: 是否为增量训练
            
        Returns:
            训练是否成功
        """
        logger.info(f"🚀 开始{'增量' if incremental else '完整'}训练...")
        
        try:
            # 1. 整理反馈数据，提取有用样本
            useful_samples = self._extract_useful_samples()
            
            if not useful_samples:
                logger.warning("⚠️ 没有可用的训练样本")
                return False
            
            # 2. 合并到训练数据
            self._merge_feedback_to_training(useful_samples)
            
            # 3. 更新训练数据文件
            save_json(self.training_data_path, self.training_data)
            
            # 4. 备份旧模型
            if TRAINING_CONFIG['backup_enabled']:
                self._backup_model()
            
            # 5. 重新创建Ollama模型
            success = self._recreate_ollama_model()
            
            # 6. 记录训练历史
            self._record_training_history(success, incremental, len(useful_samples))
            
            # 7. 清理已处理的反馈数据
            if success:
                self._clear_processed_feedback()
            
            if success:
                logger.info("🎉 训练成功完成！")
            else:
                logger.error("❌ 训练失败")
            
            return success
            
        except Exception as e:
            logger.error(f"训练异常: {str(e)}", exc_info=True)
            return False
    
    def _extract_useful_samples(self) -> List[Dict]:
        """提取有用的反馈样本"""
        try:
            useful = []
            
            # 提取错误预测的样本（作为修正样本）
            for feedback in self.feedback_data:
                if not feedback.get('is_correct', True):
                    actual = feedback.get('actual', {})
                    useful.append({
                        "input": feedback['input_text'],
                        "output": json.dumps({
                            "emotion": actual.get('emotion', feedback['predicted']['emotion']),
                            "intensity": actual.get('intensity', feedback['predicted']['intensity'])
                        }, ensure_ascii=False)
                    })
            
            # 添加一些正确的样本以保持多样性
            correct_samples = [f for f in self.feedback_data if f.get('is_correct', True)]
            sample_count = min(TRAINING_CONFIG['max_correct_samples'], len(correct_samples))
            
            if sample_count > 0 and correct_samples:
                useful.extend([{
                    "input": f['input_text'],
                    "output": json.dumps({
                        "emotion": f['predicted']['emotion'],
                        "intensity": f['predicted']['intensity']
                    }, ensure_ascii=False)
                } for f in random.sample(correct_samples, sample_count)])
            
            logger.debug(f"提取到 {len(useful)} 条有用样本")
            return useful
            
        except Exception as e:
            logger.error(f"提取样本失败: {str(e)}", exc_info=True)
            return []
    
    def _merge_feedback_to_training(self, samples: List[Dict]) -> None:
        """合并反馈样本到训练数据"""
        try:
            existing_inputs = set(item['input'] for item in self.training_data)
            added_count = 0
            
            for sample in samples:
                if sample['input'] not in existing_inputs:
                    self.training_data.append(sample)
                    existing_inputs.add(sample['input'])
                    added_count += 1
            
            logger.info(f"📊 新增 {added_count} 条训练样本，总计 {len(self.training_data)} 条")
            
        except Exception as e:
            logger.error(f"合并样本失败: {str(e)}", exc_info=True)
    
    def _backup_model(self) -> None:
        """备份当前模型"""
        try:
            backup_dir = self.training_data_path.parent / "model_backups"
            backup_path = backup_file(self.training_data_path, backup_dir)
            
            if backup_path:
                logger.info(f"📦 模型已备份到 {backup_path}")
            else:
                logger.warning("⚠️ 模型备份失败")
            
        except Exception as e:
            logger.error(f"备份模型失败: {str(e)}", exc_info=True)
    
    def _recreate_ollama_model(self) -> bool:
        """重新创建Ollama模型"""
        try:
            # 检查Ollama是否可用
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Ollama未安装或不可用")
                return False
            
            # 检查Modelfile是否存在
            if not self.modelfile_path.exists():
                logger.error(f"❌ Modelfile不存在: {self.modelfile_path}")
                return False
            
            # 停止旧模型（如果运行中）
            subprocess.run(["ollama", "stop", self.model_name], 
                         capture_output=True, text=True)
            
            # 删除旧模型
            subprocess.run(["ollama", "rm", self.model_name], 
                         capture_output=True, text=True)
            
            # 创建新模型
            logger.info(f"🔧 创建模型: {self.model_name}")
            result = subprocess.run(
                ["ollama", "create", self.model_name, "-f", str(self.modelfile_path)],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ 模型创建成功")
                return True
            else:
                logger.error(f"❌ 模型创建失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ 模型创建超时")
            return False
        except Exception as e:
            logger.error(f"❌ 模型创建异常: {str(e)}", exc_info=True)
            return False
    
    def _record_training_history(self, success: bool, incremental: bool, sample_count: int) -> None:
        """记录训练历史"""
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "type": "incremental" if incremental else "full",
                "success": success,
                "samples_added": sample_count,
                "total_samples": len(self.training_data),
                "previous_performance": self.current_performance,
                "notes": f"{'增量训练' if incremental else '完整训练'}，新增{sample_count}条样本"
            }
            
            self.training_history.append(record)
            save_json(self.training_history_path, self.training_history)
            
            logger.debug("训练记录已保存")
            
        except Exception as e:
            logger.error(f"记录训练历史失败: {str(e)}", exc_info=True)
    
    def _clear_processed_feedback(self) -> None:
        """清理已处理的反馈数据"""
        try:
            # 保留最近的一些反馈作为参考
            keep_count = TRAINING_CONFIG['max_feedback_to_keep']
            self.feedback_data = self.feedback_data[-keep_count:]
            save_json(self.feedback_data_path, self.feedback_data)
            logger.info(f"🧹 已清理已处理的反馈数据，保留 {len(self.feedback_data)} 条")
            
        except Exception as e:
            logger.error(f"清理反馈数据失败: {str(e)}", exc_info=True)
    
    def get_training_summary(self) -> Dict:
        """获取训练摘要"""
        try:
            recent_history = self.training_history[-5:] if self.training_history else []
            
            return {
                "model_name": self.model_name,
                "total_training_samples": len(self.training_data),
                "pending_feedback": len(self.feedback_data),
                "current_performance": self.current_performance,
                "training_history_count": len(self.training_history),
                "recent_training": recent_history,
                "threshold_settings": {
                    "min_feedback": self.min_feedback_threshold,
                    "performance": self.performance_threshold
                }
            }
        except Exception as e:
            logger.error(f"获取训练摘要失败: {str(e)}", exc_info=True)
            return {}
    
    def manual_trigger_training(self, incremental: bool = False) -> bool:
        """手动触发训练"""
        logger.info(f"👋 手动触发{'增量' if incremental else '完整'}训练...")
        return self._perform_training(incremental)
    
    def check_ollama_status(self) -> bool:
        """检查Ollama服务状态"""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"检查Ollama状态失败: {str(e)}")
            return False


# 全局训练器实例（单例模式）
_self_trainer: Optional[SelfTrainer] = None


def get_self_trainer() -> SelfTrainer:
    """获取全局自我训练器实例"""
    global _self_trainer
    if _self_trainer is None:
        _self_trainer = SelfTrainer()
    return _self_trainer


# 示例用法
if __name__ == "__main__":
    trainer = SelfTrainer()
    
    # 添加模拟反馈
    trainer.add_feedback(
        input_text="今天心情非常好！",
        predicted_emotion="喜悦",
        predicted_intensity=85.0,
        actual_emotion="喜悦",
        actual_intensity=90.0,
        is_correct=True
    )
    
    trainer.add_feedback(
        input_text="我很生气",
        predicted_emotion="悲伤",
        predicted_intensity=70.0,
        actual_emotion="愤怒",
        actual_intensity=85.0,
        is_correct=False,
        user_comment="模型误判了愤怒情绪"
    )
    
    # 获取训练摘要
    summary = trainer.get_training_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
