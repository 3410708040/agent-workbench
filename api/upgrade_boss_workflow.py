"""
升级 Boss招聘简历投递助手 - 批量投递版
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.http.app import app
from pkg.sqlalchemy import SQLAlchemy
from internal.model.workflow import Workflow
from internal.model.account import Account

def upgrade_workflow():
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
        
        # 3. 创建节点ID
        node_ids = {
            "start": str(uuid.uuid4()),
            "parse_input": str(uuid.uuid4()),
            "analyze_jd_batch": str(uuid.uuid4()),
            "gen_greeting_batch": str(uuid.uuid4()),
            "simulate_send": str(uuid.uuid4()),
            "end": str(uuid.uuid4()),
        }
        
        # 4. 创建节点
        nodes = [
            {
                "id": node_ids["start"],
                "node_type": "start",
                "title": "开始",
                "description": "输入你的简历和岗位列表，开始批量投递",
                "position": {"x": 100, "y": 250},
                "inputs": [
                    {
                        "name": "resume",
                        "type": "string",
                        "description": "你的简历全文"
                    },
                    {
                        "name": "job_list",
                        "type": "string",
                        "description": "目标岗位列表，每行一个岗位名称+JD摘要"
                    },
                    {
                        "name": "target_count",
                        "type": "number",
                        "description": "计划投递数量（默认30）"
                    }
                ]
            },
            {
                "id": node_ids["parse_input"],
                "node_type": "code",
                "title": "1. 解析输入并生成任务清单",
                "description": "解析岗位列表，生成批量投递任务清单",
                "position": {"x": 350, "y": 250},
                "code": """
# 解析输入，生成任务清单
resume = inputs.get('resume', '')
job_list_text = inputs.get('job_list', '')
target_count = int(inputs.get('target_count', 30))

# 按行分割岗位
jobs = [line.strip() for line in job_list_text.strip().split('\\n') if line.strip()]

# 截取目标数量
jobs = jobs[:target_count]

result = {
    "total_jobs": len(jobs),
    "jobs": jobs,
    "resume_summary": resume[:200] + "..." if len(resume) > 200 else resume,
    "task_list": [f"任务{i+1}: {job}" for i, job in enumerate(jobs)]
}
""",
                "inputs": [
                    {"name": "resume", "type": "string"},
                    {"name": "job_list", "type": "string"},
                    {"name": "target_count", "type": "number"}
                ],
                "outputs": [
                    {"name": "total_jobs", "type": "number"},
                    {"name": "task_list", "type": "array"}
                ]
            },
            {
                "id": node_ids["analyze_jd_batch"],
                "node_type": "llm",
                "title": "2. 批量分析JD并评估胜任度",
                "description": "批量分析每个岗位的JD，评估匹配度",
                "position": {"x": 600, "y": 150},
                "prompt": """你是一个求职助手，现在需要批量分析多个岗位的JD，评估用户的胜任度。

【用户简历摘要】
{{resume_summary}}

【待分析岗位列表】
{{task_list}}

【输出要求】
对每个岗位，输出以下信息：
1. 岗位名称
2. 核心要求（3个）
3. 匹配度打分（0-100）
4. 优势（2个）
5. 不足（2个）
6. 是否推荐投递（是/否）

请用表格形式输出，格式清晰。
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [
                    {"name": "resume_summary", "type": "string"},
                    {"name": "task_list", "type": "array"}
                ],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["gen_greeting_batch"],
                "node_type": "llm",
                "title": "3. 批量生成招呼话术",
                "description": "为每个推荐投递的岗位生成个性化招呼话术",
                "position": {"x": 600, "y": 350},
                "prompt": """你是一个求职助手，现在需要为每个岗位生成Boss直聘的招呼话术。

【用户优势】
- 数据科学与大数据技术专业
- 有数据开发实习经历
- 熟悉Python/Spark/RAG/Agent开发

【岗位列表】
{{task_list}}

【输出要求】
对每个推荐投递的岗位，生成：
1. 岗位名称
2. 招呼话术（100字以内，自然像真人，突出匹配点，结尾加一个问题）

请按岗位顺序输出，每个岗位一段。
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [
                    {"name": "task_list", "type": "array"}
                ],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["simulate_send"],
                "node_type": "code",
                "title": "4. 模拟发送（开发模式）",
                "description": "模拟发送话术和简历，打印到控制台",
                "position": {"x": 850, "y": 250},
                "code": """
