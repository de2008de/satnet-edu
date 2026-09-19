# SatNet Edu（`satnet-edu`）：Codex 开发计划

> **交付目标：基于原 INFOCOM 研究代码的通用 Python 卫星网络仿真器 + 结构化仿真记录 + 独立 Web 回放库。**
>
> 本文是一份开发规格，不表示下面的接口、格式或功能已经实现。请先完成 **M0–M4（v0.1）**，通过验收后停止扩大范围；网页建造、挑战与在线执行属于 **M5 以后**。

- 计划版本：1.1（命名与独立教育定位修订；实现范围与 M0–M4 顺序不变）
- 原计划日期：2026-09-18
- 本次修订日期：2026-09-19
- 正式项目名称：**SatNet Edu**
- GitHub repository 名称：`satnet-edu`
- Python import：`satnet_edu`；Web library 全局名称：`SatNetEduPlayer`。以下技术名称是本项目的实现约定，不表示已创建仓库、发布或占用了公共包名。
- 主要受众：普通学生、第一次接触卫星网络的学习者，以及希望编写小型实验的学生。
- 产品定位：**独立、通用的卫星网络教育工具，不是研究实验室，也不是某篇论文的互动教材。**
- 平台关系：**不归 UDTJ 独占，不绑定任何学校、课程或网站。** UDTJ、个人网页和其他教学平台都只是可使用或嵌入本工具的宿主。

---

## 0. 给 Codex 的执行摘要

先读完整份计划，再审查输入代码。不要从零另写一个无关的轨道引擎，然后仅在网页上加入 INFOCOM 字样。

本次开发遵循以下主流程：

```text
学生编写 Python / 加载场景配置
                  ↓
基于 UserGS 原代码提取、适配的 Python 仿真核心
                  ↓
结构化 simulation trace（JSON）
                  ↓
独立 Web UI library 读取 trace
                  ↓
二维地图回放、暂停、跳转和状态检查
```

### 本轮必须守住的决定

1. **仿真与展示分离。** Python 是模型、链路、路由和指标的计算端；播放器消费已记录的结果。
2. **log 指结构化 simulation trace，不是 stdout、调试字符串，也不是只有平均值的 CSV。**
3. **先离线可用。** 运行完 Python、关闭 Python 后，学生仍能打开导出的 HTML，或在静态播放器中导入 JSON。
4. **基础工具不依赖论文拍卖场景。** SusCO、报价、合作组选择、付款和履约可靠性均不进入默认流程。
5. **复用原研究核心需要真实可追溯。** 明确继承的函数、修改和新增能力；不能把上一轮新写的教学引擎当作原论文核心。
6. **保持已认可的 UI。** 白底黑字、二维地图、细线、衬线标题、紧凑控制栏；不要重建营销式 landing page。
7. **播放器不悄悄重新仿真。** 不在 JavaScript 中重新传播轨道、判断物理连接、运行 Dijkstra 或伪造故障后果。
8. **先完成最小闭环，再扩展。** 第一条真实闭环必须是：原核心产生一个小实验 → 写 JSON → 独立播放器读取并显示。
9. **独立教育品牌。** 新项目、文档、包和默认 UI 统一使用 SatNet Edu / `satnet-edu`；不以 Lab 或 UDTJ 前缀命名，不把 UDTJ 导航、账户或品牌资源设为运行依赖。

### 已确认的命名与平台定位

| 用途 | 统一名称 |
|---|---|
| 项目展示名、README 标题、默认播放器标题 | **SatNet Edu** |
| GitHub repository 与工程根目录 | `satnet-edu` / `satnet-edu/` |
| Python distribution 目标名称 | `satnet-edu`（是否公开发布另行决定） |
| Python import、模块目录、CLI 模块 | `satnet_edu` / `src/satnet_edu/` / `python -m satnet_edu` |
| Web library 发布文件 | `satnet-edu-player.js`；单脚本全局入口为 `SatNetEduPlayer` |
| 场景、轨迹、挑战的 format 标识 | `satnet-edu.scenario` / `satnet-edu.trace` / `satnet-edu.challenge` |
| 本开发计划文件 | `satnet-edu-codex-plan.md` |

Python import 使用下划线形式；仓库名与 distribution 名使用连字符形式。示例、包配置、CLI、schema 和播放器必须使用同一套约定，不保留相互冲突的新旧命名。

项目的默认介绍：

> **Build satellite networks. Explore how they work.**
>
> An educational satellite networking toolkit with a simple Python API and an embeddable, trace-driven web viewer.

默认独立 demo 展示 SatNet Edu，不强制带 UDTJ 页眉、徽标或链接；宿主页面可自行添加自己的外围导航。研究背景放在 `Research origins` / `PROVENANCE.md`，不把会议名变成教育工具的品牌。后续挑战功能仍按 M5+ 实现，未完成前不得写成现成功能。

本修订只更新开发规格与交接命名，不表示已有参考代码已经迁移。§3.2 中的旧 UI 路径以及 `inputs/`、`references/` 的历史文件名保持真实原名，供 Codex 正确定位；不得为了更名改动原始归档或抹除原作者、第三方与素材来源。

### 本次第一条指令

> 在新开发目录或分支中保留原始资料，完成 M0 的代码审查和依赖核对，随后依次实施 M1–M4。每个里程碑提交可运行的代码、测试与进度记录。不要止步于再次写计划，也不要提前做在线账户、拍卖教学或挑战社区。

---

## 1. 输入资料与证据边界

### 1.1 应提供给 Codex 的文件

| 优先级 | 文件 | 用途 |
|---|---|---|
| 必需 | `UserGS_simulation-main.zip` | 原研究代码；新引擎的来源。 |
| 必需 | 本 Markdown | 产品范围、实现顺序和验收标准。 |
| 强烈建议 | `orbits_to_routes_simple_python.zip` | 已认可的精简 UI 源码；主要复用地图、样式、控件和本地地图资产。 |
| 建议 | `orbits_to_routes_simple_preview.png` | 精简 UI 的视觉参照。 |
| 建议 | `e1d797cb-63ea-4a08-9094-3d617826563d.png` | 用户提供的 UDTJ 网站视觉风格参照；仅参考排版，不沿用站点品牌或导航。 |
| 建议 | `UserGS_framework_source_notes.md` | 先前的源码定位记录；只作导航，事实以当前 ZIP 为准。 |
| 可选 | INFOCOM 论文 PDF | 仅用于来源与模型边界核对，不把它变成当前产品的课程大纲。 |

随附材料包中，ZIP 放在 `inputs/`，图片和源码笔记放在 `references/`。单独使用本 Markdown 时，按上述文件名寻找输入，不依赖任何聊天会话或 `/mnt/data/` 绝对路径。

### 1.2 已确认的输入标识

