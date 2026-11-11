import re
import logging
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from injector import inject
from flask import request

from internal.core.language_model import LanguageModelManager
from internal.core.language_model.entities.model_entity import (
    ModelEntity,
    ModelFeature,
    ModelType,
    ModelParameter,
    ModelParameterType,
)
from internal.core.language_model.entities.provider_entity import Provider, ProviderEntity
from internal.core.language_model.entities.default_model_parameter_template import (
    DEFAULT_MODEL_PARAMETER_TEMPLATE,
)
from internal.exception import NotFoundException, ValidateErrorException
from internal.lib.helper import datetime_to_timestamp
from internal.model import CustomModelProvider
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


logger = logging.getLogger(__name__)

_CUSTOM_PROVIDER_ICON = "icon.svg"
_CUSTOM_PROVIDER_BACKGROUND = "#4F6BF6"
_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")


def _normalize_model_items(models: Any) -> list[dict[str, str]]:
    """把前端提交的模型列表归一化为 [{name,label}]。"""
    normalized: list[dict[str, str]] = []
    for item in models or []:
        if isinstance(item, dict):
            model_name = str(item.get("name", "")).strip()
            model_label = str(item.get("label", "")).strip() or model_name
        else:
            model_name = str(item).strip()
            model_label = model_name
        if model_name:
            normalized.append({"name": model_name, "label": model_label})
    return normalized


def _build_model_parameters(max_output_tokens: int) -> list[dict[str, Any]]:
    """为自定义模型构建默认参数规则（温度/TopP/最大标记）。"""
    temperature = {**DEFAULT_MODEL_PARAMETER_TEMPLATE.get("temperature", {}), "default": 0.7}
    top_p = {**DEFAULT_MODEL_PARAMETER_TEMPLATE.get("top_p", {}), "default": 1}
    max_tokens = {**DEFAULT_MODEL_PARAMETER_TEMPLATE.get("max_tokens", {})}
    if max_output_tokens and max_output_tokens > 0:
        max_tokens["max"] = max_output_tokens
    return [temperature, top_p, max_tokens]


