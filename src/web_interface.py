"""
情绪光谱仪 - Web界面模块

负责构建Gradio界面，包含：
- 用户认证（登录/注册）
- UI组件定义
- 事件绑定
- 业务逻辑调用

采用模块化设计，将UI组件与业务逻辑分离
"""

import gradio as gr
import datetime
import json
import os
import tempfile
from typing import Dict, Optional

from src.config import UI_CONFIG, ART_STYLES, EMOTIONS, TEMP_DIR
from src.visualization import EmotionVisualizer
from src.api_service import get_api_service, check_ollama_status
from src.self_trainer import get_self_trainer
from src.logging_config import get_logger
from src.utils import generate_filename, truncate_text
from src.database import DatabaseManager

# 获取日志记录器
logger = get_logger(__name__)


class UserAuthService:
    """
    用户认证服务类
    
    处理用户注册、登录和数据库操作
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
    
    def register(self, username: str, password: str, confirm_password: str, email: str = "") -> str:
        """注册新用户"""
        if not username or not password:
            return "❌ 用户名和密码不能为空"
        
        if password != confirm_password:
            return "❌ 两次输入的密码不一致"
        
        if len(password) < 6:
            return "❌ 密码长度至少需要6位"
        
        success = self.db.register_user(username, password, email)
        if success:
            return "✅ 注册成功！请登录"
        else:
            return "❌ 用户名已存在"
    
    def login(self, username: str, password: str) -> str:
        """用户登录"""
        if not username or not password:
            return "❌ 用户名和密码不能为空"
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            logger.info(f"用户登录成功: {username}")
            return f"✅ 欢迎回来, {username}！"
        else:
            return "❌ 用户名或密码错误"
    
    def logout(self) -> str:
        """用户退出"""
        self.current_user = None
        return "✅ 已退出登录"
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[dict]:
        """获取当前用户信息"""
        return self.current_user
    
    def get_user_history(self) -> list:
        """获取用户历史记录"""
        if self.current_user:
            return self.db.get_history(self.current_user['id'], limit=50)
        return []
    
    def add_user_history(self, input_text: str, emotion_result: Dict):
        """添加用户历史记录到数据库"""
        if self.current_user:
            emotion = emotion_result.get("emotion", "中性")
            intensity = emotion_result.get("intensity", 50)
            confidence = emotion_result.get("confidence", 0.8)
            
            self.db.add_history(
                user_id=self.current_user['id'],
                input_text=input_text,
                emotion_result=emotion,
                emotion_intensity=intensity,
                confidence=confidence
            )


class EmotionAnalysisService:
    """
    情绪分析业务服务类
    
    处理核心业务逻辑，与UI层解耦
    """
    
    def __init__(self):
        self.visualizer = EmotionVisualizer()
        self.api_service = get_api_service()
        self.trainer = get_self_trainer()
        self.user_auth = UserAuthService()
        self.last_analysis_result = None
        self.last_art_fig = None
        self.last_radar_fig = None
        self.temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
    
    def analyze_emotion(self, text: str, voice_input=None) -> Dict:
        """
        分析情绪（统一入口）
        
        Args:
            text: 文本输入
            voice_input: 语音输入
            
        Returns:
            分析结果字典
        """
        input_text = text if text else ""
        
        if voice_input is not None:
            input_text = "[语音输入] 语音情绪分析"
        
        if not input_text:
            return {"success": False, "message": "请输入分析数据"}
        
        # 调用API服务
        emotion_result = self.api_service.analyze_emotion(input_text)
        
        # 存储结果
        self.last_analysis_result = {
            "input_text": input_text,
            "emotion": emotion_result["emotion"],
            "intensity": emotion_result["intensity"]
        }
        
        # 如果用户已登录，保存到数据库
        if self.user_auth.is_logged_in():
            self.user_auth.add_user_history(input_text, emotion_result)
        
        return emotion_result
    
    def generate_visualizations(self, emotion_result: Dict, art_style: str):
        """
        生成可视化图表
        
        Args:
            emotion_result: 情绪分析结果
            art_style: 艺术风格
            
        Returns:
            雷达图和艺术光谱图
        """
        emotion = emotion_result.get("emotion", "中性")
        intensity = emotion_result.get("intensity", 50)
        
        # 创建情绪分数字典
        score_dict = {e: 0 for e in EMOTIONS}
        if emotion in score_dict:
            score_dict[emotion] = intensity / 100
        
        # 生成可视化
        radar_fig = self.visualizer.create_radar_chart(score_dict)
        art_fig = self.visualizer.generate_art_spectrum(score_dict, style=art_style)
        
        # 保存引用
        self.last_art_fig = art_fig
        self.last_radar_fig = radar_fig
        
        return radar_fig, art_fig
    
    def get_user_history(self):
        """获取用户历史记录（从数据库）"""
        return self.user_auth.get_user_history()
    
    def get_history_plot(self, history_data):
        """获取历史时序图"""
        # 将数据库历史格式转换为可视化所需格式
        history_records = []
        for record in history_data:
            emotion = record.get("emotion_result", "中性")
            intensity = record.get("emotion_intensity", 50)
            history_records.append({
                "timestamp": record.get("created_at", ""),
                "text": truncate_text(record.get("input_text", ""), max_length=50),
                "emotion": emotion,
                "intensity": intensity,
                "valence": intensity if emotion in ['喜悦', '惊讶'] else -intensity,
                "arousal": intensity
            })
        return self.visualizer.create_time_series(history_records)
    
    def export_data(self) -> str:
        """导出数据为JSON"""
        history_data = self.get_user_history()
        export_data = {
            "export_time": datetime.datetime.now().isoformat(),
            "record_count": len(history_data),
            "records": history_data
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    def submit_feedback(self, feedback_emotion: str, feedback_intensity: int, 
                        is_correct: bool, comment: str) -> str:
        """
        提交用户反馈
        
        Args:
            feedback_emotion: 用户反馈的情绪
            feedback_intensity: 用户反馈的强度
            is_correct: 是否正确
            comment: 用户备注
            
        Returns:
            反馈结果消息
        """
        if self.last_analysis_result is None:
            return "### ⚠️ 请先进行情绪分析"
        
        self.trainer.add_feedback(
            input_text=self.last_analysis_result["input_text"],
            predicted_emotion=self.last_analysis_result["emotion"],
            predicted_intensity=self.last_analysis_result["intensity"],
            actual_emotion=feedback_emotion,
            actual_intensity=feedback_intensity,
            is_correct=is_correct,
            user_comment=comment
        )
        
        return "### ✅ 反馈已提交\n\n您的反馈将用于模型的持续优化训练。"
    
    def get_trainer_summary(self) -> str:
        """获取训练器摘要"""
        summary = self.trainer.get_training_summary()
        return json.dumps(summary, ensure_ascii=False, indent=2)
    
    def trigger_training(self, incremental: bool) -> str:
        """触发训练"""
        success = self.trainer.manual_trigger_training(incremental=incremental)
        if success:
            return "### 🚀 训练成功！\n\n模型已完成自我迭代优化。"
        else:
            return "### ❌ 训练失败\n\n请检查Ollama服务是否正常运行。"
    
    def download_art_image(self) -> Optional[str]:
        """下载艺术光谱图"""
        if self.last_art_fig is not None:
            filename = generate_filename("emotion_art", ".png")
            filepath = os.path.join(self.temp_dir, filename)
            self.last_art_fig.savefig(filepath, format='png', dpi=150, 
                                     bbox_inches='tight', pad_inches=0)
            logger.info(f"艺术图片已保存: {filepath}")
            return filepath
        logger.warning("没有可下载的艺术图片")
        return None
    
    def download_radar_image(self) -> Optional[str]:
        """下载雷达图"""
        if self.last_radar_fig is not None:
            filename = generate_filename("emotion_radar", ".png")
            filepath = os.path.join(self.temp_dir, filename)
            self.last_radar_fig.savefig(filepath, format='png', dpi=150, 
                                       bbox_inches='tight', pad_inches=0)
            logger.info(f"雷达图片已保存: {filepath}")
            return filepath
        logger.warning("没有可下载的雷达图片")
        return None
    
    def download_history_json(self) -> Optional[str]:
        """下载历史记录JSON文件"""
        data = self.export_data()
        filename = generate_filename("emotion_history", ".json")
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        logger.info(f"历史记录已保存: {filepath}")
        return filepath
    
    def login(self, username: str, password: str) -> str:
        """用户登录"""
        return self.user_auth.login(username, password)
    
    def register(self, username: str, password: str, confirm_password: str, email: str = "") -> str:
        """用户注册"""
        return self.user_auth.register(username, password, confirm_password, email)
    
    def logout(self) -> str:
        """用户退出"""
        return self.user_auth.logout()
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.user_auth.is_logged_in()
    
    def get_current_username(self) -> str:
        """获取当前用户名"""
        user = self.user_auth.get_current_user()
        return user['username'] if user else "未登录"


class EmotionUI:
    """
    情绪分析UI组件类
    
    负责构建Gradio界面组件
    """
    
    def __init__(self):
        self.service = EmotionAnalysisService()
        self.css = self._get_custom_css()
    
    def _get_custom_css(self) -> str:
        """获取自定义CSS样式"""
        return """
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=Orbitron:wght@400;700&display=swap');
        
        body, .gradio-container {
            background: #0a0a0a !important;
            color: #00fff0 !important;
            font-family: 'Noto Sans SC', 'Orbitron', sans-serif !important;
        }

        .main-title {
            text-align: center;
            font-size: clamp(1.8rem, 5vw, 3.5rem) !important;
            background: linear-gradient(90deg, #00fff0, #ff00ff, #00fff0);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 3s linear infinite;
            text-shadow: 0 0 30px rgba(0, 255, 240, 0.3);
            margin: 20px 0 !important;
            font-weight: bold;
        }

        @keyframes shine {
            to { background-position: 200% center; }
        }

        .gr-button-primary {
            background: linear-gradient(45deg, #00fff0, #0080ff) !important;
            border: 2px solid #00fff0 !important;
            color: #0d0d0d !important;
            font-weight: bold !important;
            box-shadow: 0 0 15px #00fff0;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border-radius: 12px !important;
        }

        .gr-button-primary:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 0 30px #00fff0;
        }

        .gr-button-secondary {
            background: rgba(0, 255, 240, 0.08) !important;
            border: 1px solid #00fff0 !important;
            color: #00fff0 !important;
            border-radius: 12px !important;
        }

        .gr-box, .gr-input, .gr-panel, .gr-textbox, .gr-dropdown {
            background: rgba(15, 15, 15, 0.95) !important;
            border: 1px solid #00fff0 !important;
            border-radius: 12px !important;
            box-shadow: inset 0 0 15px rgba(0, 255, 240, 0.08);
        }

        .login-card {
            background: rgba(15, 15, 15, 0.98) !important;
            border: 2px solid #00fff0 !important;
            border-radius: 20px !important;
            box-shadow: 0 0 40px rgba(0, 255, 240, 0.2);
            padding: 30px !important;
        }

        footer { display: none !important; }

        @media (max-width: 768px) {
            .main-title { font-size: 1.5rem !important; }
            .gr-button { width: 100% !important; }
        }
        """
    
    def _create_auth_tab(self):
        """创建用户认证标签页"""
        with gr.Column(scale=1, elem_classes=["login-card"]):
            gr.Markdown("### 🔐 用户认证")
            
            # 用户名
            username = gr.Textbox(
                label="用户名",
                placeholder="请输入用户名",
                lines=1
            )
            
            # 密码
            password = gr.Textbox(
                label="密码",
                placeholder="请输入密码",
                type="password",
                lines=1
            )
            
            # 确认密码（注册时显示）
            confirm_password = gr.Textbox(
                label="确认密码",
                placeholder="请再次输入密码",
                type="password",
                lines=1,
                visible=False
            )
            
            # 邮箱（注册时显示）
            email = gr.Textbox(
                label="邮箱（可选）",
                placeholder="请输入邮箱地址",
                lines=1,
                visible=False
            )
            
            # 切换注册/登录模式
            with gr.Row():
                login_mode = gr.Radio(
                    choices=[("登录", "login"), ("注册", "register")],
                    label="操作类型",
                    value="login"
                )
            
            # 登录/注册按钮
            auth_btn = gr.Button("⚡ 执行", variant="primary", size="lg")
            
            # 状态输出
            auth_status = gr.Markdown("")
            
            # 用户状态显示
            user_status = gr.Markdown(f"当前用户: {self.service.get_current_username()}")
            
            # 退出按钮
            logout_btn = gr.Button("🚪 退出登录", variant="secondary", visible=False)
        
        return (username, password, confirm_password, email, login_mode, 
                auth_btn, auth_status, user_status, logout_btn)
    
    def _create_input_tab(self):
        """创建输入标签页"""
        with gr.Column(scale=1):
            gr.Markdown("### 📡 神经链路: 数据输入")
            
            text_input = gr.Textbox(
                label="文本输入", 
                placeholder="请输入您的情绪文本...",
                lines=5
            )
            
            voice_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 语音输入"
            )
            
            art_style = gr.Dropdown(
                choices=ART_STYLES,
                value="glitch",
                label="🎨 艺术风格"
            )
            
            analyze_btn = gr.Button("⚡ 执行神经扫描", variant="primary", size="lg")
            status_out = gr.Markdown("🟢 核心系统就绪")
        
        with gr.Column(scale=1):
            gr.Markdown("### 💎 情绪雷达图")
            radar_plot = gr.Plot(label="情绪分布")
            download_radar_btn = gr.Button("📥 下载雷达图", variant="secondary")
        
        return text_input, voice_input, art_style, analyze_btn, status_out, radar_plot, download_radar_btn
    
    def _create_art_tab(self):
        """创建艺术光谱标签页"""
        with gr.Column():
            gr.Markdown("### 🌌 艺术光谱输出")
            art_plot = gr.Plot(label="艺术光谱")
            download_art_btn = gr.Button("🖼️ 下载艺术图片", variant="primary")
            
            gr.Markdown("""
            ### 🎨 艺术风格说明
            
            | 风格 | 效果 |
            |------|------|
            | 🎭 故障艺术 | 经典数字故障效果 |
            | 🌊 流体渐变 | 柔和色彩流动 |
            | ⚡ 霓虹脉冲 | 赛博朋克风格 |
            | 🔲 赛博网格 | 数字网格矩阵 |
            | 🎨 粒子风暴 | 动态粒子效果 |
            | 🖌️ 水墨意境 | 东方水墨风格 |
            """)
        
        return art_plot, download_art_btn
    
    def _create_history_tab(self):
        """创建历史记录标签页"""
        with gr.Column():
            gr.Markdown("### 📊 情绪历史记录")
            gr.Markdown("登录后可查看个人历史记录")
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 刷新记录", variant="secondary")
            
            history_plot = gr.Plot(label="情绪时间序列")
            history_list = gr.JSON(label="详细记录")
        
        return refresh_btn, history_plot, history_list
    
    def _create_export_tab(self):
        """创建数据导出标签页"""
        with gr.Column():
            gr.Markdown("### 📤 数据导出中心")
            with gr.Row():
                export_btn = gr.Button("📥 导出JSON数据", variant="primary")
                download_btn = gr.Button("⬇️ 下载文件", variant="secondary")
            export_output = gr.Textbox(label="导出数据", lines=8, interactive=False)
        
        return export_btn, download_btn, export_output
    
    def _create_training_tab(self):
        """创建模型训练标签页"""
        with gr.Column():
            gr.Markdown("### 🧠 自我训练中心")
            gr.Markdown("""
            该模块实现了模型的持续自我训练和迭代优化功能：
            - **自动收集反馈**: 用户可以对分析结果进行反馈
            - **智能触发训练**: 当反馈积累到一定数量自动触发训练
            - **性能监控**: 持续监控模型准确率，自动迭代优化
            """)
            
            gr.Markdown("---")
            gr.Markdown("### 📝 反馈提交")
            
            feedback_emotion = gr.Dropdown(
                choices=EMOTIONS,
                label="实际情绪",
                value="喜悦"
            )
            feedback_intensity = gr.Slider(
                minimum=0, maximum=100, step=1, label="情绪强度", value=50
            )
            is_correct = gr.Radio(
                choices=[("✅ 分析正确", True), ("❌ 分析错误", False)],
                label="分析是否正确",
                value=True
            )
            feedback_comment = gr.Textbox(
                label="备注（可选）",
                placeholder="如有误判，请描述原因..."
            )
            submit_feedback_btn = gr.Button("📤 提交反馈", variant="primary")
            feedback_status = gr.Markdown("")
            
            gr.Markdown("---")
            gr.Markdown("### 📊 训练状态")
            trainer_summary = gr.Textbox(
                label="训练器状态",
                lines=8,
                interactive=False
            )
            refresh_summary_btn = gr.Button("🔄 刷新状态", variant="secondary")
            
            gr.Markdown("---")
            gr.Markdown("### 🚀 手动训练")
            with gr.Row():
                incremental_train_btn = gr.Button("🔄 增量训练", variant="secondary")
                full_train_btn = gr.Button("🔥 完整训练", variant="primary")
            train_status = gr.Markdown("")
        
        return (feedback_emotion, feedback_intensity, is_correct, feedback_comment,
                submit_feedback_btn, feedback_status, trainer_summary, 
                refresh_summary_btn, incremental_train_btn, full_train_btn, train_status)
    
    def _bind_events(self, username, password, confirm_password, email, login_mode,
                     auth_btn, auth_status, user_status, logout_btn,
                     text_input, voice_input, art_style, analyze_btn, status_out,
                     radar_plot, download_radar_btn, art_plot, download_art_btn,
                     refresh_btn, history_plot, history_list,
                     export_btn, download_btn, export_output,
                     feedback_emotion, feedback_intensity, is_correct, feedback_comment,
                     submit_feedback_btn, feedback_status, trainer_summary,
                     refresh_summary_btn, incremental_train_btn, full_train_btn, train_status):
        """绑定所有事件"""
        
        # 切换登录/注册模式
        def toggle_auth_mode(mode):
            show_extra = mode == "register"
            return gr.update(visible=show_extra), gr.update(visible=show_extra), \
                   gr.update(value="注册" if mode == "register" else "登录")
        
        login_mode.change(
            fn=toggle_auth_mode,
            inputs=[login_mode],
            outputs=[confirm_password, email, auth_btn]
        )
        
        # 登录/注册
        def handle_auth(username_val, password_val, confirm_password_val, email_val, mode):
            if mode == "login":
                result = self.service.login(username_val, password_val)
            else:
                result = self.service.register(username_val, password_val, confirm_password_val, email_val)
            
            logged_in = self.service.is_logged_in()
            return result, gr.update(value=self.service.get_current_username()), \
                   gr.update(visible=logged_in), gr.update(visible=not logged_in)
        
        auth_btn.click(
            fn=handle_auth,
            inputs=[username, password, confirm_password, email, login_mode],
            outputs=[auth_status, user_status, logout_btn, auth_btn]
        )
        
        # 退出登录
        def handle_logout():
            result = self.service.logout()
            return result, gr.update(value=self.service.get_current_username()), \
                   gr.update(visible=False), gr.update(visible=True)
        
        logout_btn.click(
            fn=handle_logout,
            outputs=[auth_status, user_status, logout_btn, auth_btn]
        )
        
        # 情绪分析
        def process_analysis(text, voice, style):
            # 分析情绪
            result = self.service.analyze_emotion(text, voice)
            
            if not result.get("success", True):
                return None, None, result.get("message", "分析失败"), []
            
            # 生成可视化
            radar_fig, art_fig = self.service.generate_visualizations(result, style)
            
            # 获取用户历史（从数据库）
            history_data = self.service.get_user_history()
            
            # 构建状态消息
            emotion = result.get("emotion", "中性")
            intensity = result.get("intensity", 50)
            reason = result.get("reason", "未知")
            status_msg = f"### 🟢 扫描完成: {emotion} (强度: {intensity}%)\n\n**分析原因:** {reason}"
            
            return radar_fig, art_fig, status_msg, history_data
        
        analyze_btn.click(
            fn=process_analysis,
            inputs=[text_input, voice_input, art_style],
            outputs=[radar_plot, art_plot, status_out, history_list]
        )
        
        download_art_btn.click(
            fn=self.service.download_art_image,
            outputs=gr.File()
        )
        
        download_radar_btn.click(
            fn=self.service.download_radar_image,
            outputs=gr.File()
        )
        
        # 刷新历史
        def refresh_history():
            history_data = self.service.get_user_history()
            plot = self.service.get_history_plot(history_data)
            return plot, history_data
        
        refresh_btn.click(
            fn=refresh_history,
            outputs=[history_plot, history_list]
        )
        
        export_btn.click(
            fn=self.service.export_data,
            outputs=export_output
        )
        
        download_btn.click(
            fn=self.service.download_history_json,
            outputs=gr.File()
        )
        
        submit_feedback_btn.click(
            fn=self.service.submit_feedback,
            inputs=[feedback_emotion, feedback_intensity, is_correct, feedback_comment],
            outputs=feedback_status
        )
        
        refresh_summary_btn.click(
            fn=self.service.get_trainer_summary,
            outputs=trainer_summary
        )
        
        incremental_train_btn.click(
            fn=lambda: self.service.trigger_training(incremental=True),
            outputs=train_status
        )
        
        full_train_btn.click(
            fn=lambda: self.service.trigger_training(incremental=False),
            outputs=train_status
        )
    
    def launch(self):
        """启动Gradio界面"""
        with gr.Blocks(title=UI_CONFIG['title']) as interface:
            gr.Markdown(f"# {UI_CONFIG['title']}", elem_classes=["main-title"])
            gr.Markdown(f"## {UI_CONFIG['subtitle']}", elem_classes=["main-title"])
            
            with gr.Tabs():
                # 用户认证标签页
                with gr.Tab("🔐 用户中心"):
                    with gr.Row():
                        auth_components = self._create_auth_tab()
                
                # 实时扫描标签页
                with gr.Tab("📊 实时扫描"):
                    with gr.Row():
                        input_components = self._create_input_tab()
                
                # 艺术光谱标签页
                with gr.Tab("🎨 艺术光谱"):
                    with gr.Row():
                        art_components = self._create_art_tab()
                
                # 历史记录标签页
                with gr.Tab("📝 历史记录"):
                    with gr.Row():
                        history_components = self._create_history_tab()
                
                # 数据导出标签页
                with gr.Tab("📤 数据导出"):
                    with gr.Row():
                        export_components = self._create_export_tab()
                
                # 模型训练标签页
                with gr.Tab("🧠 模型训练"):
                    with gr.Row():
                        training_components = self._create_training_tab()
            
            # 绑定事件
            self._bind_events(
                *auth_components,
                *input_components,
                *art_components,
                *history_components,
                *export_components,
                *training_components
            )
        
        interface.launch(
            server_port=UI_CONFIG['server_port'], 
            server_name=UI_CONFIG['server_name'],
            css=self.css
        )