原 ZIP：

```text
UserGS_simulation-main.zip
SHA-256: 93bca9f4c25352f3d8320bcb809ad3d593c91bf697b722a4e830a2e24ecdb2dc
```

精简 UI ZIP：

```text
orbits_to_routes_simple_python.zip
SHA-256: 1dc40a366d46a1daeec06e896c2cf491af4f1f5966a573ca1e2e792a39deeeef
```

哈希用于识别本计划依据的输入版本，不是软件正确性证明。若收到的 ZIP 不同，先记录差异并重新核对相关位置。

### 1.3 区分三种信息

- **源代码观察**：下文 §3 的文件路径和行为，依据以上 ZIP 的静态检查。
- **用户确认的需求**：日志驱动架构、简洁二维 UI、友好 Python API、后续建造与挑战。
- **本计划的新设计**：`Network` 适配、trace schema、独立播放器、物理链路检查、测试和分阶段交付；不要说成原代码已经实现。

先前对话中的旧原型测试数字，不是本次 UserGS 教育版的测试结果。本次必须重新测试。未完成原研究全实验复现，不以此作为本轮前置条件，也不宣称已经完成。

---

## 2. 产品范围：现在做什么，不做什么

### 2.1 v0.1 必做

- 可安装、可单独使用的 Python 包；目标运行环境先采用原 README 使用的 Python 3.11。
- 从原 UserGS 提取和重构的星座创建、轨道位置计算与时间处理。
- 常规星座、通用地面站、星间链路与地面接入的清晰模型。
- 无副作用的状态查询与路径查询。
- 最少跳数、最小单向传播时延两种内置选路。
- 原始状态、选定路径及相关指标的 JSON trace 导出。
- 独立 Web library：读文件、播放、暂停、单步、跳转、选择已记录查询、检查对象。
- 独立品牌的静态播放器 demo；可嵌入任何教学网站、课程页面或个人网页，UDTJ 只是其中一个使用示例。
- 一键导出自包含 HTML，供离线打开与分享。
- 示例、schema、来源说明、模型说明、测试与安装文档。

### 2.2 后续阶段，不纳入 v0.1 完成条件

- 网页点击添加轨道、放置卫星的场景编辑器。
- 覆盖、连通、时延与资源上限的挑战定义和自动评估。
- 学生创建挑战、提交自己的可行方案并分享题目。
- 网页提交配置给 Python 服务运行的可选桥接。
- 能源、日照、GS 合作卸载等可选扩展。
- 更大数据量的分块、压缩、增量 trace。

### 2.3 明确不做

不做论文算法课程；不复现全部论文图表；不默认启用拍卖、预算或 GS 商业报价；不做账户、排行榜或社区；不优先做 3D 地球；不做流量队列、TCP/UDP、拥塞或路由协议收敛仿真；不宣称真实运营星座性能；不接收陌生用户的任意 Python 代码在公网执行。

基础模式的指标应写 **one-way propagation delay / 单向传播时延**，不能标成完整网络延迟、RTT 或应用响应时间。

---

## 3. 原代码的复用地图与改造注意事项

以下路径相对于原 ZIP 中的 `UserGS_simulation-main/`。行号对应当前输入版本，后续重构后应保留映射。

| 来源 | 已观察到的行为 | 本轮处理 |
|---|---|---|
| `README.md:5–14` | 标明原结果使用 Python 3.11，入口是 `source/main.py`，数据写入 output。 | 用于环境审查；不要把批量论文入口作为新包的 import 副作用。 |
| `source/helpers/generate_tle.py:17–24,63–141` | 使用 `sgp4` 构造合成 TLE；固定历元、近圆轨道、RAAN 与奇数轨道半间隔相位；另有改写 TLE 第一行的逻辑。 | 核心候选。保留来源，显式管理 epoch 和相位；不能无声替换为另一种 Walker 参数约定。 |
| `source/helpers/read_tles.py:62–79` | 从 TLE 解析历元并构造 `ephem` 对象；其中出现 `scale="tdb"`。 | 核对时间尺度与接口含义；不要直接把标签改为 UTC 却不检查数值。 |
| `source/models/satellite.py:9–47` | 创建卫星时同时创建随机电池状态并生成轨道对象。 | 分离轨道状态和能源扩展；基础网络不必抽样电池寿命。 |
| `source/models/satellite.py:119–138` | 根据同一 observer 下的角度与 range 求卫星间距离；注释说明借鉴 Hypatia。 | 可复用/作对照；保留第三方来源并核对许可。 |
| `source/models/constellation.py:9–54` | 根据规则生成星座，并按时间更新卫星的 `ephem` 状态。 | 提取为通用星座和传播适配器；与用户分布、随机耗电解耦。 |
| `source/models/topology.py:10–39` | 原图按轨道/卫星编号建立前后、左右固定邻接，边权为 1；没有在这里执行每时刻地球遮挡检查。 | 保留候选邻接逻辑，新增明确的物理可用性过滤；区分“被安排为邻居”和“当前可通信”。 |
| `source/simulation.py:6–73` | 注册回调、按步执行、推进 `TimeStep`。 | 复用时间推进与事件组织思想/实现中适合的部分，消除共享可变默认参数与全局状态依赖。 |
| `source/models/task.py:47–51` | 原最短路实际通过 NetworkX 的 `shortest_path` 计算。 | 提取成查询函数，不让普通选路依赖论文 Task 或 Bid。 |
| `source/models/routing.py:32–96` | `route_traffic()` 会更新流量、耗电、卸载/失败与统计；不是只读选路。 | 不作为地图“查看路径”的直接接口。 |
| `source/models/delay_manager.py:16–35,45–55,64–93` | 混合传播、排队、传输和卸载估计；部分 GSL 使用固定 550 km。 | 基础模式只保留/整理传播距离逻辑；地空距离按实际几何计算。其余研究模型保留在可选区，不默认导入。 |
| `source/models/dish.py` | 地理位置、容量与报价/履约绑定。 | 新建通用 `GroundStation` 数据对象，明确这是解耦改造，不要求普通 GS 参与拍卖。 |
| `source/models/data_manager.py:9–32` | 按实验/预算/算法目录写不同 CSV。 | 不直接等同于回放 trace；新建通用 recorder。 |
| `source/models/energy.py:4–13` | 每步充电量按原 60 秒间隔设定。 | 后续能源模块接入时，必须按实际 `dt` 处理；本轮不默认启用。 |
| `source/main.py:30–79,89–135` | 固定研究参数、回调链和批量多进程实验。 | 不运行整套批实验来启动播放器，不在 import 时触发。 |

### 3.1 已知需要复核的边界

