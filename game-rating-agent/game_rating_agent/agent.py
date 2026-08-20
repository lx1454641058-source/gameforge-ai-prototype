"""无外部依赖的游戏评分 Agent 内核。"""  # SPDX-License-Identifier: MIT | 描述模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import asdict, dataclass, field  # SPDX-License-Identifier: MIT | 使用标准库定义结构化合同。
from datetime import datetime, timezone  # SPDX-License-Identifier: MIT | 生成可审计 UTC 时间。
from enum import Enum  # SPDX-License-Identifier: MIT | 定义受控业务状态。
from hashlib import sha256  # SPDX-License-Identifier: MIT | 冻结输入内容哈希。
from typing import Any, Protocol  # SPDX-License-Identifier: MIT | 定义模型适配接口和 JSON 类型。
import json  # SPDX-License-Identifier: MIT | 生成稳定输入快照与报告。
import re  # SPDX-License-Identifier: MIT | 检查常见提示词注入信号。
import uuid  # SPDX-License-Identifier: MIT | 生成本地运行标识。
from .knowledge_base import GenreKnowledgeBase  # SPDX-License-Identifier: MIT | 接入类型知识库进行结构化同质化比对。

DIMENSIONS = (  # SPDX-License-Identifier: MIT | 定义九维游戏认知模型。
    "core_loop",  # SPDX-License-Identifier: MIT | 核心循环维度。
    "first_attraction",  # SPDX-License-Identifier: MIT | 首次吸引维度。
    "sustained_motivation",  # SPDX-License-Identifier: MIT | 持续动机维度。
    "progression_feedback",  # SPDX-License-Identifier: MIT | 成长反馈维度。
    "content_structure",  # SPDX-License-Identifier: MIT | 内容结构维度。
    "social_competition",  # SPDX-License-Identifier: MIT | 社交竞争维度。
    "value_exchange",  # SPDX-License-Identifier: MIT | 价值交换维度。
    "feasibility",  # SPDX-License-Identifier: MIT | 产品可实现性维度，假设可获得充足团队与资金后判断游戏本身能否做出来。
    "innovation_candidate",  # SPDX-License-Identifier: MIT | 创新候选维度。
)  # SPDX-License-Identifier: MIT | 九维定义结束。

WORKFLOW = (  # SPDX-License-Identifier: MIT | 定义可审计的 Agent 步骤。
    "freeze_input",  # SPDX-License-Identifier: MIT | 冻结输入版本和哈希。
    "ingestion",  # SPDX-License-Identifier: MIT | 校验字段并隔离不可信内容。
    "structure",  # SPDX-License-Identifier: MIT | 提取核心循环与系统关系。
    "motivation",  # SPDX-License-Identifier: MIT | 提取首次吸引和持续动机。
    "value",  # SPDX-License-Identifier: MIT | 分析商业模式和价值交换。
    "feasibility",  # SPDX-License-Identifier: MIT | 判断范围、技术路径、平台约束和关键风险下的产品可实现性。
    "innovation",  # SPDX-License-Identifier: MIT | 记录差异点和新类型候选。
    "rule_engine",  # SPDX-License-Identifier: MIT | 由确定性规则写业务结论。
    "report",  # SPDX-License-Identifier: MIT | 生成证据化报告。
)  # SPDX-License-Identifier: MIT | 工作流定义结束。

INJECTION_PATTERNS = (  # SPDX-License-Identifier: MIT | 定义基础注入风险信号而非完整防护。
    r"ignore\s+(all\s+)?previous\s+instructions",  # SPDX-License-Identifier: MIT | 检测英文覆盖指令。
    r"reveal\s+(the\s+)?system\s+prompt",  # SPDX-License-Identifier: MIT | 检测系统提示词窃取。
    r"忽略.{0,8}(之前|以上).{0,8}(指令|规则)",  # SPDX-License-Identifier: MIT | 检测中文覆盖指令。
    r"输出.{0,8}(系统提示词|system prompt)",  # SPDX-License-Identifier: MIT | 检测中文提示词窃取。
)  # SPDX-License-Identifier: MIT | 注入风险信号定义结束。

class AssessmentResult(str, Enum):  # SPDX-License-Identifier: MIT | 限制 AI 初筛结果集合。
    D = "D"  # SPDX-License-Identifier: MIT | 表示存在致命缺失。
    C = "C"  # SPDX-License-Identifier: MIT | 表示基本完整但尚不足。
    B_GATE = "B_GATE"  # SPDX-License-Identifier: MIT | 表示值得进入真人市场验证。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 防止运行步骤记录被后续修改。
class StepRecord:  # SPDX-License-Identifier: MIT | 描述单个 Agent 步骤审计记录。
    name: str  # SPDX-License-Identifier: MIT | 保存步骤名称。
    status: str  # SPDX-License-Identifier: MIT | 保存步骤完成状态。
    detail: str  # SPDX-License-Identifier: MIT | 保存步骤结果摘要。
    completed_at: str  # SPDX-License-Identifier: MIT | 保存 UTC 完成时间。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结单项维度证据。
