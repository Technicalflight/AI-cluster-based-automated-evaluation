import sys
import json
from typing import Dict, List
import random
from PySide6.QtCore import Qt, QPoint, Property, QThread, Signal, QSize
from PySide6.QtGui import QMouseEvent, QColor, QFont, QPainter, QPainterPath, QLinearGradient, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QStackedWidget, QScrollArea, QTextEdit, QFileDialog, QSpinBox,
    QGraphicsDropShadowEffect, QMessageBox, QDialog, QLineEdit, QProgressDialog
)
from openai import OpenAI
import os

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 配置")
        self.resize(800, 600)  # 设置初始大小
        self.setMinimumSize(600, 400)  # 设置最小大小
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #34495e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        
        # Add import/export buttons at the top
        settings_layout = QHBoxLayout()
        import_btn = QPushButton("导入配置")
        import_btn.clicked.connect(self.import_settings)
        export_btn = QPushButton("导出配置")
        export_btn.clicked.connect(self.export_settings)
        settings_layout.addWidget(import_btn)
        settings_layout.addWidget(export_btn)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
        
        # OpenAI API Key
        openai_group = QFrame()
        openai_group.setObjectName("config-group")
        openai_layout = QVBoxLayout(openai_group)
        
        openai_title = QLabel("OpenAI 配置")
        openai_title.setObjectName("config-title")
        openai_layout.addWidget(openai_title)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        key_label.setFixedWidth(80)
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.Password)
        self.openai_key.setPlaceholderText("输入 OpenAI API key")
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.openai_key)
        openai_layout.addLayout(key_layout)
        
        # API Base URL input
        base_layout = QHBoxLayout()
        base_label = QLabel("API Base:")
        base_label.setFixedWidth(80)
        self.openai_base = QLineEdit()
        self.openai_base.setPlaceholderText("输入自定义 API base URL (可选)")
        current_base = os.getenv("OPENAI_API_BASE")
        if current_base:
            self.openai_base.setText(current_base)
        base_layout.addWidget(base_label)
        base_layout.addWidget(self.openai_base)
        openai_layout.addLayout(base_layout)
        
        # Model Selection and System Content
        models_group = QFrame()
        models_group.setObjectName("config-group")
        models_layout = QVBoxLayout(models_group)
        
        models_title = QLabel("模型配置")
        models_title.setObjectName("config-title")
        models_layout.addWidget(models_title)
        
        # Answer Model
        answer_group = QFrame()
        answer_group.setObjectName("model-group")
        answer_layout = QVBoxLayout(answer_group)
        
        answer_header = QHBoxLayout()
        answer_label = QLabel("回答模型:")
        answer_label.setFixedWidth(80)
        self.answer_model = QLineEdit()
        self.answer_model.setPlaceholderText("输入回答模型名称")
        current_answer_model = os.getenv("OPENAI_ANSWER_MODEL", "gpt-3.5-turbo")
        self.answer_model.setText(current_answer_model)
        answer_header.addWidget(answer_label)
        answer_header.addWidget(self.answer_model)
        answer_layout.addLayout(answer_header)
        
        answer_content_label = QLabel("System Content:")
        self.answer_content = QTextEdit()
        self.answer_content.setPlaceholderText("输入回答模型的system content（可选）")
        current_answer_content = os.getenv("OPENAI_ANSWER_CONTENT", "You are a helpful assistant that provides clear and concise answers.")
        self.answer_content.setText(current_answer_content)
        self.answer_content.setMaximumHeight(60)
        answer_layout.addWidget(answer_content_label)
        answer_layout.addWidget(self.answer_content)
        models_layout.addWidget(answer_group)
        
        # Evaluation Model
        eval_group = QFrame()
        eval_group.setObjectName("model-group")
        eval_layout = QVBoxLayout(eval_group)
        
        eval_header = QHBoxLayout()
        eval_label = QLabel("评测模型:")
        eval_label.setFixedWidth(80)
        self.eval_model = QLineEdit()
        self.eval_model.setPlaceholderText("输入评测模型名称")
        current_eval_model = os.getenv("OPENAI_EVAL_MODEL", "gpt-4")
        self.eval_model.setText(current_eval_model)
        eval_header.addWidget(eval_label)
        eval_header.addWidget(self.eval_model)
        eval_layout.addLayout(eval_header)
        
        eval_content_label = QLabel("System Content:")
        self.eval_content = QTextEdit()
        self.eval_content.setPlaceholderText("输入评测模型的system content（可选）")
        current_eval_content = os.getenv("OPENAI_EVAL_CONTENT", """你是一位专业的评测专家。请严格按照以下格式对答案进行评分。注意：你必须严格遵守格式要求，否则评分将被拒绝并要求重新评分。

格式要求：
1. 必需首先输出"[分析理由]"标记，后跟详细分析
2. 必须最后输出"[评分]"标记，后跟0-5之间的分数（可带一位小数）
3. 不允许输出任何其他格式的内容
4. 不允许更改标记的文字或格式

评分标准：
- 5分：完美的答案，准确、完整、清晰
- 4分：很好的答案，有小的改进空间
- 3分：基本合格的答案，但有明显缺陷
- 2分：答案不够好，有重要内容缺失
- 1分：答案质量差，大部分内容有问题
- 0分：完全错误或文不对题

分析要求：
1. 分析必须具体指出答案的优点和缺点
2. 分析必须与最终评分相符
3. 分析必须客观公正，有理有据

示例格式：
[分析理由]该答案结构清晰，论述准确，但在细节描述上略有不足。优点：1. 主要概念解释准确；2. 逻辑性强。缺点：1. 缺少具体示例；2. 部分专业术语解释不够详细。
[评分]4.5""")
        self.eval_content.setText(current_eval_content)
        self.eval_content.setMaximumHeight(60)
        eval_layout.addWidget(eval_content_label)
        eval_layout.addWidget(self.eval_content)
        models_layout.addWidget(eval_group)
        
        # Quality Check Model
        quality_group = QFrame()
        quality_group.setObjectName("model-group")
        quality_layout = QVBoxLayout(quality_group)
        
        quality_header = QHBoxLayout()
        quality_label = QLabel("质检模型:")
        quality_label.setFixedWidth(80)
        self.quality_model = QLineEdit()
        self.quality_model.setPlaceholderText("输入质检模型名称")
        current_quality_model = os.getenv("OPENAI_QUALITY_MODEL", "gpt-4")
        self.quality_model.setText(current_quality_model)
        quality_header.addWidget(quality_label)
        quality_header.addWidget(self.quality_model)
        quality_layout.addLayout(quality_header)
        
        quality_content_label = QLabel("System Content:")
        self.quality_content = QTextEdit()
        self.quality_content.setPlaceholderText("输入质检模型的system content（可选）")
        current_quality_content = os.getenv("OPENAI_QUALITY_CONTENT", """你是一位资深的质量控制专家。请严格按照以下格式对存在分歧的评分进行分析。注意：你必须严格遵守格式要求，否则分析将被拒绝并要求重新评分。

格式要求：
1. 必须首先输出"[分析理由]"标记，后跟详细分析
2. 必须最后输出"[评分]"标记，后跟0-5之间的分数（可带一位小数）
3. 不允许输出任何其他格式的内容
4. 不允许更改标记的文字或格式

分析要求：
1. 必需分析两位评分员的观点差异
2. 必须结合问题和答案进行综合判断
3. 必须给出详细的理由支持你的最终评分
4. 分析必须客观公正，有理有据

评分标准：
- 5分：完美的答案，准确、完整、清晰
- 4分：很好的答案，有小的改进空间
- 3分：基本合格的答案，但有明显缺陷
- 2分：答案不够好，有重要内容缺失
- 1分：答案质量差，大部分内容有问题
- 0分：完全错误或文不对题

示例格式：
[分析理由]评分员1给出4.5分，认为答案结构清晰但细节不足；评分员2给出3.5分，认为答案有明显疏漏。经过分析，我同意评分员1的观点，因为：1. 答案确实结构完整；2. 细节虽有不足但不影响整体质量；3. 评分员2对细节问题的考虑过重。
[评分]4.2""")
        self.quality_content.setText(current_quality_content)
        self.quality_content.setMaximumHeight(60)
        quality_layout.addWidget(quality_content_label)
        quality_layout.addWidget(self.quality_content)
        models_layout.addWidget(quality_group)
        
        layout.addWidget(openai_group)
        layout.addWidget(models_group)
        
        # 将内容添加到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area, 1)  # 1表示可以拉伸
        
        # Buttons at the bottom (在主布局中，不在滚动区域内)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)  # 增加上边距
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
        # 修改TextEdit的最大高度
        for text_edit in [self.answer_content, self.eval_content, self.quality_content]:
            text_edit.setMaximumHeight(80)  # 增加文本框高度
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #ecf0f1;
            }
            #config-group {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }
            #config-title {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel {
                color: #ecf0f1;
            }
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 5px;
                selection-background-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            #model-group {
                background-color: #1e2538;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def import_settings(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "导入配置", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # Load API settings
                    self.openai_key.setText(settings.get('openai_api_key', ''))
                    self.openai_base.setText(settings.get('openai_api_base', ''))
                    
                    # Load model settings
                    self.answer_model.setText(settings.get('answer_model', 'gpt-3.5-turbo'))
                    self.eval_model.setText(settings.get('eval_model', 'gpt-4'))
                    self.quality_model.setText(settings.get('quality_model', 'gpt-4'))
                    
                    # Load system contents
                    self.answer_content.setText(settings.get('answer_content', ''))
                    self.eval_content.setText(settings.get('eval_content', ''))
                    self.quality_content.setText(settings.get('quality_content', ''))
                    
                QMessageBox.information(self, "成功", "配置导入成功！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导入配置失败: {str(e)}")

    def export_settings(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "导出配置", "", "JSON Files (*.json)")
            if file_name:
                settings = {
                    'openai_api_key': self.openai_key.text(),
                    'openai_api_base': self.openai_base.text(),
                    'answer_model': self.answer_model.text(),
                    'eval_model': self.eval_model.text(),
                    'quality_model': self.quality_model.text(),
                    'answer_content': self.answer_content.toPlainText(),
                    'eval_content': self.eval_content.toPlainText(),
                    'quality_content': self.quality_content.toPlainText()
                }
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", "配置导出成功！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出配置失败: {str(e)}")

class AIButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self._animation_progress = 0
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        if self.isDown():
            gradient.setColorAt(0, QColor(41, 128, 185))
            gradient.setColorAt(1, QColor(44, 62, 80))
        else:
            gradient.setColorAt(0, QColor(52, 152, 219))
            gradient.setColorAt(1, QColor(41, 128, 185))

        # Draw rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        painter.fillPath(path, gradient)

        # Draw text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class AITextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #3498db;
            }
            QScrollBar:vertical {
                border: none;
                background: #34495e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.setFont(QFont("Consolas", 10))

class ModelThread(QThread):
    result_ready = Signal(dict)
    error_occurred = Signal(str)
    progress_updated = Signal(int)  # 新增进度信号

    def __init__(self, input_data: dict, model_type: str):
        super().__init__()
        self.input_data = input_data
        self.model_type = model_type
        self.openai_client = None
        self.result = None  # 添加result属性
        self.setup_clients()

    def setup_clients(self):
        try:
            # Initialize OpenAI client with custom base URL
            openai_api_key = os.getenv("OPENAI_API_KEY")
            openai_api_base = os.getenv("OPENAI_API_BASE")
            
            if openai_api_key:
                client_args = {"api_key": openai_api_key}
                if openai_api_base:
                    client_args["base_url"] = openai_api_base
                self.openai_client = OpenAI(**client_args)
        except Exception as e:
            self.error_occurred.emit(f"Error setting up API clients: {str(e)}")

    def run(self):
        try:
            if not self.openai_client:
                self.error_occurred.emit("API client not initialized. Please set up API keys.")
                return

            if self.model_type == "answer":
                self.result = self.generate_answers()
            elif self.model_type == "evaluate":
                self.result = self.evaluate_answers()
            elif self.model_type == "quality":
                self.result = self.quality_check()
            self.result_ready.emit(self.result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def wait(self) -> None:
        super().wait()
        return self.result  # 返回结果

    def generate_answers(self) -> dict:
        answers = {}
        try:
            model_name = os.getenv("OPENAI_ANSWER_MODEL", "gpt-3.5-turbo")
            system_content = os.getenv("OPENAI_ANSWER_CONTENT", "You are a helpful assistant that provides clear and concise answers.")
            total = len(self.input_data)
            for i, (qid, question) in enumerate(self.input_data.items(), 1):
                completion = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": question}
                    ]
                )
                answers[qid] = completion.choices[0].message.content
                self.progress_updated.emit(int(i * 100 / total))
        except Exception as e:
            self.error_occurred.emit(f"Error generating answers: {str(e)}")
        return answers

    def evaluate_answers(self) -> dict:
        scores = {}
        reasons = {}
        try:
            model_name = os.getenv("OPENAI_EVAL_MODEL", "gpt-4")
            system_content = os.getenv("OPENAI_EVAL_CONTENT", """你是一位专业的评测专家。请严格按照以下格式对答案进行评分。注意：你必须严格遵守格式要求，否则评分将被拒绝并要求重新评分。

格式要求：
1. 必须首先输出"[分析理由]"标记，后跟详细分析
2. 必须最后输出"[评分]"标记，后跟0-5之间的分数（可带一位小数）
3. 不允许输出任何其他格式的内容
4. 不允许更改标记的文字或格式

评分标准：
- 5分：完美的答案，准确、完整、清晰
- 4分：很好的答案，有小的改进空间
- 3分：基本合格的答案，但有明显缺陷
- 2分：答案不够好，有重要内容缺失
- 1分：答案质量差，大部分内容有问题
- 0分：完全错误或文不对题

分析要求：
1. 分析必须具体指出答案的优点和缺点
2. 分析必须与最终评分相符
3. 分析必须客观公正，有理有据

示例格式：
[分析理由]该答案结构清晰，论述准确，但在细节描述上略有不足。优点：1. 主要概念解释准确；2. 逻辑性强。缺点：1. 缺少具体示例；2. 部分专业术语解释不够详细。
[评分]4.5""")
            total = len(self.input_data)
            for i, (qid, answer) in enumerate(self.input_data.items(), 1):
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    completion = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_content},
                            {"role": "user", "content": f"需要评分的答案: {answer}"}
                        ]
                    )
                    response = completion.choices[0].message.content.strip()
                    try:
                        if '[分析理由]' in response and '[评分]' in response:
                            reason = response.split('[评分]')[0].replace('[分析理由]', '').strip()
                            score_text = response.split('[评分]')[1].strip()
                            score = float(score_text)
                            if 0 <= score <= 5:
                                scores[qid] = score
                                reasons[qid] = reason
                                break
                        retry_count += 1
                        if retry_count == max_retries:
                            scores[qid] = 2.5
                            reasons[qid] = "多次评分格式错误，使用默认分数"
                    except ValueError:
                        retry_count += 1
                        if retry_count == max_retries:
                            scores[qid] = 2.5
                            reasons[qid] = "多次评分格式错误，使用默认分数"
                self.progress_updated.emit(int(i * 100 / total))
        except Exception as e:
            self.error_occurred.emit(f"评测过程出错: {str(e)}")
        return {"scores": scores, "reasons": reasons}

    def quality_check(self) -> dict:
        final_scores = {}
        reasons = {}
        try:
            model_name = os.getenv("OPENAI_QUALITY_MODEL", "gpt-4")
            system_content = os.getenv("OPENAI_QUALITY_CONTENT", """你是一位资深的质量控制专家。请严格按照以下格式对存在分歧的评分进行分析。注意：你必须严格遵守格式要求，否则分析将被拒绝并要求重新评分。

格式要求：
1. 必须首先输出"[分析理由]"标记，后跟详细分析
2. 必须最后输出"[评分]"标记，后跟0-5之间的分数（可带一位小数）
3. 不允许输出任何其他格式的内容
4. 不允许更改标记的文字或格式

分析要求：
1. 必须分析两位评分员的观点差异
2. 必须结合问题和答案进行综合判断
3. 必须给出详细的理由支持你的最终评分
4. 分析必须客观公正，有理有据

评分标准：
- 5分：完美的答案，准确、完整、清晰
- 4分：很好的答案，有小的改进空间
- 3分：基本合格的答案，但有明显缺陷
- 2分：答案不够好，有重要内容缺失
- 1分：答案质量差，大部分内容有问题
- 0分：完全错误或文不对题

示例格式：
[分析理由]评分员1给出4.5分，认为答案结构清晰但细节不足；评分员2给出3.5分，认为答案有明显疏漏。经过分析，我同意评分员1的观点，因为：1. 答案确实结构完整；2. 细节虽有不足但不影响整体质量；3. 评分员2对细节问题的考虑过重。
[评分]4.2""")
            questions = self.input_data['questions']
            answers = self.input_data['answers']
            scores1 = self.input_data['scores1']['scores']
            scores2 = self.input_data['scores2']['scores']
            reasons1 = self.input_data['scores1']['reasons']
            reasons2 = self.input_data['scores2']['reasons']

            total = len(questions)
            for i, qid in enumerate(questions, 1):
                score1 = scores1[qid]
                score2 = scores2[qid]
                if abs(score1 - score2) < 0.5:
                    final_scores[qid] = (score1 + score2) / 2
                    reasons[qid] = f"评分接近，取平均值。\n评分1原因：{reasons1[qid]}\n评分2原因：{reasons2[qid]}"
                else:
                    max_retries = 3
                    retry_count = 0
                    while retry_count < max_retries:
                        completion = self.openai_client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_content},
                                {"role": "user", "content": f"Question: {questions[qid]}\nAnswer: {answers[qid]}\nScore 1: {score1} (Reason: {reasons1[qid]})\nScore 2: {score2} (Reason: {reasons2[qid]})\nAnalyze the scores and provide your final score with reasoning."}
                            ]
                        )
                        response = completion.choices[0].message.content.strip()
                        try:
                            if '[分析理由]' in response and '[评分]' in response:
                                reason = response.split('[评分]')[0].replace('[分析理由]', '').strip()
                                score_text = response.split('[评分]')[1].strip()
                                score = float(score_text)
                                if 0 <= score <= 5:
                                    final_scores[qid] = score
                                    reasons[qid] = f"质检分析：{reason}\n原评分1原因：{reasons1[qid]}\n原评分2原因：{reasons2[qid]}"
                                    break
                            retry_count += 1
                            if retry_count == max_retries:
                                final_scores[qid] = (score1 + score2) / 2
                                reasons[qid] = "多次质检格式错误，取平均值"
                        except ValueError:
                            retry_count += 1
                            if retry_count == max_retries:
                                final_scores[qid] = (score1 + score2) / 2
                                reasons[qid] = "多次质检格式错误，取平均值"
                self.progress_updated.emit(int(i * 100 / total))
        except Exception as e:
            self.error_occurred.emit(f"Error in quality check: {str(e)}")
        return {"scores": final_scores, "reasons": reasons}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1200, 800)

        self._drag_pos = None
        self.current_data = {}
        self.setup_ui()
        self.check_api_keys()
        
        # 创建进度条
        self.progress = QProgressDialog(self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setWindowTitle("处理中")
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressDialog {
                background-color: #1a1a2e;
                color: #ecf0f1;
            }
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                background-color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
                margin: 0.5px;
            }
        """)

    def check_api_keys(self):
        if not os.getenv("OPENAI_API_KEY"):
            self.show_api_key_dialog()

    def show_api_key_dialog(self):
        dialog = APIKeyDialog(self)
        if dialog.exec():
            # Save API keys and base URL to environment variables
            os.environ["OPENAI_API_KEY"] = dialog.openai_key.text()
            if dialog.openai_base.text().strip():
                os.environ["OPENAI_API_BASE"] = dialog.openai_base.text().strip()
            elif "OPENAI_API_BASE" in os.environ:
                del os.environ["OPENAI_API_BASE"]
            
            # Save model configurations
            os.environ["OPENAI_ANSWER_MODEL"] = dialog.answer_model.text().strip()
            os.environ["OPENAI_EVAL_MODEL"] = dialog.eval_model.text().strip()
            os.environ["OPENAI_QUALITY_MODEL"] = dialog.quality_model.text().strip()
            
            # Save system contents
            os.environ["OPENAI_ANSWER_CONTENT"] = dialog.answer_content.toPlainText().strip()
            os.environ["OPENAI_EVAL_CONTENT"] = dialog.eval_content.toPlainText().strip()
            os.environ["OPENAI_QUALITY_CONTENT"] = dialog.quality_content.toPlainText().strip()
        else:
            QMessageBox.warning(self, "警告", "需要配置API才能正常使用程序。")

    def setup_ui(self):
        # Main layout with dark theme background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create main container with rounded corners and gradient background
        container = QFrame(self)
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Title bar with AI-style design
        title_bar = QFrame()
        title_bar.setObjectName("title-bar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        # AI Icon and Title
        title_layout.addWidget(QLabel("🤖"), 0)
        title = QLabel("AI 模型评测系统")
        title.setObjectName("title")
        title_layout.addWidget(title, 1)
        
        # Add settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("window-button")
        settings_btn.setToolTip("设置")
        settings_btn.clicked.connect(self.show_api_key_dialog)
        
        # Add API server button
        api_server_btn = QPushButton("🌐")
        api_server_btn.setObjectName("window-button")
        api_server_btn.setToolTip("API服务")
        api_server_btn.clicked.connect(self.show_api_server_dialog)
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        controls_layout.addWidget(settings_btn)
        controls_layout.addWidget(api_server_btn)
        
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("window-button")
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("window-button")
        close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(close_btn)
        title_layout.addLayout(controls_layout)
        
        container_layout.addWidget(title_bar)

        # Content area
        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Split view for input and output
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # Left panel - Input
        input_panel = QFrame()
        input_panel.setObjectName("panel")
        input_layout = QVBoxLayout(input_panel)
        
        input_header = QLabel("输入问题")
        input_header.setObjectName("panel-header")
        input_layout.addWidget(input_header)

        self.input_text = AITextEdit()
        self.input_text.setPlaceholderText("在此输入JSON格式的问题...")
        input_layout.addWidget(self.input_text)

        load_btn = AIButton("加载问题")
        load_btn.clicked.connect(self.load_questions)
        input_layout.addWidget(load_btn)

        split_layout.addWidget(input_panel)

        # Right panel - Output
        output_panel = QFrame()
        output_panel.setObjectName("panel")
        output_layout = QVBoxLayout(output_panel)
        
        output_header = QLabel("评测结果")
        output_header.setObjectName("panel-header")
        output_layout.addWidget(output_header)

        self.output_text = AITextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("结果将在此显示...")
        output_layout.addWidget(self.output_text)

        save_btn = AIButton("保存结果")
        save_btn.clicked.connect(self.save_results)
        output_layout.addWidget(save_btn)

        split_layout.addWidget(output_panel)
        content_layout.addLayout(split_layout)

        # Process controls
        process_layout = QHBoxLayout()
        process_layout.setSpacing(15)

        generate_btn = AIButton("生成答案")
        generate_btn.clicked.connect(self.generate_answers)
        process_layout.addWidget(generate_btn)

        evaluate_btn = AIButton("评测答案")
        evaluate_btn.clicked.connect(self.evaluate_answers)
        process_layout.addWidget(evaluate_btn)

        quality_btn = AIButton("质量检查")
        quality_btn.clicked.connect(self.quality_check)
        process_layout.addWidget(quality_btn)

        content_layout.addLayout(process_layout)
        container_layout.addWidget(content)
        
        # Add container to main layout
        main_layout.addWidget(container)
        
        # Apply shadow effect to container
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)

        self.setStyleSheet(self.get_stylesheet())

    def load_questions(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "加载问题", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保显示为UTF-8格式
                    formatted_data = {}
                    for key, value in data.items():
                        formatted_data[key] = value
                    self.current_data = {'questions': formatted_data}
                    self.input_text.setText(json.dumps(formatted_data, ensure_ascii=False, indent=2))
        except Exception as e:
            self.output_text.setText(f"加载文件出错: {str(e)}")

    def generate_answers(self):
        if not self.current_data.get('questions'):
            self.output_text.setText("请先加载问题。")
            return

        # 设置进度条
        self.progress.setLabelText("正在生成答案...")
        self.progress.setValue(0)
        self.progress.show()

        self.thread = ModelThread(self.current_data['questions'], "answer")
        self.thread.result_ready.connect(self.handle_answers)
        self.thread.error_occurred.connect(self.handle_error)
        
        # 更新进度条
        def update_progress(value):
            self.progress.setValue(value)
        
        self.thread.progress_updated.connect(update_progress)
        self.thread.start()

    def evaluate_answers(self):
        if not self.current_data.get('answers'):
            self.output_text.setText("请先生成答案。")
            return

        # 设置进度条
        self.progress.setLabelText("正在评测答案...")
        self.progress.setValue(0)
        self.progress.show()

        self.eval_thread1 = ModelThread(self.current_data['answers'], "evaluate")
        self.eval_thread2 = ModelThread(self.current_data['answers'], "evaluate")
        
        self.eval_thread1.result_ready.connect(lambda x: self.handle_evaluation(x, 1))
        self.eval_thread2.result_ready.connect(lambda x: self.handle_evaluation(x, 2))
        self.eval_thread1.error_occurred.connect(self.handle_error)
        self.eval_thread2.error_occurred.connect(self.handle_error)
        
        # 更新进度条
        def update_progress(value):
            self.progress.setValue(value // 2)  # 两个线程各占50%进度
        
        self.eval_thread1.progress_updated.connect(update_progress)
        self.eval_thread2.progress_updated.connect(lambda x: update_progress(x + 50))
        
        self.eval_thread1.start()
        self.eval_thread2.start()

    def quality_check(self):
        if not all(k in self.current_data for k in ['questions', 'answers', 'scores1', 'scores2']):
            self.output_text.setText("请先完成评测。")
            return

        # 设置进度条
        self.progress.setLabelText("正在进行质量检查...")
        self.progress.setValue(0)
        self.progress.show()

        self.thread = ModelThread(self.current_data, "quality")
        self.thread.result_ready.connect(self.handle_quality)
        self.thread.error_occurred.connect(self.handle_error)
        
        # 更新进进度条
        def update_progress(value):
            self.progress.setValue(value)
        
        self.thread.progress_updated.connect(update_progress)
        self.thread.start()

    def handle_answers(self, result):
        self.current_data['answers'] = result
        self.output_text.setText(json.dumps(result, ensure_ascii=False, indent=2))
        self.progress.hide()

    def handle_evaluation(self, result, evaluator_num):
        self.current_data[f'scores{evaluator_num}'] = result
        current_text = self.output_text.toPlainText()
        formatted_output = []
        for qid, score in result['scores'].items():
            reason = result['reasons'][qid]
            formatted_output.append(f"问题 {qid}:\n分数: {score}\n原因: {reason}\n")
        
        self.output_text.setText(f"{current_text}\n\n评测员 {evaluator_num} 评分:\n" + "\n".join(formatted_output))
        if evaluator_num == 2:  # 当两个评测都完成时
            self.progress.hide()

    def handle_quality(self, result):
        self.current_data['final_scores'] = result
        formatted_output = []
        for qid, score in result['scores'].items():
            reason = result['reasons'][qid]
            formatted_output.append(f"问题 {qid}:\n最终分数: {score}\n分析过程:\n{reason}\n")
        
        self.output_text.setText("质量检查结果:\n" + "\n".join(formatted_output))
        self.progress.hide()

    def handle_error(self, error_msg):
        self.output_text.setText(f"错误: {error_msg}")
        self.progress.hide()

    def save_results(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "保存结果", "", "JSON Files (*.json)")
            if file_name:
                # 格式化保存数据，包含所有评分和原因
                save_data = {
                    "questions": self.current_data['questions'],
                    "answers": self.current_data['answers'],
                    "evaluation_1": self.current_data['scores1'],
                    "evaluation_2": self.current_data['scores2'],
                    "final_evaluation": self.current_data['final_scores']
                }
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.output_text.setText(f"保存文件出错: {str(e)}")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def get_stylesheet(self):
        return """
        QWidget {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            color: #ecf0f1;
        }
        
        #container {
            background-color: #1a1a2e;
            border-radius: 15px;
        }
        
        #title-bar {
            background-color: #16213e;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            border-bottom: 1px solid #2c3e50;
        }
        
        #title {
            color: #ecf0f1;
            font-size: 18px;
            font-weight: bold;
        }
        
        #window-button {
            background-color: transparent;
            border: none;
            color: #ecf0f1;
            font-size: 16px;
            padding: 5px 10px;
            border-radius: 4px;
        }
        
        #window-button:hover {
            background-color: #2c3e50;
        }
        
        #content {
            background-color: #1a1a2e;
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;
        }
        
        #panel {
            background-color: #16213e;
            border-radius: 10px;
            padding: 15px;
        }
        
        #panel-header {
            color: #3498db;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #2c3e50;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background: #3498db;
            border-radius: 5px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QFileDialog {
            background-color: #1a1a2e;
            color: #ecf0f1;
        }
        
        QFileDialog QLabel {
            color: #ecf0f1;
        }
        
        QFileDialog QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
        }
        
        QFileDialog QPushButton:hover {
            background-color: #2980b9;
        }
        """

    def show_api_server_dialog(self):
        dialog = APIServerDialog(self)
        dialog.exec_()

class APIServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 服务配置")
        self.resize(600, 400)
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Server Status
        status_group = QFrame()
        status_group.setObjectName("config-group")
        status_layout = QVBoxLayout(status_group)
        
        status_title = QLabel("服务状态")
        status_title.setObjectName("config-title")
        status_layout.addWidget(status_title)
        
        status_info = QHBoxLayout()
        self.status_label = QLabel("状态：未运行")
        self.port_label = QLabel("端口：-")
        status_info.addWidget(self.status_label)
        status_info.addWidget(self.port_label)
        status_layout.addLayout(status_info)
        
        # Server Controls
        controls_layout = QHBoxLayout()
        
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(8000)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        
        self.start_btn = QPushButton("启动服务")
        self.start_btn.clicked.connect(self.toggle_server)
        
        controls_layout.addLayout(port_layout)
        controls_layout.addWidget(self.start_btn)
        status_layout.addLayout(controls_layout)
        
        # API Documentation
        docs_group = QFrame()
        docs_group.setObjectName("config-group")
        docs_layout = QVBoxLayout(docs_group)
        
        docs_title = QLabel("API 文档")
        docs_title.setObjectName("config-title")
        docs_layout.addWidget(docs_title)
        
        docs_text = QTextEdit()
        docs_text.setReadOnly(True)
        docs_text.setPlaceholderText("API 文档将在服务启动后显示...")
        docs_text.setText("""
