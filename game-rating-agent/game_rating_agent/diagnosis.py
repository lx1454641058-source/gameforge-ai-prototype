"""将评分证据转换为模块、投入、团队、制作和上架路线。"""  # SPDX-License-Identifier: MIT | 描述诊断规划职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import asdict, dataclass  # SPDX-License-Identifier: MIT | 定义结构化诊断报告。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容项目输入。
from .agent import RatingResult  # SPDX-License-Identifier: MIT | 使用评分结果生成后续路线。
from .capabilities import CapabilityRequirement, CapabilityRequirementResolver, TalentMatchRequest, TalentMatchResponse, TalentCapabilityAgentGateway  # SPDX-License-Identifier: MIT | 将职业缺口转换为能力需求并调用人才能力 Agent。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结单个缺失模块诊断。
class ModuleGap:  # SPDX-License-Identifier: MIT | 描述游戏仍需补齐的产品或生产模块。
    module_id: str  # SPDX-License-Identifier: MIT | 保存稳定模块代码。
    name: str  # SPDX-License-Identifier: MIT | 保存创作者可读模块名称。
    current_state: str  # SPDX-License-Identifier: MIT | 保存问卷声明的当前状态。
    reason: str  # SPDX-License-Identifier: MIT | 保存该模块为何需要补齐。
    priority: str  # SPDX-License-Identifier: MIT | 保存 P0、P1 或 P2 优先级。
    evidence_needed: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存模块完成时需要提交的证据。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结单项投入诊断。
class InvestmentNeed:  # SPDX-License-Identifier: MIT | 描述投入类型和可计算差额。
    category: str  # SPDX-License-Identifier: MIT | 保存投入类别。
    reason: str  # SPDX-License-Identifier: MIT | 保存投入用途。
    amount_gap: float | None  # SPDX-License-Identifier: MIT | 仅在创作者提供数字时计算资金差额。
    unit: str  # SPDX-License-Identifier: MIT | 保存金额单位或非金额说明。
    confidence: str  # SPDX-License-Identifier: MIT | 说明诊断确定性。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结单个团队角色缺口。
class RoleGap:  # SPDX-License-Identifier: MIT | 描述团队需要补齐的角色。
    role: str  # SPDX-License-Identifier: MIT | 保存标准角色名称。
    reason: str  # SPDX-License-Identifier: MIT | 保存需要该角色的项目依据。
    timing: str  # SPDX-License-Identifier: MIT | 保存建议进入项目的阶段。
    engagement: str  # SPDX-License-Identifier: MIT | 保存建议全职、兼职或外包方式。
    priority: str  # SPDX-License-Identifier: MIT | 保存来源模块的 P0、P1 或 P2 优先级。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结路线中的一个阶段。
class RoadmapStep:  # SPDX-License-Identifier: MIT | 描述制作或上架步骤和退出条件。
    order: int  # SPDX-License-Identifier: MIT | 保存步骤顺序。
    name: str  # SPDX-License-Identifier: MIT | 保存步骤名称。
    objective: str  # SPDX-License-Identifier: MIT | 保存步骤目标。
    exit_criteria: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存进入下一阶段前的验收条件。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结一次创作者诊断报告。