1. 原邻接算法在单轨道面小配置下可能产生自环；新代码要有 `1×1`、`1×3`、`2×3` 测试。保留原始文件，不直接修改归档以掩盖差异。
2. 原卫星整数 ID 与列表位置/轨道位置存在耦合；公共 API 使用稳定字符串 ID，内部显式映射，不能靠字符串解析或 `id == list index`。
3. `generate_tle.py` 中的 TLE 第一行改写包含历元文本；开放 epoch 时要检查实际导出的 TLE，而非只改 Python 参数。
4. `helpers/distance.py` 引用了归档中未出现的 `tles.generate_tle` 路径；不要不加审查地把整目录全部导入。
5. 原 requirements 包含绘图/统计及宽泛依赖，部分源码还有其他导入；先做 import 审查，再为新包整理必要依赖。不要为了“全部安装成功”盲装来源不明的包。
6. 原文件有 Hypatia 来源注释，但本次 ZIP 未提供顶层 LICENSE；保留归属，建立 `THIRD_PARTY_NOTICES.md` 和许可待核对记录。未确认前，不擅自给整套衍生代码授予一个新许可证或发布公共包。

### 3.2 旧 UI 的复用边界特别重要

精简 UI ZIP 中，前缀是 `orbits_to_routes/`：

- 视觉/交互参考：`satlab/assets/lab.html`、`lab.css`、`lab.js`。
- 本地地图资产：`satlab/assets/coastlines.json`，保留来源说明。
- 旧 `satlab/model.py` 是此前另写的教学模型，**不是本次的 INFOCOM 核心来源**。
- 旧 `lab.js` 中有 `route()`、`recalculate()` 和停用节点后重算路径的逻辑。新播放器应移除这类模型计算，而非原样复制。
- 旧页面可任意切换端点/故障，是因为它在浏览器里重算；新 trace-only 播放器只允许选择已经记录的查询或运行。
- 旧 `export.py` 的安全内嵌方式可作参考，但应调用同一份新播放器构建产物，不另维护一套复制代码。

---

## 4. 建议的目录与依赖边界

在新仓库或隔离目录开发。原始归档保持不变；参考代码不作为隐式环境路径。

```text
satnet-edu/
├── pyproject.toml
├── README.md
├── DEVELOPMENT_STATUS.md
├── src/satnet_edu/
│   ├── __init__.py
│   ├── network.py             # 学生使用的 facade
│   ├── config.py              # 可序列化场景配置
│   ├── state.py               # Snapshot / NodeState / LinkState / Route
│   ├── engine/
│   │   ├── usergs_adapter.py  # 原核心提取/重构后的入口
│   │   ├── orbit.py
│   │   ├── clock.py
│   │   ├── geometry.py
│   │   ├── topology.py
│   │   └── routing.py
│   ├── trace/
│   │   ├── recorder.py
│   │   ├── validate.py
│   │   └── io.py
│   ├── export.py              # 将 trace + 同一播放器打包
│   ├── cli.py
│   └── assets/               # 打包用的播放器发布产物，不手工维护第二份逻辑
├── schemas/
│   ├── scenario.schema.json
│   └── trace.schema.json
├── web/
│   ├── player/src/            # 独立组件；不依赖任意宿主页的品牌或全局变量
│   ├── player/dist/           # ESM + 可离线嵌入的单脚本发布版
│   ├── assets/                # 本地海岸线与归属说明
│   └── demo/                  # 静态文件导入页与双实例示例
├── examples/
│   ├── first_network.py
│   ├── compare_routes.py
│   ├── scheduled_failure.py
│   ├── custom_constellation.py
│   └── data/                  # 由真实引擎生成的小 trace
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── API.md
│   ├── TRACE_FORMAT.md
│   ├── MODEL.md
│   ├── PROVENANCE.md
│   ├── LEGACY_AUDIT.md
│   ├── MIGRATION.md
│   └── TEST_REPORT.md
└── THIRD_PARTY_NOTICES.md
```

目录可按实际工程略调，但保持三条依赖规则：

- 核心 Python 不依赖浏览器、Web server、UI 组件或论文绘图脚本。
- Web library 不依赖 Python 正在运行，也不读取 Python 内部对象。
- 两端依赖共同的数据契约；`export_html()` 只是打包器。

建议沿用已存在的 Python 科学计算依赖中真正需要的部分；Web 侧用轻量 JavaScript/TypeScript 模块，不强制 React/Vue。构建工具是开发依赖；学生安装 Python 包或打开最终 HTML 时，不应必须安装 Node 或进行前端构建。

---

## 5. Python API：目标用法与行为契约

本节均为本次待实现 API，不是原 UserGS 已有接口。优先稳定名字和单位，避免让学生操作 `TimeStep`、Bid 或内部 `ephem` 对象。

### 5.1 最小示例

```python
from satnet_edu import Network

net = Network(
    "My satellite network",
    epoch="2000-01-01T00:00:00Z",  # 示例基准，不是实时卫星数据
    seed=42,
)

net.add_constellation(
    planes=6,
    sats_per_plane=12,
    altitude_km=1000,
    inclination_deg=53,
)
net.add_ground_station("A", lat=49.28, lon=-123.12, label="Vancouver")
net.add_ground_station("B", lat=35.68, lon=139.69, label="Tokyo")
net.set_link_policy(
    topology="orbital_neighbors",
    max_isl_km=4000,
    min_elevation_deg=10,
)

run = net.run(
    duration_s=1800,
    step_s=5,
    record_routes=[("A", "B")],  # 简写，默认 metric="delay"
)
run.save("outputs/experiment.json")
run.export_html("outputs/experiment.html", language="en")
```

上述参数只展示用法，不保证 A—B 在整个时段连通。示例生成后应报告真实结果；不要为了让 demo 连通而绕过遮挡或偷偷增加链路。

### 5.2 状态查询与路由比较

```python
from satnet_edu import RouteQuery

snapshot = net.at(120)
route = snapshot.route("A", "B", metric="delay")

if route.reachable:
    print(route.path)
    print(route.hops, route.distance_km, route.propagation_ms)
else:
    print(route.reason)

run = net.run(
    duration_s=1800,
    step_s=5,
    record_routes=[
        RouteQuery(id="A-B-delay", source="A", target="B", metric="delay"),
        RouteQuery(id="A-B-hops", source="A", target="B", metric="hops"),
    ],
)
```

播放器中的路由选项来自 `RouteQuery` 清单，不通过选择下拉框重新算路径。多记录一条查询才多提供一个可回放结果。

### 5.3 MVP 必须明确的 API 语义