API 端点：

1. 生成答案
POST /generate
请求体：
{
    "questions": {
        "question_id": "问题内容",
        ...
    }
}

2. 评测答案
POST /evaluate
请求体：
{
    "answers": {
        "answer_id": "答案内容",
        ...
    }
}

3. 质量检查
POST /quality-check
请求体：
{
    "questions": {
        "question_id": "问题内容",
        ...
    },
    "evaluation_1": {
        "scores": { ... },
        "reasons": { ... }
    },
    "evaluation_2": {
        "scores": { ... },
        "reasons": { ... }
    }
}

所有响应格式均为 JSON，包含状态码和数据：
{
    "status": "success/error",
    "data": {
        "answers": {
            "answer_id": "生成的答案内容",
            ...
        },
        "scores": {
            "answer_id": 分数,
            ...
        },
        "reasons": {
            "answer_id": "分析理由",
            ...
        }
    }
}
        """)
        docs_layout.addWidget(docs_text)
        
        layout.addWidget(status_group)
        layout.addWidget(docs_group)
        
        # Close button
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.server_thread = None
        self.server_running = False
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #ecf0f1;
            }
            #config-group {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }
            #config-title {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QSpinBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        from flask import Flask, request, jsonify
        import threading
        
        app = Flask(__name__)
        
        @app.route('/generate', methods=['POST'])
        def generate():
            try:
                data = request.get_json()
                thread = ModelThread(data['questions'], "answer")
                thread.start()
                result = thread.wait()  # 等待并获取结果
                if result is None:
                    return jsonify({"status": "error", "message": "Failed to generate answers"}), 500
                return jsonify({"status": "success", "data": result})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 400
        
        @app.route('/evaluate', methods=['POST'])
        def evaluate():
            try:
                data = request.get_json()
                # 创建两个评测线程
                thread1 = ModelThread(data['answers'], "evaluate")
                thread2 = ModelThread(data['answers'], "evaluate")
                
                # 启动两个线程
                thread1.start()
                thread2.start()
                
                # 等待并获取两个评测结果
                result1 = thread1.wait()
                result2 = thread2.wait()
                
                if result1 is None or result2 is None:
                    return jsonify({
                        "status": "error", 
                        "message": "Failed to evaluate answers"
                    }), 500
                
                # 返回两个评测结果
                return jsonify({
                    "status": "success", 
                    "data": {
                        "evaluation_1": result1,
                        "evaluation_2": result2
                    }
                })
            except Exception as e:
                return jsonify({
                    "status": "error", 
                    "message": str(e)
                }), 400
        
        @app.route('/quality-check', methods=['POST'])
        def quality_check():
            try:
                data = request.get_json()
                
                # 验证必要的数据是否存在
                required_fields = ['questions', 'evaluation_1', 'evaluation_2']
                if not all(field in data for field in required_fields):
                    return jsonify({
                        "status": "error",
                        "message": f"Missing required fields. Need: {', '.join(required_fields)}"
                    }), 400
                
                # 首先根据问题生成答案
                answer_thread = ModelThread(data['questions'], "answer")
                answer_thread.start()
                answers = answer_thread.wait()
                
                if answers is None:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to generate answers"
                    }), 500
                
                # 重新组织数据结构以匹配质量检查的处理逻辑
                check_data = {
                    'questions': data['questions'],
                    'answers': answers,
                    'scores1': data['evaluation_1'],
                    'scores2': data['evaluation_2']
                }
                
                # 进行质量检查
                thread = ModelThread(check_data, "quality")
                thread.start()
                result = thread.wait()
                
                if result is None:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to perform quality check"
                    }), 500
                
                # 返回质检结果，包含生成的答案
                return jsonify({
                    "status": "success",
                    "data": {
                        "answers": answers,  # 包含生成的答案
                        "scores": result["scores"],
                        "reasons": result["reasons"]
                    }
                })
            except KeyError as e:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {str(e)}"
                }), 400
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400
        
        # 添加关闭服务器的路由
        @app.route('/shutdown', methods=['GET'])
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                return jsonify({"status": "error", "message": "Not running with werkzeug server"}), 500
            func()
            return jsonify({"status": "success", "message": "Server shutting down..."})
        
        def run_server():
            app.run(host='0.0.0.0', port=self.port_input.value())
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.server_running = True
        self.status_label.setText("状态：运行中")
        self.port_label.setText(f"端口：{self.port_input.value()}")
        self.start_btn.setText("停止服务")
        self.port_input.setEnabled(False)

    def stop_server(self):
        if self.server_thread:
            # 在这里添加停止服务器的逻辑
            import requests
            try:
                requests.get(f"http://localhost:{self.port_input.value()}/shutdown")
            except:
                pass
            
            self.server_thread = None
            self.server_running = False
            self.status_label.setText("状态：未运行")
            self.port_label.setText("端口：-")
            self.start_btn.setText("启动服务")
            self.port_input.setEnabled(True)

    def closeEvent(self, event):
        if self.server_running:
            self.stop_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
