"""组合上传、问卷、持久化、评分诊断和能力匹配的应用服务。"""  # SPDX-License-Identifier: MIT | 描述应用服务职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from pathlib import Path  # SPDX-License-Identifier: MIT | 配置本地隔离存储和数据库路径。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容 API 数据。
import base64  # SPDX-License-Identifier: MIT | 解码 JSON API 中的文件内容。
from dataclasses import asdict  # SPDX-License-Identifier: MIT | 将隔离资料记录保存为 JSON 对象。
from .artifacts import ArtifactStore, ArtifactValidationError, StoredArtifact  # SPDX-License-Identifier: MIT | 接收并验证方案和 Demo 文件。
from .capabilities import CapabilityFulfillmentFeedback, TalentCapabilityAgentGateway  # SPDX-License-Identifier: MIT | 处理能力匹配和履约回写。
from .diagnosis import DiagnosticPlanner  # SPDX-License-Identifier: MIT | 注入人才能力 Agent 网关。
from .intake import SubmissionNotReadyError  # SPDX-License-Identifier: MIT | 区分创作者可修复输入问题。
from .knowledge_base import GenreKnowledgeBase  # SPDX-License-Identifier: MIT | 接入只读游戏类型评分知识库。
from .pipeline import CreatorAssessmentPipeline  # SPDX-License-Identifier: MIT | 执行评分和完整诊断。
from .questionnaire import ConservativeQuestionnairePrefiller, OpenAIQuestionnairePrefiller, QuestionnairePrefiller, questionnaire_contract  # SPDX-License-Identifier: MIT | 生成问卷和 AI 代填草稿。
from .repository import AgentRepository  # SPDX-License-Identifier: MIT | 保存提交、运行和审计。

