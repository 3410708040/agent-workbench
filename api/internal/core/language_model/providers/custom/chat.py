from langchain_openai import ChatOpenAI
from internal.core.language_model.entities.model_entity import BaseLanguageModel
from internal.core.language_model.providers._defaults import apply_default_model_timeout


class Chat(ChatOpenAI, BaseLanguageModel):
    """通用 OpenAI 兼容聊天模型

    用于「模型管理」界面手动添加的自定义模型服务（DeepSeek / 通义千问 / OpenAI / Ollama 等），
    支持通过 attributes 显式传入 api_key 与 base_url。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **apply_default_model_timeout(kwargs))