| API/对象 | 行为 |
|---|---|
| `Network(name, epoch=..., seed=...)` | epoch 明确为 `t=0` 的 UTC 基准；合成轨道的实际 TLE epoch 也要被正确设置并记录。缺省值必须固定且文档化，不能隐式用今天。 |
| `add_constellation(...)` | 返回星座标识/描述对象；内部产生稳定 ID。默认相位保留原代码的交替半槽语义并记录其名称，不能假称为任意标准星座。 |
| `add_ground_station(id, lat, lon, label=None)` | GS 是普通网络端点，不创建报价、商业容量或信誉状态。 |
| `set_link_policy(...)` | 保存可序列化规则；单位明确。 |
| `at(t_s, disabled=())` | 无副作用地得到该时刻完整快照；调用顺序不影响结果，不扣电、不推进隐藏时钟、不消耗随机数。 |
| `Snapshot.nodes / links` | 稳定 ID 的只读或独立副本，供学生编写自己的分析；不能泄露共享可变传播对象。 |
| `Snapshot.route(...)` | 只读查询；支持 `delay`、`hops`。 |
| `run(start_s=0, duration_s=..., step_s=..., record_routes=...)` | 从配置独立运行，生成可回放结果；相同配置不因上一次运行残留状态而改变。 |
| `Run.save(path, pretty=False)` | 写出经过验证的标准 trace，返回实际 `Path`。 |
| `Run.export_html(path, language="en")` | 安全内嵌同一 trace 和同一份发布版播放器；不再运行仿真。 |
| `Network.to_dict() / from_dict()` | 场景配置往返，无代码执行；不从 trace 猜回缺失配置。 |

所有数值输入检查 finite、类型与范围；不要把 `True` 当作卫星数量 1。使用清楚的 `ValueError` 或项目异常类型，并指明错误字段。

`Route` 至少有 `reachable`、`path`、`link_ids`、`hops`、`distance_km`、`propagation_ms`、`metric`、`reason`。不连通时路径为空，数值指标为 `None`；未知节点是输入错误，不是不连通。合法自查询返回单节点、0 跳、0 时延。网页可只展示不同端点的查询。

### 5.4 预设故障：由 Python 计算，不由播放器伪造

M2/M4 提供一个简单可序列化的时间故障，例如：

```python
net.add_failure(node_id="S01-01", start_s=300, end_s=600)
```

区间定义为 `[start_s, end_s)`，开始前正常、开始时禁用、结束时恢复。`at(t_s, disabled=...)` 在该时刻的预设故障之外叠加显式 disabled；只影响返回快照，不修改场景或后续运行。在 trace 中仍保留节点位置和 `enabled=false`，删除其可用链路，并由 Python 重算记录中的路由。正常对照需要独立正常运行的 trace，不能拿上个时刻冒充。

### 5.5 学生扩展点与后续接口

v0.1 至少公开快照节点/边，允许学生独立分析。精确控制轨道的接口应在核心抽取时预留：

```python
net.add_satellite(
    "Test-1",
    altitude_km=1000,
    inclination_deg=60,
    raan_deg=20,
    phase_deg=45,
)
```

`phase_deg` 的轨道含义必须写清，不是地面经度；与原合成 TLE 初始相位定义保持可解释的对应。逐颗添加和自定义连线回调可在 M4 作为增强，若阻碍主要闭环，应记录并推迟，不能假装已完成。

任意 Python 策略只在本地可信环境执行。回调不能序列化为可执行字符串放入公开 JSON；未来需要插件名/版本及显式本地注册。trace 仍可回放插件输出，但不等于只有 JSON 就能重新运行插件。

---

## 6. 引擎语义：保留研究来源，明确教育版的新假设

### 6.1 时间与轨道

先让原合成 TLE → 原传播路径工作，并保存小型对照结果，再做解耦。不得跳过原路径直接换成前一版教学圆轨道代码。

教育 API 新增 epoch/参数时，建立明确的兼容测试。记录合成轨道参数、实际 TLE、传播器及依赖版本。地图二维展示不代表轨道或链路距离用二维坐标计算。

### 6.2 坐标系：M0 必须冻结一项明确决定

公共快照至少包含：`position_ecef_km`、`lat_deg`、`lon_deg`、`altitude_km`。所有模型距离使用同一时刻、同一地球固定坐标系的三维状态。

原代码不直接提供新的完整 ECEF trace 契约。实现前必须核对已有 `ephem` 字段的坐标/高度定义，选择并记录 `earth_model`、`latitude_kind` 和转换方式。不要把地理纬度直接当作地心纬度、把 TEME/ECI 当作 ECEF，或拼接两个不相容的地球模型。

允许选择有明确说明的球形地球教学几何，但必须：

- 明示它是教育版新增/简化模型；写出实际半径与单位。
- 从原传播结果得到一致的三维状态；不能只为动画重新生成位置。
- 地面站、仰角和遮挡使用相容的几何定义。
- 以原星间距离函数或可验证的几何案例进行对照，记录容差和差异来源。

这一选择只需形成简短 ADR，不需要无限扩展为航天精度研究。

### 6.3 连接规则

将连接分为“候选边”和“当前可用边”：

- `orbital_neighbors`：从原规则星座的同轨前后邻居、邻轨对应槽位生成候选边，去除自环和重复。
- 可选 `distance`：适用于手动卫星或不同星座；检查所有候选对后按物理与距离条件连线。明确它不代表真实卫星拥有无限通信终端。
- 候选边必须通过地球遮挡、最大 ISL 距离、节点 enabled 等检查后才写入可用边。
- GSL 必须检查最低仰角，距离使用真实斜距，不使用轨道高度或二维地图线长替代。
- v0.1 为无向链路；GS 只作路由端点，没有默认地面互联网捷径，也不能作免费的中间中继。
- 不同 shell 不自动按相同数组索引连线。手动卫星与 `orbital_neighbors` 不适配时给出说明，要求选择适用规则，不静默猜测。

物理过滤与通用 GS 接入属于本次新增能力，不宣称与原论文所有网络假设完全相同。回归比较只对齐共同且明确的假设。

### 6.4 路由与度量

- `delay`：主目标为所有链路传播时延之和；`hops`：主目标为边数。
- 建议确定性 tie-break：主目标相同，比较另一目标；再比较稳定节点 ID 序列。浮点相等策略写入测试，不随图构建顺序随机改变。
- `propagation_ms = distance_km / c_km_s × 1000`；常数值记录在模型元数据中。
- 不存在路径是正常实验结果。不能抛异常中断整次仿真、记为 0 ms，或人为建立穿地链路。
- 路径是当前拓扑上的快照查询，不包含分布式协议收敛时间。
- 即使播放“包沿路径移动”的解释动画，也必须标记为示意；v0.1 没有分组级通信引擎。

---

## 7. 三类文件分清：场景、轨迹、挑战

