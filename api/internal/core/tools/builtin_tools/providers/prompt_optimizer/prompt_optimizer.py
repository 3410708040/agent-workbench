from typing import Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class PromptOptimizerInput(BaseModel):
    """Prompt 优化工具的输入模型"""
    prompt: str = Field(..., description="需要优化的原始 prompt")
    target: str = Field(default="general", description="目标场景：general/general 通用，code 编程，writing 写作，analysis 分析")


class PromptOptimizerTool(BaseTool):
    """Prompt 优化工具"""
    name: str = "prompt_optimizer"
    description: str = "优化用户的 prompt，让大模型回复更准确、更高效。支持通用、编程、写作、分析等场景。"
    args_schema: type[BaseModel] = PromptOptimizerInput

    def _run(self, prompt: str, target: str = "general", **kwargs: Any) -> str:
        """优化 prompt"""
        if not prompt:
            return "请提供需要优化的 prompt 内容"

        optimized = self._build_optimized_prompt(prompt, target)

        return f"""【原始 Prompt】
{prompt}

【优化后 Prompt】
{optimized}

【优化说明】
- 明确了角色和目标
- 结构化了输出要求
- 补充了上下文引导
- 优化了逻辑层次"""

    def _build_optimized_prompt(self, prompt: str, target: str) -> str:
        """构建优化后的 prompt"""
        if target == "code":
            return f"""你是一位资深的软件工程师。请帮我完成以下编程任务：

任务描述：{prompt}

要求：
1. 先分析需求，列出实现思路
2. 给出完整可运行的代码
3. 解释关键代码的作用
4. 说明可能的边界情况和注意事项"""

        elif target == "writing":
            return f"""你是一位专业的内容创作者。请帮我创作以下内容：

主题：{prompt}

要求：
1. 先明确目标受众和写作目的
2. 结构清晰，层次分明
3. 语言流畅，有感染力
4. 结尾有明确的行动号召或总结"""

        elif target == "analysis":
            return f"""你是一位资深分析师。请帮我分析以下问题：

分析对象：{prompt}

要求：
1. 先拆解问题，列出关键维度
2. 给出结构化的分析过程
3. 总结核心结论
4. 提出可行的建议或下一步行动"""

        else:
            return f"""请帮我完成以下任务：

{prompt}

要求：
1. 先理解需求，确认目标
2. 给出清晰、有条理的回答
3. 重要内容用列表或分点说明
4. 如果有不确定的地方，请明确指出"""

    async def _arun(self, prompt: str, target: str = "general", **kwargs: Any) -> str:
        """异步优化 prompt"""
        return self._run(prompt=prompt, target=target, **kwargs)


def prompt_optimizer(**kwargs: Any) -> BaseTool:
    """工厂函数：返回 prompt 优化工具"""
    return PromptOptimizerTool()