@inject
@dataclass
class CustomModelService(BaseService):
    """自定义模型提供商服务：用户通过「模型管理」界面手动添加 OpenAI 兼容模型服务"""

    db: SQLAlchemy
    language_model_manager: LanguageModelManager

    # ---------- 查询与构建 ----------

    def _get_record(self, provider_id: UUID | str) -> CustomModelProvider:
        record = self.db.session.query(CustomModelProvider).filter(
            CustomModelProvider.id == provider_id
        ).first()
        if record is None:
            raise NotFoundException("该自定义模型提供商不存在")
        return record

    def get_custom_provider_records(self) -> list[CustomModelProvider]:
        """获取全部（含停用）自定义模型提供商记录。"""
        return self.db.session.query(CustomModelProvider).order_by(
            CustomModelProvider.created_at.asc()
        ).all()

    def get_active_custom_providers(self) -> list[CustomModelProvider]:
        """获取启用的自定义模型提供商记录。"""
        return self.db.session.query(CustomModelProvider).filter(
            CustomModelProvider.is_active.is_(True)
        ).order_by(CustomModelProvider.created_at.asc()).all()

    def build_custom_provider(self, record: CustomModelProvider) -> Optional[Provider]:
        """根据数据库记录构建 Provider 对象（模型实体直接注入，跳过 YAML 文件加载）。"""
        return self._build_provider(
            name=record.name,
            label=record.label or record.name,
            api_key=record.api_key,
            base_url=record.base_url,
            model_type=record.model_type or ModelType.CHAT.value,
            models=record.models or [],
            features=record.features or [],
            context_window=record.context_window or 0,
            max_output_tokens=record.max_output_tokens or 0,
        )

    def _build_provider(
        self,
        *,
        name: str,
        label: str,
        api_key: str,
        base_url: str,
        model_type: str,
        models: list[Any],
        features: list[str],
        context_window: int,
        max_output_tokens: int,
    ) -> Optional[Provider]:
        """根据归一化配置构建 Provider 对象（模型实体直接注入，跳过 YAML 文件加载）。"""
        model_type_enum = ModelType(model_type or ModelType.CHAT.value)
        supported_features = {
            ModelFeature.TOOL_CALL.value,
            ModelFeature.AGENT_THOUGHT.value,
            ModelFeature.IMAGE_INPUT.value,
        }
        feature_list = [f for f in (features or []) if f in supported_features]

        provider_entity = ProviderEntity(
            name=name,
            label=label or name,
            description="用户手动添加的 OpenAI 兼容模型服务",
            icon=_CUSTOM_PROVIDER_ICON,
            background=_CUSTOM_PROVIDER_BACKGROUND,
            supported_model_types=[model_type_enum],
        )

        model_entity_map: dict[str, ModelEntity] = {}
        for item in _normalize_model_items(models):
            model_name = item["name"]
            model_entity_map[model_name] = ModelEntity(
                model_name=model_name,
                label=item["label"],
                model_type=model_type_enum,
                features=feature_list,
                context_window=context_window or 0,
                max_output_tokens=max_output_tokens or 0,
                attributes={
                    "model": model_name,
                    "api_key": api_key,
                    "base_url": base_url,
                },
                parameters=_build_model_parameters(max_output_tokens or 0),
                metadata={},
            )

        if not model_entity_map:
            return None

        return Provider(
            name=name,
            position=1000,
            provider_entity=provider_entity,
            model_entity_map=model_entity_map,
            is_custom=True,
        )

    def get_custom_provider(self, provider_name: str) -> Optional[Provider]:
        """根据提供商名获取启用的自定义 Provider，未命中返回 None。"""
        record = self.db.session.query(CustomModelProvider).filter(
            CustomModelProvider.name == provider_name,
            CustomModelProvider.is_active.is_(True),
        ).first()
        if record is None:
            return None
        return self.build_custom_provider(record)

    # ---------- 列表序列化 ----------

    def to_language_model_dict(self, record: CustomModelProvider) -> dict[str, Any]:
        """把数据库记录转换成与内置提供商一致的 /language-models 结构。"""
        provider = self.build_custom_provider(record)
        models = []
        if provider is not None:
            for entity in provider.get_model_entities():
                models.append({
                    "model_name": entity.model_name,
                    "label": entity.label,
                    "model_type": entity.model_type.value,
                    "features": [f.value for f in entity.features],
                    "context_window": entity.context_window,
                    "max_output_tokens": entity.max_output_tokens,
                    "attributes": entity.attributes,
                    "parameters": [p.model_dump() for p in entity.parameters],
                    "metadata": entity.metadata,
                })
        return {
            "name": record.name,
            "position": 1000,
            "label": record.label or record.name,
            "icon": _CUSTOM_PROVIDER_ICON,
            "description": "用户手动添加的 OpenAI 兼容模型服务",
            "background": _CUSTOM_PROVIDER_BACKGROUND,
            "support_model_types": [record.model_type or ModelType.CHAT.value],
            "is_custom": True,
            "models": models,
        }

    def list_custom_models(self) -> list[dict[str, Any]]:
        """获取全部自定义模型提供商（含停用状态与配置信息，供管理界面使用）。"""
        result = []
        for record in self.get_custom_provider_records():
            item = self.to_language_model_dict(record)
            item.update({
                "id": str(record.id),
                "api_key": record.api_key,
                "base_url": record.base_url,
                "model_type": record.model_type,
                "model_names": [m.get("name") for m in _normalize_model_items(record.models)],
                "features": record.features or [],
                "context_window": record.context_window,
                "max_output_tokens": record.max_output_tokens,
                "is_active": record.is_active,
                "created_at": datetime_to_timestamp(record.created_at) if record.created_at else None,
                "updated_at": datetime_to_timestamp(record.updated_at) if record.updated_at else None,
            })
            result.append(item)
        return result

    # ---------- 增删改 ----------

    def _validate_payload(self, payload: dict[str, Any], exclude_name: Optional[str] = None) -> dict[str, Any]:
        """校验并归一化创建/更新请求。"""
        name = str(payload.get("name", "")).strip()
        label = str(payload.get("label", "")).strip()
        api_key = str(payload.get("api_key", "")).strip()
        base_url = str(payload.get("base_url", "")).strip()
        model_type = str(payload.get("model_type", ModelType.CHAT.value)).strip()
        features = payload.get("features") or ["tool_call"]
        models = _normalize_model_items(payload.get("models"))

        if not name:
            raise ValidateErrorException("提供商名称不能为空")
        if not _NAME_PATTERN.match(name):
            raise ValidateErrorException("提供商名称只能包含字母、数字、下划线或中划线，且不超过63个字符")
        if exclude_name is None or name != exclude_name:
            existing = self.db.session.query(CustomModelProvider).filter(
                CustomModelProvider.name == name
            ).first()
            if existing is not None:
                raise ValidateErrorException("提供商名称已存在，请更换")
        if not label:
            label = name
        if not api_key:
            raise ValidateErrorException("API Key 不能为空")
        if not base_url:
            raise ValidateErrorException("Base URL 不能为空")
        if not base_url.startswith(("http://", "https://")):
            raise ValidateErrorException("Base URL 必须以 http:// 或 https:// 开头")
        if model_type not in {ModelType.CHAT.value, ModelType.COMPLETION.value}:
            raise ValidateErrorException("不支持的模型类型")
        if not models:
            raise ValidateErrorException("请至少添加一个模型")

        allowed_features = {
            ModelFeature.TOOL_CALL.value,
            ModelFeature.AGENT_THOUGHT.value,
            ModelFeature.IMAGE_INPUT.value,
        }
        features = [f for f in features if f in allowed_features]
        if not features:
            features = [ModelFeature.TOOL_CALL.value]

        try:
            context_window = int(payload.get("context_window", 0) or 0)
        except (TypeError, ValueError):
            context_window = 0
        try:
            max_output_tokens = int(payload.get("max_output_tokens", 0) or 0)
        except (TypeError, ValueError):
            max_output_tokens = 0

        return {
            "name": name,
            "label": label,
            "api_key": api_key,
            "base_url": base_url,
            "model_type": model_type,
            "models": models,
            "features": features,
            "context_window": max(0, context_window),
            "max_output_tokens": max(0, max_output_tokens),
            "is_active": bool(payload.get("is_active", True)),
        }

    def create_custom_model(self, payload: dict[str, Any]) -> CustomModelProvider:
        data = self._validate_payload(payload)
        return self.create(CustomModelProvider, **data)

    def update_custom_model(self, provider_id: UUID | str, payload: dict[str, Any]) -> CustomModelProvider:
        record = self._get_record(provider_id)
        data = self._validate_payload(payload, exclude_name=record.name)
        self.update(record, **data)
        return record

    def delete_custom_model(self, provider_id: UUID | str) -> None:
        record = self._get_record(provider_id)
        self.delete(record)

    # ---------- 连接测试 ----------

    def test_custom_model(self, provider_id: UUID | str, model_name: Optional[str] = None) -> dict[str, Any]:
        """对自定义提供商发起一次真实调用，验证 API Key / Base URL / 模型是否可用。"""
        record = self._get_record(provider_id)
        provider = self.build_custom_provider(record)
        if provider is None:
            raise ValidateErrorException("该提供商下没有可用模型，请先添加模型")

        return self._test_provider(provider, model_name, provider_name=record.name)

    def test_custom_model_payload(self, payload: dict[str, Any], model_name: Optional[str] = None) -> dict[str, Any]:
        """根据尚未保存的表单内容构建临时 Provider 并发起测试（不落库、不校验名称唯一）。"""
        data = self._validate_payload(payload)
        provider = self._build_provider(
            name=data["name"],
            label=data["label"],
            api_key=data["api_key"],
            base_url=data["base_url"],
            model_type=data["model_type"],
            models=data["models"],
            features=data["features"],
            context_window=data["context_window"],
            max_output_tokens=data["max_output_tokens"],
        )
        if provider is None:
            raise ValidateErrorException("该提供商下没有可用模型，请先添加模型")
        return self._test_provider(provider, model_name, provider_name=data["name"])

    def _test_provider(
        self,
        provider: Provider,
        model_name: Optional[str],
        provider_name: str,
    ) -> dict[str, Any]:
        if model_name and model_name in provider.model_entity_map:
            target_model_name = model_name
        else:
            target_model_name = next(iter(provider.model_entity_map))

        model_entity = provider.model_entity_map[target_model_name]
        model_class = provider.get_model_class(model_entity.model_type)
        llm = model_class(
            **model_entity.attributes,
            temperature=0.1,
            max_tokens=16,
            features=model_entity.features,
            metadata=model_entity.metadata,
        )

        try:
            response = llm.invoke("你好，请只回复四个字：连接成功")
            content = str(getattr(response, "content", response))[:200]
            return {"ok": True, "model": target_model_name, "message": "连接成功", "response": content}
        except Exception as exc:
            logger.warning("自定义模型连接测试失败: provider=%s model=%s error=%s", provider_name, target_model_name, exc)
            return {
                "ok": False,
                "model": target_model_name,
                "message": f"连接失败：{type(exc).__name__}: {exc}",
                "response": "",
            }
