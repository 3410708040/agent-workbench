from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    PrimaryKeyConstraint,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import UTC, datetime

from internal.extension.database_extension import db


def _utcnow_naive() -> datetime:
    """返回无时区的 UTC 时间，兼容数据库 DateTime 列且避免 utcnow 退化警告。"""
    return datetime.now(UTC).replace(tzinfo=None)


class CustomModelProvider(db.Model):
    """自定义模型提供商

    用户通过「模型管理」界面手动添加 OpenAI 兼容的模型服务（DeepSeek / 通义千问 / OpenAI / Ollama 等），
    运行时按 OpenAI 兼容协议实例化模型，无需修改 .env 或重启服务。
    """

    __tablename__ = "custom_model_provider"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_custom_model_provider_id"),
        Index("custom_model_provider_name_idx", "name"),
    )

    id = Column(UUID, nullable=False, server_default=text('uuid_generate_v4()'))
    # 提供商唯一标识（作为 provider 名出现在应用模型配置中）
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    label = Column(String(255), nullable=False, server_default=text("''::character varying"))
    api_key = Column(Text, nullable=False, server_default=text("''::text"))
    base_url = Column(String(1024), nullable=False, server_default=text("''::character varying"))
    # chat / completion
    model_type = Column(String(64), nullable=False, server_default=text("'chat'::character varying"))
    # 模型列表：[{"name": "deepseek-chat", "label": "deepseek-chat"}]
    models = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    # 能力特性：["tool_call", "agent_thought", "image_input"]
    features = Column(JSONB, nullable=False, server_default=text("'[\"tool_call\"]'::jsonb"))
    context_window = Column(Integer, nullable=False, server_default=text("0"))
    max_output_tokens = Column(Integer, nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
        default=_utcnow_naive,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