class GameRatingApplicationService:  # SPDX-License-Identifier: MIT | 提供 HTTP 和 CLI 共用的真实应用用例。
    def __init__(self, data_root: Path, capability_gateway: TalentCapabilityAgentGateway | None = None, prefiller: QuestionnairePrefiller | None = None) -> None:  # SPDX-License-Identifier: MIT | 配置本地数据目录和可选跨 Agent 连接。
        self.data_root = data_root.resolve()  # SPDX-License-Identifier: MIT | 固定应用数据根目录。
        self.data_root.mkdir(parents=True, exist_ok=True)  # SPDX-License-Identifier: MIT | 创建应用数据目录。
        self.artifacts = ArtifactStore(self.data_root / "artifacts")  # SPDX-License-Identifier: MIT | 将上传存储在独立子目录。
        self.repository = AgentRepository(self.data_root / "game_rating_agent.sqlite3")  # SPDX-License-Identifier: MIT | 初始化持久化仓库。
        self.capability_gateway = capability_gateway  # SPDX-License-Identifier: MIT | 保存可选人才能力 Agent 网关。
        self.prefiller = prefiller or ConservativeQuestionnairePrefiller()  # SPDX-License-Identifier: MIT | 默认使用无 API Key 的保守代填器。
        self.knowledge_base = GenreKnowledgeBase()  # SPDX-License-Identifier: MIT | 初始化与评分内核同版本的类型知识库查询服务。
        self.pipeline = CreatorAssessmentPipeline(planner=DiagnosticPlanner(capability_gateway=capability_gateway))  # SPDX-License-Identifier: MIT | 连接评分诊断与人才能力 Agent。
        self.repository.recover_interrupted_runs()  # SPDX-License-Identifier: MIT | 启动时恢复被中断的运行供重试。

    @classmethod  # SPDX-License-Identifier: MIT | 提供按环境选择 AI 代填的便捷构造器。
    def from_environment(cls, data_root: Path, capability_gateway: TalentCapabilityAgentGateway | None = None) -> GameRatingApplicationService:  # SPDX-License-Identifier: MIT | 读取模型环境配置但不要求必须存在。
        prefiller: QuestionnairePrefiller = OpenAIQuestionnairePrefiller() if __import__("os").getenv("OPENAI_API_KEY") else ConservativeQuestionnairePrefiller()  # SPDX-License-Identifier: MIT | 有密钥时启用 Structured Outputs，否则安全降级。
        return cls(data_root, capability_gateway, prefiller)  # SPDX-License-Identifier: MIT | 返回配置完成的应用服务。

    def get_questionnaire(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 返回客户端可渲染问卷合同。
        return questionnaire_contract()  # SPDX-License-Identifier: MIT | 返回版本化问卷定义。

    def get_knowledge_base(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 返回前端和管理工具可读取的类型评分规则。
        return self.knowledge_base.contract()  # SPDX-License-Identifier: MIT | 返回不含项目数据的版本化只读知识库合同。

    def ingest_artifact_base64(self, payload: dict[str, Any]) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 从 JSON API 接收一个 Base64 资料文件。
        encoded = payload.get("content_base64")  # SPDX-License-Identifier: MIT | 读取 Base64 文件内容。
        if not isinstance(encoded, str):  # SPDX-License-Identifier: MIT | 要求文件内容使用字符串编码。
            raise ArtifactValidationError("缺少 content_base64")  # SPDX-License-Identifier: MIT | 返回明确上传错误。
        try:  # SPDX-License-Identifier: MIT | 严格解码 Base64 并拒绝非法字符。
            content = base64.b64decode(encoded, validate=True)  # SPDX-License-Identifier: MIT | 将受限请求内容解码为字节。
        except ValueError as error:  # SPDX-License-Identifier: MIT | 处理无效 Base64 输入。
            raise ArtifactValidationError("content_base64 无效") from error  # SPDX-License-Identifier: MIT | 返回安全用户错误。
        artifact = self.artifacts.ingest(str(payload.get("project_id") or ""), str(payload.get("filename") or ""), str(payload.get("kind") or "other"), content)  # SPDX-License-Identifier: MIT | 验证签名、结构并隔离保存文件。
        self.repository.save_artifact(asdict(artifact))  # SPDX-License-Identifier: MIT | 持久化资料元数据和有限提取文本供问卷代填。
        response = artifact.to_dict()  # SPDX-License-Identifier: MIT | 创建不暴露内部路径的资料元数据响应。
        response["submission_artifact"] = artifact.manifest_record()  # SPDX-License-Identifier: MIT | 同时返回可直接进入评分提交的资料清单记录。
        return response  # SPDX-License-Identifier: MIT | 返回上传结果和提交清单记录。

    def prefill_by_artifact_ids(self, artifact_ids: tuple[str, ...], creator_values: dict[str, Any] | None = None) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 从持久化资料生成问卷草稿。
        artifacts = self.repository.get_artifacts(artifact_ids)  # SPDX-License-Identifier: MIT | 只加载明确引用的隔离资料。
        project_ids = {str(item.get("project_id")) for item in artifacts}  # SPDX-License-Identifier: MIT | 检查资料是否属于同一项目。
        if len(project_ids) > 1:  # SPDX-License-Identifier: MIT | 禁止跨项目拼接问卷上下文。
            raise ValueError("问卷代填资料必须属于同一项目")  # SPDX-License-Identifier: MIT | 阻止跨项目数据越权。
        return self.prefill_questionnaire(artifacts, creator_values)  # SPDX-License-Identifier: MIT | 调用版本化保守或 AI 代填器。

    def prefill_questionnaire(self, artifacts: tuple[StoredArtifact | dict[str, Any], ...], creator_values: dict[str, Any] | None = None) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 根据已授权资料生成待确认问卷草稿。
        normalized = tuple(self._artifact_payload(item) for item in artifacts)  # SPDX-License-Identifier: MIT | 统一资料对象和 API 字典。
        answers = self.prefiller.prefill(normalized, creator_values)  # SPDX-License-Identifier: MIT | 调用保守或 Structured Outputs 代填器。
        return {"questionnaire_version": questionnaire_contract()["version"], "prefiller_version": self.prefiller.version, "answers": answers}  # SPDX-License-Identifier: MIT | 返回版本化代填结果。

    def submit(self, payload: dict[str, Any]) -> str:  # SPDX-License-Identifier: MIT | 保存一次创作者确认后的提交版本。
        frozen_payload = dict(payload)  # SPDX-License-Identifier: MIT | 复制调用方数据避免原对象被意外修改。
        raw_artifact_ids = frozen_payload.get("artifact_ids")  # SPDX-License-Identifier: MIT | 读取客户端上传阶段返回的资料标识。
        if not isinstance(raw_artifact_ids, list):  # SPDX-License-Identifier: MIT | HTTP 服务只接受上传接口签发的资料标识。
            raise ValueError("提交必须提供 artifact_ids，不能自行声明 artifacts 清单")  # SPDX-License-Identifier: MIT | 阻止伪造哈希、类型和解析状态绕过可信上传链。
        artifact_ids = tuple(str(item) for item in raw_artifact_ids)  # SPDX-License-Identifier: MIT | 规范资料标识列表。
        records = self.repository.get_artifacts(artifact_ids)  # SPDX-License-Identifier: MIT | 从服务端可信元数据重建提交清单。
        project_id = str(frozen_payload.get("project_id") or "")  # SPDX-License-Identifier: MIT | 读取提交所属项目。
        if any(str(item.get("project_id")) != project_id for item in records):  # SPDX-License-Identifier: MIT | 阻止引用其他项目的上传资料。
            raise ValueError("提交资料必须属于当前项目")  # SPDX-License-Identifier: MIT | 返回明确跨项目引用错误。
        frozen_payload["artifacts"] = [self._manifest_from_record(item) for item in records]  # SPDX-License-Identifier: MIT | 仅使用服务端校验后的哈希和解析状态。
        frozen_payload.pop("artifact_ids", None)  # SPDX-License-Identifier: MIT | 移除仅用于组装的临时字段。
        return self.repository.create_submission(frozen_payload)  # SPDX-License-Identifier: MIT | 返回不可覆盖提交标识。

    def create_and_execute_run(self, submission_id: str) -> str:  # SPDX-License-Identifier: MIT | 创建运行并同步执行用于 MVP API。
        run_id = self.repository.create_run(submission_id)  # SPDX-License-Identifier: MIT | 先保存 queued 状态确保失败可恢复。
        self.execute_run(run_id)  # SPDX-License-Identifier: MIT | 在当前进程执行完整诊断。
        return run_id  # SPDX-License-Identifier: MIT | 返回可查询运行标识。

    def execute_run(self, run_id: str) -> None:  # SPDX-License-Identifier: MIT | 执行或重试一个未完成运行。
        claimed = self.repository.claim_run(run_id)  # SPDX-License-Identifier: MIT | 原子领取任务并增加尝试次数。
        submission = self.repository.get_submission(claimed["submission_id"])  # SPDX-License-Identifier: MIT | 读取冻结提交快照。
        if submission is None:  # SPDX-License-Identifier: MIT | 防御异常外键或数据库损坏。
            self.repository.fail_run(run_id, "submission_missing", "运行引用的提交不存在", False)  # SPDX-License-Identifier: MIT | 保存不可重试失败且不生成报告。
            return  # SPDX-License-Identifier: MIT | 结束异常运行。
        try:  # SPDX-License-Identifier: MIT | 区分创作者行动、系统失败和成功报告。
            report = self.pipeline.run(submission).to_dict()  # SPDX-License-Identifier: MIT | 执行问卷确认、评分、诊断和能力匹配。
        except SubmissionNotReadyError as error:  # SPDX-License-Identifier: MIT | 处理待补充或确认问卷。
            self.repository.require_creator_action(run_id, error.issues)  # SPDX-License-Identifier: MIT | 保存可修复输入问题。
            return  # SPDX-License-Identifier: MIT | 不生成假评分报告。
        except Exception as error:  # SPDX-License-Identifier: MIT | 捕获未预料执行故障并允许安全重试。
            self.repository.fail_run(run_id, "agent_execution_failed", str(error), True)  # SPDX-License-Identifier: MIT | 保存系统失败原因和重试属性。
            return  # SPDX-License-Identifier: MIT | 不生成部分或伪造报告。
        self.repository.complete_run(run_id, report)  # SPDX-License-Identifier: MIT | 原子保存完整报告和完成状态。

    def get_run(self, run_id: str) -> dict[str, Any] | None:  # SPDX-License-Identifier: MIT | 返回运行进度、报告或错误。
        return self.repository.get_run(run_id)  # SPDX-License-Identifier: MIT | 委托持久化仓库读取。

    def retry_run(self, run_id: str) -> None:  # SPDX-License-Identifier: MIT | 只重试显式标记为可重试的系统失败运行。
        current = self.repository.get_run(run_id)  # SPDX-License-Identifier: MIT | 读取当前状态防止覆盖完成报告。
        if current is None:  # SPDX-License-Identifier: MIT | 拒绝未知运行标识。
            raise KeyError(f"运行不存在：{run_id}")  # SPDX-License-Identifier: MIT | 返回领域错误。
        if current["status"] != "failed" or not isinstance(current.get("error"), dict) or current["error"].get("retryable") is not True:  # SPDX-License-Identifier: MIT | 拒绝完成、运行中、排队、待补充和不可重试失败。
            raise ValueError("只有 retryable=true 的 failed 运行可以重试；资料或问卷变更请创建新提交")  # SPDX-License-Identifier: MIT | 保持冻结提交和运行历史语义一致。
        self.execute_run(run_id)  # SPDX-License-Identifier: MIT | 重新执行冻结提交。

    def record_fulfillment(self, payload: dict[str, Any]) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 将真实项目履约结果回写人才能力 Agent。
        if self.capability_gateway is None:  # SPDX-License-Identifier: MIT | 未连接能力 Agent 时不伪造成功回执。
            raise RuntimeError("未配置人才能力 Agent 网关")  # SPDX-License-Identifier: MIT | 返回明确集成错误。
        if not isinstance(payload.get("skill_ids"), list) or not isinstance(payload.get("evidence_ids"), list):  # SPDX-License-Identifier: MIT | 防止字符串被逐字符解释为标识列表。
            raise ValueError("skill_ids 和 evidence_ids 必须是数组")  # SPDX-License-Identifier: MIT | 返回明确履约合同错误。
        if not isinstance(payload.get("accepted"), bool) or not isinstance(payload.get("integration_verified"), bool):  # SPDX-License-Identifier: MIT | 验收结论必须使用真实 JSON 布尔值。
            raise ValueError("accepted 和 integration_verified 必须是 boolean")  # SPDX-License-Identifier: MIT | 阻止字符串真假值被静默改写。
        rework_count = payload.get("rework_count", 0)  # SPDX-License-Identifier: MIT | 读取返工次数供范围校验。
        if not isinstance(rework_count, int) or isinstance(rework_count, bool) or rework_count < 0:  # SPDX-License-Identifier: MIT | 返工次数必须是非负整数。
            raise ValueError("rework_count 必须是非负整数")  # SPDX-License-Identifier: MIT | 阻止负数或布尔值污染履约统计。
        feedback = CapabilityFulfillmentFeedback(str(payload.get("feedback_id") or ""), str(payload.get("project_id") or ""), str(payload.get("project_version") or ""), str(payload.get("talent_id") or ""), tuple(str(item) for item in payload["skill_ids"]), str(payload.get("milestone_id") or ""), payload["accepted"], payload["integration_verified"], rework_count, tuple(str(item) for item in payload["evidence_ids"]), str(payload.get("reviewer_id") or ""))  # SPDX-License-Identifier: MIT | 创建通过类型和范围校验的履约反馈合同。
        return self.capability_gateway.record_fulfillment(feedback).__dict__  # SPDX-License-Identifier: MIT | 返回幂等能力 Agent 回执。

    def _artifact_payload(self, item: StoredArtifact | dict[str, Any]) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 统一资料对象为代填器输入。
        if isinstance(item, StoredArtifact):  # SPDX-License-Identifier: MIT | 处理本地隔离资料对象。
            return {"artifact_id": item.artifact_id, "original_filename": item.original_filename, "sha256": item.sha256, "parse_status": item.parse_status, "extracted_text": item.extracted_text}  # SPDX-License-Identifier: MIT | 只暴露问卷代填需要的授权字段。
        return dict(item)  # SPDX-License-Identifier: MIT | 复制调用方字典防止意外修改。

    def _manifest_from_record(self, item: dict[str, Any]) -> dict[str, str]:  # SPDX-License-Identifier: MIT | 将持久化上传记录转换为评分资料清单。
        return {"artifact_id": str(item.get("artifact_id") or ""), "kind": str(item.get("kind") or "other"), "filename": str(item.get("original_filename") or ""), "sha256": str(item.get("sha256") or ""), "parse_status": str(item.get("parse_status") or "pending")}  # SPDX-License-Identifier: MIT | 只返回评分输入合同允许的可信字段。
