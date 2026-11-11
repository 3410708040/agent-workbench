from typing import Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class TokenCounterInput(BaseModel):
    """Token 统计工具的输入模型"""
    text: str = Field(..., description="需要统计 token 数量的文本内容")


class TokenCounterTool(BaseTool):
    """Token 数量统计工具"""
    name: str = "token_counter"
    description: str = "统计给定文本的 token 数量估算值，帮助用户了解对话消耗。中文约 1.5 字/token，英文约 4 字符/token。"
    args_schema: type[BaseModel] = TokenCounterInput

    def _run(self, text: str, **kwargs: Any) -> str:
        """统计文本 token 数量"""
        if not text:
            return "文本为空，token 数量为 0"

        # 简单估算：中文字符 + 英文字符分开计算
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars

        # 估算：中文约 1.5 字/token，其他约 4 字符/token
        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)

        return f"文本长度：{len(text)} 字符\n中文字符：{chinese_chars}\n其他字符：{other_chars}\n估算 token 数：约 {estimated_tokens} tokens"

    async def _arun(self, text: str, **kwargs: Any) -> str:
        """异步统计 token 数量"""
        return self._run(text=text, **kwargs)


def token_counter(**kwargs: Any) -> BaseTool:
    """工厂函数：返回 token 统计工具"""
    return TokenCounterTool()