| 文件类型 | 建议 format | 内容 | 谁消费 |
|---|---|---|---|
| 场景配置 | `satnet-edu.scenario` | 网络、轨道、地面站、链路策略、时钟、预设故障、查询配置 | Python 引擎；后续网页编辑器 |
| 仿真轨迹 | `satnet-edu.trace` | 一次运行的已记录状态、路径、指标和事件 | Web 播放器、离线分析工具 |
| 挑战定义（后续） | `satnet-edu.challenge` | 固定环境、允许编辑项、资源上限、评估规则 | Python 评估器、挑战编辑器 |

用例：编辑器产生 scenario → Python 运行 → 产生 trace → 播放器展示。不要让播放器通过移动图标直接修改已有 trace 的“真实结果”。

调试日志仍可另存 `.log`；它不是 trace schema 的一部分。

---

## 8. Trace v1：跨 Python 与网页的数据契约

### 8.1 格式策略

第一版使用 UTF-8 JSON，完整快照；格式标识 `satnet-edu.trace`，独立 `schema_version="1.0.0"`。引擎版本和格式版本分开。

- 数组按时间/稳定 ID 确定排序，不把 list position 当作永久节点 ID。
- 禁止 JSON 中的 NaN、Infinity、Python 对象 repr、pickle 或任意执行代码。
- `null` 表示明确缺失的数值，不能与零混用。
- 每一条声明记录的 route query 在每个 frame 都有结果；不连通也要显式记录。
- schema 做结构校验，额外做引用、时间、单位和路径一致性检查。
- trace 不包含原论文 PDF、账户信息、访问令牌或机器绝对路径。

### 8.2 顶层字段（目标契约）

| 字段 | 要求 |
|---|---|
| `format` | 固定为 `satnet-edu.trace`。 |
| `schema_version` | `1.0.0`；不支持的主版本应清楚报错。 |
| `producer` | 引擎名称、版本、源码修订/原 ZIP 标识、关键依赖版本；若没有 Git commit 不能编造。 |
| `experiment` | ID、名称、epoch UTC、seed、可序列化 scenario 或对它的完整内嵌描述。 |
| `model` | 传播器、地球/坐标定义、长度/角度/时间单位、链路规则、传播时延模型、限制。 |
| `recording` | 起止相对秒、目标步长、实际 sample_count、route_queries、已记录/未记录能力。 |
| `objects` | 稳定卫星/轨道/地面站定义。显示 label 与 ID 分离。 |
| `frames` | 按 `t_s` 升序排列的完整快照。 |
| `events` | 可空；由引擎记录的采样变化或预设事件，不是浏览器猜出来的真实发生时刻。 |
| `summary` | 可选；Python 计算的汇总，声明分母、时间范围与采样口径。 |
| `extensions` | 可选命名空间，供后续能耗等使用；不能覆盖核心字段语义。 |

能力元数据应能让播放器判断 `routes`、`energy`、`packet_events` 是否被记录。没有记录电量时显示“未记录”，不要默认 100%；没有记录路径时显示“未记录路径”，不要显示“网络不连通”。

### 8.3 每帧的最低内容

```text
Frame
  t_s: number
  node_states: [
    id, enabled,
    position_ecef_km: [x, y, z],
    lat_deg, lon_deg, altitude_km
  ]
  links: [
    id, source, target,
    kind: "isl" | "gsl",
    distance_km, propagation_ms
  ]
  routes: [
    query_id,
    status: "reachable" | "unreachable",
    node_ids: [...], link_ids: [...],
    hops, distance_km, propagation_ms,
    reason
  ]
```

在结构有效的完整 trace 中，不允许漏掉声明过的节点状态或查询结果后让前端猜。节点失效仍有位置；其 `enabled=false`，且没有可用 incident links。

不可达 route：`node_ids=[]`、`link_ids=[]`，`hops/distance_km/propagation_ms=null`，reason 可用稳定代码例如 `no_path` 或 `endpoint_disabled`。未知 query、悬空节点引用、路径使用不存在的边都属于坏文件，不是正常不连通。

未来加入任意策略时，query 记录策略 ID/版本，结果仍符合相同 route 契约。播放器只需要会显示结果，不需要安装策略。

### 8.4 精确时间语义

- `epoch_utc` 是 `t_s=0` 的基准，不依赖运行电脑的本地时区。
- frame 时间使用实际相对秒，不靠 `index × step_s` 恢复。
- 基本采样包含开始与结束；例如 `start=0,duration=10,step=4` 输出 `[0,4,8,10]`，不重复末帧。
- MVP 预设故障的起止时刻并入采样集合：`常规采样 ∪ 范围内事件边界`，排序去重。
- 同一时刻先应用预设事件/故障状态，再计算并记录快照。
- `duration=0` 可以导出单帧供检查；不能拿它计算时间覆盖比例。
- 对由采样发现的变化，记录 `observed_at_sample`，不要声称精确得到了两个采样点之间的发生时间。

### 8.5 不把回放等同于可重运行

trace 必须保存运行依据：场景配置、实际轨道参数/TLE、种子、规则、依赖与引擎标识。它足以原样回放，不保证任何未来依赖版本都逐 bit 复现。

标准配置应能重新运行并在规定容差下对照。自定义插件存在时，明确它需要插件源码/注册环境；不能悄悄回退为默认算法。

若有 `created_at_utc` 这类生成时间，用作附加信息即可；确定性测试比较稳定 payload，不让墙上时间或随机运行 ID 破坏“相同配置得到相同模型结果”。

### 8.6 正式 fixture 的要求

Codex 在冻结 schema 后创建：

- 一个最小合法 trace；
- 一个真实 UserGS 适配器生成的多帧 trace；
- 一个有可达和不可达查询的 trace；
- 一个含预设故障和恢复的 trace；
- 不合法版本、NaN/Infinity、重复 ID、未知边、缺失查询等坏文件 fixture。

手写结构 fixture 可以测试解析器，但必须命名 `synthetic-contract-fixture`，不能当成“真实引擎已运行”的证明。演示 trace 必须由实际 Python 引擎产生。

---

## 9. Web UI library：只展示已记录的世界

### 9.1 目标接口

```javascript
import { createPlayer } from "./satnet-edu-player.js";

const player = createPlayer(document.getElementById("satnet-edu-viewer"), {
  language: "en",
  showInspector: true,
});

await player.load(traceObject);       // 同时执行格式与语义检查
player.play();
player.pause();
player.seek(120);                     // 单位为相对秒
player.setSpeed(60);                  // 每真实秒播放 60 仿真秒
player.selectQuery("A-B-delay");     // 仅选择 trace 里存在的 query
player.destroy();
```

这是待实现的目标，不表示已有公共 npm 包。给出一个无需框架的 demo 和可复制的嵌入代码。

library 对象与 standalone 页面分离：读取文件的按钮可以属于 demo wrapper；默认 standalone 页面标题为 SatNet Edu。UDTJ 或其他宿主的页眉只由各自的外围页面提供，不进入库的依赖或默认品牌。

