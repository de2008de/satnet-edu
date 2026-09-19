SatNet Edu（satnet-edu）— Codex 交接材料

先阅读 satnet-edu-codex-plan.md（计划版本 1.1）。

本包是开发规格和参考输入，不是已完成的新仿真器。
本次修订统一项目命名与独立教育定位，保留原计划的架构、M0–M4 开发阶段和验收要求。

命名约定：
- 展示名称：SatNet Edu
- GitHub repository / 工程根目录：satnet-edu
- Python distribution 目标名称：satnet-edu
- Python import / CLI 模块：satnet_edu / python -m satnet_edu
- Web 发布文件 / 单脚本全局入口：satnet-edu-player.js / SatNetEduPlayer
- 数据格式：satnet-edu.scenario、satnet-edu.trace、satnet-edu.challenge
这些是开发命名约定，不表示已创建仓库、占用包名或发布软件。

这是独立、通用的卫星网络教育工具，不是研究 Lab，也不是 UDTJ 独占项目。
UDTJ、个人网页和其他课程网站都只是可嵌入或展示它的平台。默认 UI 标题使用 SatNet Edu。

inputs/ 中两个原 ZIP 未作修改；references/ 包含已认可 UI、视觉风格图和源码定位笔记。
原 UI 归档中的 satlab/、lab.* 路径仍是历史原名，只用于寻找参考代码；新工程按上面的命名迁移。
截图仅用作排版参考，不要求沿用其中的 UDTJ 标志、导航或旧项目标题。
论文 PDF 不在本包中；本次目标是通用教育仿真器，不是论文互动教程。

可直接给 Codex 的任务：
请依据 satnet-edu-codex-plan.md 开发 SatNet Edu，仓库/根目录名称为 satnet-edu。
先审查输入代码，依次完成 M0–M4：
基于 UserGS 原核心的 Python API → 结构化 simulation trace → 独立、可离线使用的 Web 播放器。
统一使用 satnet_edu import/CLI、satnet-edu.trace 格式和 SatNet Edu 的独立品牌。
保留精简白底黑字二维 UI。原代码归档保持不变；不要使用旧 UI 原型的自写引擎冒充研究核心。
不要在浏览器中重新仿真，不做拍卖教学，不提前做 M5+ 的挑战社区或在线执行。
每个里程碑报告实际测试、源码继承关系、未实现项和下一步；完成 v0.1 后交付。
