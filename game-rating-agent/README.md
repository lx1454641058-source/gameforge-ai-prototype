# GameForge AI 游戏评分 Agent

这是一个可独立运行的游戏项目诊断 MVP，不依赖平台原型。它实现了完整主链路：创作者上传方案与 Demo → 系统生成问卷草稿 → 创作者确认关键答案 → Agent 分析评分 → 输出缺失模块、投入缺口、团队能力缺口、制作流程与上架流程 → 与人才能力 Agent 交换能力需求和履约反馈。

## 已完成的能力

- 安全接收 DOCX、PDF、TXT、Markdown、JSON、图片、视频和 Demo ZIP；检查扩展名、文件签名、大小、ZIP 路径穿越、条目数、展开体积和异常压缩比。
- 上传文件使用系统随机名并按项目隔离保存，不执行 Demo，不解压 Demo，不把用户文件名当存储路径。
- 本地提取 TXT、Markdown、JSON 和 DOCX 主文档纯文本；不会读取宏、嵌入对象或外部链接。
- 提供 25 题版本化问卷；其中类型、玩法特征、对标作品、创新位置、创新机制与验证方式使用结构化答案，不按自由文本长度判断创新。
- 内置 `GF-GENRE-KB-1.0` 游戏类型知识库，覆盖 28 个常见主类型和商业子类型；每个类型包含常规机制、高密度同质化组合、创新验证位置和九维评分重点。
- Agent 在评分前先完成类型知识库比对，再按所选类型生成归一化九维动态权重；报告会保留命中的基线、拥挤组合、类型常规复用项、创新候选和验证证据。
- AI 草稿不能覆盖创作者已填写事实，关键答案必须经创作者确认，否则运行终止为 `needs_creator_action`，不会生成假评分。
- 评分运行具有 SQLite 持久化、输入冻结、报告快照、失败重试、中断恢复和追加式审计记录。
- 输出 D、C 或 `B_GATE`。AI 不直接授予真人 BAS 分数；`B_GATE` 也不等于已经满足真人审核门槛。
- 输出游戏九维诊断、缺失制作模块、投入差额、七阶段制作路线、Steam/Google Play 上架路线和团队能力需求。
- 职业名称会拆成具体能力；人才匹配依据能力 ID、等级、有效期、集成证据、履约历史和合作偏好，不依据职位名称排序。
- 提供无第三方运行依赖的 Bearer Token HTTP API 和命令行入口。

## 快速验证

项目使用 MIT License，没有引入 GPL 代码。Python 3.11 或更新版本即可运行，核心服务没有第三方依赖。

```powershell
cd D:\codex项目\2\game-rating-agent # SPDX-License-Identifier: MIT | 进入 Agent 项目目录。
python -m unittest discover -s tests -v # SPDX-License-Identifier: MIT | 运行安全、业务、持久化和 HTTP 回归测试。
python -m game_rating_agent.pipeline_cli examples\creator_submission.json --output examples\creator_diagnostic.report.json # SPDX-License-Identifier: MIT | 执行完整诊断样例。
python -m examples.talent_match_demo # SPDX-License-Identifier: MIT | 从项目根目录执行评分 Agent 与人才能力 Agent 联动样例。
```

## 启动 HTTP 服务

```powershell
$env:GAMEFORGE_AGENT_TOKEN="replace-with-a-long-random-token" # SPDX-License-Identifier: MIT | 配置至少 16 字符的本地 API 令牌。
$env:GAMEFORGE_AGENT_DATA="D:\codex项目\2\game-rating-agent\var" # SPDX-License-Identifier: MIT | 将数据库和隔离文件保存在 D 盘项目目录。
python -m game_rating_agent.api --host 127.0.0.1 --port 8765 # SPDX-License-Identifier: MIT | 默认只监听本机地址。
```

启动后访问 `http://127.0.0.1:8765/` 即可使用配套前端。前端覆盖连接配置、资料上传、问卷代填与确认、提交评分、诊断报告、运行刷新和审计查看；API Token 只保存在当前页面内存，不写入 `localStorage` 或 `sessionStorage`。

需要 AI 代填时再设置 `OPENAI_API_KEY`；未设置时服务会安全降级到本地保守代填，不会因为缺少密钥而停止。

## API 主流程