### 9.2 最低播放器能力

- 文件选择与拖入 JSON；默认本地解析，不上传。
- 播放、暂停、上一步/下一步、回到开头、时间轴跳转、速度选择。
- 2D 地图上的卫星、GS、ISL/GSL 和当前记录路径。
- 切换已记录的 route query；没有记录的目标不提供可用选项。
- 点击节点/边打开右侧检查器，显示 trace 中对应数据。
- 关闭其他链路、切换标签等仅影响展示的选项。
- 清楚显示模型类型、采样时间和“单向传播时延”。
- 中文/英文文案表，不把按钮标签硬编码进计算逻辑。
- 同一页面两个 player 实例独立工作；CSS 作用域和事件不冲突。
- 重复加载、销毁时释放 RAF、监听器与对象 URL。

### 9.3 不允许进入 Player 的功能

禁止保留旧 UI 的浏览器选路/故障重算。禁止从两帧位置重新计算链路可用性或认证挑战成绩。禁止直接把 trace 内容放入 `innerHTML` 或作为脚本执行。

如果用户在播放器里点击“停用卫星”，本轮应没有这个操作；可以显示已经录制的故障状态。后续 editor 可把这类操作转换为新 scenario，要求重新运行，而不是修改当前 trace。

### 9.4 回放精度与插值

v0.1 先采用离散帧回放，seek 选择不晚于目标时刻的最近采样点，并显示实际采样时间。范围外输入夹到范围端点或明示错误，采用一种一致策略并测试。

平滑动画可后续添加：只对显示位置做处理，不能生成新的链路、路径、性能指标；暂停检查落到真实采样时刻。经度跨 ±180° 不能从地图中央反向横穿。

地图始终固定范围，不随卫星位置自动缩放。地图上的线是三维链路的二维呈现，不以屏幕长度计算距离；世界边界处拆线，避免一条链路错误横贯整张图。

---

## 10. UI 视觉规格：沿用用户认可的精简版

### 必须保留

白/近白背景，黑字与灰色辅助线；衬线标题；简洁无装饰的控件；地图为页面主体；细边框；图例、单位与时间清楚。卫星与地面站使用不同形状，选中路径用线宽/线型突出，不只依赖颜色。

默认布局：

```text
轻量标题 / 导入文件 / 语言
────────────────────────────────────────
播放  单步  时间轴  时间  速度
──────────────────────────┬─────────────
                          │ 已记录查询
        二维地图          │ 当前结果
                          │ 对象检查器
                          │ （按需展开）
──────────────────────────┴─────────────
采样与模型说明（短行） / 文件导出
```

### 不再加回来

大幅宣传语、渐变、发光、星空壁纸、卡片瀑布、徽章、排行榜；默认展开的长篇模型介绍；下半页的时延曲线、逐跳大表格、问答、实验笔记和教程章节。API 与方法说明放独立文档或简短弹窗。

保留研究来源的短句/入口，但不把 INFOCOM logo 或“顶会级”作为主视觉。默认产品标题为 **SatNet Edu**，具体实验名称作为次级标题或记录名称；不使用 Lab 或 UDTJ 作为新项目品牌。

### 可访问性与嵌入

控件支持键盘、标签和可见焦点；地图信息不能只有 hover 才能读取；长 label 不撑坏布局；移动端可将检查器折叠到地图后，不出现页面水平溢出。UI 库不污染宿主页的 `body`、通用 `button` 或全局 ID。

地图资产沿用本地资源并附归属；不要默认请求在线地图瓦片或字体。不要复制、分发系统字体文件。

---

## 11. 离线导出与静态部署

提供三种交付形式，底层共用同一 trace 解析器和播放器：

1. **JSON**：`Run.save()`，学生导入静态播放器。
2. **自包含 HTML**：`Run.export_html()`，内嵌 trace、地图、CSS 和播放器单脚本。
3. **Web library 分发目录**：供任意教学网站、课程页面或个人网页以模块或经典脚本嵌入；另带 SatNet Edu 静态 demo。UDTJ 是可选宿主之一。

v0.1 离线 HTML 在 `file://` 双击打开时，不依赖相邻文件的 `fetch()`、远程 CDN 或模块加载。单文件使用打包的经典脚本/IIFE 版本；模块版留给 HTTP 托管页面。

安全要求：

- 内嵌 JSON 时对 `<`、`>`、`&` 及适当字符进行安全编码，防止 label 中的 `</script>` 结束脚本块。
- 标签/描述以 `textContent` 或等效安全方式呈现。
- 校验文件大小与结构；对过大的记录报明确错误，不静默截断数据。
- 只加载用户指定文件，不读取任意本地路径；格式字段不允许执行脚本或下载附带的“插件”。
- 本地 trace 内容可能暴露用户自定义地点；默认不自动上传或记录分析事件。

核心仿真不依赖 Flask/FastAPI、数据库、WebSocket 或公网服务。需要一个本地静态文件服务器时，它只是开发便利工具，不是实时仿真后端。

---

## 12. 复现、规模与故障处理

### 12.1 复现标准

- 明确 epoch、seed、实际采样时刻、轨道参数、模型常数、算法与版本。
- 使用局部 RNG；不得在查询时改变全局随机状态。
- 同配置、同版本和同依赖环境重复运行，稳定结果一致。
- 浮点容差以单位定义，并依据适配对照确定；不能放宽到足以掩盖坐标系错误。
- 保留原来源与新实现的对应关系；回归测试只对齐共同模型，不要求新增物理过滤后的路由与原固定图完全相同。

### 12.2 暂定基准场景（是测试规模，不是已经验证的性能承诺）

| 规模 | 卫星数 | 采样数 | 用途 |
|---|---:|---:|---|
| 小 | 24 | 61 | 开发与集成测试 |
| 标准 | 72 | 361 | 教学 demo 与回放性能 |
| 较大 | 144 | 721 | 记录体积、内存与载入观察 |

记录 Python 运行时间、trace 大小、浏览器解析/渲染时间和峰值内存（测不到的项目明确标记）。不要用模拟时间长度推断实际耗时，不预先保证帧率。

设置可配置的节点、采样和文件大小保护，具体默认值在测试后确定。不能为了满足大小限制而删掉查询结果、丢弃断连帧或减少采样却不更新元数据。优先给出明确限制，再考虑分块压缩。

### 12.3 常见失败的用户提示

- 配置错误：给字段路径和允许范围。
- 依赖缺失：指出安装/环境步骤，不回退到一个隐藏的假引擎。
- 未知 trace 版本：说明支持的版本。
- trace 坏引用/坏路径：指出帧与对象 ID。
- 已运行但无路径：正常显示 `No path at this sample`。
- 没有记录该数据：显示 `Not recorded`，与上项区分。

