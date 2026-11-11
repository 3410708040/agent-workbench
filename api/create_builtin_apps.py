"""
创建内置 AI 应用：文档格式转换
"""
import sys
import os
import uuid

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.http.app import app
from pkg.sqlalchemy import SQLAlchemy
from internal.model.app import App, AppConfig
from internal.model.account import Account

def create_builtin_apps():
    with app.app_context():
        # 获取 db 实例
        db = app.extensions['sqlalchemy']
        
        # 1. 获取当前用户账号（用第一个用户）
        account = Account.query.first()
        if not account:
            print("❌ 没有找到用户账号，请先登录一次")
            return
        
        print(f"✅ 使用账号: {account.email} (ID: {account.id})")
        
        # 2. 创建文档格式转换应用
        app_id = uuid.uuid4()
        
        # 检查是否已经存在
        existing_app = App.query.filter_by(name="文档格式转换").first()
        if existing_app:
            print(f"⚠️ 文档格式转换应用已存在，ID: {existing_app.id}")
            return
        
        # 创建 App 记录
        doc_converter_app = App(
            id=app_id,
            account_id=account.id,
            name="文档格式转换",
            icon="📄",
            description="支持 Markdown ↔ HTML ↔ 纯文本格式互转，内置常用转换规则，一键转换",
            status="published",
            is_public=False,
            tags=["内置工具", "文档处理"],
        )
        db.session.add(doc_converter_app)
        db.session.commit()
        print(f"✅ 创建应用成功: {doc_converter_app.name} (ID: {doc_converter_app.id})")
        
        # 创建 AppConfig 配置
        config_id = uuid.uuid4()
        app_config = AppConfig(
            id=config_id,
            app_id=app_id,
            model_config={
                "provider": "custom",
                "model": "ep-20261023215214-s5p27",
                "temperature": 0.7,
            },
            preset_prompt="""你是一个专业的文档格式转换助手。请根据用户的需求，将输入的文档内容转换为指定格式。

支持的转换：
1. Markdown → HTML：将 Markdown 语法转换为对应的 HTML 标签
2. HTML → Markdown：将 HTML 标签转换为对应的 Markdown 语法
3. 任意格式 → 纯文本：去除所有格式标记，只保留纯文本内容
4. 纯文本 → Markdown：将纯文本格式化为易读的 Markdown 格式

转换要求：
- 保持原有内容不变，只转换格式
- 保留标题层级、列表、代码块、链接等结构
- 输出只包含转换后的内容，不要多余解释
""",
            opening_statement="你好！我是文档格式转换助手 👋\n\n我可以帮你：\n- Markdown 转 HTML\n- HTML 转 Markdown\n- 去除格式转纯文本\n- 纯文本格式化\n\n直接把需要转换的内容发给我，告诉我要转成什么格式就行！",
            opening_questions=[
                "帮我把这段 Markdown 转成 HTML",
                "把这个网页内容转成 Markdown",
                "帮我去除所有格式，只保留纯文本",
            ],
            tools=[],
            long_term_memory={"enable": False},
        )
        db.session.add(app_config)
        
        # 关联应用和配置
        doc_converter_app.app_config_id = config_id
        db.session.commit()
        print(f"✅ 创建应用配置成功")
        
        print("\n🎉 内置应用创建完成！")
        print(f"应用名称: {doc_converter_app.name}")
        print(f"应用描述: {doc_converter_app.description}")
        print(f"刷新前端页面即可在个人空间看到！")

if __name__ == "__main__":
    create_builtin_apps()
