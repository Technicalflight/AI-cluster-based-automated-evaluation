<div align="center">
  <img src="logo.png"alt="AI 集群自动化评测系统 Logo" width="100">
  <p>AI 集群自动化评测系统</p>
  <h1>ai_cluster_evaluator</h1>
  <p>一款用于AI训练无监督评测工具-AI集群式自动化评测</p>  
</div>

# 🤖 AI 集群自动化评测系统

一个基于 PySide6 和 OpenAI API 的多模型集群自监督模型数据评测软件。

## 😊 功能特点

1. 现代化界面
   - 深色主题设计
   - 流畅的动画效果
   - 可拖拽的无边框窗口
   - 实时进度显示

2. 模型评测功能
   - 支持批量问题处理
   - 双重评测机制
   - 质量检查系统
   - 评分理由详细分析

3. 自定义设置
   - 可配置 OpenAI API 密钥和基础 URL
   - 可自定义各个模型（回答、评测、质检）
   - 支持自定义系统提示词（System Content）
   - 配置导入/导出功能

4. API 服务
   - 提供 RESTful API 接口
   - 支持远程调用
   - 完整的 API 文档
   - 可配置服务端口

## 安装要求

```bash
pip install -r requirements.txt
```

主要依赖：
- PySide6>=6.0.0
- openai>=1.0.0
- flask>=3.0.0
- requests>=2.31.0
- json5>=0.9.14
- typing-extensions>=4.7.1

## 📝 使用说明

### 基本使用

1. 启动程序
```bash
python ai_cluster_evaluator.py
```

2. 配置 API
   - 点击界面右上角的⚙️按钮
   - 输入 OpenAI API 密钥
   - 可选：配置自定义 API 基础 URL
   - 可选：自定义模型设置和系统提示词

3. 评测流程
   - 加载问题集（JSON 格式）
   - 点击"生成答案"
   - 点击"评测答案"（将进行两次独立评测）
   - 点击"质量检查"（对评测结果进行分析）
   - 保存结果

### 🎉 API 服务使用

1. 启动 API 服务
   - 点击界面右上角的🌐按钮
   - 设置端口号（默认 8000）
   - 点击"启动服务"

2. API 端点说明

#### 🤗 生成答案
```http
POST /generate
Content-Type: application/json

{
    "questions": {
        "q1": "问题1",
        "q2": "问题2",
        ...
    }
}
```

#### 😜 评测答案
```http
POST /evaluate
Content-Type: application/json

{
    "answers": {
        "q1": "答案1",
        "q2": "答案2",
        ...
    }
}
```

#### 😎 质量检查
```http
POST /quality-check
Content-Type: application/json

{
    "questions": {
        "q1": "问题1",
        "q2": "问题2",
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
```

### 🧐 数据格式

1. 问题集格式
```json
{
    "q1": "问题1的内容",
    "q2": "问题2的内容",
    "q3": "问题3的内容"
}
```

2. 评测结果格式
```json
{
    "questions": { ... },
    "answers": { ... },
    "evaluation_1": {
        "scores": {
            "q1": 4.5,
            "q2": 4.0,
            ...
        },
        "reasons": {
            "q1": "分析理由...",
            "q2": "分析理由...",
            ...
        }
    },
    "evaluation_2": { ... },
    "final_evaluation": {
        "scores": { ... },
        "reasons": { ... }
    }
}
```

## 📝 特性说明

1. 评分标准（0-5分）
   - 5分：完美的答案，准确、完整、清晰
   - 4分：很好的答案，有小的改进空间
   - 3分：基本合格的答案，但有明显缺陷
   - 2分：答案不够好，有重要内容缺失
   - 1分：答案质量差，大部分内容有问题
   - 0分：完全错误或文不对题

2. 质量检查机制
   - 自动生成标准答案
   - 分析评测员观点差异
   - 综合判断给出最终评分
   - 提供详细的分析理由

3. 错误处理
   - 自动重试机制
   - 详细的错误提示
   - 优雅的失败处理
   - 进度实时显示

## 注意事项

1. API 密钥安全
   - 请妥善保管 API 密钥
   - 可使用配置文件导入/导出功能
   - 支持自定义 API 基础 URL

2. 性能考虑
   - 大量请求时注意 API 限制
   - 建议批量处理时控制并发数
   - 注意网络连接稳定性

3. 使用建议
   - 定期保存评测结果
   - 适当调整系统提示词
   - 根据需要调整评分标准
   - 定期导出配置备份
  
## 🤝 贡献指南

作者个人能力和项目经验都还有许多不足，如果在使用过程遇到的Bug，欢迎提交 Issue 和 Pull Request 帮助改进项目。

## 免责声明

1. 开源许可
   - 本项目采用 BSD-3-Clause license 许可证开源
   - 您可以自由使用、修改和分发本项目
   - 请在使用时保留原作者版权信息

2. 使用责任
   - 本项目仅供学习和研究使用
   - 使用本项目所产生的任何后果由使用者自行承担
   - 作者不对使用本项目造成的任何损失负责

3. API 使用
   - 本项目使用 OpenAI API，您需要自行承担 API 使用费用
   - 请遵守 OpenAI 的使用条款和政策
   - 作者不对 API 的可用性和稳定性做任何保证

4. 数据安全
   - 请勿在本项目中使用敏感或机密数据
   - 用户需自行确保数据的安全性和合规性
   - 作者不对数据泄露或丢失承担责任

5. 商业使用
   - 如需商业使用，请确保符合相关法律法规
   - 商业使用所产生的风险由使用者自行承担
   - 建议在商业使用前寻求法律意见

6. 版权声明
   - 本项目的界面设计和代码实现版权归作者所有
   - 使用到的第三方库和框架的版权归其各自的所有者所有

7. 更新和维护
   - 作者不保证定期更新和维护本项目
   - 不保证本项目在所有环境下都能正常运行
   - 使用者可以根据需要自行修改和维护代码

8. 隐私政策
   - 本项目不会收集用户的个人信息
   - 所有的评测数据都存储在本地
   - API 密钥等敏感信息由用户自行管理

Copyright (c) 2024 [Technicalflight]

特此声明，任何个人或组织在使用本项目时均视为已经仔细阅读并同意本免责声明的所有条款。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Technicalflight/AI-cluster-based-automated-evaluation&type=Timeline)](https://star-history.com/#Technicalflight/AI-cluster-based-automated-evaluation&Timeline)

## 💖 支持作者

如果觉得项目对你有帮助，可以给项目点个Star，这将是对我最大的鼓励和支持！

<div align="center">
  <img src="alipay.jpg" alt="支付宝二维码" width="30%">
  <img src="wechat.jpg" alt="微信二维码" width="30%">
</div>
