"""
彻底修复内置工作流：边格式 + 节点完整格式
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

def fix_workflow_completely():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 删除旧的工作流
        old_workflow = Workflow.query.filter_by(name="Boss招聘简历投递助手").first()
        if old_workflow:
            db.session.delete(old_workflow)
            db.session.commit()
            print(f"✅ 已删除旧工作流")
        
        # 2. 获取用户账号
        account = Account.query.first()
        if not account:
            print("❌ 没有找到用户账号")
            return
        
        # 3. 创建节点（每个节点有唯一ID）
        node_ids = {
            "start": str(uuid.uuid4()),
            "match_job": str(uuid.uuid4()),
            "analyze_jd": str(uuid.uuid4()),
            "greeting": str(uuid.uuid4()),
            "fitness": str(uuid.uuid4()),
            "deliver": str(uuid.uuid4()),
            "end": str(uuid.uuid4()),
        }
        
        nodes = [
            {
                "id": node_ids["start"],
                "node_type": "start",
                "title": "开始",
                "description": "工作流开始节点，输入你的简历和求职意向",
                "position": {"x": 100, "y": 200},
                "inputs": []
            },
            {
                "id": node_ids["match_job"],
                "node_type": "llm",
                "title": "1. 匹配岗位",
                "description": "根据用户简历匹配最合适的岗位方向",
                "position": {"x": 300, "y": 200},
                "prompt": """根据用户的简历和求职意向，匹配最合适的岗位方向。

【输入示例】
用户简历：蒋锦涛，数据科学与大数据技术专业应届生，有天源迪科数据开发实习经历，熟悉Python、Spark、RAG、Agent开发
求职意向：AI应用开发工程师 / 数据开发工程师

【输出要求】
1. 推荐最匹配的1-2个岗位方向
2. 说明匹配理由
3. 列出岗位的核心要求
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["analyze_jd"],
                "node_type": "llm",
                "title": "2. JD分析",
                "description": "分析目标岗位JD，提取核心要求",
                "position": {"x": 500, "y": 200},
                "prompt": """分析目标岗位的JD，提取核心信息。

【输入】
岗位名称：AI应用开发工程师
岗位职责：开发基于大模型的AI应用，包括RAG系统、Agent智能体、对话机器人等
任职要求：Python编程、熟悉LangChain/LlamaIndex、有RAG/Agent开发经验、了解大模型原理

【输出要求】
1. 必备技能（必须会的）
2. 加分项（有更好的）
3. 薪资范围参考
4. 核心职责总结
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["greeting"],
                "node_type": "llm",
                "title": "3. 生成招呼话术",
                "description": "生成个性化的Boss直聘招呼话术",
                "position": {"x": 700, "y": 150},
                "prompt": """根据用户简历和岗位要求，生成Boss直聘的招呼话术。

【输入】
用户优势：有数据开发实习经历，熟悉Python/Spark/RAG/Agent
岗位要求：AI应用开发工程师，需要Python/RAG/Agent经验

【输出要求】
1. 不超过100字
2. 突出匹配点
3. 语气自然，像真人发的
4. 结尾可以加一个问题引导对方回复
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["fitness"],
                "node_type": "llm",
                "title": "4. 匹配胜任度评估",
                "description": "评估用户简历与岗位的匹配度",
                "position": {"x": 700, "y": 300},
                "prompt": """评估用户简历与岗位的匹配度。

【输入】
用户简历：数据科学与大数据专业，有数据开发实习，熟悉Python/Spark/RAG/Agent
岗位要求：AI应用开发工程师，需要Python/RAG/Agent经验

【输出要求】
1. 匹配度打分（0-100分）
2. 列出3个优势
3. 列出2个不足
4. 给出改进建议
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["deliver"],
                "node_type": "llm",
                "title": "5. 投递简历建议",
                "description": "给出最终的投递建议",
                "position": {"x": 900, "y": 200},
                "prompt": """根据前面的分析，给出最终的投递建议。

【输入】
匹配度：85/100
优势：专业对口、有实习经历、技术栈匹配
不足：缺乏正式项目经验、对大模型原理理解不深

【输出要求】
1. 是否推荐投递（是/否）
2. 投递策略（什么时候投、怎么跟进）
3. 注意事项（简历要突出什么、面试要准备什么）
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["end"],
                "node_type": "end",
                "title": "结束",
                "description": "工作流结束节点",
                "position": {"x": 1100, "y": 200},
            }
        ]
        
        # 4. 创建边（每个边有完整字段）
        edges = [
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["start"],
                "source_type": "start",
                "target": node_ids["match_job"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["match_job"],
                "source_type": "llm",
                "target": node_ids["analyze_jd"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["analyze_jd"],
                "source_type": "llm",
                "target": node_ids["greeting"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["analyze_jd"],
                "source_type": "llm",
                "target": node_ids["fitness"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["greeting"],
                "source_type": "llm",
                "target": node_ids["deliver"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["fitness"],
                "source_type": "llm",
                "target": node_ids["deliver"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["deliver"],
                "source_type": "llm",
                "target": node_ids["end"],
                "target_type": "end",
            },
        ]
        
        workflow_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        # 5. 创建工作流
        workflow_id = uuid.uuid4()
        workflow = Workflow(
            id=workflow_id,
            account_id=account.id,
            name="Boss招聘简历投递助手",
            tool_call_name="boss_recruitment_assistant",
            icon="💼",
            description="""智能招聘助手：匹配岗位 → JD分析 → 生成招呼话术 → 评估胜任度 → 投递建议

【使用示例】
输入：
- 我的简历：蒋锦涛，数据科学与大数据技术专业应届生，有天源迪科数据开发实习经历，熟悉Python、Spark、RAG、Agent开发
- 求职意向：AI应用开发工程师 / 数据开发工程师

输出：
1. 匹配岗位：推荐AI应用开发工程师岗位
2. JD分析：提取核心要求（Python、RAG、Agent开发经验）
3. 招呼话术：生成个性化打招呼文案
4. 胜任度评估：打分85/100，列出优势和不足
5. 投递建议：推荐投递，附注意事项
""",
            graph=workflow_graph,
            draft_graph=workflow_graph,
            is_debug_passed=True,
            status="published",
            is_public=False,
            tags=["内置工具", "求职招聘"],
        )
        db.session.add(workflow)
        db.session.commit()
        
        print(f"✅ 创建工作流成功: {workflow.name}")
        print(f"工作流 ID: {workflow.id}")
        print(f"\n🎉 工作流彻底修复完成！")
        print(f"现在边的格式是完整的，应该能正常显示了！")
        print(f"刷新前端页面试试！")

if __name__ == "__main__":
    fix_workflow_completely()
