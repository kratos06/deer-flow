# DeerFlow技术上下文

## 技术架构
DeerFlow实现了模块化多代理系统架构，设计用于自动化研究和代码分析。系统基于LangGraph构建，支持灵活的基于状态的工作流，组件通过定义良好的消息传递系统进行通信。

主要组件包括：
1. **Coordinator**：入口点，管理工作流生命周期
2. **Planner**：任务分解和规划的战略组件
3. **Research Team**：专业代理集合，执行计划
4. **Reporter**：研究输出的最终阶段处理器
