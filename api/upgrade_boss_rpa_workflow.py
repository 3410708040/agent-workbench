"""
升级 Boss招聘助手 - RPA自动化版
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.http.app import app
from pkg.sqlalchemy import SQLAlchemy
from internal.model.workflow import Workflow
from internal.model.account import Account

def upgrade_workflow_rpa():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 删除旧的工作流
        old_workflow = Workflow.query.filter_by(name="Boss招聘简历投递助手（批量版）").first()
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
            "load_resume": str(uuid.uuid4()),
            "gen_job_pool": str(uuid.uuid4()),
            "parse_input": str(uuid.uuid4()),
            "analyze_jd": str(uuid.uuid4()),
            "gen_greeting": str(uuid.uuid4()),
            "rpa_simulate": str(uuid.uuid4()),
            "end": str(uuid.uuid4()),
        }
        
        # 4. 创建节点
        nodes = [
            {
                "id": node_ids["start"],
                "node_type": "start",
                "title": "开始",
                "description": "输入简历路径和投递要求，开始自动化投递",
                "position": {"x": 80, "y": 300},
                "inputs": [
                    {
                        "name": "resume_path",
                        "type": "string",
                        "description": "本地简历文件路径（如：D:/resume.pdf）"
                    },
                    {
                        "name": "platform",
                        "type": "string",
                        "description": "招聘平台（如：Boss直聘）"
                    },
                    {
                        "name": "target_count",
                        "type": "number",
                        "description": "计划投递数量（默认30）"
                    }
                ]
            },
            {
                "id": node_ids["load_resume"],
                "node_type": "code",
                "title": "1. 读取本地简历",
                "description": "读取本地简历文件，提取简历内容",
                "position": {"x": 300, "y": 200},
                "code": """
# 模拟读取本地简历文件（开发模式）
resume_path = inputs.get('resume_path', '')

# 开发模式：模拟读取简历内容
# 真实版本后续会用pdfplumber/PyPDF2读取真实PDF
mock_resume = '''
蒋锦涛
数据科学与大数据技术专业 应届生
实习经历：天源迪科 - 数据开发实习生（智慧蓉城项目）
技能栈：Python、Spark、Hive、RAG、Agent开发、TCP/IP
项目：医疗数据中台、招聘网站数据分析、YOLO害虫识别
求职意向：AI应用开发 / 数据开发 / Python开发
'''

result = {
    "resume_content": mock_resume,
    "resume_path": resume_path,
    "load_success": True
}
""",
                "inputs": [
                    {"name": "resume_path", "type": "string"}
                ],
                "outputs": [
                    {"name": "resume_content", "type": "string"},
                    {"name": "load_success", "type": "boolean"}
                ]
            },
            {
                "id": node_ids["gen_job_pool"],
                "node_type": "llm",
                "title": "2. 自动生成岗位库",
                "description": "根据简历自动匹配适合的岗位方向，生成岗位库",
                "position": {"x": 300, "y": 400},
                "prompt": """根据用户的简历，自动生成适合投递的岗位库。

【用户简历】
{{resume_content}}

【输出要求】
生成10个适合的岗位方向，每个岗位包含：
1. 岗位名称
2. 岗位核心要求（3个）
3. 匹配度打分（0-100）