class CreatorDiagnosticReport:  # SPDX-License-Identifier: MIT | 聚合评分与所有后续行动路线。
    rating: RatingResult  # SPDX-License-Identifier: MIT | 保存 D、C、B_GATE 评分报告。
    missing_modules: tuple[ModuleGap, ...]  # SPDX-License-Identifier: MIT | 保存缺失或未完成模块。
    investment_needs: tuple[InvestmentNeed, ...]  # SPDX-License-Identifier: MIT | 保存投入诊断。
    missing_roles: tuple[RoleGap, ...]  # SPDX-License-Identifier: MIT | 保存团队角色缺口。
    capability_requirements: tuple[CapabilityRequirement, ...]  # SPDX-License-Identifier: MIT | 保存真正用于检索和推荐的能力需求包。
    talent_match: TalentMatchResponse | None  # SPDX-License-Identifier: MIT | 保存人才能力 Agent 返回的可解释候选。
    production_roadmap: tuple[RoadmapStep, ...]  # SPDX-License-Identifier: MIT | 保存个性化制作路线。
    release_roadmap: dict[str, tuple[RoadmapStep, ...]]  # SPDX-License-Identifier: MIT | 按目标平台保存上架路线。
    assumptions: tuple[str, ...]  # SPDX-License-Identifier: MIT | 明示不能从现有证据确认的假设。

    def to_dict(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 转换为 API 友好的 JSON 对象。
        payload = asdict(self)  # SPDX-License-Identifier: MIT | 递归展开诊断数据类。
        payload["rating"] = self.rating.to_dict()  # SPDX-License-Identifier: MIT | 保持评分枚举序列化规则。
        return payload  # SPDX-License-Identifier: MIT | 返回完整诊断报告。

BASE_MODULES = (  # SPDX-License-Identifier: MIT | 定义所有游戏首版需要观察的基础模块。
    ("core_design", "核心玩法与规则", "P0", ("可复现的核心循环说明", "关键规则表")),  # SPDX-License-Identifier: MIT | 定义核心设计模块。
    ("prototype", "可玩原型", "P0", ("可启动构建", "一局完整流程录像")),  # SPDX-License-Identifier: MIT | 定义可玩原型模块。
    ("ux_onboarding", "交互与新手引导", "P1", ("首局流程", "可用性测试记录")),  # SPDX-License-Identifier: MIT | 定义体验引导模块。
    ("art_pipeline", "美术生产管线", "P1", ("风格基准", "资产清单与规范")),  # SPDX-License-Identifier: MIT | 定义美术管线模块。
    ("audio", "音频与反馈", "P1", ("音频清单", "关键反馈试听")),  # SPDX-License-Identifier: MIT | 定义音频模块。
    ("qa", "测试与质量保障", "P0", ("测试计划", "缺陷与回归记录")),  # SPDX-License-Identifier: MIT | 定义质量保障模块。
    ("store_assets", "商店素材与产品说明", "P1", ("真实玩法截图", "预告片", "功能一致的商店文案")),  # SPDX-License-Identifier: MIT | 定义商店素材模块。
    ("compliance", "隐私、内容与平台合规", "P0", ("隐私说明", "内容声明", "第三方 SDK 清单")),  # SPDX-License-Identifier: MIT | 定义合规模块。
)  # SPDX-License-Identifier: MIT | 基础模块定义结束。

class DiagnosticPlanner:  # SPDX-License-Identifier: MIT | 将项目事实映射为可执行诊断。
    def __init__(self, capability_gateway: TalentCapabilityAgentGateway | None = None, resolver: CapabilityRequirementResolver | None = None) -> None:  # SPDX-License-Identifier: MIT | 支持注入真实人才能力 Agent 网关。
        self.capability_gateway = capability_gateway  # SPDX-License-Identifier: MIT | 保存可选人才能力 Agent 连接。
        self.resolver = resolver or CapabilityRequirementResolver()  # SPDX-License-Identifier: MIT | 默认使用版本化职业能力映射。

    def build(self, project: dict[str, Any], rating: RatingResult) -> CreatorDiagnosticReport:  # SPDX-License-Identifier: MIT | 生成完整创作者诊断报告。
        modules = self._module_gaps(project, rating)  # SPDX-License-Identifier: MIT | 识别缺失或未完成模块。
        roles = self._role_gaps(project, modules)  # SPDX-License-Identifier: MIT | 根据模块和目标平台识别团队缺口。
        capabilities = self.resolver.resolve(tuple(roles))  # SPDX-License-Identifier: MIT | 将职业标签进一步拆为可验证能力单元。
        talent_match = self._match_talent(project, rating, capabilities)  # SPDX-License-Identifier: MIT | 通过人才能力 Agent 获取有证据的候选推荐。
        investments = self._investment_needs(project, modules, roles)  # SPDX-License-Identifier: MIT | 生成资金和非资金投入需求。
        production = self._production_roadmap(project, modules)  # SPDX-License-Identifier: MIT | 生成阶段化制作路线。
        release = {platform: self._release_steps(platform) for platform in self._platforms(project)}  # SPDX-License-Identifier: MIT | 按目标平台生成上架路线。
        assumptions = self._assumptions(project)  # SPDX-License-Identifier: MIT | 收集无法由证据确认的事项。
        return CreatorDiagnosticReport(rating, tuple(modules), tuple(investments), tuple(roles), capabilities, talent_match, tuple(production), release, tuple(assumptions))  # SPDX-License-Identifier: MIT | 返回含能力包和人才候选的完整诊断报告。

    def _match_talent(self, project: dict[str, Any], rating: RatingResult, capabilities: tuple[CapabilityRequirement, ...]) -> TalentMatchResponse | None:  # SPDX-License-Identifier: MIT | 建立评分 Agent 到人才能力 Agent 的交互请求。
        if self.capability_gateway is None or not capabilities:  # SPDX-License-Identifier: MIT | 没有能力 Agent 连接或无需能力时不伪造候选。
            return None  # SPDX-License-Identifier: MIT | 返回空匹配并保留能力需求供后续异步调用。
        preferences = project.get("collaboration_preferences") if isinstance(project.get("collaboration_preferences"), list) else ["cash"]  # SPDX-License-Identifier: MIT | 读取创作者接受的合作方式。
        request = TalentMatchRequest(f"tmr_{rating.run_id}", rating.project_id, rating.project_version, rating.run_id, capabilities, tuple(str(item) for item in preferences), tuple(rating.risks))  # SPDX-License-Identifier: MIT | 创建版本化、幂等的跨 Agent 请求。
        return self.capability_gateway.match(request)  # SPDX-License-Identifier: MIT | 获取已验证能力、履约和合作偏好驱动的候选。

    def _module_gaps(self, project: dict[str, Any], rating: RatingResult) -> list[ModuleGap]:  # SPDX-License-Identifier: MIT | 识别必需和条件模块的缺口。
        status = project.get("module_status") if isinstance(project.get("module_status"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取模块状态问卷。
        catalog = list(BASE_MODULES)  # SPDX-License-Identifier: MIT | 从基础模块开始构建项目目录。
        if project.get("multiplayer") is True or project.get("online_service") is True:  # SPDX-License-Identifier: MIT | 联机项目需要额外在线能力。
            catalog.extend((("backend_online", "在线服务与后端", "P0", ("服务架构", "压测与故障恢复记录")), ("security_anticheat", "安全与反作弊", "P0", ("威胁清单", "滥用与封禁流程"))))  # SPDX-License-Identifier: MIT | 添加在线和安全模块。
        if project.get("business_model") in {"iap", "subscription", "ads"}:  # SPDX-License-Identifier: MIT | 持续变现模式需要经济和运营设计。
            catalog.extend((("economy", "经济与商业化系统", "P0", ("货币流图", "付费点与公平性说明")), ("analytics_liveops", "数据分析与持续运营", "P1", ("事件埋点表", "运营节奏与回滚方案"))))  # SPDX-License-Identifier: MIT | 添加经济和持续运营模块。
        gaps: list[ModuleGap] = []  # SPDX-License-Identifier: MIT | 初始化模块缺口列表。
        for module_id, name, priority, evidence in catalog:  # SPDX-License-Identifier: MIT | 逐项检查项目模块目录。
            current = str(status.get(module_id) or "unknown")  # SPDX-License-Identifier: MIT | 读取创作者声明的当前状态。
            if current not in {"ready", "validated"}:  # SPDX-License-Identifier: MIT | 仅验证完成的模块不列为缺口。
                reason = f"当前状态为 {current}；需在进入下一阶段前形成可验证证据"  # SPDX-License-Identifier: MIT | 生成基于状态的缺口理由。
                gaps.append(ModuleGap(module_id, name, current, reason, priority, tuple(evidence)))  # SPDX-License-Identifier: MIT | 追加结构化模块缺口。
        if rating.assessment_result.value != "B_GATE":  # SPDX-License-Identifier: MIT | 评分未过门槛时优先关联规则阻塞项。
            gaps.insert(0, ModuleGap("rating_blockers", "评分阻塞项修复", "blocked", "；".join(rating.blocking_issues) or "评分证据不足", "P0", ("新版本问卷", "更新后的方案或 Demo", "阻塞项差异说明")))  # SPDX-License-Identifier: MIT | 添加评分阻塞修复模块。
        return gaps  # SPDX-License-Identifier: MIT | 返回模块缺口列表。

    def _role_gaps(self, project: dict[str, Any], modules: list[ModuleGap]) -> list[RoleGap]:  # SPDX-License-Identifier: MIT | 将模块缺口映射为团队角色。
        team = project.get("team") if isinstance(project.get("team"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取团队结构。
        existing = {str(role).lower() for role in team.get("roles", [])} if isinstance(team.get("roles"), list) else set()  # SPDX-License-Identifier: MIT | 规范化现有角色名称。
        requirements = {  # SPDX-License-Identifier: MIT | 定义模块到标准角色的首版映射。
            "core_design": ("游戏策划", "原型期", "全职或核心合伙人"),  # SPDX-License-Identifier: MIT | 映射核心玩法设计角色。
            "prototype": ("客户端程序", "立即", "全职或长期合作"),  # SPDX-License-Identifier: MIT | 映射可玩原型开发角色。
            "ux_onboarding": ("UX/交互设计", "垂直切片前", "兼职或外包"),  # SPDX-License-Identifier: MIT | 映射交互设计角色。
            "art_pipeline": ("美术负责人", "垂直切片前", "核心成员"),  # SPDX-License-Identifier: MIT | 映射美术生产角色。
            "audio": ("音频设计", "垂直切片后", "外包或兼职"),  # SPDX-License-Identifier: MIT | 映射音频角色。
            "qa": ("QA/测试", "垂直切片开始", "兼职后转持续投入"),  # SPDX-License-Identifier: MIT | 映射质量保障角色。
            "store_assets": ("发行运营", "上线准备期", "外包或合作方"),  # SPDX-License-Identifier: MIT | 映射商店与发行角色。
            "compliance": ("合规/隐私顾问", "上线准备期", "专项外部顾问"),  # SPDX-License-Identifier: MIT | 映射合规角色。
            "backend_online": ("后端/服务端程序", "原型期", "全职或长期合作"),  # SPDX-License-Identifier: MIT | 映射在线服务角色。
            "security_anticheat": ("安全工程师", "联机测试前", "专项顾问或服务商"),  # SPDX-License-Identifier: MIT | 映射安全角色。
            "economy": ("数值/经济策划", "垂直切片前", "核心成员"),  # SPDX-License-Identifier: MIT | 映射经济设计角色。
            "analytics_liveops": ("数据与运营", "测试期", "兼职后转持续投入"),  # SPDX-License-Identifier: MIT | 映射数据运营角色。
        }  # SPDX-License-Identifier: MIT | 模块角色映射结束。
        aliases = {"游戏策划": {"游戏策划", "策划", "designer"}, "客户端程序": {"客户端程序", "程序", "programmer", "developer"}, "UX/交互设计": {"ux/交互设计", "ux", "交互", "交互设计"}, "美术负责人": {"美术负责人", "美术", "artist", "art"}, "音频设计": {"音频设计", "音频", "sound", "audio"}, "QA/测试": {"qa/测试", "qa", "测试", "tester"}, "发行运营": {"发行运营", "发行", "运营", "publishing"}, "合规/隐私顾问": {"合规/隐私顾问", "合规", "隐私", "legal"}, "后端/服务端程序": {"后端/服务端程序", "后端", "服务端", "backend"}, "安全工程师": {"安全工程师", "安全", "security"}, "数值/经济策划": {"数值/经济策划", "数值策划", "经济策划"}, "数据与运营": {"数据与运营", "数据", "数据分析", "liveops"}}  # SPDX-License-Identifier: MIT | 定义常见中英文现有角色别名避免重复推荐。
        gaps: list[RoleGap] = []  # SPDX-License-Identifier: MIT | 初始化团队角色缺口。
        for gap in modules:  # SPDX-License-Identifier: MIT | 逐个缺失模块检查责任角色。
            requirement = requirements.get(gap.module_id)  # SPDX-License-Identifier: MIT | 读取模块对应角色要求。
            if requirement is None:  # SPDX-License-Identifier: MIT | 没有专属角色的模块由现有负责人协调。
                continue  # SPDX-License-Identifier: MIT | 跳过无法可靠映射的模块。
            role, timing, engagement = requirement  # SPDX-License-Identifier: MIT | 展开角色建议。
            accepted_names = aliases.get(role, {role.lower()})  # SPDX-License-Identifier: MIT | 获取角色名称别名。
            if not any(name.lower() in existing for name in accepted_names):  # SPDX-License-Identifier: MIT | 判断团队是否已经覆盖该角色。
                gaps.append(RoleGap(role, f"负责补齐模块：{gap.name}", timing, engagement, gap.priority))  # SPDX-License-Identifier: MIT | 追加有模块依据并继承优先级的角色缺口。
        unique = {(gap.role, gap.timing): gap for gap in gaps}  # SPDX-License-Identifier: MIT | 按角色和进入时机去重。
        return list(unique.values())  # SPDX-License-Identifier: MIT | 返回团队角色缺口。

    def _investment_needs(self, project: dict[str, Any], modules: list[ModuleGap], roles: list[RoleGap]) -> list[InvestmentNeed]:  # SPDX-License-Identifier: MIT | 生成可解释投入需求。
        schedule = project.get("schedule") if isinstance(project.get("schedule"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取预算数据。
        required = schedule.get("budget")  # SPDX-License-Identifier: MIT | 读取创作者预计总预算。
        available = schedule.get("available_funding")  # SPDX-License-Identifier: MIT | 读取创作者现有资金。
        numeric = all(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0 for value in (required, available))  # SPDX-License-Identifier: MIT | 确认两个数字均可安全计算。
        amount_gap = max(0.0, float(required) - float(available)) if numeric else None  # SPDX-License-Identifier: MIT | 仅使用创作者数字计算资金差额。
        needs = [InvestmentNeed("cash", "覆盖创作者填写预算与现有资金之间的差额", amount_gap, "CNY" if numeric else "待创作者填写", "calculated" if numeric else "unknown")]  # SPDX-License-Identifier: MIT | 添加资金投入诊断。
        needs.append(InvestmentNeed("people", f"需要补齐 {len(roles)} 类角色能力", None, "角色/人月需团队估算", "derived_from_module_gaps"))  # SPDX-License-Identifier: MIT | 添加人才投入诊断。
        needs.append(InvestmentNeed("production", f"仍有 {len(modules)} 个模块未达到 validated", None, "工作量需拆解后估算", "derived_from_questionnaire"))  # SPDX-License-Identifier: MIT | 添加制作投入诊断。
        if any(module.module_id in {"qa", "compliance", "store_assets"} for module in modules):  # SPDX-License-Identifier: MIT | 上线准备缺口需要专项外部服务。
            needs.append(InvestmentNeed("external_services", "测试设备、合规咨询、商店素材或发行支持", None, "按报价确认", "requires_vendor_quotes"))  # SPDX-License-Identifier: MIT | 添加不能由 Agent 猜价的外部服务投入。
        return needs  # SPDX-License-Identifier: MIT | 返回投入需求列表。

    def _production_roadmap(self, project: dict[str, Any], modules: list[ModuleGap]) -> list[RoadmapStep]:  # SPDX-License-Identifier: MIT | 生成不绑定具体引擎的制作路线。
        missing_names = tuple(module.name for module in modules if module.priority == "P0")  # SPDX-License-Identifier: MIT | 收集必须优先解决的模块。
        return [  # SPDX-License-Identifier: MIT | 返回阶段化制作路线。
            RoadmapStep(1, "资料与目标冻结", "确认问卷、目标玩家、平台、范围和预算", ("所有 AI 代填关键答案由创作者确认", "方案文件与资料清单哈希冻结")),  # SPDX-License-Identifier: MIT | 定义输入冻结阶段。
            RoadmapStep(2, "核心原型", "用最低成本证明核心循环和首次吸引", ("可从启动进入一局完整循环", "关键假设有试玩证据")),  # SPDX-License-Identifier: MIT | 定义核心原型阶段。
            RoadmapStep(3, "垂直切片", "用接近目标质量的一小段验证内容生产与团队协作", ("核心美术、音频、UX 达到目标基准", "工期与成本可被重新估算")),  # SPDX-License-Identifier: MIT | 定义垂直切片阶段。
            RoadmapStep(4, "正式生产", "按里程碑扩展内容并持续控制范围", ("P0 模块已关闭：" + "、".join(missing_names) if missing_names else "所有 P0 模块已验证", "每个里程碑有可运行构建和回归记录")),  # SPDX-License-Identifier: MIT | 定义正式生产阶段。
            RoadmapStep(5, "Alpha/Beta 与真人验证", "完成全部功能后验证稳定性、留存和体验", ("功能锁定", "关键缺陷关闭", "完成度与 B_GATE 满足平台真人评分入口")),  # SPDX-License-Identifier: MIT | 定义测试与真人验证阶段。
            RoadmapStep(6, "候选版本与上线", "锁定候选构建并完成目标商店审核", ("构建、商店描述和声明一致", "平台检查、人工终审和回滚方案完成")),  # SPDX-License-Identifier: MIT | 定义上线阶段。
            RoadmapStep(7, "上线后运营", "监控质量、反馈和商业指标并控制更新风险", ("崩溃与关键指标可观测", "热修复、客服和版本回退流程可执行")),  # SPDX-License-Identifier: MIT | 定义上线后运营阶段。
        ]  # SPDX-License-Identifier: MIT | 制作路线定义结束。

    def _platforms(self, project: dict[str, Any]) -> tuple[str, ...]:  # SPDX-License-Identifier: MIT | 规范化目标发布平台。
        raw = project.get("platforms")  # SPDX-License-Identifier: MIT | 读取问卷中的目标平台。
        return tuple(str(platform).lower() for platform in raw) if isinstance(raw, list) else (str(raw).lower(),) if raw else ("unspecified",)  # SPDX-License-Identifier: MIT | 返回稳定平台列表。

    def _release_steps(self, platform: str) -> tuple[RoadmapStep, ...]:  # SPDX-License-Identifier: MIT | 按平台生成可核对的上架路线。
        if platform in {"steam", "pc_steam"}:  # SPDX-License-Identifier: MIT | 生成 Steam 官方审核要点对应路线。
            return (  # SPDX-License-Identifier: MIT | 返回 Steam 上架步骤。
                RoadmapStep(1, "Steamworks 准备", "配置产品、商店信息和内容问卷", ("内容问卷完成", "商店功能只描述首发真实内容")),  # SPDX-License-Identifier: MIT | 定义 Steam 基础配置。
                RoadmapStep(2, "商店素材与页面", "提交真实玩法截图、可读标题素材和连贯说明", ("截图为真实玩法", "文案、功能与构建一致")),  # SPDX-License-Identifier: MIT | 定义 Steam 商店页准备。
                RoadmapStep(3, "近最终构建", "验证所有声明支持的系统和功能", ("支持系统均可启动", "商店所列功能已实现", "交易规则符合 Steam 要求")),  # SPDX-License-Identifier: MIT | 定义 Steam 构建准备。
                RoadmapStep(4, "提交审核", "将商店页与构建标记为准备审核", ("按计划至少预留七个工作日", "处理 Valve 反馈并重新提交")),  # SPDX-License-Identifier: MIT | 定义 Steam 审核提交。
                RoadmapStep(5, "发行与更新", "审核通过后安排发行并持续更新", ("页面和构建为 Ready for release", "上线监控和更新流程已建立")),  # SPDX-License-Identifier: MIT | 定义 Steam 发行阶段。
            )  # SPDX-License-Identifier: MIT | Steam 路线定义结束。
        if platform in {"android", "google_play", "play"}:  # SPDX-License-Identifier: MIT | 生成 Google Play 官方准备步骤。
            return (  # SPDX-License-Identifier: MIT | 返回 Google Play 上架步骤。
                RoadmapStep(1, "Play Console 与应用资料", "创建游戏并完成分类、联系信息和商店资料", ("应用类别与目标市场确认", "截图、视频和说明完成")),  # SPDX-License-Identifier: MIT | 定义 Play Console 基础配置。
                RoadmapStep(2, "应用内容与合规声明", "完成隐私、广告、目标受众、内容和数据安全信息", ("隐私政策可访问", "敏感权限和审核访问方式已说明")),  # SPDX-License-Identifier: MIT | 定义 Google Play 合规准备。
                RoadmapStep(3, "测试轨道", "使用内部或封闭测试收集发布前反馈", ("测试要求满足账户类型规则", "关键崩溃与阻塞问题关闭")),  # SPDX-License-Identifier: MIT | 定义 Google Play 测试阶段。
                RoadmapStep(4, "发布构建", "生成签名 App Bundle、发布说明并完成预审核检查", ("App Signing 状态正常", "Bundle、映射或符号文件按项目需要上传")),  # SPDX-License-Identifier: MIT | 定义 Google Play 构建准备。
                RoadmapStep(5, "提交审核与生产发布", "发送审核并在通过后分阶段发布", ("所有强制任务完成", "监控崩溃、政策反馈和版本指标")),  # SPDX-License-Identifier: MIT | 定义 Google Play 上线阶段。
            )  # SPDX-License-Identifier: MIT | Google Play 路线定义结束。
        return (RoadmapStep(1, "平台待确认", "目标平台尚无受控发布模板", ("选择具体商店和地区", "由发行或合规负责人核对最新官方要求")),)  # SPDX-License-Identifier: MIT | 对未知平台明确不编造流程。

    def _assumptions(self, project: dict[str, Any]) -> list[str]:  # SPDX-License-Identifier: MIT | 收集报告必须披露的未知项。
        assumptions: list[str] = []  # SPDX-License-Identifier: MIT | 初始化假设列表。
        schedule = project.get("schedule") if isinstance(project.get("schedule"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取预算问卷。
        if not isinstance(schedule.get("available_funding"), (int, float)):  # SPDX-License-Identifier: MIT | 检查是否能够计算资金缺口。
            assumptions.append("未提供现有资金，Agent 不估算现金缺口")  # SPDX-License-Identifier: MIT | 明示现金估算限制。
        if not project.get("module_status"):  # SPDX-License-Identifier: MIT | 检查是否提供模块现状。
            assumptions.append("未填写模块现状，所有模块暂按 unknown 输出")  # SPDX-License-Identifier: MIT | 明示模块诊断保守假设。
        assumptions.append("工期、人月和外包价格必须由团队拆解任务或取得报价后确认")  # SPDX-License-Identifier: MIT | 禁止 Agent 凭空给出项目估价。
        return assumptions  # SPDX-License-Identifier: MIT | 返回诊断假设列表。
