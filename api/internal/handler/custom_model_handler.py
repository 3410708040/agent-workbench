from uuid import UUID
from flask import request
from injector import inject
from flask_login import login_required
from dataclasses import dataclass
from internal.service import CustomModelService
from pkg.response import success_json, success_message


@inject
@dataclass
class CustomModelHandler:
    """自定义模型提供商处理器（模型管理界面后端 API）"""

    custom_model_service: CustomModelService

    @login_required
    def list_custom_models(self):
        """获取用户手动添加的全部自定义模型提供商"""
        return success_json(self.custom_model_service.list_custom_models())

    @login_required
    def create_custom_model(self):
        """添加自定义模型提供商"""
        payload = request.get_json(silent=True) or {}
        self.custom_model_service.create_custom_model(payload)
        return success_message("添加模型成功")

    @login_required
    def update_custom_model(self, provider_id: UUID):
        """更新自定义模型提供商"""
        payload = request.get_json(silent=True) or {}
        self.custom_model_service.update_custom_model(provider_id, payload)
        return success_message("更新模型成功")

    @login_required
    def delete_custom_model(self, provider_id: UUID):
        """删除自定义模型提供商"""
        self.custom_model_service.delete_custom_model(provider_id)
        return success_message("删除模型成功")

    @login_required
    def test_custom_model(self, provider_id: UUID):
        """测试自定义模型提供商连接（发起一次真实调用）"""
        payload = request.get_json(silent=True) or {}
        model_name = str(payload.get("model_name") or "").strip() or None
        return success_json(self.custom_model_service.test_custom_model(provider_id, model_name))

    @login_required
    def test_custom_model_payload(self):
        """根据未保存的表单内容测试连接（不落库）"""
        payload = request.get_json(silent=True) or {}
        model_name = str(payload.get("model_name") or "").strip() or None
        return success_json(self.custom_model_service.test_custom_model_payload(payload, model_name))