---

## 13. 里程碑与每阶段验收

所有任务初始均未完成。完成后在 `DEVELOPMENT_STATUS.md` 标明实际命令、结果、遗留问题和对应提交，不照抄旧原型的测试报告。

### M0 — 原核心审查与最小来源验证

**输出**：`LEGACY_AUDIT.md`、`PROVENANCE.md` 初版、依赖清单、坐标/时间 ADR、小型原核心运行 fixture。

- [ ] 核对输入 ZIP/实际源码；归档不修改。
- [ ] 找到可运行的合成轨道与位置更新路径，不执行全批量 `main.py`。
- [ ] 记录必须解耦的随机电池、用户分布、路径与全局参数。
- [ ] 在少量卫星、若干时刻运行原传播/距离逻辑；保存配置、输出和环境。
- [ ] 核对 epoch、坐标含义与单位，说明教育几何决策。
- [ ] 记录第三方来源、缺失许可/依赖，不自行编造授权。

**通过条件**：有可复现的小型原核心结果及明确复用路线。若来源代码确实不可执行，报告具体异常与最小阻塞；不能悄悄用旧教学引擎代替并标为成功。

### M1 — 第一条真实端到端通路

**输出**：最小 `Network`、初版 trace schema/recorder、只显示/跳转的最小 player。

- [ ] 从原核心产生卫星位置、多帧状态，写入结构化 JSON。
- [ ] 最小播放器读取实际 JSON，在二维地图显示并前后切换帧。
- [ ] 暂时没有完整路由也可以，但元数据明确未记录。
- [ ] 删除演示依赖中的假数据替代；真实 demo 与手工 contract fixture 分开。

**通过条件**：关闭 Python 后，播放器仍能导入刚生成的文件并显示对应状态。实际位置可逐字段与 Python 输出对照。

### M2 — 通用网络 API、链路与记录完善

**输出**：§5 的主要 API、GS 接入、物理过滤、两种选路、故障记录、稳定 schema 与校验器。

- [ ] 实现稳定 ID、场景序列化、只读 Snapshot。
- [ ] 原邻接候选图去自环；增加实际物理可用性检查与通用 GSL。
- [ ] 查询路由与任何状态更新严格分离。
- [ ] 记录两种算法、多端点查询及不可达结果。
- [ ] 预设故障/恢复和不整除时间窗口语义通过测试。
- [ ] Python 正常和坏输入的契约测试通过。

**通过条件**：`first_network.py` 和 `compare_routes.py` 从新安装包运行；产出的所有 trace 能通过 schema 和语义验证。无路径不会让运行崩溃。

### M3 — 正式独立播放器与离线导出

**输出**：可嵌入 library、静态文件导入页、离线 HTML、用户认可风格的 UI。

- [ ] 复用精简 UI 的视觉，不复用其浏览器路由模型。
- [ ] 完成播放控制、实际时间跳转、query 切换、对象检查与双语。
- [ ] 两个实例同页独立运行，CSS 不影响宿主网页。
- [ ] 模块版与离线单脚本版来自同一实现。
- [ ] JSON 文件导入无需 Python；导出 HTML 无网络也能打开。
- [ ] 无数据/不可达/坏文件分别显示；错误不能只留在控制台。

**通过条件**：在浏览器离线、Python 进程关闭的情况下，导出的 HTML 和静态播放器导入流程均可用；选择算法只切换已记录结果，JavaScript 中不运行模型。

### M4 — 测试、打包与交接

**输出**：可安装包、示例、测试报告、README、API/trace/模型/来源说明、发布前清单。

- [ ] 在干净环境验证安装和所有示例；不要依赖开发目录相对路径。
- [ ] Python 单元/集成测试和浏览器 smoke/integration 测试通过。
- [ ] 按 §12 记录至少小型与标准场景的性能；未测试规模如实写出。
- [ ] 添加预设故障、不可达、跨日期变更线与多个查询的演示。
- [ ] 比较导出 HTML、库模式与 Python trace 的记录结果，无二次算法偏差。
- [ ] 检查包内地图、脚本、schema 是否齐全，无字体/密钥/私人路径。
- [ ] 检查 README/默认 UI 的 SatNet Edu 名称、`satnet-edu` 工程与 format 标识、`satnet_edu` import/CLI、Web 发布文件命名一致；历史来源路径除外。
- [ ] 记录未实现与待核对事项；暂停进入 M5，交付 v0.1。

**通过条件**：新用户按 README 能从 Python 创建网络，到文件导出，再到独立网页回放；没有服务端部署前置条件。

---

## 14. 最低测试矩阵

| 类别 | 必测案例 |
|---|---|
| 来源回归 | 原轨道生成/传播适配前后，在相同历元、参数、时刻下对照位置与距离；保留容差依据。 |
| 时间 | t=0、非整除末段、duration=0、负值错误、事件恰好在边界、重复运行确定性。 |
| 坐标/几何 | 米/公里、弧度/角度、地球自转、两点三维距离、近地平线、穿地 ISL、最大距离阈值。 |
| 拓扑 | 1×1、1×3、2×3、常规星座；自环、重复边、空候选、手动卫星不适用规则。 |
| 路由 | 可达、断连、端点失效、自查询、未知节点、已知小图最优值、两策略不同、tie-break。 |
| 状态纯度 | 连续重复 at/route、乱序查询、两次 run、两实例；不改变此前快照或随机状态。 |
| Trace | schema、版本、finite 数值、稳定 ID、每帧 query 齐全、路径边存在、路径度量之和、序列化往返。 |
| 安全导出 | label 含中文、引号、`</script>`、HTML 标签；不得执行脚本或破坏 JSON。 |
| Player | 暂停/播放/回退/结束/重载/销毁、单帧、未知 query、未记录/不可达区分、两个实例。 |
| 地图 | 日期变更线、极区、太平洋/格林尼治中心切换、固定缩放、节点/边检查。 |
| 离线 | 浏览器断网、Python 关闭、file:// 自包含 HTML、JSON 拖入本地静态播放器。 |
| UI | 桌面与窄屏、键盘、焦点、弹窗/折叠区、标签过长、宿主页 CSS 隔离。 |

测试图可以手写以验证算法，但 demo 位置必须来自真实引擎。不要为了测试全部通过而只用永远连通的全连接图。

建议最终记录的验收命令（实际 CLI 可在 M0 小幅调整，但文档、实现和测试要一致）：

```bash
python -m pip install -e ".[dev]"
python -m pytest
python examples/first_network.py
python -m satnet_edu validate outputs/experiment.json
python -m satnet_edu export-html outputs/experiment.json --output outputs/experiment.html
```

