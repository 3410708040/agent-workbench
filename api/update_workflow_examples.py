"""
更新内置工作流：添加使用示例和测试用例
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

def update_workflow_with_examples():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 找到工作流
        workflow = Workflow.query.filter_by(name="Boss招聘简历投递助手").first()
        if not workflow:
            print("❌ 没有找到工作流")
            return
        
        print(f"✅ 找到工作流: {workflow.name}")
        
        # 2. 更新描述，加上使用示例
        new_description = """智能招聘助手：匹配岗位 → JD分析 → 生成招呼话术 → 评估胜任度 → 投递建议

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
"""
        
        # 3. 更新工作流节点的 prompt，加上示例
        old_graph = workflow.graph
        nodes = old_graph.get("nodes", [])
        
        # 更新每个节点的描述
        for node in nodes:
            if node.get("node_type") == "start":
                node["description"] = """输入你的简历和求职意向，例如：
"我是蒋锦涛，数据科学与大数据专业应届生，有数据开发实习经历，熟悉Python/Spark/RAG，想找AI应用开发岗位"
            """
            elif node.get("title") == "1. 匹配岗位":
                node["prompt"] = """根据用户的简历和求职意向，匹配最合适的岗位方向。

【输入示例】
用户简历：蒋锦涛，数据科学与大数据技术专业应届生，有天源迪科数据开发实习经历，熟悉Python、Spark、RAG、Agent开发
求职意向：AI应用开发工程师 / 数据开发工程师

【输出要求】
1. 推荐最匹配的1-2个岗位方向
2. 说明匹配理由
3. 列出岗位的核心要求
                """
            elif node.get("title") == "2. JD分析":
                node["prompt"] = """分析目标岗位的JD，提取核心信息。

【输入】
岗位名称：AI应用开发工程师
岗位职责：开发基于大模型的AI应用，包括RAG系统、Agent智能体、对话机器人等
任职要求：Python编程、熟悉LangChain/LlamaIndex、有RAG/Agent开发经验、了解大模型原理

【输出要求】
1. 必备技能（必须会的）
2. 加分项（有更好的）
3. 薪资范围参考
4. 核心职责总结
                """
            elif node.get("title") == "3. 生成招呼话术":
                node["prompt"] = """根据用户简历和岗位要求，生成Boss直聘的招呼话术。

【输入】
用户优势：有数据开发实习经历，熟悉Python/Spark/RAG/Agent
岗位要求：AI应用开发工程师，需要Python/RAG/Agent经验

【输出要求】
1. 不超过100字
2. 突出匹配点
3. 语气自然，像真人发的
4. 结尾可以加一个问题引导对方回复
                """
            elif node.get("title") == "4. 匹配胜任度评估":
                node["prompt"] = """评估用户简历与岗位的匹配度。

【输入】
用户简历：数据科学与大数据专业，有数据开发实习，熟悉Python/Spark/RAG/Agent
岗位要求：AI应用开发工程师，需要Python/RAG/Agent经验

【输出要求】
1. 匹配度打分（0-100分）
2. 列出3个优势
3. 列出2个不足
4. 给出改进建议
                """
            elif node.get("title") == "5. 投递简历建议":
                node["prompt"] = """根据前面的分析，给出最终的投递建议。

【输入】
匹配度：85/100
优势：专业对口、有实习经历、技术栈匹配
不足：缺乏正式项目经验、对大模型原理理解不深

【输出要求】
1. 是否推荐投递（是/否）
2. 投递策略（什么时候投、怎么跟进）
3. 注意事项（简历要突出什么、面试要准备什么）
                """
        
        new_graph = {
            "nodes": nodes,
            "edges": old_graph.get("edges", [])
        }
        
        # 4. 更新工作流
        workflow.description = new_description
        workflow.graph = new_graph
        workflow.draft_graph = new_graph
        db.session.commit()
        
        print(f"✅ 工作流更新成功！")
        print(f"已添加使用示例到描述和每个节点的prompt中")
        print(f"\n现在用户打开这个工作流，就能看到怎么用了！")

if __name__ == "__main__":
    update_workflow_with_examples()
