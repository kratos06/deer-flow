# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"
    FINANCIAL_ANALYSIS = "financial_analysis"


class Step(BaseModel):
    need_web_search: bool = Field(
        ..., description="Must be explicitly set for each step"
    )
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool
    thought: str
    title: str
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "steps": [
                        {
                            "need_web_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        }
                    ],
                },
                {
                    "has_enough_context": False,
                    "thought": (
                        "To analyze the financial status and investment value of Tencent, we need detailed financial data and market analysis."
                    ),
                    "title": "Tencent Financial Analysis Plan",
                    "steps": [
                        {
                            "need_web_search": True,
                            "title": "Tencent Financial Statement Analysis",
                            "description": (
                                "Analyze Tencent's financial statements, including balance sheet, income statement, and cash flow statement. Calculate key financial ratios and trends."
                            ),
                            "step_type": "financial_analysis",
                        }
                    ],
                }
            ]
        }