class DimensionEvidence:  # SPDX-License-Identifier: MIT | 描述维度分数和输入依据。
    score: int  # SPDX-License-Identifier: MIT | 使用零到四的首版离散分。
    rationale: str  # SPDX-License-Identifier: MIT | 保存可读判定理由。
    evidence_paths: tuple[str, ...]  # SPDX-License-Identifier: MIT | 指向输入字段而非模型自由声称。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结证据提取结果。
class ExtractionResult:  # SPDX-License-Identifier: MIT | 作为模型层和规则层之间的结构合同。
    dimensions: dict[str, DimensionEvidence]  # SPDX-License-Identifier: MIT | 保存九维结构化证据。
    hard_gates: dict[str, bool]  # SPDX-License-Identifier: MIT | 保存四个硬门槛事实。
    human_review_ready: bool  # SPDX-License-Identifier: MIT | 标记是否达到真人评分申请所需的完成度和可运行版本门槛。
    strengths: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存有字段依据的优势。
    risks: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存有字段依据的风险。
    uncertainties: tuple[str, ...]  # SPDX-License-Identifier: MIT | 明确记录未知信息。
    confidence: float  # SPDX-License-Identifier: MIT | 表示提取可靠度而非成功概率。
    injection_signals: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存不可信内容中的风险信号。
    knowledge_comparison: dict[str, Any]  # SPDX-License-Identifier: MIT | 保存类型知识库的可解释对比快照。
    resource_readiness: dict[str, Any]  # SPDX-License-Identifier: MIT | 单独保存当前团队、计划与资金准备度，不参与九维评分。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结确定性规则配置。
class ProvisionalRubric:  # SPDX-License-Identifier: MIT | 定义等待领域专家校准的首版阈值。
    version: str = "GF-GAME-RUBRIC-0.4-PROVISIONAL"  # SPDX-License-Identifier: MIT | 标记增加真人评分完成度门槛后的暂定规则。
    min_average_for_b_gate: float = 2.6  # SPDX-License-Identifier: MIT | 设置 B 门槛平均维度暂定值。
    min_confidence_for_b_gate: float = 0.65  # SPDX-License-Identifier: MIT | 设置 B 门槛最低证据可靠度。
    required_dimension_scores: dict[str, int] = field(default_factory=lambda: {  # SPDX-License-Identifier: MIT | 定义关键维度暂定下限。
        "core_loop": 3,  # SPDX-License-Identifier: MIT | 要求核心循环清晰且有证据。
        "first_attraction": 2,  # SPDX-License-Identifier: MIT | 要求首次吸引至少可解释。
        "sustained_motivation": 3,  # SPDX-License-Identifier: MIT | 要求持续动机较完整。
        "value_exchange": 2,  # SPDX-License-Identifier: MIT | 要求对应商业模式的价值逻辑成立。
        "feasibility": 2,  # SPDX-License-Identifier: MIT | 要求产品在资源充足假设下不存在未处理的实现阻断。
        "innovation_candidate": 3,  # SPDX-License-Identifier: MIT | 要求提供对标、规则差异和验证方案，避免同质化项目自动进入 B 门槛。
    })  # SPDX-License-Identifier: MIT | 关键维度暂定下限结束。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结一次评分业务结果。
