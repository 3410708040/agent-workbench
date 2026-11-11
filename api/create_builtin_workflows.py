"""
创建内置工作流：Boss 招聘简历投递工作流
包含：匹配岗位 → JD分析 → 招呼话术 → 匹配胜任度 → 投递简历
"""
import sys
import os
import uuid

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.http.app import app
from pkg.sqlalchemy import SQLAlchemy
from internal.model.workflow import Workflow
from internal.model.account import Account

def create_builtin_workflows():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 获取用户账号
        account = Account.query.first()
        if not account:
            print("❌ 没有找到用户账号")
            return
        
        print(f"✅ 使用账号: {account.email} (ID: {account.id})")
        
        # 2. 创建 Boss 招聘简历投递工作流
        workflow_id = uuid.uuid4()
        
        # 检查是否已存在
        existing = Workflow.query.filter_by(name="Boss招聘简历投递助手").first()
        if existing:
            print(f"⚠️ 工作流已存在，ID: {existing.id}")
            return
        
        # 工作流图配置（节点+边）
        workflow_graph = {
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "position": {"x": 100, "y": 200},
                    "data": {"label": "开始"}
                },
                {
                    "id": "match_job",
                    "type": "llm",
                    "position": {"x": 300, "y": 200},
                    "data": {
                        "label": "1. 匹配岗位",
                        "prompt": "根据用户的简历和求职意向，从岗位列表中匹配最合适的岗位，输出岗位名称和匹配理由。",
                        "model": "ep-20261023215214-s5p27"
                    }
                },
                {
                    "id": "analyze_jd",
                    "type": "llm",
                    "position": {"x": 500, "y": 200},
                    "data": {
                        "label": "2. JD分析",
                        "prompt": "分析岗位JD，提取核心要求：必备技能、加分项、薪资范围、岗位职责。",
                        "model": "ep-20261023215214-s5p27"
                    }
                },
                {
                    "id": "greeting",
                    "type": "llm",
                    "position": {"x": 700, "y": 150},
                    "data": {
                        "label": "3. 生成招呼话术",
                        "prompt": "根据JD分析和用户简历，生成个性化的Boss直聘招呼话术，突出匹配点，不超过100字。",
                        "model": "ep-20261023215214-s5p27"
                    }
                },
                {
                    "id": "fitness",
                    "type": "llm",
                    "position": {"x": 700, "y": 300},
                    "data": {
                        "label": "4. 匹配胜任度评估",
                        "prompt": "评估用户简历与岗位的匹配度，打分（0-100），列出优势和不足，给出改进建议。",
                        "model": "ep-20261023215214-s5p27"
                    }
                },
                {
                    "id": "deliver",
                    "type": "llm",
                    "position": {"x": 900, "y": 200},
                    "data": {
                        "label": "5. 投递简历建议",
                        "prompt": "根据前面的分析，给出最终的投递建议：是否推荐投递、投递策略、注意事项。",
                        "model": "ep-20261023215214-s5p27"
                    }
                },
                {
                    "id": "end",
                    "type": "end",
                    "position": {"x": 1100, "y": 200},
                    "data": {"label": "结束"}
                }
            ],
            "edges": [
                {"source": "start", "target": "match_job"},
                {"source": "match_job", "target": "analyze_jd"},
                {"source": "analyze_jd", "target": "greeting"},
                {"source": "analyze_jd", "target": "fitness"},
                {"source": "greeting", "target": "deliver"},
                {"source": "fitness", "target": "deliver"},
                {"source": "deliver", "target": "end"}
            ]
        }
        
        workflow = Workflow(
            id=workflow_id,
            account_id=account.id,
            name="Boss招聘简历投递助手",
            tool_call_name="boss_recruitment_assistant",
            icon="💼",
            description="智能招聘助手：匹配岗位 → JD分析 → 生成招呼话术 → 评估胜任度 → 投递建议",
            graph=workflow_graph,
            draft_graph=workflow_graph,
            is_debug_passed=True,
            status="published",
            is_public=False,
            tags=["内置工具", "求职招聘"],
        )
        db.session.add(workflow)
        db.session.commit()
        print(f"✅ 创建工作流成功: {workflow.name} (ID: {workflow.id})")
        
        print("\n🎉 内置工作流创建完成！")
        print(f"工作流名称: {workflow.name}")
        print(f"工作流描述: {workflow.description}")
        print(f"包含步骤: 匹配岗位 → JD分析 → 招呼话术 → 匹配胜任度 → 投递简历")
        print(f"刷新前端页面即可在个人空间看到！")

if __name__ == "__main__":
    create_builtin_workflows()