CLI 的 `export-html` 应只读取/打包 trace，不再次运行模型。Web 测试/构建命令按所选工具记录，不要求 Python 用户运行它们。

---

## 15. 后续 M5：场景编辑与挑战，不推翻前面的架构

本节是后续路线，不是当前 v0.1 的任务清单。

### 15.1 网页建造

网页只编辑 `scenario.json`，独立于已生成的 trace。添加轨道、在轨道上放置卫星、设置初始相位、添加 GS。不能把 LEO 卫星固定在任意地面经纬度上。

用户编辑场景后标记“方案已修改，需重新运行”。已有 trace 保持只读并显示它对应的配置版本。编辑器可以调用本地工具或将配置交给 Python 服务，但播放器本身不因此承担物理计算。

### 15.2 挑战文件

单独定义起止时间、采样规则、固定场景、可修改项、卫星/轨道数量限制以及覆盖/时延指标。作者参考解与公开题目分开保存。

至少区分：

- 地面点覆盖：某点是否有满足条件的卫星接入。
- 端到端连通：两端之间是否存在完整路径。
- 带时延约束的服务可用性：存在路径且单向传播时延不超过上限。

时延指标分母不能只取连通样本。未服务/断连时刻不达标，不能因为跳过它们而获得高分。

若采用时间占比，明确为采样保持近似：对 `[t_i,t_{i+1})` 用该采样状态加权，末帧只用于展示，不再额外计一个完整步长；不宣称连续时间严格保证。评估步长和窗口由题目固定，不能由解题者随意缩短。

### 15.3 自动评估与分享

先验证作者至少有一个可行解，再标记“已验证有解”；这不是最优性证明。题目未验证时注明状态，不随意断言不可能。

普通同学可以分享挑战 JSON 和结果文件。正式评估由 Python 读取 scenario 和固定 challenge 重新执行，不能把学生可编辑 trace 里的 `passed=true` 当作可信成绩。

失败反馈返回具体要求、失败时刻/时间段及关联对象，让播放器跳转检查，不重新添加整页问答和成绩卡片。

### 15.4 可选在线执行桥接

后续网页 Run：scenario → Python job → trace → 现有 player。先支持受限配置，不接收任意代码；再处理任务隔离、限流、超时、资源上限及文件保留。

不需要因为加入在线执行而改造播放器为“必须连接服务器才能播放”。已下载结果仍能离线回放。

---

## 16. 来源、署名和可宣传的边界

新项目的 `PROVENANCE.md` 至少记录：

- 原 ZIP/仓库及版本标识；
- 被继承/重构的文件、函数和新的所在位置；
- 新增的通用 GS、物理过滤、trace、API、UI 等；
- 保留和改变的假设；
- 第三方代码/地图来源与许可核对状态；
- 已完成的回归验证，未复现的研究结果。

研究来源可记录为：

> *Commercial Dishes Can Be My Ladder: Sustainable and Collaborative Data Offloading in LEO Satellite Networks*, IEEE INFOCOM 2025. DOI: `10.1109/INFOCOM55648.2025.11044527`.

在真实接入原核心、完成来源记录之后，可以使用：

> A student-friendly satellite network simulator, adapted from the simulation framework used in our IEEE INFOCOM 2025 research.

不要写成 IEEE/INFOCOM 官方、会议认证、教育版通过论文评审、完整复现论文结果，或用户已经取得了未验证的学习效果。研究来源是背景，不是默认教学大纲。

---

## 17. 完成定义：交付前逐项检查

- [ ] 原研究核心的实际继承可以从源码、来源说明和小型回归结果看出来。
- [ ] 默认 Python API 不依赖拍卖、用户商业报价或论文实验参数目录。
- [ ] 学生能以少量 Python 建立自己的网络并生成 trace。
- [ ] trace 中有真实多帧位置、可用链路、已选定路径和明确单位/模型信息。
- [ ] 同一个 Web library 能播放不同网络产生的 trace，没有写死某个星座。
- [ ] 播放器没有隐藏的轨道/图生成/路径计算器。
- [ ] 关闭 Python、断开网络后，自包含 HTML 仍能正常回放。
- [ ] 不连通、未记录和格式错误分别处理。
- [ ] 模型修改必须重新运行；单纯展示变化不影响实验数据。
- [ ] 用户认可的白底黑字二维 UI 保留，下半部冗余内容没有重新出现。
- [ ] 图形/时间轴按实际采样工作，地图不自动缩放，不把二维长度当链路距离。
- [ ] README、API、schema、测试命令、测试报告和限制与实际实现一致。
- [ ] 项目独立展示为 SatNet Edu，不被描述为 UDTJ 专属或研究 Lab；脱离 UDTJ 也能安装、导入和嵌入。
- [ ] 代码/地图归属、许可待核对项和实验来源写清楚，未擅自发布或修改原归档。
- [ ] M5+ 功能没有被写成已完成，也没有拖延 v0.1 的基础闭环。

### 给 Codex 的最终交付回复模板

1. 已实现哪些 M0–M4 项目，以及主要代码入口。
2. 从原 UserGS 保留/重构了哪些模块，哪些是新增模块。
3. 安装与运行命令，以及实际生成的 JSON/HTML 示例位置。
4. 实際执行的测试与结果；未运行的测试明确说明。
5. 已知模型限制、来源/许可阻塞和下一阶段事项。

**最终判断标准：学生编写 Python，得到自己的卫星网络实验；网页读取这次实验的记录，而不是重新编造一个相似的世界。**

---

## 附：本计划依据

- **[S1] 原代码**：`inputs/UserGS_simulation-main.zip`，以 §1.2 的 SHA-256 标识；§3 给出源文件/行号。来源观察只指这份归档，不代表其他版本。
- **[S2] UI 原型**：`inputs/orbits_to_routes_simple_python.zip`，同样以 §1.2 的 SHA-256 标识；其计算引擎不是研究来源，只复用合适的 UI/资产。
- **[S3] 定位笔记**：`references/UserGS_framework_source_notes.md`，包含先前有限源码检查与小拓扑测试的范围；对不一致处重新核对 [S1]。
- **[S4] 论文**：上述 IEEE INFOCOM 2025 论文，PDF 第 3–4 页描述离散时间区间内的网络，页 1 给出 DOI。只用作来源与模型边界背景。
- **[R] 用户确认的设计**：项目正式定名 **SatNet Edu**，GitHub repo 为 `satnet-edu`；独立通用教育工具，不以 Lab 命名，不归 UDTJ 独占。保留研究框架、友好 Python API、trace → Web library 回放、简洁二维 UI；挑战与互相出题是后续功能。

除 §3 中明确标注的源码观察和本节来源信息外，本文的接口、schema、目录、里程碑与验收要求均为**本次拟议设计**，不是对原软件现成功能的断言。