class RatingResult:  # SPDX-License-Identifier: MIT | 描述可序列化的最终评分报告。
    run_id: str  # SPDX-License-Identifier: MIT | 保存运行唯一标识。
    project_id: str  # SPDX-License-Identifier: MIT | 保存被评分项目标识。
    project_version: str  # SPDX-License-Identifier: MIT | 保存被评分项目版本。
    assessment_result: AssessmentResult  # SPDX-License-Identifier: MIT | 保存 D、C 或 B_GATE。
    game_dna: dict[str, int]  # SPDX-License-Identifier: MIT | 保存九维分数快照。
    hard_gates: dict[str, bool]  # SPDX-License-Identifier: MIT | 保存硬门槛快照。
    human_review_ready: bool  # SPDX-License-Identifier: MIT | 保存是否可以申请真人评分的独立完成度判定。
    blocking_issues: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存阻止 B 门槛的问题。
    strengths: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存证据化优势。
    risks: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存证据化风险。
    improvement_actions: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存按规则生成的优先行动。
    confidence: float  # SPDX-License-Identifier: MIT | 保存证据提取可靠度。
    needs_human_review: bool  # SPDX-License-Identifier: MIT | 标记异常或低置信度人工复核。
    rubric_version: str  # SPDX-License-Identifier: MIT | 保存规则版本用于回放。
    extractor_version: str  # SPDX-License-Identifier: MIT | 保存提取器版本用于回放。
    input_hash: str  # SPDX-License-Identifier: MIT | 保存输入快照哈希。
    steps: tuple[StepRecord, ...]  # SPDX-License-Identifier: MIT | 保存完整步骤审计链。
    limitations: tuple[str, ...]  # SPDX-License-Identifier: MIT | 对外说明结论能力边界。
    knowledge_comparison: dict[str, Any]  # SPDX-License-Identifier: MIT | 保存类型基线、拥挤组合和创新候选比对结果。
    resource_readiness: dict[str, Any]  # SPDX-License-Identifier: MIT | 保存不计入九维的团队与资金现状，供缺口诊断使用。

    def to_dict(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 转换为 API 友好的 JSON 对象。
        payload = asdict(self)  # SPDX-License-Identifier: MIT | 递归展开不可变数据类。
        payload["assessment_result"] = self.assessment_result.value  # SPDX-License-Identifier: MIT | 将枚举转换为稳定字符串。
        return payload  # SPDX-License-Identifier: MIT | 返回结构化报告。

class EvidenceExtractor(Protocol):  # SPDX-License-Identifier: MIT | 定义可替换模型供应商接口。
    version: str  # SPDX-License-Identifier: MIT | 要求每个提取器提供可审计版本。

    def extract(self, project: dict[str, Any]) -> ExtractionResult:  # SPDX-License-Identifier: MIT | 约束提取器输出结构。
        ...  # SPDX-License-Identifier: MIT | 协议方法无需实现。

class DeterministicEvidenceExtractor:  # SPDX-License-Identifier: MIT | 提供无 API Key 的离线 MVP 提取器。
    version = "deterministic-extractor-1.1"  # SPDX-License-Identifier: MIT | 标记产品可实现性与分层成长反馈证据结构升级。

    def __init__(self, knowledge_base: GenreKnowledgeBase | None = None) -> None:  # SPDX-License-Identifier: MIT | 支持注入经审核的新知识库版本。
        self.knowledge_base = knowledge_base or GenreKnowledgeBase()  # SPDX-License-Identifier: MIT | 默认使用内置类型评分知识库。

    def extract(self, project: dict[str, Any]) -> ExtractionResult:  # SPDX-License-Identifier: MIT | 从规范项目表单提取证据。
        signals = self._find_injection_signals(project)  # SPDX-License-Identifier: MIT | 将文档内容视作不可信数据检查。
        knowledge_comparison = self.knowledge_base.compare(project)  # SPDX-License-Identifier: MIT | 在评分前完成类型、机制和创新位置的数据比对。
        dimensions = {  # SPDX-License-Identifier: MIT | 为九维生成基于字段存在度的可复现分数。
            "core_loop": self._chain_score(project.get("core_loop"), "core_loop"),  # SPDX-License-Identifier: MIT | 评估行为链完整度。
            "first_attraction": self._text_score(project.get("first_session_hook"), "first_session_hook"),  # SPDX-License-Identifier: MIT | 评估首次吸引描述。
            "sustained_motivation": self._text_score(project.get("long_term_motivation"), "long_term_motivation"),  # SPDX-License-Identifier: MIT | 评估持续动机描述。
            "progression_feedback": self._progression_score(project.get("progression_feedback")),  # SPDX-License-Identifier: MIT | 按局内、局外或混合模式评估成长反馈闭环。
            "content_structure": self._text_score(project.get("content_structure"), "content_structure"),  # SPDX-License-Identifier: MIT | 评估内容结构描述。
            "social_competition": self._optional_score(project.get("social_competition"), "social_competition"),  # SPDX-License-Identifier: MIT | 不因单机或非社交设计机械扣分。
            "value_exchange": self._value_score(project),  # SPDX-License-Identifier: MIT | 按商业模式评估价值交换。
            "feasibility": self._product_feasibility_score(project),  # SPDX-License-Identifier: MIT | 在资源充足假设下评估范围、技术路径、平台约束与风险。
            "innovation_candidate": self._differentiation_score(knowledge_comparison),  # SPDX-License-Identifier: MIT | 按知识库的结构化比对结果评估同质化风险。
        }  # SPDX-License-Identifier: MIT | 九维证据生成结束。
        evidence_items = project.get("evidence", []) if isinstance(project.get("evidence"), list) else []  # SPDX-License-Identifier: MIT | 安全读取上传证据清单。
        evidence_count = len(evidence_items)  # SPDX-License-Identifier: MIT | 统计所有可验证资料数量。
        demo_count = sum(1 for item in evidence_items if isinstance(item, dict) and item.get("type") == "demo")  # SPDX-License-Identifier: MIT | 单独统计可运行 Demo 证据。
        development_stage = str(project.get("development_stage") or "")  # SPDX-License-Identifier: MIT | 读取已规范化的项目制作阶段。
        early_stage = development_stage in {"idea", "concept", "pre_prototype"}  # SPDX-License-Identifier: MIT | 识别尚不应强制要求 Demo 的早期阶段。
        human_review_ready = development_stage in {"vertical_slice", "alpha", "beta", "release_candidate"} and demo_count > 0  # SPDX-License-Identifier: MIT | 仅允许垂直切片及以后且含可运行版本的项目申请真人评分。
        required_fields = ("project_id", "version", "title", "pitch", "core_loop", "business_model", "scope", "production_feasibility")  # SPDX-License-Identifier: MIT | 关键门槛只检查产品定义，不把现有团队和资金当成游戏能否实现的条件。
        critical_complete = all(self._present(project.get(key)) for key in required_fields)  # SPDX-License-Identifier: MIT | 检查关键字段是否齐全。
        hard_gates = {  # SPDX-License-Identifier: MIT | 生成四个事实硬门槛。
            "critical_fields_complete": critical_complete,  # SPDX-License-Identifier: MIT | 记录关键字段完整门槛。
            "core_loop_defined": dimensions["core_loop"].score >= 2,  # SPDX-License-Identifier: MIT | 记录核心循环门槛。
            "stage_evidence_consistent": early_stage or demo_count > 0,  # SPDX-License-Identifier: MIT | 早期允许无 Demo，进入原型后必须有可运行证据。
            "basic_product_feasibility": dimensions["feasibility"].score >= 2,  # SPDX-License-Identifier: MIT | 记录资源充足假设下的产品可实现性门槛。
        }  # SPDX-License-Identifier: MIT | 硬门槛生成结束。
        missing_dimensions = tuple(name for name, evidence in dimensions.items() if evidence.score <= 1)  # SPDX-License-Identifier: MIT | 收集薄弱或未知维度。
        strengths = tuple(f"{name} 有明确输入依据" for name, evidence in dimensions.items() if evidence.score >= 3)  # SPDX-License-Identifier: MIT | 仅从高分字段生成优势。
        knowledge_risk = (f"类型知识库同质化风险={knowledge_comparison.homogeneity_risk}；{knowledge_comparison.rationale}",) if knowledge_comparison.homogeneity_risk != "低" else ()  # SPDX-License-Identifier: MIT | 将中高同质化风险写入报告而不是隐去数据比对结果。
        risks = tuple(f"{name} 证据不足" for name in missing_dimensions) + knowledge_risk  # SPDX-License-Identifier: MIT | 从低分维度和类型比对生成风险。
        uncertainties = tuple(f"待补充 {name}" for name in missing_dimensions)  # SPDX-License-Identifier: MIT | 明确区分未知与负面判断。
        coverage = sum(1 for evidence in dimensions.values() if evidence.score >= 2) / len(DIMENSIONS)  # SPDX-License-Identifier: MIT | 计算九维信息覆盖率。
        confidence = round(max(0.25, min(0.95, 0.45 + coverage * 0.4 + min(evidence_count, 3) * 0.04 - len(signals) * 0.2)), 2)  # SPDX-License-Identifier: MIT | 计算可复现的提取可靠度。
        resource_readiness = self._resource_readiness(project)  # SPDX-License-Identifier: MIT | 另算当前资源准备度供团队和资金缺口报告使用。
        return ExtractionResult(dimensions, hard_gates, human_review_ready, strengths, risks, uncertainties, confidence, signals, knowledge_comparison.__dict__, resource_readiness)  # SPDX-License-Identifier: MIT | 返回九维、真人评分资格、知识库比对和不计分资源准备度合同。

    def _present(self, value: Any) -> bool:  # SPDX-License-Identifier: MIT | 统一判断字段是否具有实际内容。
        return bool(value.strip()) if isinstance(value, str) else value not in (None, [], {})  # SPDX-License-Identifier: MIT | 排除空值、空集合和纯空白字符串。

    def _chain_score(self, value: Any, path: str) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 评估核心行为链字段。
        count = sum(1 for item in value if isinstance(item, str) and item.strip()) if isinstance(value, list) else 0  # SPDX-License-Identifier: MIT | 只统计结构化列表中的非空行为步骤。
        score = 4 if count >= 5 else 3 if count >= 4 else 2 if count >= 3 else 1 if count >= 1 else 0  # SPDX-License-Identifier: MIT | 根据行为链长度生成首版离散分。
        return DimensionEvidence(score, f"结构化行为链包含 {count} 个步骤", (path,) if count else ())  # SPDX-License-Identifier: MIT | 返回带字段路径的证据。

    def _text_score(self, value: Any, path: str) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 评估必需的叙述字段。
        length = len(value.strip()) if isinstance(value, str) else 0  # SPDX-License-Identifier: MIT | 统计清洗后的文本长度。
        score = 4 if length >= 100 else 3 if length >= 45 else 2 if length >= 18 else 1 if length else 0  # SPDX-License-Identifier: MIT | 使用透明长度规则衡量描述充分度。
        return DimensionEvidence(score, f"字段包含 {length} 个字符，尚未验证设计质量", (path,) if length else ())  # SPDX-License-Identifier: MIT | 避免把文本长度冒充设计质量。

    def _progression_score(self, value: Any) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 按游戏真实时间尺度评估成长与反馈闭环。
        if not isinstance(value, dict):  # SPDX-License-Identifier: MIT | 旧版自由文本缺少局内局外结构，不能继续按字数给高分。
            score = 1 if self._present(value) else 0  # SPDX-License-Identifier: MIT | 对旧版非空描述只保留最低迁移分，要求重新结构化确认。
            return DimensionEvidence(score, "成长反馈尚未按局内、局外或混合模式结构化", ("progression_feedback",) if score else ())  # SPDX-License-Identifier: MIT | 明确旧答案需要迁移而非判定设计失败。
        mode = str(value.get("mode") or "unknown")  # SPDX-License-Identifier: MIT | 读取局内、局外、混合或无成长模式。
        in_match = self._nonempty_list(value.get("in_match_progression"))  # SPDX-License-Identifier: MIT | 读取单局内经济、科技、兵力、地图或构筑进程。
        meta = self._nonempty_list(value.get("meta_progression"))  # SPDX-License-Identifier: MIT | 读取局间解锁、账号成长或长期内容进程。
        signals = self._nonempty_list(value.get("feedback_signals"))  # SPDX-License-Identifier: MIT | 读取视觉、音频、数值、状态变化或因果报告反馈。
        tradeoffs = self._present(value.get("decision_tradeoffs"))  # SPDX-License-Identifier: MIT | 检查成长是否改变选择而非只增加数值。
        failure = self._present(value.get("failure_learning"))  # SPDX-License-Identifier: MIT | 检查失败、回退、复盘或再尝试反馈。
        layer_present = bool(in_match) if mode == "in_match" else bool(meta) if mode == "meta" else bool(in_match and meta) if mode == "hybrid" else bool(in_match or meta) if mode == "none" else False  # SPDX-License-Identifier: MIT | 只要求所选主要时间尺度具备实际成长，RTS 不因没有局外成长被扣分。
        checks = (layer_present, bool(signals), tradeoffs, failure)  # SPDX-License-Identifier: MIT | 使用四项结构证据而非文本长度计算成长反馈。
        score = sum(checks)  # SPDX-License-Identifier: MIT | 每个闭环证据贡献一分，总分零到四。
        rationale = f"模式={mode}；局内机制={len(in_match)}；局外机制={len(meta)}；反馈信号={len(signals)}；选择影响={tradeoffs}；失败学习={failure}"  # SPDX-License-Identifier: MIT | 生成可复核的分层成长反馈理由。
        return DimensionEvidence(score, rationale, ("progression_feedback",) if score else ())  # SPDX-License-Identifier: MIT | 返回不偏向局外成长的结构化维度证据。

    def _optional_score(self, value: Any, path: str) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 评估不适用时不应惩罚的维度。
        if isinstance(value, dict) and self._present(value.get("not_applicable_reason")):  # SPDX-License-Identifier: MIT | 只接受含实际文字理由的不适用声明。
            return DimensionEvidence(2, "项目声明该维度不适用并提供了理由", (path,))  # SPDX-License-Identifier: MIT | 给予中性分避免类型偏见。
        text = value if isinstance(value, str) else ""  # SPDX-License-Identifier: MIT | 将非字符串按未知处理。
        return self._text_score(text, path)  # SPDX-License-Identifier: MIT | 复用透明文本充分度规则。

    def _differentiation_score(self, comparison: Any) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 将知识库比对结果转换为创新候选维度证据。
        paths = ("genre_ids", "gameplay_features", "reference_games", "innovation_axes", "innovation_features", "validation_methods")  # SPDX-License-Identifier: MIT | 只引用结构化类型和验证字段而非叙述文本长度。
        return DimensionEvidence(comparison.differentiation_score, comparison.rationale, paths)  # SPDX-License-Identifier: MIT | 返回由类型基线和证据闭环决定的离散分。

    def _value_score(self, project: dict[str, Any]) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 按商业模式检查价值交换。
        model = project.get("business_model")  # SPDX-License-Identifier: MIT | 读取结构化商业模式。
        statement = project.get("value_exchange")  # SPDX-License-Identifier: MIT | 读取玩家价值说明。
        base = self._text_score(statement, "value_exchange")  # SPDX-License-Identifier: MIT | 先评估价值说明充分度。
        known_models = {"buyout", "iap", "ads", "subscription", "dlc", "noncommercial"}  # SPDX-License-Identifier: MIT | 定义首版支持的价值模式。
        score = min(4, base.score + 1) if model in known_models and base.score >= 1 else base.score  # SPDX-License-Identifier: MIT | 有明确模式时提高结构完整度而非商业优劣。
        return DimensionEvidence(score, f"商业模式={model or '未知'}；{base.rationale}", tuple(path for path in ("business_model", "value_exchange") if self._present(project.get(path))))  # SPDX-License-Identifier: MIT | 返回模式相关证据路径。

    def _product_feasibility_score(self, project: dict[str, Any]) -> DimensionEvidence:  # SPDX-License-Identifier: MIT | 在团队资金充足假设下评估产品能否实现。
        value = project.get("production_feasibility") if isinstance(project.get("production_feasibility"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取产品可实现性结构答案。
        impossible = self._nonempty_list(value.get("blocking_constraints"))  # SPDX-License-Identifier: MIT | 读取物理、平台政策或关键依赖层面的明确阻断。
        unresolved = self._nonempty_list(value.get("unresolved_high_risks"))  # SPDX-License-Identifier: MIT | 读取尚未验证的高风险技术或内容问题。
        checks = (value.get("scope_bounded") is True, value.get("technical_path_known") is True, value.get("platform_constraints_known") is True, value.get("prototype_validation_plan") is True)  # SPDX-License-Identifier: MIT | 检查范围、技术路径、平台约束和原型验证四类产品证据。
        evidence_count = sum(checks)  # SPDX-License-Identifier: MIT | 统计与当前团队规模和资金无关的实现证据。
        if impossible:  # SPDX-License-Identifier: MIT | 明确存在不可绕过阻断时直接判定当前方案不可实现。
            score = 0  # SPDX-License-Identifier: MIT | 将未解决的硬阻断映射为零分。
        elif unresolved and value.get("prototype_validation_plan") is not True:  # SPDX-License-Identifier: MIT | 高风险存在且无验证方案时限制产品可实现性。
            score = min(1, evidence_count)  # SPDX-License-Identifier: MIT | 防止只写技术路线却不处理核心未知获得高分。
        elif unresolved:  # SPDX-License-Identifier: MIT | 有验证计划的高风险项目仍需保守限制。
            score = min(3, evidence_count)  # SPDX-License-Identifier: MIT | 允许进入验证但不能视为无风险可实现。
        else:  # SPDX-License-Identifier: MIT | 无明确高风险或阻断时按四类证据覆盖评分。
            score = evidence_count  # SPDX-License-Identifier: MIT | 范围、技术、平台、验证各贡献一分。
        rationale = f"资源充足假设；范围受控={checks[0]}；技术路径明确={checks[1]}；平台约束明确={checks[2]}；原型验证计划={checks[3]}；高风险={len(unresolved)}；硬阻断={len(impossible)}"  # SPDX-License-Identifier: MIT | 明确分数不由当前团队和资金决定。
        return DimensionEvidence(score, rationale, ("scope", "production_feasibility"))  # SPDX-License-Identifier: MIT | 返回产品范围与实现约束证据路径。

    def _resource_readiness(self, project: dict[str, Any]) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 单独计算当前资源准备度供缺口诊断展示。
        team = project.get("team") if isinstance(project.get("team"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取当前团队事实。
        schedule = project.get("schedule") if isinstance(project.get("schedule"), dict) else {}  # SPDX-License-Identifier: MIT | 安全读取当前计划与资金事实。
        roles = self._nonempty_list(team.get("roles"))  # SPDX-License-Identifier: MIT | 读取当前已覆盖角色。
        checks = (self._positive(team.get("size")), bool(roles), self._positive(schedule.get("months")), self._positive(schedule.get("budget")), self._positive(schedule.get("available_funding")))  # SPDX-License-Identifier: MIT | 检查人数、角色、周期、预算和已落实资金。
        count = sum(checks)  # SPDX-License-Identifier: MIT | 统计当前资源准备证据数量。
        score = 4 if count == 5 else 3 if count == 4 else 2 if count >= 2 else 1 if count == 1 else 0  # SPDX-License-Identifier: MIT | 将五项现状映射为独立零到四级准备度。
        return {"score": score, "evidence_count": count, "total_checks": 5, "counts_toward_game_dna": False, "rationale": f"当前资源准备证据 {count}/5；该结果只用于团队、资金和周期缺口，不参与九维总分或评分门槛"}  # SPDX-License-Identifier: MIT | 返回明确声明不计入九维的资源准备度。

    def _nonempty_list(self, value: Any) -> tuple[str, ...]:  # SPDX-License-Identifier: MIT | 统一清洗结构化字符串列表。
        return tuple(item.strip() for item in value if isinstance(item, str) and item.strip()) if isinstance(value, list) else ()  # SPDX-License-Identifier: MIT | 排除空白、非字符串和非列表输入。

    def _positive(self, value: Any) -> bool:  # SPDX-License-Identifier: MIT | 检查数值是否为有效正数。
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0  # SPDX-License-Identifier: MIT | 排除布尔值和非正数。

    def _find_injection_signals(self, project: dict[str, Any]) -> tuple[str, ...]:  # SPDX-License-Identifier: MIT | 扫描不可信文本中的常见注入信号。
        serialized = json.dumps(project, ensure_ascii=False, sort_keys=True)  # SPDX-License-Identifier: MIT | 将所有输入内容统一为扫描文本。
        return tuple(pattern for pattern in INJECTION_PATTERNS if re.search(pattern, serialized, re.IGNORECASE))  # SPDX-License-Identifier: MIT | 返回命中的规则标识而不执行输入指令。

class GameRatingAgent:  # SPDX-License-Identifier: MIT | 编排证据提取、规则判定和报告生成。
    def __init__(self, extractor: EvidenceExtractor | None = None, rubric: ProvisionalRubric | None = None) -> None:  # SPDX-License-Identifier: MIT | 支持替换模型提取器和规则版本。
        self.extractor = extractor or DeterministicEvidenceExtractor()  # SPDX-License-Identifier: MIT | 默认使用可离线回归的提取器。
        self.rubric = rubric or ProvisionalRubric()  # SPDX-License-Identifier: MIT | 默认使用明确标记为暂定的规则。

    def run(self, project: dict[str, Any]) -> RatingResult:  # SPDX-License-Identifier: MIT | 执行一次不可覆盖的评分运行。
        snapshot = json.dumps(project, ensure_ascii=False, sort_keys=True, separators=(",", ":"))  # SPDX-License-Identifier: MIT | 创建规范化输入快照。
        input_hash = sha256(snapshot.encode("utf-8")).hexdigest()  # SPDX-License-Identifier: MIT | 计算输入快照哈希。
        run_id = f"gfr_{uuid.uuid4().hex[:16]}"  # SPDX-License-Identifier: MIT | 创建本地运行标识。
        steps: list[StepRecord] = []  # SPDX-License-Identifier: MIT | 初始化步骤审计记录。
        self._step(steps, "freeze_input", f"已冻结 sha256:{input_hash[:12]}")  # SPDX-License-Identifier: MIT | 记录输入冻结结果。
        extraction = self.extractor.extract(project)  # SPDX-License-Identifier: MIT | 调用只负责证据提取的适配器。
        self._step(steps, "ingestion", f"关键字段门槛={extraction.hard_gates['critical_fields_complete']}；注入信号={len(extraction.injection_signals)}")  # SPDX-License-Identifier: MIT | 记录解析和输入风险。
        self._step(steps, "structure", self._score_detail(extraction, ("core_loop", "content_structure")))  # SPDX-License-Identifier: MIT | 记录结构分析摘要。
        self._step(steps, "motivation", self._score_detail(extraction, ("first_attraction", "sustained_motivation", "progression_feedback")))  # SPDX-License-Identifier: MIT | 记录动机分析摘要。
        self._step(steps, "value", self._score_detail(extraction, ("value_exchange", "social_competition")))  # SPDX-License-Identifier: MIT | 记录价值分析摘要。
        self._step(steps, "feasibility", f"{self._score_detail(extraction, ('feasibility',))}；资源准备度={extraction.resource_readiness.get('score', 0)}/4（不计分）")  # SPDX-License-Identifier: MIT | 同时审计产品可实现性与不计分的资源准备度。
        self._step(steps, "innovation", self._score_detail(extraction, ("innovation_candidate",)))  # SPDX-License-Identifier: MIT | 记录创新候选摘要。
        result, blockers = self._decide(extraction)  # SPDX-License-Identifier: MIT | 仅由确定性规则形成业务结论。
        self._step(steps, "rule_engine", f"规则版本={self.rubric.version}；结论={result.value}")  # SPDX-License-Identifier: MIT | 记录规则引擎结论和版本。
        actions = self._actions(blockers, extraction)  # SPDX-License-Identifier: MIT | 从阻塞项生成优先行动。
        self._step(steps, "report", f"生成 {len(blockers)} 个阻塞项和 {len(actions)} 个行动项")  # SPDX-License-Identifier: MIT | 记录报告生成摘要。
        needs_review = bool(extraction.injection_signals) or extraction.confidence < self.rubric.min_confidence_for_b_gate  # SPDX-License-Identifier: MIT | 低可靠度或注入信号转人工。
        project_id = str(project.get("project_id") or "unknown")  # SPDX-License-Identifier: MIT | 安全读取项目标识。
        project_version = str(project.get("version") or "unknown")  # SPDX-License-Identifier: MIT | 安全读取项目版本。
        dna = {name: extraction.dimensions[name].score for name in DIMENSIONS}  # SPDX-License-Identifier: MIT | 固定九维输出顺序与范围。
        limitations = (  # SPDX-License-Identifier: MIT | 声明首版 Agent 的能力边界。
            "该结果只包含 D、C、B_GATE，不是公开 S、A、B 评级。",  # SPDX-License-Identifier: MIT | 防止 AI 初筛与真人评级混淆。
            "当前阈值尚未经过领域专家和种子项目校准。",  # SPDX-License-Identifier: MIT | 防止暂定阈值被误认为标准。
            "类型知识库覆盖常见商业类型和机制组合，但不会替代接入实时商店、国内渠道或竞品数据库后的市场全量比对。",  # SPDX-License-Identifier: MIT | 明确内置知识库与未来实时市场数据源的边界。
            "进入真人评分仍需项目完成度达到平台规定门槛。",  # SPDX-License-Identifier: MIT | 保留真人评分阶段门槛。
        )  # SPDX-License-Identifier: MIT | 能力边界定义结束。
        return RatingResult(run_id, project_id, project_version, result, dna, extraction.hard_gates, extraction.human_review_ready, tuple(blockers), extraction.strengths, extraction.risks, tuple(actions), extraction.confidence, needs_review, self.rubric.version, self.extractor.version, input_hash, tuple(steps), limitations, extraction.knowledge_comparison, extraction.resource_readiness)  # SPDX-License-Identifier: MIT | 返回九维、真人评分资格、类型比对和不计分资源准备度的完整报告。

    def _decide(self, extraction: ExtractionResult) -> tuple[AssessmentResult, list[str]]:  # SPDX-License-Identifier: MIT | 使用暂定规则计算业务结论。
        failed_gates = [name for name, passed in extraction.hard_gates.items() if not passed]  # SPDX-License-Identifier: MIT | 收集致命硬门槛失败项。
        if failed_gates:  # SPDX-License-Identifier: MIT | 硬门槛优先于维度平均分。
            return AssessmentResult.D, [f"硬门槛未通过：{name}" for name in failed_gates]  # SPDX-License-Identifier: MIT | 任何致命缺失返回 D。
        blockers = []  # SPDX-License-Identifier: MIT | 初始化不通过 B 门槛的可解释原因。
        for name, minimum in self.rubric.required_dimension_scores.items():  # SPDX-License-Identifier: MIT | 逐项检查每个关键维度的暂定下限。
            if extraction.dimensions[name].score >= minimum:  # SPDX-License-Identifier: MIT | 已满足下限的维度不生成阻塞项。
                continue  # SPDX-License-Identifier: MIT | 继续检查下一维度。
            if name == "innovation_candidate":  # SPDX-License-Identifier: MIT | 为同质化风险提供创作者可执行的专用说明。
                blockers.append("同质化风险未解除：请补充同类对标、规则或体验层差异，以及试玩或数据验证计划")  # SPDX-License-Identifier: MIT | 明确说明未达到 B 门槛的补充要求。
                continue  # SPDX-License-Identifier: MIT | 避免再生成不易理解的内部维度名称。
            blockers.append(f"{name} 低于暂定门槛 {minimum}")  # SPDX-License-Identifier: MIT | 保留其他维度原有的透明阈值提示。
        weight_pairs = extraction.knowledge_comparison.get("dimension_weights", ())  # SPDX-License-Identifier: MIT | 读取知识库按游戏类型生成的完整九维权重。
        weights = {str(name): float(weight) for name, weight in weight_pairs if str(name) in extraction.dimensions}  # SPDX-License-Identifier: MIT | 只接受当前九维合同中登记的权重项。
        average = sum(extraction.dimensions[name].score * weights.get(name, 0.0) for name in DIMENSIONS) if weights else sum(item.score for item in extraction.dimensions.values()) / len(DIMENSIONS)  # SPDX-License-Identifier: MIT | 优先计算类型加权分并为外部旧提取器保留等权降级。
        if average < self.rubric.min_average_for_b_gate:  # SPDX-License-Identifier: MIT | 检查平均维度暂定门槛。
            blockers.append(f"类型加权九维分 {average:.2f} 低于暂定门槛 {self.rubric.min_average_for_b_gate:.2f}")  # SPDX-License-Identifier: MIT | 记录按类型评分重点计算的阻塞证据。
        if extraction.confidence < self.rubric.min_confidence_for_b_gate:  # SPDX-License-Identifier: MIT | 防止低可靠度自动进入 B 门槛。
            blockers.append(f"证据可靠度 {extraction.confidence:.2f} 低于暂定门槛 {self.rubric.min_confidence_for_b_gate:.2f}")  # SPDX-License-Identifier: MIT | 记录可靠度阻塞证据。
        if extraction.injection_signals:  # SPDX-License-Identifier: MIT | 不可信内容命中注入信号时拒绝自动放行。
            blockers.append("输入包含疑似提示词注入内容，需人工复核")  # SPDX-License-Identifier: MIT | 记录安全复核阻塞项。
        if not extraction.human_review_ready:  # SPDX-License-Identifier: MIT | 未达到完成度时允许继续获得诊断但禁止进入真人评分候选。
            blockers.append("当前完成度未达到真人评分申请门槛：请至少完成垂直切片并提交可运行版本")  # SPDX-License-Identifier: MIT | 用创作者可执行的语言说明完成度与 Demo 要求。
        return (AssessmentResult.C, blockers) if blockers else (AssessmentResult.B_GATE, [])  # SPDX-License-Identifier: MIT | 无阻塞时才返回 B_GATE。

    def _actions(self, blockers: list[str], extraction: ExtractionResult) -> list[str]:  # SPDX-License-Identifier: MIT | 将问题映射为可执行补充动作。
        actions = [f"修复：{blocker}" for blocker in blockers]  # SPDX-License-Identifier: MIT | 为每个规则阻塞生成明确动作。
        actions.extend(extraction.uncertainties[:3])  # SPDX-License-Identifier: MIT | 最多追加三个优先未知项避免报告泛滥。
        return list(dict.fromkeys(actions))  # SPDX-License-Identifier: MIT | 保序去重后返回行动列表。

    def _score_detail(self, extraction: ExtractionResult, names: tuple[str, ...]) -> str:  # SPDX-License-Identifier: MIT | 生成步骤可读分数摘要。
        return "；".join(f"{name}={extraction.dimensions[name].score}" for name in names)  # SPDX-License-Identifier: MIT | 只引用结构化维度结果。

    def _step(self, steps: list[StepRecord], name: str, detail: str) -> None:  # SPDX-License-Identifier: MIT | 追加一个不可变审计步骤。
        if name not in WORKFLOW:  # SPDX-License-Identifier: MIT | 拒绝未注册的工作流步骤。
            raise ValueError(f"未知工作流步骤：{name}")  # SPDX-License-Identifier: MIT | 暴露编排配置错误。
        timestamp = datetime.now(timezone.utc).isoformat()  # SPDX-License-Identifier: MIT | 生成带时区的 UTC 时间。
        steps.append(StepRecord(name, "completed", detail, timestamp))  # SPDX-License-Identifier: MIT | 记录步骤完成事实。
