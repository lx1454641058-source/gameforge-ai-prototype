"""职业到能力单元的分解及人才能力 Agent 交互合同。"""  # SPDX-License-Identifier: MIT | 描述跨 Agent 能力匹配职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import asdict, dataclass  # SPDX-License-Identifier: MIT | 定义结构化能力与推荐合同。
from datetime import date  # SPDX-License-Identifier: MIT | 判断能力记录有效期。
from typing import Any, Protocol  # SPDX-License-Identifier: MIT | 定义人才能力 Agent 网关接口。
from threading import Lock  # SPDX-License-Identifier: MIT | 保护内存参考网关的幂等履约回写免受并发竞争。

LEVEL_VALUES = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}  # SPDX-License-Identifier: MIT | 定义能力等级的稳定比较顺序。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结项目所需的单项能力。
class CapabilityRequirement:  # SPDX-License-Identifier: MIT | 描述可验证、可匹配的项目能力需求。
    skill_id: str  # SPDX-License-Identifier: MIT | 保存稳定能力代码而非职位名。
    name: str  # SPDX-License-Identifier: MIT | 保存能力的人类可读名称。
    category: str  # SPDX-License-Identifier: MIT | 保存程序、美术、策划、发行等能力分类。
    scope: str  # SPDX-License-Identifier: MIT | 保存能力在本项目中的明确边界。
    minimum_level: str  # SPDX-License-Identifier: MIT | 保存人才能力 Agent 认证最低等级。
    required_evidence: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存匹配时需要核验的证据类型。
    integration_context: str  # SPDX-License-Identifier: MIT | 保存能力接入真实项目的环境约束。
    stage_needed: str  # SPDX-License-Identifier: MIT | 保存该能力进入项目的时机。
    engagement: str  # SPDX-License-Identifier: MIT | 保存建议合作方式。
    priority: str  # SPDX-License-Identifier: MIT | 保存项目需求优先级。
    source_role: str  # SPDX-License-Identifier: MIT | 保留职业标签仅用于解释能力来源。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结人才能力 Agent 的匹配请求。
