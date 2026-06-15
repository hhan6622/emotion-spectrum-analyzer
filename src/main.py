"""
情绪光谱仪 - 主入口文件

提供统一的应用启动入口，支持多种运行模式：
- Web UI模式（默认）
- 命令行模式
- 训练模式

使用方式：
    # 启动Web界面
    python main.py
    
    # 启动Web界面（指定端口）
    python main.py --port 7861
    
    # 命令行模式
    python main.py --cli "今天心情很好"
    
    # 检查服务状态
    python main.py --status
    
    # 手动触发训练
    python main.py --train

命令行参数：
    --help, -h          显示帮助信息
    --port, -p          指定端口（默认7861）
    --cli, -c           命令行模式，直接分析文本
    --status, -s        检查服务状态
    --train, -t         触发模型训练
    --incremental, -i   增量训练模式（配合--train使用）
    --debug, -d         调试模式，输出详细日志
"""

import argparse
import sys
from typing import Optional

from src.config import UI_CONFIG, VERSION_INFO
from src.logging_config import get_logger
from src.services import (
    ServiceFactory, 
    get_api_service, 
    get_self_trainer,
    get_service_status
)

# 获取日志记录器
logger = get_logger(__name__)


def print_banner():
    """打印应用启动横幅"""
    banner = f"""
╔════════════════════════════════════════════════════════════╗
║                    神经情绪光谱仪 v{VERSION_INFO['version']}                    ║
║                    {VERSION_INFO['description']}                     ║
║                    Build: {VERSION_INFO['build_date']}                     ║
╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_cli_mode(text: str):
    """
    命令行模式：直接分析文本情绪
    
    Args:
        text: 待分析的文本
    """
    print(f"\n🔍 分析文本: {text}")
    
    try:
        api_service = get_api_service()
        result = api_service.analyze_emotion(text)
        
        if result.get('success', False):
            emotion = result.get('emotion', '中性')
            intensity = result.get('intensity', 50)
            reason = result.get('reason', '')
            
            print(f"\n✅ 分析结果:")
            print(f"   情绪类型: {emotion}")
            print(f"   情绪强度: {intensity}%")
            print(f"   分析原因: {reason}")
        else:
            print(f"\n❌ 分析失败: {result.get('reason', '未知错误')}")
            
    except Exception as e:
        logger.error(f"命令行分析异常: {str(e)}", exc_info=True)
        print(f"\n❌ 分析异常: {str(e)}")


def check_services_status():
    """检查并打印所有服务状态"""
    print("\n" + get_service_status())
    
    status = ServiceFactory.check_all_services()
    all_ok = all(status.values())
    
    if all_ok:
        print("\n✅ 所有服务运行正常！")
    else:
        print("\n⚠️ 部分服务未就绪，请检查相关依赖")


def trigger_training(incremental: bool = False):
    """
    触发模型训练
    
    Args:
        incremental: 是否为增量训练
    """
    print(f"\n🚀 开始{'增量' if incremental else '完整'}训练...")
    
    try:
        trainer = get_self_trainer()
        success = trainer.manual_trigger_training(incremental=incremental)
        
        if success:
            print("🎉 训练成功！模型已完成自我迭代优化")
            
            # 打印训练摘要
            summary = trainer.get_training_summary()
            print("\n📊 训练摘要:")
            print(f"   训练样本数: {summary.get('total_training_samples', 0)}")
            print(f"   当前性能: {summary.get('current_performance', 0):.2%}")
        else:
            print("❌ 训练失败，请检查Ollama服务是否正常运行")
            
    except Exception as e:
        logger.error(f"训练异常: {str(e)}", exc_info=True)
        print(f"❌ 训练异常: {str(e)}")


def run_web_ui(port: Optional[int] = None):
    """
    启动Web UI界面
    
    Args:
        port: 服务器端口
    """
    # 延迟导入以加快启动速度
    from src.web_interface import EmotionUI
    
    print(f"\n🌐 启动Web界面...")
    print(f"   端口: {port or UI_CONFIG['server_port']}")
    print(f"   访问地址: http://localhost:{port or UI_CONFIG['server_port']}")
    
    try:
        app = EmotionUI()
        app.launch()
    except Exception as e:
        logger.error(f"启动Web界面失败: {str(e)}", exc_info=True)
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)


def main():
    """主函数：解析命令行参数并执行相应操作"""
    # 打印启动横幅
    print_banner()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="神经情绪光谱仪 - 多模态情绪分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python main.py                          # 启动Web界面（默认端口7861）
  python main.py -p 8080                  # 启动Web界面（端口8080）
  python main.py -c "今天心情很好"         # 命令行模式分析文本
  python main.py -s                       # 检查服务状态
  python main.py -t                       # 触发完整训练
  python main.py -t -i                    # 触发增量训练
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=UI_CONFIG['server_port'],
        help=f"指定Web服务端口（默认: {UI_CONFIG['server_port']}"
    )
    
    parser.add_argument(
        '--cli', '-c',
        type=str,
        help="命令行模式，直接分析文本"
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help="检查服务状态"
    )
    
    parser.add_argument(
        '--train', '-t',
        action='store_true',
        help="触发模型训练"
    )
    
    parser.add_argument(
        '--incremental', '-i',
        action='store_true',
        help="增量训练模式（配合--train使用）"
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help="调试模式，输出详细日志"
    )
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        import logging
        from src.config import LOG_CONFIG
        LOG_CONFIG['level'] = 'DEBUG'
        logger.setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    # 根据参数执行不同操作
    if args.cli:
        # 命令行模式
        run_cli_mode(args.cli)
        
    elif args.status:
        # 检查服务状态
        check_services_status()
        
    elif args.train:
        # 触发训练
        check_services_status()
        trigger_training(incremental=args.incremental)
        
    else:
        # 默认启动Web UI
        check_services_status()
        run_web_ui(port=args.port)


if __name__ == "__main__":
    main()