按匹配度从高到低排序。
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [
                    {"name": "resume_content", "type": "string"}
                ],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["parse_input"],
                "node_type": "code",
                "title": "3. 解析投递任务",
                "description": "解析岗位库，生成批量投递任务清单",
                "position": {"x": 550, "y": 300},
                "code": """
# 生成投递任务清单
resume_content = inputs.get('resume_content', '')
job_pool = inputs.get('job_pool', '')
target_count = int(inputs.get('target_count', 30))

# 开发模式：生成模拟任务列表
tasks = []
for i in range(min(target_count, 30)):
    tasks.append({
        "job_id": i + 1,
        "job_name": f"AI应用开发工程师 - 公司{i+1}",
        "company": f"科技公司{i+1}",
        "salary": f"{15 + i//5}k-{20 + i//5}k"
    })

result = {
    "total_tasks": len(tasks),
    "task_list": tasks,
    "resume_summary": resume_content[:150]
}
""",
                "inputs": [
                    {"name": "resume_content", "type": "string"},
                    {"name": "job_pool", "type": "string"},
                    {"name": "target_count", "type": "number"}
                ],
                "outputs": [
                    {"name": "total_tasks", "type": "number"},
                    {"name": "task_list", "type": "array"}
                ]
            },
            {
                "id": node_ids["analyze_jd"],
                "node_type": "llm",
                "title": "4. 批量分析JD并评估",
                "description": "批量分析每个岗位的JD，评估匹配度",
                "position": {"x": 800, "y": 150},
                "prompt": """批量分析岗位JD，评估用户匹配度。

【用户简历】
{{resume_summary}}

【待分析岗位】
{{task_list}}

【输出要求】
对每个岗位输出：
1. 岗位名称
2. 匹配度打分（0-100）
3. 是否推荐投递（是/否）
4. 推荐理由（1句话）
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [
                    {"name": "resume_summary", "type": "string"},
                    {"name": "task_list", "type": "array"}
                ],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["gen_greeting"],
                "node_type": "llm",
                "title": "5. 批量生成招呼话术",
                "description": "为每个推荐岗位生成个性化招呼话术",
                "position": {"x": 800, "y": 450},
                "prompt": """为每个岗位生成Boss直聘招呼话术。

【用户优势】
- 数据科学与大数据专业
- 有数据开发实习经历
- 熟悉Python/Spark/RAG/Agent

【岗位列表】
{{task_list}}

【输出要求】
每个岗位生成：
1. 岗位名称
2. 招呼话术（100字以内，自然像真人，结尾加问题）
""",
                "model_config": {"model": "ep-20261023215214-s5p27"},
                "inputs": [
                    {"name": "task_list", "type": "array"}
                ],
                "outputs": [{"name": "output", "value": {"type": "generated"}}]
            },
            {
                "id": node_ids["rpa_simulate"],
                "node_type": "code",
                "title": "6. RPA自动化模拟（开发模式）",
                "description": "模拟浏览器自动化操作：打开平台→点击发送→投递简历",
                "position": {"x": 1050, "y": 300},
                "code": """
# RPA自动化模拟（开发模式）
platform = inputs.get('platform', 'Boss直聘')
task_list = inputs.get('task_list', [])

# 生成RPA操作步骤日志
rpa_log = '=== RPA自动化投递流程 ===\\n'
rpa_log += '目标平台: ' + platform + '\\n'
rpa_log += '计划投递: ' + str(len(task_list)) + ' 个岗位\\n\\n'

rpa_log += '[步骤1] 打开浏览器，访问 ' + platform + ' 官网\\n'
rpa_log += '[步骤2] 自动登录账号（已保存Cookie）\\n'
rpa_log += '[步骤3] 进入职位搜索页\\n\\n'

for i, task in enumerate(task_list[:5]):  # 先模拟前5个
    rpa_log += '--- 处理岗位 ' + str(i+1) + ': ' + task['job_name'] + ' ---\\n'
    rpa_log += '  → 点击岗位卡片进入详情\\n'
    rpa_log += '  → 点击"立即沟通"按钮\\n'
    rpa_log += '  → 自动输入招呼话术\\n'
    rpa_log += '  → 点击发送按钮\\n'
    rpa_log += '  → 等待1秒后自动发送简历附件\\n'
    rpa_log += '  → 记录投递成功\\n\\n'

rpa_log += '[完成] 已成功投递 ' + str(len(task_list)) + ' 个岗位！\\n'

result = {
    "rpa_log": rpa_log,
    "success_count": len(task_list),
    "status": "completed"
}
""",
                "inputs": [
                    {"name": "platform", "type": "string"},
                    {"name": "task_list", "type": "array"}
                ],
                "outputs": [
                    {"name": "rpa_log", "type": "string"},
                    {"name": "success_count", "type": "number"},
                    {"name": "status", "type": "string"}
                ]
            },
            {
                "id": node_ids["end"],
                "node_type": "end",
                "title": "结束",
                "description": "输出投递结果汇总",
                "position": {"x": 1300, "y": 300},
            }
        ]
        
        # 5. 创建边
        edges = [
            # start -> load_resume
            {"id": str(uuid.uuid4()), "source": node_ids["start"], "source_type": "start", "target": node_ids["load_resume"], "target_type": "code"},
            # start -> gen_job_pool (并行)
            {"id": str(uuid.uuid4()), "source": node_ids["start"], "source_type": "start", "target": node_ids["gen_job_pool"], "target_type": "llm"},
            # load_resume -> parse_input
            {"id": str(uuid.uuid4()), "source": node_ids["load_resume"], "source_type": "code", "target": node_ids["parse_input"], "target_type": "code"},
            # gen_job_pool -> parse_input
            {"id": str(uuid.uuid4()), "source": node_ids["gen_job_pool"], "source_type": "llm", "target": node_ids["parse_input"], "target_type": "code"},
            # parse_input -> analyze_jd
            {"id": str(uuid.uuid4()), "source": node_ids["parse_input"], "source_type": "code", "target": node_ids["analyze_jd"], "target_type": "llm"},
            # parse_input -> gen_greeting
            {"id": str(uuid.uuid4()), "source": node_ids["parse_input"], "source_type": "code", "target": node_ids["gen_greeting"], "target_type": "llm"},
            # analyze_jd -> rpa_simulate
            {"id": str(uuid.uuid4()), "source": node_ids["analyze_jd"], "source_type": "llm", "target": node_ids["rpa_simulate"], "target_type": "code"},
            # gen_greeting -> rpa_simulate
            {"id": str(uuid.uuid4()), "source": node_ids["gen_greeting"], "source_type": "llm", "target": node_ids["rpa_simulate"], "target_type": "code"},
            # rpa_simulate -> end
            {"id": str(uuid.uuid4()), "source": node_ids["rpa_simulate"], "source_type": "code", "target": node_ids["end"], "target_type": "end"},
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
            name="Boss招聘RPA自动化投递",
            tool_call_name="boss_rpa_auto_delivery",
            icon="🤖",
            description="""Boss直聘RPA自动化投递助手：读取简历→生成岗位库→批量分析JD→生成话术→模拟RPA操作

【使用方法】
在对话框直接说：
"帮我在Boss直聘投递30份简历，简历路径是D:/resume.pdf"

【自动化流程】
1. 读取本地简历文件
2. 根据简历自动生成适合的岗位库
3. 批量分析JD，评估匹配度
4. 为每个岗位生成个性化招呼话术
5. 模拟RPA操作：打开浏览器→自动登录→逐个岗位发送话术+简历

【开发说明】
当前是开发模式：RPA操作是模拟的（打印步骤到控制台）
后续升级：接入Playwright实现真正的浏览器自动化
""",
            graph=workflow_graph,
            draft_graph=workflow_graph,
            is_debug_passed=True,
            status="published",
            is_public=False,
            tags=["内置工具", "求职招聘", "RPA自动化"],
        )
        db.session.add(workflow)
        db.session.commit()
        
        print(f"✅ 创建工作流成功: {workflow.name}")
        print(f"工作流 ID: {workflow.id}")
        print(f"\n🎉 RPA自动化版工作流升级完成！")
        print(f"现在支持：读取简历路径 + 自动生成岗位库 + 模拟RPA操作！")
        print(f"刷新前端页面试试！")

if __name__ == "__main__":
    upgrade_workflow_rpa()