class TalentMatchRequest:  # SPDX-License-Identifier: MIT | 定义评分 Agent 发往人才能力 Agent 的合同。
    request_id: str  # SPDX-License-Identifier: MIT | 保存幂等请求标识。
    project_id: str  # SPDX-License-Identifier: MIT | 保存项目标识。
    project_version: str  # SPDX-License-Identifier: MIT | 保存冻结项目版本。
    rating_run_id: str  # SPDX-License-Identifier: MIT | 关联产生需求的评分运行。
    requirements: tuple[CapabilityRequirement, ...]  # SPDX-License-Identifier: MIT | 保存项目真正检索的能力包。
    allowed_engagements: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存创作者接受的合作方式。
    project_risk_summary: tuple[str, ...]  # SPDX-License-Identifier: MIT | 向候选人披露与能力相关的项目风险。

    def to_dict(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 转换为跨服务 JSON 合同。
        return asdict(self)  # SPDX-License-Identifier: MIT | 递归展开不可变数据类。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结人才的单项已验证能力记录。
class CapabilityRecord:  # SPDX-License-Identifier: MIT | 对齐人才能力 Agent 的能力资产输出。
    skill_id: str  # SPDX-License-Identifier: MIT | 保存已认证能力代码。
    level: str  # SPDX-License-Identifier: MIT | 保存 L1 到 L4 能力等级。
    scope_tags: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存已验证工具、引擎或场景范围。
    evidence_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存任务、产物、日志和问答证据。
    integration_verified: bool  # SPDX-License-Identifier: MIT | 标记是否完成真实项目接入验证。
    valid_until: str  # SPDX-License-Identifier: MIT | 保存能力记录有效期。
    delivery_success_rate: float  # SPDX-License-Identifier: MIT | 保存不可删除的历史履约统计。
    assessment_version: str  # SPDX-License-Identifier: MIT | 保存能力考核规则版本。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结一个人才能力 Agent 候选档案。
class TalentProfile:  # SPDX-License-Identifier: MIT | 描述人才匹配所需的最小授权数据。
    talent_id: str  # SPDX-License-Identifier: MIT | 保存人才标识。
    display_name: str  # SPDX-License-Identifier: MIT | 保存公开展示名称。
    capabilities: tuple[CapabilityRecord, ...]  # SPDX-License-Identifier: MIT | 保存已验证能力资产而非简历职位。
    engagement_preferences: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存现金、分成、技术入股或入队偏好。
    available: bool  # SPDX-License-Identifier: MIT | 标记当前是否接受项目匹配。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结单个候选人的推荐解释。
class TalentRecommendation:  # SPDX-License-Identifier: MIT | 描述按能力而非职位生成的推荐结果。
    talent_id: str  # SPDX-License-Identifier: MIT | 保存候选人才标识。
    display_name: str  # SPDX-License-Identifier: MIT | 保存候选人才展示名称。
    match_score: float  # SPDX-License-Identifier: MIT | 保存零到一百的可解释排序分。
    covered_skill_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存已满足的项目能力代码。
    unmet_skill_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存该候选仍不能覆盖的能力代码。
    evidence_summary: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存推荐使用的能力证据摘要。
    engagement_fit: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存双方可接受的合作方式交集。
    requires_reassessment: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存已过期或范围不符需复验的能力。
    explanation: str  # SPDX-License-Identifier: MIT | 保存面向创作者的匹配原因。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结人才能力 Agent 的匹配响应。
class TalentMatchResponse:  # SPDX-License-Identifier: MIT | 定义人才能力 Agent 返回评分 Agent 的合同。
    request_id: str  # SPDX-License-Identifier: MIT | 回传原始幂等请求标识。
    capability_agent_version: str  # SPDX-License-Identifier: MIT | 保存能力 Agent 版本用于审计。
    recommendations: tuple[TalentRecommendation, ...]  # SPDX-License-Identifier: MIT | 保存排序后的能力匹配候选。
    uncovered_requirements: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存当前人才池无人覆盖的项目能力。
    generated_assessment_requests: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存建议新建或复验的能力考核请求。

    def to_dict(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 转换为跨服务 JSON 合同。
        return asdict(self)  # SPDX-License-Identifier: MIT | 递归展开不可变数据类。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结真实项目履约回写事件。
class CapabilityFulfillmentFeedback:  # SPDX-License-Identifier: MIT | 定义项目侧回传人才能力 Agent 的事实合同。
    feedback_id: str  # SPDX-License-Identifier: MIT | 保存幂等反馈标识。
    project_id: str  # SPDX-License-Identifier: MIT | 保存产生履约事实的项目。
    project_version: str  # SPDX-License-Identifier: MIT | 保存合作发生时的项目版本。
    talent_id: str  # SPDX-License-Identifier: MIT | 保存被回写的人才标识。
    skill_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存本次合作实际使用的能力代码。
    milestone_id: str  # SPDX-License-Identifier: MIT | 保存里程碑或验收标识。
    accepted: bool  # SPDX-License-Identifier: MIT | 标记项目交付是否通过验收。
    integration_verified: bool  # SPDX-License-Identifier: MIT | 标记产物是否成功接入真实项目。
    rework_count: int  # SPDX-License-Identifier: MIT | 保存验收前返工次数。
    evidence_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存产物哈希、日志、验收和变更证据。
    reviewer_id: str  # SPDX-License-Identifier: MIT | 保存授权验收人的审计标识。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结能力 Agent 对履约回写的确认。
class CapabilityFeedbackReceipt:  # SPDX-License-Identifier: MIT | 描述履约事实是否被能力档案接收。
    feedback_id: str  # SPDX-License-Identifier: MIT | 回传原始幂等反馈标识。
    status: str  # SPDX-License-Identifier: MIT | 保存 recorded、duplicate 或 rejected。
    affected_skill_ids: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存将更新可信度的能力代码。
    capability_agent_version: str  # SPDX-License-Identifier: MIT | 保存处理反馈的能力 Agent 版本。

class TalentCapabilityAgentGateway(Protocol):  # SPDX-License-Identifier: MIT | 定义评分 Agent 对人才能力 Agent 的唯一依赖。
    def match(self, request: TalentMatchRequest) -> TalentMatchResponse:  # SPDX-License-Identifier: MIT | 根据能力需求返回有证据的候选人。
        ...  # SPDX-License-Identifier: MIT | 协议方法无需本地实现。

    def record_fulfillment(self, feedback: CapabilityFulfillmentFeedback) -> CapabilityFeedbackReceipt:  # SPDX-License-Identifier: MIT | 将真实项目履约结果回写能力资产。
        ...  # SPDX-License-Identifier: MIT | 协议方法无需本地实现。

ROLE_CAPABILITY_CATALOG: dict[str, tuple[tuple[str, str, str, str, tuple[str, ...], str], ...]] = {  # SPDX-License-Identifier: MIT | 定义职业标签到可验证能力单元的首版映射。
    "游戏策划": (  # SPDX-License-Identifier: MIT | 拆解游戏策划角色能力。
        ("design.core_loop_spec", "核心循环规格化", "策划", "将玩家行为、系统状态、奖励与失败条件写成可实现规则", ("规则文档", "可玩验证", "变更追问"), "L3"),  # SPDX-License-Identifier: MIT | 定义核心循环规格能力。
        ("design.system_integration", "系统规则接入", "策划", "把新系统接入既有数值、内容和制作流程并处理变更", ("接入方案", "版本差异", "项目验证"), "L3"),  # SPDX-License-Identifier: MIT | 定义策划系统接入能力。
    ),  # SPDX-License-Identifier: MIT | 游戏策划能力结束。
    "客户端程序": (  # SPDX-License-Identifier: MIT | 拆解客户端程序角色能力。
        ("engineering.gameplay_prototype", "核心玩法原型实现", "程序", "在目标引擎中实现可运行核心循环和调试接口", ("可运行构建", "源码或产物哈希", "自动测试"), "L3"),  # SPDX-License-Identifier: MIT | 定义玩法原型实现能力。
        ("engineering.project_integration", "游戏模块工程接入", "程序", "遵循现有接口、资源和性能约束接入模块", ("标准工程接入", "兼容性测试", "异常日志"), "L3"),  # SPDX-License-Identifier: MIT | 定义工程接入能力。
    ),  # SPDX-License-Identifier: MIT | 客户端程序能力结束。
    "UX/交互设计": (  # SPDX-License-Identifier: MIT | 拆解 UX 角色能力。
        ("ux.first_session_flow", "首局交互流程设计", "UX", "把首次吸引、教学和核心操作组织为可测试首局流程", ("用户流程图", "交互原型", "变更记录"), "L2"),  # SPDX-License-Identifier: MIT | 定义首局流程能力。
        ("ux.usability_test", "游戏可用性测试", "UX", "设计任务、观察玩家行为并将问题转为可执行改进", ("测试脚本", "观察记录", "问题优先级"), "L2"),  # SPDX-License-Identifier: MIT | 定义可用性测试能力。
    ),  # SPDX-License-Identifier: MIT | UX 能力结束。
    "美术负责人": (  # SPDX-License-Identifier: MIT | 拆解美术负责人角色能力。
        ("art.style_bible", "游戏视觉规范建立", "美术", "建立角色、场景、UI、色彩和可读性统一规范", ("风格基准", "资产示例", "审核清单"), "L3"),  # SPDX-License-Identifier: MIT | 定义视觉规范能力。
        ("art.engine_pipeline", "美术资产引擎管线", "美术", "按命名、规格、性能预算和资源组织规则交付可导入资产", ("引擎导入", "性能检查", "资源目录"), "L3"),  # SPDX-License-Identifier: MIT | 定义美术管线能力。
    ),  # SPDX-License-Identifier: MIT | 美术负责人能力结束。
    "音频设计": (  # SPDX-License-Identifier: MIT | 拆解音频角色能力。
        ("audio.interactive_feedback", "交互音频反馈设计", "音频", "用音效和音乐状态强化操作、危险、奖励和界面反馈", ("音频清单", "状态映射", "试听构建"), "L2"),  # SPDX-License-Identifier: MIT | 定义交互音频能力。
        ("audio.engine_integration", "音频引擎接入", "音频", "按资源、响度、混音和性能约束接入目标引擎", ("引擎工程", "资源规范", "性能记录"), "L2"),  # SPDX-License-Identifier: MIT | 定义音频接入能力。
    ),  # SPDX-License-Identifier: MIT | 音频能力结束。
    "QA/测试": (  # SPDX-License-Identifier: MIT | 拆解 QA 角色能力。
        ("qa.game_test_plan", "游戏测试计划设计", "测试", "覆盖核心循环、边界、存档、设备和回归风险", ("测试计划", "覆盖矩阵", "退出条件"), "L2"),  # SPDX-License-Identifier: MIT | 定义测试计划能力。
        ("qa.repro_regression", "缺陷复现与回归", "测试", "稳定复现缺陷、记录环境和验证修复不引入回归", ("缺陷单", "复现录像", "回归记录"), "L2"),  # SPDX-License-Identifier: MIT | 定义缺陷回归能力。
        ("qa.platform_compatibility", "平台兼容性验证", "测试", "按目标平台、设备和系统矩阵验证启动与关键功能", ("兼容矩阵", "设备日志", "阻塞报告"), "L2"),  # SPDX-License-Identifier: MIT | 定义平台兼容能力。
    ),  # SPDX-License-Identifier: MIT | QA 能力结束。
    "发行运营": (  # SPDX-License-Identifier: MIT | 拆解发行运营角色能力。
        ("release.store_page", "游戏商店页制作", "发行", "让文案、截图、视频、功能和当前构建保持一致", ("商店页草稿", "素材清单", "一致性检查"), "L2"),  # SPDX-License-Identifier: MIT | 定义商店页制作能力。
        ("release.submission_coordination", "平台提审与发布协调", "发行", "管理平台清单、提审反馈、发布日程和回滚准备", ("提审清单", "反馈关闭记录", "发布计划"), "L3"),  # SPDX-License-Identifier: MIT | 定义提审协调能力。
    ),  # SPDX-License-Identifier: MIT | 发行运营能力结束。
    "合规/隐私顾问": (  # SPDX-License-Identifier: MIT | 拆解合规顾问角色能力。
        ("compliance.data_mapping", "游戏数据与隐私梳理", "合规", "识别数据、权限、SDK、用户和地区要求并形成披露输入", ("数据流图", "SDK 清单", "隐私说明输入"), "L3"),  # SPDX-License-Identifier: MIT | 定义隐私梳理能力。
        ("compliance.platform_declaration", "平台内容与政策声明", "合规", "根据实际构建准备内容、年龄、广告和访问声明", ("声明清单", "构建对照", "复核记录"), "L3"),  # SPDX-License-Identifier: MIT | 定义平台声明能力。
    ),  # SPDX-License-Identifier: MIT | 合规能力结束。
    "后端/服务端程序": (  # SPDX-License-Identifier: MIT | 拆解服务端程序角色能力。
        ("backend.game_service", "游戏在线服务实现", "程序", "实现认证、状态、匹配或持久化服务并处理故障", ("服务接口", "集成测试", "故障恢复"), "L3"),  # SPDX-License-Identifier: MIT | 定义在线服务能力。
        ("backend.load_observability", "在线服务压测与观测", "程序", "建立容量基线、指标、告警和降级策略", ("压测报告", "监控面板", "降级演练"), "L3"),  # SPDX-License-Identifier: MIT | 定义压测观测能力。
    ),  # SPDX-License-Identifier: MIT | 服务端能力结束。
    "安全工程师": (  # SPDX-License-Identifier: MIT | 拆解安全角色能力。
        ("security.game_abuse_model", "游戏滥用与作弊建模", "安全", "识别作弊、经济滥用、账号和服务攻击路径", ("威胁清单", "检测策略", "处置流程"), "L3"),  # SPDX-License-Identifier: MIT | 定义滥用建模能力。
        ("security.anticheat_integration", "反作弊方案接入", "安全", "在性能、隐私和误报约束下接入反作弊能力", ("集成构建", "误报测试", "运行日志"), "L3"),  # SPDX-License-Identifier: MIT | 定义反作弊接入能力。
    ),  # SPDX-License-Identifier: MIT | 安全能力结束。
    "数值/经济策划": (  # SPDX-License-Identifier: MIT | 拆解数值经济角色能力。
        ("economy.value_flow", "游戏价值流与货币系统设计", "策划", "定义产出、消耗、付费点、公平性和异常回收", ("价值流图", "参数表", "模拟记录"), "L3"),  # SPDX-License-Identifier: MIT | 定义价值流能力。
        ("economy.balance_iteration", "经济平衡验证与迭代", "策划", "基于测试数据识别通胀、卡点和付费压力并调整", ("平衡模型", "测试数据", "版本差异"), "L3"),  # SPDX-License-Identifier: MIT | 定义经济迭代能力。
    ),  # SPDX-License-Identifier: MIT | 数值经济能力结束。
    "数据与运营": (  # SPDX-License-Identifier: MIT | 拆解数据运营角色能力。
        ("analytics.game_event_schema", "游戏行为事件设计", "数据", "将核心循环、留存和流失假设映射为可分析事件", ("事件字典", "埋点验证", "指标口径"), "L2"),  # SPDX-License-Identifier: MIT | 定义事件设计能力。
        ("liveops.content_operation", "游戏持续运营计划", "运营", "按内容、活动、奖励和风险建立可回滚运营节奏", ("运营日历", "配置规范", "回滚方案"), "L2"),  # SPDX-License-Identifier: MIT | 定义持续运营能力。
    ),  # SPDX-License-Identifier: MIT | 数据运营能力结束。
}  # SPDX-License-Identifier: MIT | 职业能力映射定义结束。

class CapabilityRequirementResolver:  # SPDX-License-Identifier: MIT | 将团队角色缺口收窄为项目能力包。
    def resolve(self, role_gaps: tuple[Any, ...]) -> tuple[CapabilityRequirement, ...]:  # SPDX-License-Identifier: MIT | 从诊断角色缺口生成可查询能力。
        requirements: list[CapabilityRequirement] = []  # SPDX-License-Identifier: MIT | 初始化能力需求列表。
        for gap in role_gaps:  # SPDX-License-Identifier: MIT | 逐个处理人类可读职业缺口。
            entries = ROLE_CAPABILITY_CATALOG.get(gap.role, ())  # SPDX-License-Identifier: MIT | 读取该职业对应的能力单元。
            for skill_id, name, category, scope, evidence, level in entries:  # SPDX-License-Identifier: MIT | 展开每个可验证能力定义。
                requirements.append(CapabilityRequirement(skill_id, name, category, scope, level, evidence, gap.reason, gap.timing, gap.engagement, gap.priority, gap.role))  # SPDX-License-Identifier: MIT | 创建继承模块优先级和项目上下文的能力需求。
        unique = {requirement.skill_id: requirement for requirement in requirements}  # SPDX-License-Identifier: MIT | 按稳定能力代码去重。
        return tuple(unique.values())  # SPDX-License-Identifier: MIT | 返回可供能力 Agent 查询的需求包。

class InMemoryTalentCapabilityAgent:  # SPDX-License-Identifier: MIT | 提供跨 Agent 合同的离线参考实现。
    version = "talent-capability-agent-contract-0.1"  # SPDX-License-Identifier: MIT | 固定参考能力 Agent 版本。

    def __init__(self, profiles: tuple[TalentProfile, ...]) -> None:  # SPDX-License-Identifier: MIT | 注入经过授权的人才能力档案。
        self.profiles = profiles  # SPDX-License-Identifier: MIT | 保存只读人才池。
        self.fulfillment_audit: dict[str, CapabilityFulfillmentFeedback] = {}  # SPDX-License-Identifier: MIT | 保存离线参考实现的幂等履约审计。
        self._fulfillment_lock = Lock()  # SPDX-License-Identifier: MIT | 为检查和写入同一反馈标识建立原子临界区。

    def match(self, request: TalentMatchRequest) -> TalentMatchResponse:  # SPDX-License-Identifier: MIT | 按能力覆盖、证据和履约生成候选推荐。
        recommendations = [item for profile in self.profiles if (item := self._score_profile(profile, request)) is not None]  # SPDX-License-Identifier: MIT | 过滤不可用或无能力覆盖的候选。
        recommendations.sort(key=lambda item: (-item.match_score, item.talent_id))  # SPDX-License-Identifier: MIT | 使用稳定排序保证相同输入可回归。
        covered_pool = {skill_id for item in recommendations for skill_id in item.covered_skill_ids}  # SPDX-License-Identifier: MIT | 汇总人才池已覆盖能力。
        uncovered = tuple(requirement.skill_id for requirement in request.requirements if requirement.skill_id not in covered_pool)  # SPDX-License-Identifier: MIT | 识别无人满足的能力需求。
        assessment_requests = tuple(f"assess:{skill_id}" for skill_id in uncovered)  # SPDX-License-Identifier: MIT | 为人才池缺口生成能力考核模板需求。
        return TalentMatchResponse(request.request_id, self.version, tuple(recommendations[:10]), uncovered, assessment_requests)  # SPDX-License-Identifier: MIT | 返回最多十名可解释候选。

    def record_fulfillment(self, feedback: CapabilityFulfillmentFeedback) -> CapabilityFeedbackReceipt:  # SPDX-License-Identifier: MIT | 记录真实项目验收事实供能力可信度更新。
        required_text = (feedback.feedback_id, feedback.project_id, feedback.project_version, feedback.talent_id, feedback.milestone_id, feedback.reviewer_id)  # SPDX-License-Identifier: MIT | 收集履约审计必须存在的标识字段。
        if any(not value.strip() for value in required_text) or feedback.rework_count < 0 or not feedback.skill_ids:  # SPDX-License-Identifier: MIT | 拒绝缺少主体、版本、里程碑、审核人或非法返工数的事件。
            return CapabilityFeedbackReceipt(feedback.feedback_id, "rejected", (), self.version)  # SPDX-License-Identifier: MIT | 返回拒绝且不写入幂等历史。
        profile = next((item for item in self.profiles if item.talent_id == feedback.talent_id), None)  # SPDX-License-Identifier: MIT | 检查人才是否存在于授权能力池。
        known_skills = {record.skill_id for record in profile.capabilities} if profile else set()  # SPDX-License-Identifier: MIT | 获取人才已登记能力代码。
        affected = tuple(skill_id for skill_id in feedback.skill_ids if skill_id in known_skills)  # SPDX-License-Identifier: MIT | 只允许回写人才实际登记的能力。
        if profile is None or not affected or not feedback.evidence_ids:  # SPDX-License-Identifier: MIT | 拒绝无人才、无关联能力或无证据的反馈。
            return CapabilityFeedbackReceipt(feedback.feedback_id, "rejected", affected, self.version)  # SPDX-License-Identifier: MIT | 返回拒绝结果且不污染能力历史。
        with self._fulfillment_lock:  # SPDX-License-Identifier: MIT | 原子执行重复检测和首次写入，确保并发重试只有一个请求被记录。
            if feedback.feedback_id in self.fulfillment_audit:  # SPDX-License-Identifier: MIT | 防止并发或串行消息重试重复计入履约历史。
                return CapabilityFeedbackReceipt(feedback.feedback_id, "duplicate", feedback.skill_ids, self.version)  # SPDX-License-Identifier: MIT | 返回幂等重复确认。
            self.fulfillment_audit[feedback.feedback_id] = feedback  # SPDX-License-Identifier: MIT | 保存不可覆盖的履约事实供后续能力聚合服务消费。
        return CapabilityFeedbackReceipt(feedback.feedback_id, "recorded", affected, self.version)  # SPDX-License-Identifier: MIT | 确认履约事件已记录。

    def _score_profile(self, profile: TalentProfile, request: TalentMatchRequest) -> TalentRecommendation | None:  # SPDX-License-Identifier: MIT | 计算单个人才的项目能力适配度。
        if not profile.available:  # SPDX-License-Identifier: MIT | 不推荐当前不接受项目的人才。
            return None  # SPDX-License-Identifier: MIT | 结束不可用候选计算。
        records = {record.skill_id: record for record in profile.capabilities}  # SPDX-License-Identifier: MIT | 按能力代码索引人才资产。
        covered: list[str] = []  # SPDX-License-Identifier: MIT | 初始化已覆盖能力。
        unmet: list[str] = []  # SPDX-License-Identifier: MIT | 初始化未满足能力。
        reassess: list[str] = []  # SPDX-License-Identifier: MIT | 初始化需复验能力。
        evidence: list[str] = []  # SPDX-License-Identifier: MIT | 初始化推荐证据摘要。
        points = 0.0  # SPDX-License-Identifier: MIT | 初始化能力匹配积分。
        for requirement in request.requirements:  # SPDX-License-Identifier: MIT | 逐项检查项目能力需求。
            record = records.get(requirement.skill_id)  # SPDX-License-Identifier: MIT | 查找对应已验证能力记录。
            if record is None or LEVEL_VALUES.get(record.level, 0) < LEVEL_VALUES.get(requirement.minimum_level, 99):  # SPDX-License-Identifier: MIT | 检查能力是否存在且等级达标。
                unmet.append(requirement.skill_id)  # SPDX-License-Identifier: MIT | 记录无法覆盖的能力。
                continue  # SPDX-License-Identifier: MIT | 继续检查其他能力。
            if self._expired(record.valid_until) or not record.evidence_ids or not record.assessment_version:  # SPDX-License-Identifier: MIT | 检查能力有效期、证据和考核版本是否完整。
                reassess.append(requirement.skill_id)  # SPDX-License-Identifier: MIT | 过期能力不能作为自动匹配依据。
                unmet.append(requirement.skill_id)  # SPDX-License-Identifier: MIT | 将过期或无证据能力计入未满足。
                continue  # SPDX-License-Identifier: MIT | 继续检查其他能力。
            covered.append(requirement.skill_id)  # SPDX-License-Identifier: MIT | 记录达到等级和有效期要求的能力。
            integration_points = 1.0 if record.integration_verified else 0.65  # SPDX-License-Identifier: MIT | 项目接入验证高于纯任务验证。
            points += integration_points * max(0.0, min(1.0, record.delivery_success_rate))  # SPDX-License-Identifier: MIT | 结合能力接入与真实履约计算积分。
            evidence.append(f"{requirement.skill_id}:{record.level}；接入验证={record.integration_verified}；证据={','.join(record.evidence_ids)}")  # SPDX-License-Identifier: MIT | 保存推荐所用证据而非简历描述。
        if not covered:  # SPDX-License-Identifier: MIT | 至少覆盖一个项目能力才进入候选列表。
            return None  # SPDX-License-Identifier: MIT | 排除没有实际能力覆盖的人才。
        coverage = len(covered) / max(1, len(request.requirements))  # SPDX-License-Identifier: MIT | 计算能力需求覆盖率。
        quality = points / len(covered)  # SPDX-License-Identifier: MIT | 计算已覆盖能力的平均证据质量。
        engagement_fit = tuple(sorted(set(profile.engagement_preferences).intersection(request.allowed_engagements)))  # SPDX-License-Identifier: MIT | 计算合作方式交集。
        engagement_factor = 1.0 if engagement_fit else 0.75  # SPDX-License-Identifier: MIT | 合作偏好不匹配时降权但不隐藏能力证据。
        score = round((coverage * 0.65 + quality * 0.35) * engagement_factor * 100, 1)  # SPDX-License-Identifier: MIT | 以覆盖为主、证据质量为辅生成透明排序分。
        explanation = f"覆盖 {len(covered)}/{len(request.requirements)} 项能力；推荐基于有效能力考核、项目接入和履约记录"  # SPDX-License-Identifier: MIT | 生成面向创作者的推荐解释。
        return TalentRecommendation(profile.talent_id, profile.display_name, score, tuple(covered), tuple(unmet), tuple(evidence), engagement_fit, tuple(reassess), explanation)  # SPDX-License-Identifier: MIT | 返回单个人才推荐结果。

    def _expired(self, valid_until: str) -> bool:  # SPDX-License-Identifier: MIT | 判断能力记录是否需要复验。
        try:  # SPDX-License-Identifier: MIT | 安全解析 ISO 日期。
            return date.fromisoformat(valid_until) < date.today()  # SPDX-License-Identifier: MIT | 将过期日期标记为需复验。
        except ValueError:  # SPDX-License-Identifier: MIT | 无效有效期不能被当作有效记录。
            return True  # SPDX-License-Identifier: MIT | 保守要求重新考核。
