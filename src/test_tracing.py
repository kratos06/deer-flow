#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
OpenTelemetry集成测试脚本

此脚本用于测试DeerFlow项目中的OpenTelemetry集成功能。
它模拟了多代理系统的行为，创建追踪跨度并验证数据是否正确发送到Jaeger。
"""

import asyncio
import logging
import time
import random
import sys
from src.tracing import DeerFlowTracer, trace_agent
from opentelemetry.trace import SpanKind

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# 初始化追踪器
tracer = DeerFlowTracer(service_name="deerflow-test")

# 模拟代理函数
@trace_agent(tracer)
async def coordinator_agent(query):
    """模拟协调器代理行为"""
    logger.info(f"协调器处理查询: {query}")
    await asyncio.sleep(0.5)  # 模拟处理延迟
    
    with tracer.start_span("coordinator_processing", kind=SpanKind.INTERNAL, attributes={"query": query}) as span:
        # 添加事件
        tracer.add_event(span, "query_received", {"query_text": query})
        
        # 模拟一些工作
        await asyncio.sleep(0.3)
        
        # 添加另一个事件
        tracer.add_event(span, "query_processed")
    
    # 决定下一步操作
    if "research" in query.lower():
        return await research_agent(query)
    else:
        return await planner_agent(query)

@trace_agent(tracer)
async def planner_agent(query):
    """模拟规划器代理行为"""
    logger.info(f"规划器创建计划: {query}")
    
    plan_steps = ["分析查询", "研究相关信息", "生成报告"]
    
    with tracer.start_span("plan_creation", kind=SpanKind.INTERNAL, attributes={"steps_count": len(plan_steps)}) as span:
        # 模拟计划创建
        for i, step in enumerate(plan_steps):
            await asyncio.sleep(0.2)
            tracer.add_event(span, "plan_step_added", {"step_number": i+1, "step_name": step})
    
    # 随机决定下一步
    if random.choice([True, False]):
        return await research_agent(query)
    else:
        return await coding_agent(query)

@trace_agent(tracer)
async def research_agent(query):
    """模拟研究者代理行为"""
    logger.info(f"研究者收集信息: {query}")
    
    try:
        with tracer.start_span("information_gathering", kind=SpanKind.INTERNAL) as span:
            # 模拟搜索步骤
            tracer.add_event(span, "search_started")
            await asyncio.sleep(0.7)
            
            # 随机引发异常来测试错误追踪
            if random.random() < 0.3:  # 30%几率产生错误
                raise Exception("模拟搜索失败")
                
            tracer.add_event(span, "search_completed", {"results_count": random.randint(5, 20)})
    except Exception as e:
        logger.error(f"研究过程出错: {str(e)}")
        # 错误已由装饰器自动记录
        return {"status": "error", "message": str(e)}
    
    return {"status": "success", "message": "研究完成"}

@trace_agent(tracer)
async def coding_agent(query):
    """模拟编码者代理行为"""
    logger.info(f"编码者分析代码: {query}")
    
    with tracer.start_span("code_analysis", kind=SpanKind.INTERNAL) as span:
        # 模拟代码分析步骤
        tracer.add_event(span, "analysis_started")
        await asyncio.sleep(0.5)
        
        # 添加一些代码分析属性
        span.set_attribute("lines_of_code", random.randint(100, 1000))
        span.set_attribute("language", "Python")
        
        tracer.add_event(span, "analysis_completed")
    
    return {"status": "success", "message": "代码分析完成"}

@trace_agent(tracer)
async def reporter_agent(results):
    """模拟报告生成器代理行为"""
    logger.info("报告生成器开始工作")
    
    with tracer.start_span("report_generation", kind=SpanKind.INTERNAL) as span:
        # 模拟报告生成
        await asyncio.sleep(0.6)
        
        # 记录报告信息
        span.set_attribute("report_type", "technical_analysis")
        span.set_attribute("sections_count", 5)
        
        tracer.add_event(span, "report_completed")
    
    return {"status": "success", "message": "报告生成完成"}

async def run_simulation():
    """模拟运行多代理系统"""
    # 创建一些测试查询
    test_queries = [
        "分析python垃圾回收机制",
        "研究分布式系统设计模式",
        "比较不同机器学习框架的性能",
        "设计一个高并发微服务架构"
    ]
    
    results = []
    
    # 为每个查询运行模拟
    for query in test_queries:
        logger.info(f"\n=== 开始处理新查询: {query} ===")
        
        # 从协调器开始
        result = await coordinator_agent(query)
        results.append(result)
        
        # 最后用报告生成器总结
        final_report = await reporter_agent(results)
        
        logger.info(f"查询处理完成: {query}")
        logger.info(f"结果: {final_report}")
        logger.info("=" * 50)

async def main():
    """主函数"""
    logger.info("OpenTelemetry集成测试开始...")
    
    # 运行模拟
    await run_simulation()
    
    # 等待一段时间，确保所有追踪数据都被发送
    logger.info("测试完成，等待数据发送...")
    await asyncio.sleep(2)
    
    logger.info("测试结束。请访问 http://localhost:16686 查看Jaeger UI中的追踪数据。")
    logger.info("查询服务名称: deerflow-test")

if __name__ == "__main__":
    asyncio.run(main()) 