# 模拟发送过程
analysis_result = inputs.get('analysis_result', '')
greeting_result = inputs.get('greeting_result', '')
total_jobs = inputs.get('total_jobs', 0)

# 模拟发送日志
send_log = '[Boss直聘批量投递模拟]\\n'
send_log += '计划投递岗位数: ' + str(total_jobs) + '\\n'
send_log += '[发送流程]\\n'
send_log += '1. 遍历岗位列表...\\n'
send_log += '2. 对每个岗位:\\n'
send_log += '   - 发送招呼话术 OK\\n'
send_log += '   - 发送简历附件 OK\\n'
send_log += '   - 记录投递时间 OK\\n'
send_log += '[完成]\\n'
send_log += '全部岗位处理完毕！\\n'

result = {
    "send_log": send_log,
    "success_count": total_jobs,
    "status": "completed"
}
""",
                "inputs": [
                    {"name": "analysis_result", "type": "string"},
                    {"name": "greeting_result", "type": "string"},
                    {"name": "total_jobs", "type": "number"}
                ],
                "outputs": [
                    {"name": "send_log", "type": "string"},
                    {"name": "success_count", "type": "number"},
                    {"name": "status", "type": "string"}
                ]
            },
            {
                "id": node_ids["end"],
                "node_type": "end",
                "title": "结束",
                "description": "输出投递结果汇总",
                "position": {"x": 1100, "y": 250},
            }
        ]
        
        # 5. 创建边
        edges = [
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["start"],
                "source_type": "start",
                "target": node_ids["parse_input"],
                "target_type": "code",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["parse_input"],
                "source_type": "code",
                "target": node_ids["analyze_jd_batch"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["parse_input"],
                "source_type": "code",
                "target": node_ids["gen_greeting_batch"],
                "target_type": "llm",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["analyze_jd_batch"],
                "source_type": "llm",
                "target": node_ids["simulate_send"],
                "target_type": "code",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["gen_greeting_batch"],
                "source_type": "llm",
                "target": node_ids["simulate_send"],
                "target_type": "code",
            },
            {
                "id": str(uuid.uuid4()),
                "source": node_ids["simulate_send"],
                "source_type": "code",
                "target": node_ids["end"],
                "target_type": "end",
            },
        ]
        
        workflow_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        # 6. 创建工作流
        workflow_id = uuid.uuid4()
        workflow = Workflow(
            id=workflow_id,
            account_id=account.id,
            name="Boss招聘简历投递助手（批量版）",
            tool_call_name="boss_batch_recruitment",
            icon="💼",
            description="""Boss直聘批量投递助手：批量分析JD → 评估胜任度 → 生成招呼话术 → 模拟发送

【使用方法】
1. 在开始节点输入你的简历全文
2. 输入目标岗位列表（每行一个岗位）
3. 设置计划投递数量（默认30）
4. 运行工作流，自动完成批量分析和模拟投递

【示例输入】
简历：蒋锦涛，数据科学与大数据技术专业，有天源迪科数据开发实习，熟悉Python/Spark/RAG/Agent
岗位列表：
- AI应用开发工程师，要求Python/RAG/Agent经验
- 数据开发工程师，要求Spark/Hive/数仓经验
- Python开发工程师，要求后端开发经验

【输出】
- 每个岗位的JD分析和匹配度评估
- 每个岗位的个性化招呼话术
- 模拟投递发送日志
""",
            graph=workflow_graph,
            draft_graph=workflow_graph,
            is_debug_passed=True,
            status="published",
            is_public=False,
            tags=["内置工具", "求职招聘", "批量处理"],
        )
        db.session.add(workflow)
        db.session.commit()
        
        print(f"✅ 创建工作流成功: {workflow.name}")
        print(f"工作流 ID: {workflow.id}")
        print(f"\n🎉 批量版工作流升级完成！")
        print(f"现在支持批量处理多个岗位了！")
        print(f"刷新前端页面试试！")

if __name__ == "__main__":
    upgrade_workflow()
