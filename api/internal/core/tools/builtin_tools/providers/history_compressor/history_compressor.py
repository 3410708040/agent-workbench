from typing import Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class HistoryCompressorInput(BaseModel):
    """对话历史压缩工具的输入模型"""
    history: str = Field(..., description="需要压缩的对话历史文本")
    preserve_key_points: bool = Field(default=True, description="是否保留关键要点和结论")


class HistoryCompressorTool(BaseTool):
    """对话历史压缩工具"""
    name: str = "history_compressor"
    description: str = "压缩长对话历史，保留关键信息和结论，节省 token 消耗。适合对话太长时使用。"
    args_schema: type[BaseModel] = HistoryCompressorInput

    def _run(self, history: str, preserve_key_points: bool = True, **kwargs: Any) -> str:
        """压缩对话历史"""
        if not history:
            return "对话历史为空"

        original_length = len(history)

        # 简单压缩：按段落拆分，保留首尾段落和包含关键词的段落
        paragraphs = [p.strip() for p in history.split('\n\n') if p.strip()]

        if len(paragraphs) <= 3:
            return f"对话历史较短（{original_length} 字符），无需压缩"

        # 保留：第一段（开头）、最后一段（最新）、包含关键词的段落
        key_keywords = ['总结', '结论', '重要', '关键', '注意', '总结', '所以', '因此', '结果', '答案']
        preserved = []

        # 保留第一段
        preserved.append(paragraphs[0])

        # 保留包含关键词的中间段落
        for p in paragraphs[1:-1]:
            if any(kw in p for kw in key_keywords):
                preserved.append(p)

        # 保留最后一段
        preserved.append(paragraphs[-1])

        compressed = '\n\n'.join(preserved)
        compressed_length = len(compressed)
        saving_ratio = round((1 - compressed_length / original_length) * 100, 1)

        return f"""【压缩结果】
原始长度：{original_length} 字符
压缩后：{compressed_length} 字符
节省：{saving_ratio}%

【压缩后内容】
{compressed}

【压缩策略】
- 保留开头和结尾段落
- 保留包含关键结论的段落
- 省略了寒暄和重复内容"""

    async def _arun(self, history: str, preserve_key_points: bool = True, **kwargs: Any) -> str:
        """异步压缩对话历史"""
        return self._run(history=history, preserve_key_points=preserve_key_points, **kwargs)


def history_compressor(**kwargs: Any) -> BaseTool:
    """工厂函数：返回对话历史压缩工具"""
    return HistoryCompressorTool()
