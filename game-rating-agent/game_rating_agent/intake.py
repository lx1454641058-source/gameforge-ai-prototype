"""创作者资料上传、问卷溯源和评分前确认门槛。"""  # SPDX-License-Identifier: MIT | 描述输入流水线职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import dataclass  # SPDX-License-Identifier: MIT | 定义不可变输入合同。
from hashlib import sha256  # SPDX-License-Identifier: MIT | 校验文件标识格式并冻结清单。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容输入。
import json  # SPDX-License-Identifier: MIT | 生成稳定资料清单哈希。
from .questionnaire import QUESTIONNAIRE  # SPDX-License-Identifier: MIT | 复用唯一问卷注册表校验题号和答案类型。
from .knowledge_base import GENRE_IDS, INNOVATION_AXIS_IDS, VALIDATION_METHOD_IDS  # SPDX-License-Identifier: MIT | 校验评分前使用的类型、创新位置和验证方式代码已经登记。

CRITICAL_QUESTION_IDS = tuple(question.question_id for question in QUESTIONNAIRE if question.required)  # SPDX-License-Identifier: MIT | 直接从唯一问卷合同派生全部必填确认项，避免新增必填题被服务端遗漏。

ANSWER_SOURCES = {"creator", "ai_prefill", "document_extract", "demo_extract"}  # SPDX-License-Identifier: MIT | 限定问卷答案来源。
ARTIFACT_KINDS = {"design_document", "pitch_deck", "spreadsheet", "image", "video", "demo_build", "source_snapshot", "other"}  # SPDX-License-Identifier: MIT | 限定首版上传资料类型。
QUESTION_TYPES = {question.question_id: question.answer_type for question in QUESTIONNAIRE}  # SPDX-License-Identifier: MIT | 建立登记题号到答案类型的稳定映射。
DEVELOPMENT_STAGES = {"idea", "concept", "pre_prototype", "prototype", "vertical_slice", "alpha", "beta", "release_candidate"}  # SPDX-License-Identifier: MIT | 限定评分规则可解释的制作阶段代码。
BUSINESS_MODELS = {"buyout", "iap", "ads", "subscription", "dlc", "noncommercial"}  # SPDX-License-Identifier: MIT | 限定价值交换规则支持的商业模式代码。

class SubmissionNotReadyError(ValueError):  # SPDX-License-Identifier: MIT | 表示评分前仍有待创作者确认的信息。
    def __init__(self, issues: tuple[str, ...]) -> None:  # SPDX-License-Identifier: MIT | 保存所有阻塞问题。
        self.issues = issues  # SPDX-License-Identifier: MIT | 公开结构化阻塞问题。
        super().__init__("；".join(issues))  # SPDX-License-Identifier: MIT | 生成人工可读异常消息。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 防止上传资料清单在评分中被篡改。
class ArtifactRecord:  # SPDX-License-Identifier: MIT | 描述一个方案文件或 Demo。
    artifact_id: str  # SPDX-License-Identifier: MIT | 保存资料唯一标识。
    kind: str  # SPDX-License-Identifier: MIT | 保存资料类型。
    filename: str  # SPDX-License-Identifier: MIT | 保存原始文件名。
    sha256: str  # SPDX-License-Identifier: MIT | 保存内容哈希。
    parse_status: str  # SPDX-License-Identifier: MIT | 保存解析或扫描状态。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 防止评分中修改已确认答案。
class QuestionnaireAnswer:  # SPDX-License-Identifier: MIT | 描述带来源的单个问卷答案。
    value: Any  # SPDX-License-Identifier: MIT | 保存 JSON 兼容答案值。
    source: str  # SPDX-License-Identifier: MIT | 保存创作者或 AI 等答案来源。
    confidence: float  # SPDX-License-Identifier: MIT | 保存 AI 提取可靠度而非事实概率。
    evidence_refs: tuple[str, ...]  # SPDX-License-Identifier: MIT | 指向支持答案的上传资料。
    creator_confirmed: bool  # SPDX-License-Identifier: MIT | 标记创作者是否确认该答案。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结评分用输入快照。
class PreparedSubmission:  # SPDX-License-Identifier: MIT | 描述评分 Agent 可消费的规范输入。
    normalized_project: dict[str, Any]  # SPDX-License-Identifier: MIT | 保存归一化项目表单。
    artifact_manifest_hash: str  # SPDX-License-Identifier: MIT | 保存上传资料清单哈希。
    ai_prefilled_fields: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存 AI 参与填写的字段。
    confirmed_fields: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存已由创作者确认的字段。

