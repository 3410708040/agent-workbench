"""
测试 Boss招聘RPA自动化投递 工作流
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.http.app import app
from internal.service.workflow_service import WorkflowService
from pkg.sqlalchemy import SQLAlchemy
from internal.model.account import Account

def test_workflow():
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        # 1. 获取工作流
        from internal.model.workflow import Workflow
        workflow = Workflow.query.filter_by(name="Boss招聘RPA自动化投递").first()
        if not workflow:
            print("❌ 找不到工作流")
            return
        
        print(f"✅ 找到工作流: {workflow.name}")
        print(f"   ID: {workflow.id}")
        print(f"   节点数: {len(workflow.draft_graph.get('nodes', []))}")
        print(f"   边数: {len(workflow.draft_graph.get('edges', []))}")
        print()
        
        # 2. 获取用户账号
        account = Account.query.first()
        if not account:
            print("❌ 找不到用户账号")
            return
        
        print(f"✅ 用户账号: {account.id}")
        print()
        
        # 3. 准备输入参数
        inputs = {
            "resume_path": "D:/resume.pdf",
            "platform": "Boss直聘",
            "target_count": 3,  # 先测试3个，不要太多
        }
        
        print("📋 测试输入参数:")
        print(json.dumps(inputs, indent=2, ensure_ascii=False))
        print()
        
        # 4. 调用调试服务
        print("🚀 开始调试工作流...")
        try:
            service = WorkflowService(db)
            result = service.debug_workflow(workflow.id, inputs, account)
            print("✅ 工作流调试成功！")
            print()
            print("📊 输出结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            print(f"❌ 工作流调试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_workflow()