所有接口都要求 `Authorization: Bearer <token>`，响应均为 UTF-8 JSON。

1. `POST /v1/artifacts`：上传单个 Base64 文件，返回 `artifact_id` 和可直接用于提交的 `submission_artifact`。
2. `GET /v1/questionnaire`：获取当前问卷定义。
3. `GET /v1/knowledge-base`：读取当前类型基线、拥挤组合、创新位置和类型评分重点。
4. `POST /v1/questionnaire/prefill`：传入 `artifact_ids` 与可选 `creator_values`，返回待确认答案。
5. 创作者检查答案，将关键答案的 `creator_confirmed` 设为 `true`。
6. `POST /v1/submissions`：提交项目标识、版本、标题、`artifact_ids` 和已确认 `questionnaire`。服务端会从可信上传记录重建资料清单。
7. `POST /v1/runs`：传入 `submission_id`，创建并执行评分诊断。
8. `GET /v1/runs/{run_id}`：读取状态和完整报告。
9. `GET /v1/runs/{run_id}/audit`：读取运行审计时间线。
10. `POST /v1/runs/{run_id}/retry`：只重试 `failed` 且 `error.retryable=true` 的系统失败；`needs_creator_action` 必须修改资料或问卷后创建新提交和新运行，已完成报告不可覆盖。
11. `POST /v1/capability-feedback`：将人才实际履约证据回写人才能力 Agent。

问卷中的 `development_stage` 使用 `idea`、`concept`、`pre_prototype`、`prototype`、`vertical_slice`、`alpha`、`beta` 或 `release_candidate`；`business_model` 使用 `buyout`、`iap`、`ads`、`subscription`、`dlc` 或 `noncommercial`。未知代码会返回创作者行动项，不会被静默套用错误规则。

完整提交合同可参考 [creator_submission.json](examples/creator_submission.json)，完整诊断输出可参考 [creator_diagnostic.report.json](examples/creator_diagnostic.report.json)。

## 评分与安全边界

当前规则版本 `GF-GAME-RUBRIC-0.2-PROVISIONAL` 与知识库版本 `GF-GENRE-KB-1.0` 是工程启动规则，不是经过行业验证的 BAS 标准。它们必须使用专家标注项目和真实市场数据持续校准阈值、类型权重、高密度组合与阶段差异，才能进入真实业务试运行。

本 MVP 不会自动启动或试玩创作者 Demo。Demo ZIP 只做静态结构安全检查和证据登记；自动试玩需要后续建设独立沙箱、资源配额、网络隔离、恶意软件扫描、引擎适配器和可回放遥测。PDF、图片、视频当前也只登记元数据，不会假装理解其内容。

OpenAI 仅用于问卷信息抽取，不负责直接决定等级。请求设置 `store: false`，并把上传内容当作不可信材料与系统指令隔离；正式上线前仍需完成供应商数据协议、密钥管理、日志脱敏、访问控制和删除策略评审。

## 目录说明

- `game_rating_agent/artifacts.py`：上传安全和有限文本提取。
- `game_rating_agent/questionnaire.py`：问卷合同、本地代填和可选模型代填。
- `game_rating_agent/intake.py`：创作者确认门槛和评分输入冻结。
- `game_rating_agent/knowledge_base.py`：游戏类型基线、高密度机制组合、类型动态权重与同质化比对。
- `game_rating_agent/agent.py`：证据提取、九步审计与 D/C/B_GATE 规则。
- `game_rating_agent/diagnosis.py`：模块、投入、能力、制作和上架诊断。
- `game_rating_agent/capabilities.py`：能力模型、人才匹配和履约反馈。
- `game_rating_agent/repository.py`：SQLite 提交、运行和审计持久化。
- `game_rating_agent/service.py`：端到端应用服务。
- `game_rating_agent/api.py`：Bearer Token HTTP API。
- `game_rating_agent/frontend/`：与 API 同源提供的无构建步骤基础前端。
- `tests/`：业务、安全、恢复和 HTTP 回归测试。

## 下一阶段

在把它称为生产版前，还需要完成三件事：建立专家标注与争议处理机制；在真正隔离的执行环境中分析 Demo；接入生产级对象存储、数据库、队列、细粒度身份权限、审计归档、监控告警和人工复核工作台。