class SubmissionPreparer:  # SPDX-License-Identifier: MIT | 编排上传清单、问卷和确认门槛。
    def prepare(self, submission: dict[str, Any]) -> PreparedSubmission:  # SPDX-License-Identifier: MIT | 验证并归一化一次创作者提交。
        artifacts = self._parse_artifacts(submission.get("artifacts"))  # SPDX-License-Identifier: MIT | 解析上传方案和 Demo 清单。
        answers = self._parse_answers(submission.get("questionnaire"))  # SPDX-License-Identifier: MIT | 解析带来源的问卷答案。
        issues = self._readiness_issues(submission, artifacts, answers)  # SPDX-License-Identifier: MIT | 收集评分前的确认和安全问题。
        if issues:  # SPDX-License-Identifier: MIT | 阻止未确认数据进入业务评级。
            raise SubmissionNotReadyError(tuple(issues))  # SPDX-License-Identifier: MIT | 将问题交还创作者确认或补充。
        manifest = json.dumps([record.__dict__ for record in artifacts], ensure_ascii=False, sort_keys=True, separators=(",", ":"))  # SPDX-License-Identifier: MIT | 生成规范上传清单文本。
        manifest_hash = sha256(manifest.encode("utf-8")).hexdigest()  # SPDX-License-Identifier: MIT | 冻结上传资料清单哈希。
        normalized = {"project_id": str(submission["project_id"]).strip(), "version": str(submission["version"]).strip(), "title": str(submission["title"]).strip()}  # SPDX-License-Identifier: MIT | 创建去除首尾空白的基础项目表单。
        normalized.update({question_id: self._normalize_value(question_id, answer.value) for question_id, answer in answers.items() if answer.creator_confirmed and not self._empty(answer.value)})  # SPDX-License-Identifier: MIT | 只写入创作者确认且登记有效的问卷事实。
        normalized["evidence"] = [self._artifact_evidence(record) for record in artifacts if record.parse_status == "ready"]  # SPDX-License-Identifier: MIT | 将可用资料映射为证据清单。
        normalized["artifact_manifest_hash"] = manifest_hash  # SPDX-License-Identifier: MIT | 关联上传清单快照。
        ai_fields = tuple(sorted(question_id for question_id, answer in answers.items() if answer.source != "creator"))  # SPDX-License-Identifier: MIT | 记录 AI 或文档提取参与的字段。
        confirmed_fields = tuple(sorted(question_id for question_id, answer in answers.items() if answer.creator_confirmed))  # SPDX-License-Identifier: MIT | 记录创作者已确认字段。
        return PreparedSubmission(normalized, manifest_hash, ai_fields, confirmed_fields)  # SPDX-License-Identifier: MIT | 返回可评分的冻结输入。

    def _parse_artifacts(self, raw: Any) -> tuple[ArtifactRecord, ...]:  # SPDX-License-Identifier: MIT | 将 JSON 上传清单转换为不可变合同。
        records: list[ArtifactRecord] = []  # SPDX-License-Identifier: MIT | 初始化解析后的资料列表。
        if not isinstance(raw, list):  # SPDX-License-Identifier: MIT | 要求上传清单使用数组。
            return ()  # SPDX-License-Identifier: MIT | 缺失时由就绪检查给出明确问题。
        for item in raw:  # SPDX-License-Identifier: MIT | 逐项验证上传资料。
            if not isinstance(item, dict):  # SPDX-License-Identifier: MIT | 拒绝非对象资料记录。
                continue  # SPDX-License-Identifier: MIT | 忽略无效项并让总体验证发现缺失。
            kind = str(item.get("kind") or "other")  # SPDX-License-Identifier: MIT | 安全读取资料类型。
            records.append(ArtifactRecord(str(item.get("artifact_id") or ""), kind, str(item.get("filename") or ""), str(item.get("sha256") or ""), str(item.get("parse_status") or "pending")))  # SPDX-License-Identifier: MIT | 创建不可变资料记录。
        return tuple(records)  # SPDX-License-Identifier: MIT | 返回上传资料合同。

    def _parse_answers(self, raw: Any) -> dict[str, QuestionnaireAnswer]:  # SPDX-License-Identifier: MIT | 将 JSON 问卷转换为溯源答案合同。
        answers: dict[str, QuestionnaireAnswer] = {}  # SPDX-License-Identifier: MIT | 初始化问卷答案映射。
        if not isinstance(raw, dict):  # SPDX-License-Identifier: MIT | 要求问卷使用题号到答案的对象。
            return answers  # SPDX-License-Identifier: MIT | 缺失时由就绪检查给出明确问题。
        for question_id, item in raw.items():  # SPDX-License-Identifier: MIT | 逐项解析问卷答案。
            if not isinstance(item, dict):  # SPDX-License-Identifier: MIT | 拒绝没有溯源元数据的裸答案。
                continue  # SPDX-License-Identifier: MIT | 忽略不符合合同的答案。
            source = str(item.get("source") or "")  # SPDX-License-Identifier: MIT | 读取答案来源。
            confidence = item.get("confidence", 1.0 if source == "creator" else 0.0)  # SPDX-License-Identifier: MIT | 为创作者答案提供默认可靠度。
            safe_confidence = float(confidence) if isinstance(confidence, (int, float)) and not isinstance(confidence, bool) else 0.0  # SPDX-License-Identifier: MIT | 将异常置信度归零。
            refs = item.get("evidence_refs") if isinstance(item.get("evidence_refs"), list) else []  # SPDX-License-Identifier: MIT | 安全读取答案证据引用。
            answers[str(question_id)] = QuestionnaireAnswer(item.get("value"), source, max(0.0, min(1.0, safe_confidence)), tuple(str(ref) for ref in refs), item.get("creator_confirmed") is True)  # SPDX-License-Identifier: MIT | 创建带来源和确认状态的答案。
        return answers  # SPDX-License-Identifier: MIT | 返回问卷答案映射。

    def _readiness_issues(self, submission: dict[str, Any], artifacts: tuple[ArtifactRecord, ...], answers: dict[str, QuestionnaireAnswer]) -> list[str]:  # SPDX-License-Identifier: MIT | 计算评分前必须处理的问题。
        issues: list[str] = []  # SPDX-License-Identifier: MIT | 初始化阻塞问题列表。
        for key in ("project_id", "version", "title"):  # SPDX-License-Identifier: MIT | 检查提交基础标识。
            if self._empty(submission.get(key)):  # SPDX-License-Identifier: MIT | 判断基础标识是否缺失或只有空白。
                issues.append(f"缺少提交字段：{key}")  # SPDX-License-Identifier: MIT | 记录具体缺失字段。
        design_files = [record for record in artifacts if record.kind in {"design_document", "pitch_deck", "spreadsheet"}]  # SPDX-License-Identifier: MIT | 找出方案类资料。
        if not design_files:  # SPDX-License-Identifier: MIT | 要求至少上传一个方案文件。
            issues.append("至少上传一个方案文件")  # SPDX-License-Identifier: MIT | 记录方案文件缺失。
        for record in artifacts:  # SPDX-License-Identifier: MIT | 检查每个上传资料的基础安全状态。
            if record.kind not in ARTIFACT_KINDS:  # SPDX-License-Identifier: MIT | 拒绝未注册资料类型。
                issues.append(f"不支持的资料类型：{record.kind}")  # SPDX-License-Identifier: MIT | 记录未知资料类型。
            if len(record.sha256) != 64 or any(char not in "0123456789abcdefABCDEF" for char in record.sha256):  # SPDX-License-Identifier: MIT | 校验 SHA-256 十六进制格式。
                issues.append(f"资料哈希无效：{record.filename}")  # SPDX-License-Identifier: MIT | 记录无效资料哈希。
            if record.parse_status not in {"ready", "unsupported"}:  # SPDX-License-Identifier: MIT | 禁止待扫描或失败资料进入评分。
                issues.append(f"资料尚未完成安全解析：{record.filename}")  # SPDX-License-Identifier: MIT | 记录资料解析阻塞。
        artifact_ids = {record.artifact_id for record in artifacts if record.artifact_id}  # SPDX-License-Identifier: MIT | 建立本次提交允许引用的资料标识集合。
        if len(artifact_ids) != len(artifacts):  # SPDX-License-Identifier: MIT | 检测空资料标识或重复资料记录。
            issues.append("资料标识为空或重复")  # SPDX-License-Identifier: MIT | 阻止不确定的证据清单进入哈希冻结。
        for question_id, answer in answers.items():  # SPDX-License-Identifier: MIT | 校验全部答案而不只校验关键题。
            if question_id not in QUESTION_TYPES:  # SPDX-License-Identifier: MIT | 拒绝未登记题号覆盖项目内部字段。
                issues.append(f"未登记的问卷题号：{question_id}")  # SPDX-License-Identifier: MIT | 记录越界问卷字段。
                continue  # SPDX-License-Identifier: MIT | 未登记题目没有可用类型合同。
            if answer.source not in ANSWER_SOURCES:  # SPDX-License-Identifier: MIT | 限制每个非空或可选答案的来源类型。
                issues.append(f"答案来源无效：{question_id}")  # SPDX-License-Identifier: MIT | 记录无效来源。
            if not self._empty(answer.value) and not self._value_matches_type(answer.value, QUESTION_TYPES[question_id]):  # SPDX-License-Identifier: MIT | 校验实际答案与登记控件类型一致。
                issues.append(f"答案类型无效：{question_id} 应为 {QUESTION_TYPES[question_id]}")  # SPDX-License-Identifier: MIT | 返回可操作的类型错误。
            invalid_refs = sorted(set(answer.evidence_refs) - artifact_ids)  # SPDX-License-Identifier: MIT | 找出不存在或不属于本次提交的证据引用。
            if invalid_refs:  # SPDX-License-Identifier: MIT | 任何越界证据都会破坏答案溯源。
                issues.append(f"答案引用了无效资料：{question_id} -> {','.join(invalid_refs)}")  # SPDX-License-Identifier: MIT | 记录具体越界资料标识。
            if answer.source != "creator" and not self._empty(answer.value) and not answer.evidence_refs:  # SPDX-License-Identifier: MIT | AI 或文档候选必须给出资料依据。
                issues.append(f"非创作者答案缺少证据引用：{question_id}")  # SPDX-License-Identifier: MIT | 阻止无依据候选影响结论。
        for question_id in CRITICAL_QUESTION_IDS:  # SPDX-License-Identifier: MIT | 检查每个关键问卷答案。
            answer = answers.get(question_id)  # SPDX-License-Identifier: MIT | 读取关键答案。
            if answer is None or self._empty(answer.value):  # SPDX-License-Identifier: MIT | 判断关键答案是否缺失或仅有空白。
                issues.append(f"缺少关键问卷答案：{question_id}")  # SPDX-License-Identifier: MIT | 记录缺失答案。
                continue  # SPDX-License-Identifier: MIT | 跳过该答案的后续溯源检查。
            if not answer.creator_confirmed:  # SPDX-License-Identifier: MIT | 所有关键答案最终必须由创作者确认。
                issues.append(f"关键答案尚未由创作者确认：{question_id}")  # SPDX-License-Identifier: MIT | 记录未确认的 AI 代填答案。
        stage = answers.get("development_stage")  # SPDX-License-Identifier: MIT | 读取已确认制作阶段供枚举校验。
        if stage is not None and isinstance(stage.value, str) and stage.value.strip().lower() not in DEVELOPMENT_STAGES:  # SPDX-License-Identifier: MIT | 阻止未知阶段被错误套用 Demo 门槛。
            issues.append(f"制作阶段代码无效：{stage.value}")  # SPDX-License-Identifier: MIT | 要求使用规则书登记阶段代码。
        model = answers.get("business_model")  # SPDX-License-Identifier: MIT | 读取商业模式供价值规则校验。
        if model is not None and isinstance(model.value, str) and model.value.strip().lower() not in BUSINESS_MODELS:  # SPDX-License-Identifier: MIT | 阻止未知商业模式静默降分。
            issues.append(f"商业模式代码无效：{model.value}")  # SPDX-License-Identifier: MIT | 要求使用规则书登记模式代码。
        genre_ids = answers.get("genre_ids")  # SPDX-License-Identifier: MIT | 读取创作者确认的类型代码供知识库校验。
        if genre_ids is not None and isinstance(genre_ids.value, list):  # SPDX-License-Identifier: MIT | 只在类型值已通过列表类型校验时继续检查。
            unknown_genres = sorted({item.strip().lower() for item in genre_ids.value if isinstance(item, str) and item.strip()} - GENRE_IDS)  # SPDX-License-Identifier: MIT | 找出知识库中不存在的类型代码。
            if unknown_genres:  # SPDX-License-Identifier: MIT | 未登记类型不能被静默当作任意类型处理。
                issues.append(f"游戏类型代码无效：{','.join(unknown_genres)}")  # SPDX-License-Identifier: MIT | 返回可修正的具体类型代码。
        innovation_axes = answers.get("innovation_axes")  # SPDX-License-Identifier: MIT | 读取创新位置多选答案供服务端白名单校验。
        if innovation_axes is not None and isinstance(innovation_axes.value, list):  # SPDX-License-Identifier: MIT | 只在创新位置为列表时继续校验。
            unknown_axes = sorted({item.strip().lower() for item in innovation_axes.value if isinstance(item, str) and item.strip()} - INNOVATION_AXIS_IDS)  # SPDX-License-Identifier: MIT | 找出前端合同之外的创新位置代码。
            if unknown_axes:  # SPDX-License-Identifier: MIT | 未登记位置不能影响类型知识库评分。
                issues.append(f"创新位置代码无效：{','.join(unknown_axes)}")  # SPDX-License-Identifier: MIT | 返回具体未知代码供前端修正。
        validation_methods = answers.get("validation_methods")  # SPDX-License-Identifier: MIT | 读取验证方式多选答案供服务端白名单校验。
        if validation_methods is not None and isinstance(validation_methods.value, list):  # SPDX-License-Identifier: MIT | 只在验证方式为列表时继续校验。
            unknown_methods = sorted({item.strip().lower() for item in validation_methods.value if isinstance(item, str) and item.strip()} - VALIDATION_METHOD_IDS)  # SPDX-License-Identifier: MIT | 找出不受支持的验证方式代码。
            if unknown_methods:  # SPDX-License-Identifier: MIT | 不允许前端自造代码获取差异证据分。
                issues.append(f"验证方式代码无效：{','.join(unknown_methods)}")  # SPDX-License-Identifier: MIT | 返回具体未知代码供前端修正。
        return issues  # SPDX-License-Identifier: MIT | 返回完整评分前阻塞列表。

    def _empty(self, value: Any) -> bool:  # SPDX-License-Identifier: MIT | 统一识别缺失答案和纯空白文本。
        return not value.strip() if isinstance(value, str) else value in (None, [], {})  # SPDX-License-Identifier: MIT | 保留合法数字零和布尔假但排除空结构。

    def _value_matches_type(self, value: Any, answer_type: str) -> bool:  # SPDX-License-Identifier: MIT | 按问卷注册表验证 JSON 值类型。
        checks = {"text": isinstance(value, str), "list": isinstance(value, list), "object": isinstance(value, dict), "number": isinstance(value, (int, float)) and not isinstance(value, bool), "boolean": isinstance(value, bool)}  # SPDX-License-Identifier: MIT | 定义问卷类型到 Python JSON 类型的严格映射。
        if not checks.get(answer_type, False):  # SPDX-License-Identifier: MIT | 先拒绝顶层类型不匹配或未知类型。
            return False  # SPDX-License-Identifier: MIT | 返回类型失败。
        if answer_type == "list":  # SPDX-License-Identifier: MIT | 列表题还需要检查元素质量。
            return all(isinstance(item, str) and bool(item.strip()) for item in value)  # SPDX-License-Identifier: MIT | 只接受非空字符串列表避免空行为或平台计数。
        return True  # SPDX-License-Identifier: MIT | 其他登记类型通过顶层类型检查即可。

    def _normalize_value(self, question_id: str, value: Any) -> Any:  # SPDX-License-Identifier: MIT | 将规则依赖的代码值归一化为稳定表示。
        if question_id in {"development_stage", "business_model"} and isinstance(value, str):  # SPDX-License-Identifier: MIT | 归一化阶段和商业模式枚举。
            return value.strip().lower()  # SPDX-License-Identifier: MIT | 避免大小写和首尾空白造成规则漂移。
        if question_id in {"platforms", "genre_ids", "gameplay_features", "innovation_axes", "innovation_features", "validation_methods"} and isinstance(value, list):  # SPDX-License-Identifier: MIT | 归一化用于规则比对的代码列表。
            return [item.strip().lower() for item in value]  # SPDX-License-Identifier: MIT | 生成稳定上架路线键。
        return value.strip() if isinstance(value, str) else value  # SPDX-License-Identifier: MIT | 普通文本只清理首尾空白并保留结构值。

    def _artifact_evidence(self, record: ArtifactRecord) -> dict[str, str]:  # SPDX-License-Identifier: MIT | 将上传资料映射为评分证据引用。
        evidence_type = "demo" if record.kind == "demo_build" else "document"  # SPDX-License-Identifier: MIT | 区分可运行 Demo 和文档证据。
        return {"type": evidence_type, "ref": f"sha256:{record.sha256}", "artifact_id": record.artifact_id, "summary": record.filename}  # SPDX-License-Identifier: MIT | 返回不包含文件正文的安全证据索引。
