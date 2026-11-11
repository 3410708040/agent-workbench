"""
修复并重新创建内置工作流：Boss 招聘简历投递工作流
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

def fix_builtin_workflow():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 删除旧的工作流
        old_workflow = Workflow.query.filter_by(name="Boss招聘简历投递助手").first()
        if old_workflow:
            db.session.delete(old_workflow)
            db.session.commit()
            print(f"✅ 已删除旧工作流: {old_workflow.name}")
        
        # 2. 获取用户账号
        account = Account.query.first()
        if not account:
            print("❌ 没有找到用户账号")
            return
        
        print(f"✅ 使用账号: {account.email} (ID: {account.id})")
        
        # 3. 创建正确格式的工作流节点
        workflow_id = uuid.uuid4()
        
        # 正确格式的节点
        nodes = [
            {
                "id": str(uuid.uuid4()),
                "node_type": "start",
                "title": "开始",
                "description": "工作流开始节点",
                "position": {"x": 100, "y": 200}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "llm",
                "title": "1. 匹配岗位",
                "description": "根据用户简历匹配最合适的岗位",
                "position": {"x": 300, "y": 200},
                "prompt": "根据用户的简历和求职意向，从岗位列表中匹配最合适的岗位，输出岗位名称和匹配理由。",
                "model_config": {"model": "ep-20261023215214-s5p27"}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "llm",
                "title": "2. JD分析",
                "description": "分析岗位JD，提取核心要求",
                "position": {"x": 500, "y": 200},
                "prompt": "分析岗位JD，提取核心要求：必备技能、加分项、薪资范围、岗位职责。",
                "model_config": {"model": "ep-20261023215214-s5p27"}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "llm",
                "title": "3. 生成招呼话术",
                "description": "生成个性化的Boss直聘招呼话术",
                "position": {"x": 700, "y": 150},
                "prompt": "根据JD分析和用户简历，生成个性化的Boss直聘招呼话术，突出匹配点，不超过100字。",
                "model_config": {"model": "ep-20261023215214-s5p27"}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "llm",
                "title": "4. 匹配胜任度评估",
                "description": "评估用户简历与岗位的匹配度",
                "position": {"x": 700, "y": 300},
                "prompt": "评估用户简历与岗位的匹配度，打分（0-100），列出优势和不足，给出改进建议。",
                "model_config": {"model": "ep-20261023215214-s5p27"}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "llm",
                "title": "5. 投递简历建议",
                "description": "给出最终的投递建议",
                "position": {"x": 900, "y": 200},
                "prompt": "根据前面的分析，给出最终的投递建议：是否推荐投递、投递策略、注意事项。",
                "model_config": {"model": "ep-20261023215214-s5p27"}
            },
            {
                "id": str(uuid.uuid4()),
                "node_type": "end",
                "title": "结束",
                "description": "工作流结束节点",
                "position": {"x": 1100, "y": 200}
            }
        ]
        
        # 边
        edges = [
            {"source": nodes[0]["id"], "target": nodes[1]["id"]},
            {"source": nodes[1]["id"], "target": nodes[2]["id"]},
            {"source": nodes[2]["id"], "target": nodes[3]["id"]},
            {"source": nodes[2]["id"], "target": nodes[4]["id"]},
            {"source": nodes[3]["id"], "target": nodes[5]["id"]},
            {"source": nodes[4]["id"], "target": nodes[5]["id"]},
            {"source": nodes[5]["id"], "target": nodes[6]["id"]},
        ]
        
        workflow_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        # 创建工作流
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
        
        print("\n🎉 内置工作流修复完成！")
        print(f"工作流名称: {workflow.name}")
        print(f"包含步骤: 匹配岗位 → JD分析 → 招呼话术 → 匹配胜任度 → 投递简历")
        print(f"刷新前端页面即可看到！")

if __name__ == "__main__":
    fix_builtin_workflow()
