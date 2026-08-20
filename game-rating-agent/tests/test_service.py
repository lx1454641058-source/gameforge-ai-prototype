"""文件安全、问卷代填、持久化与 HTTP API 回归测试。"""  # SPDX-License-Identifier: MIT | 描述服务层测试职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from pathlib import Path  # SPDX-License-Identifier: MIT | 创建隔离临时数据目录。
from tempfile import TemporaryDirectory  # SPDX-License-Identifier: MIT | 自动清理测试数据库和上传文件。
from urllib.error import HTTPError  # SPDX-License-Identifier: MIT | 验证未授权 HTTP 响应。
from urllib.request import Request, urlopen  # SPDX-License-Identifier: MIT | 使用标准库测试真实 HTTP 服务。
from zipfile import ZipFile  # SPDX-License-Identifier: MIT | 创建受控 DOCX 和 Demo ZIP 测试夹具。
import base64  # SPDX-License-Identifier: MIT | 构造 JSON API 文件内容。
import copy  # SPDX-License-Identifier: MIT | 创建独立提交测试数据。
import io  # SPDX-License-Identifier: MIT | 在内存生成 ZIP 测试夹具。
import json  # SPDX-License-Identifier: MIT | 构造和解析 API 请求响应。
import threading  # SPDX-License-Identifier: MIT | 在测试线程启动真实 HTTP 服务。
import unittest  # SPDX-License-Identifier: MIT | 使用标准库测试框架。
from game_rating_agent.api import create_server  # SPDX-License-Identifier: MIT | 测试真实 API 路由和鉴权。
from game_rating_agent.artifacts import ArtifactStore, ArtifactValidationError  # SPDX-License-Identifier: MIT | 测试安全文件接收。
from game_rating_agent.questionnaire import ConservativeQuestionnairePrefiller, MAX_PREFILL_ARTIFACT_TEXT, MAX_PREFILL_TOTAL_TEXT, OpenAIQuestionnairePrefiller  # SPDX-License-Identifier: MIT | 测试保守代填、外部代填文本边界和不猜测的问卷草稿。
from game_rating_agent.service import GameRatingApplicationService  # SPDX-License-Identifier: MIT | 测试持久化应用服务。
import test_agent  # SPDX-License-Identifier: MIT | 通过模块访问夹具并避免测试类被重复发现。

def make_docx_bytes(text: str) -> bytes:  # SPDX-License-Identifier: MIT | 创建只含主文档 XML 的最小 DOCX 夹具。
    buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存中生成测试文件。
    with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建受控 ZIP 容器。
        xml = f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>'  # SPDX-License-Identifier: MIT | 生成简单 Word 主文档 XML。
        archive.writestr("word/document.xml", xml.encode("utf-8"))  # SPDX-License-Identifier: MIT | 写入 DOCX 必需主文档部件。
    return buffer.getvalue()  # SPDX-License-Identifier: MIT | 返回内存 DOCX 字节。

def make_demo_zip_bytes() -> bytes:  # SPDX-License-Identifier: MIT | 创建受控 Demo ZIP 测试夹具。
    buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存中生成 Demo 压缩包。
    with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建无路径穿越的 ZIP 容器。
        archive.writestr("build/README.txt", b"test demo build")  # SPDX-License-Identifier: MIT | 写入一个静态构建说明条目。
    return buffer.getvalue()  # SPDX-License-Identifier: MIT | 返回 Demo ZIP 字节。

class ArtifactStoreTests(unittest.TestCase):  # SPDX-License-Identifier: MIT | 验证上传类型、签名、隔离和压缩安全。
    def test_docx_is_renamed_and_text_is_extracted(self) -> None:  # SPDX-License-Identifier: MIT | 验证安全存储名和有限 DOCX 提取。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            store = ArtifactStore(Path(directory))  # SPDX-License-Identifier: MIT | 初始化测试资料存储。
            artifact = store.ingest("project-1", "../方案.docx", "design_document", make_docx_bytes("核心循环是探索、收集与建造。"))  # SPDX-License-Identifier: MIT | 上传带路径片段的受控 DOCX。
            self.assertNotEqual(artifact.original_filename, artifact.stored_filename)  # SPDX-License-Identifier: MIT | 确认存储名不使用用户文件名。
            self.assertIn("核心循环", artifact.extracted_text)  # SPDX-License-Identifier: MIT | 确认只提取主文档文字。
            self.assertTrue((Path(directory) / "project-1" / artifact.stored_filename).exists())  # SPDX-License-Identifier: MIT | 确认文件保存在项目隔离目录。

    def test_unicode_project_id_keeps_its_business_identity(self) -> None:  # SPDX-License-Identifier: MIT | 验证中文项目编号不会在目录清洗时发生碰撞或导致提交归属不一致。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            store = ArtifactStore(Path(directory))  # SPDX-License-Identifier: MIT | 初始化测试资料存储。
            artifact = store.ingest("星尘突围", "方案.txt", "design_document", "核心玩法说明".encode("utf-8"))  # SPDX-License-Identifier: MIT | 上传使用中文项目编号的受控设计资料。
            self.assertEqual(artifact.project_id, "星尘突围")  # SPDX-License-Identifier: MIT | 确认返回给服务层的项目归属保持原中文编号。
            self.assertTrue(any(path.name == artifact.stored_filename for path in Path(directory).rglob(artifact.stored_filename)))  # SPDX-License-Identifier: MIT | 确认资料仍写入隔离根目录下的安全哈希目录。

    def test_signature_mismatch_is_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证伪装 PDF 被拒绝。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            store = ArtifactStore(Path(directory))  # SPDX-License-Identifier: MIT | 初始化测试资料存储。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期签名校验失败。
                store.ingest("project-1", "fake.pdf", "design_document", b"not-a-pdf")  # SPDX-License-Identifier: MIT | 提交扩展名与内容不符文件。

    def test_zip_path_traversal_is_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证 Demo ZIP 路径逃逸被拒绝。
        buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存创建恶意 ZIP 夹具。
        with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建测试 ZIP 容器。
            archive.writestr("../escape.exe", b"blocked")  # SPDX-License-Identifier: MIT | 写入父目录逃逸条目。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期 Zip Slip 检查失败。
                ArtifactStore(Path(directory)).ingest("project-1", "demo.zip", "demo_build", buffer.getvalue())  # SPDX-License-Identifier: MIT | 提交恶意 Demo ZIP。

    def test_zip_windows_absolute_path_is_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证 Demo ZIP 中的 Windows 盘符绝对路径同样不能越过安全检查。
        buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存创建带 Windows 绝对路径的 ZIP 夹具。
        with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建测试 ZIP 容器。
            archive.writestr("C:/Windows/escape.exe", b"blocked")  # SPDX-License-Identifier: MIT | 写入 Windows 盘符形式的绝对路径条目。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期绝对路径条目被安全检查拒绝。
                ArtifactStore(Path(directory)).ingest("project-1", "demo.zip", "demo_build", buffer.getvalue())  # SPDX-License-Identifier: MIT | 提交含 Windows 绝对路径的恶意 Demo ZIP。

    def test_plain_text_cannot_claim_demo_kind(self) -> None:  # SPDX-License-Identifier: MIT | 验证普通文本不能冒充可玩 Demo 证据。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期业务类型与格式校验失败。
                ArtifactStore(Path(directory)).ingest("project-1", "demo.txt", "demo_build", b"not a playable build")  # SPDX-License-Identifier: MIT | 提交伪装为 Demo 的文本文件。

    def test_docx_entity_declaration_is_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证 DOCX XML 实体声明不能进入解析器。
        buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存创建恶意 DOCX 容器。
        with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建包含主文档 XML 的 ZIP。
            archive.writestr("word/document.xml", b'<!DOCTYPE x [<!ENTITY a "boom">]><x>&a;</x>')  # SPDX-License-Identifier: MIT | 写入带实体声明的恶意 XML。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期 XML 安全校验失败。
                ArtifactStore(Path(directory)).ingest("project-1", "entity.docx", "design_document", buffer.getvalue())  # SPDX-License-Identifier: MIT | 提交恶意 DOCX 资料。

    def test_malformed_docx_xml_is_a_validation_error(self) -> None:  # SPDX-License-Identifier: MIT | 验证损坏 DOCX 不会变成服务端未知错误。
        buffer = io.BytesIO()  # SPDX-License-Identifier: MIT | 在内存创建损坏 DOCX 容器。
        with ZipFile(buffer, "w") as archive:  # SPDX-License-Identifier: MIT | 创建包含主文档路径的 ZIP。
            archive.writestr("word/document.xml", b"<w:document>")  # SPDX-License-Identifier: MIT | 写入不完整 XML。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理隔离目录。
            with self.assertRaises(ArtifactValidationError):  # SPDX-License-Identifier: MIT | 预期损坏 XML 被归类为上传错误。
                ArtifactStore(Path(directory)).ingest("project-1", "broken.docx", "design_document", buffer.getvalue())  # SPDX-License-Identifier: MIT | 提交损坏 DOCX 资料。

class QuestionnaireTests(unittest.TestCase):  # SPDX-License-Identifier: MIT | 验证保守代填不制造项目事实。
    def test_prefill_keeps_unknown_fields_unconfirmed(self) -> None:  # SPDX-License-Identifier: MIT | 验证文档不足时保留未知。
        artifacts = ({"artifact_id": "doc-1", "extracted_text": "这是一份关于探索与建造的游戏方案摘要。"},)  # SPDX-License-Identifier: MIT | 创建有限文档证据。
        answers = ConservativeQuestionnairePrefiller().prefill(artifacts, {"platforms": ["steam"]})  # SPDX-License-Identifier: MIT | 使用创作者平台事实生成草稿。
        self.assertTrue(answers["platforms"]["creator_confirmed"])  # SPDX-License-Identifier: MIT | 确认创作者事实保持已确认。
        self.assertFalse(answers["core_loop"]["creator_confirmed"])  # SPDX-License-Identifier: MIT | 确认未知核心循环不能自动确认。
        self.assertIsNone(answers["core_loop"]["value"])  # SPDX-License-Identifier: MIT | 确认代填器没有凭空猜测行为链。

    def test_external_prefill_bounds_total_artifact_text(self) -> None:  # SPDX-License-Identifier: MIT | 验证多份超长资料不会无限放大外部模型请求文本。
        long_text = "游戏规则" * 200000  # SPDX-License-Identifier: MIT | 构造远超单份和总量预算的授权资料正文。
        payload = OpenAIQuestionnairePrefiller(api_key="test-key")._bounded_artifact_payload(({"artifact_id": "doc-1", "extracted_text": long_text}, {"artifact_id": "doc-2", "extracted_text": long_text}, {"artifact_id": "doc-3", "extracted_text": long_text}, {"artifact_id": "doc-4", "extracted_text": long_text}, {"artifact_id": "doc-5", "extracted_text": long_text}))  # SPDX-License-Identifier: MIT | 直接构造外部代填器将发送的受限资料载荷而不发出网络请求。
        self.assertEqual(sum(len(item["text"]) for item in payload), MAX_PREFILL_TOTAL_TEXT)  # SPDX-License-Identifier: MIT | 确认全部资料正文不会超过单次外部调用总文本预算。
        self.assertTrue(all(len(item["text"]) <= MAX_PREFILL_ARTIFACT_TEXT for item in payload))  # SPDX-License-Identifier: MIT | 确认每份资料正文同样受独立上限约束。

class ApplicationServiceTests(unittest.TestCase):  # SPDX-License-Identifier: MIT | 验证持久化运行和失败恢复语义。
    def _submission(self) -> dict:  # SPDX-License-Identifier: MIT | 复用端到端有效创作者提交。
        fixture = test_agent.CreatorAssessmentPipelineTests()  # SPDX-License-Identifier: MIT | 创建未依赖 setUp 的夹具对象。
        return fixture._submission()  # SPDX-License-Identifier: MIT | 返回完整有效提交。

    def _trusted_submission(self, service: GameRatingApplicationService, submission: dict | None = None) -> dict:  # SPDX-License-Identifier: MIT | 通过正式上传链构造可执行服务提交。
        payload = copy.deepcopy(submission or self._submission())  # SPDX-License-Identifier: MIT | 创建不修改调用方的提交副本。
        document = service.ingest_artifact_base64({"project_id": payload["project_id"], "filename": "方案.txt", "kind": "design_document", "content_base64": base64.b64encode("核心循环、团队、预算与范围。".encode("utf-8")).decode("ascii")})  # SPDX-License-Identifier: MIT | 通过正式接口接收方案文本。
        demo = service.ingest_artifact_base64({"project_id": payload["project_id"], "filename": "demo.zip", "kind": "demo_build", "content_base64": base64.b64encode(make_demo_zip_bytes()).decode("ascii")})  # SPDX-License-Identifier: MIT | 通过正式接口接收受控 Demo ZIP。
        reference_map = {"doc-1": document["artifact_id"], "demo-1": demo["artifact_id"]}  # SPDX-License-Identifier: MIT | 建立旧夹具证据到真实上传标识的映射。
        for answer in payload["questionnaire"].values():  # SPDX-License-Identifier: MIT | 更新全部问卷证据引用。
            answer["evidence_refs"] = [reference_map.get(reference, reference) for reference in answer.get("evidence_refs", [])]  # SPDX-License-Identifier: MIT | 保持空引用并替换本地占位标识。
        payload.pop("artifacts", None)  # SPDX-License-Identifier: MIT | 移除调用方自声明资料清单。
        payload["artifact_ids"] = [document["artifact_id"], demo["artifact_id"]]  # SPDX-License-Identifier: MIT | 只提交服务端签发的资料标识。
        return payload  # SPDX-License-Identifier: MIT | 返回可供服务冻结的可信提交。

    def test_completed_run_is_persisted_and_audited(self) -> None:  # SPDX-License-Identifier: MIT | 验证运行完成报告和审计可重读。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            submission_id = service.submit(self._trusted_submission(service))  # SPDX-License-Identifier: MIT | 保存通过可信上传链构造的创作者提交版本。
            run_id = service.create_and_execute_run(submission_id)  # SPDX-License-Identifier: MIT | 创建并执行完整诊断。
            run = service.get_run(run_id)  # SPDX-License-Identifier: MIT | 从 SQLite 重新读取运行。
            self.assertEqual(run["status"], "completed")  # SPDX-License-Identifier: MIT | 确认运行持久化为完成。
            self.assertEqual(run["report"]["rating"]["assessment_result"], "B_GATE")  # SPDX-License-Identifier: MIT | 确认完整报告可读取。
            events = service.repository.list_audit(run_id)  # SPDX-License-Identifier: MIT | 读取运行完整审计时间线。
            self.assertEqual([item["event_type"] for item in events], ["run.created", "run.claimed", "run.completed"])  # SPDX-License-Identifier: MIT | 确认运行状态变化全部记录。

    def test_unconfirmed_submission_has_no_fake_report(self) -> None:  # SPDX-License-Identifier: MIT | 验证待确认答案不生成评分。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            submission = self._submission()  # SPDX-License-Identifier: MIT | 创建完整创作者提交。
            submission["questionnaire"]["core_loop"]["creator_confirmed"] = False  # SPDX-License-Identifier: MIT | 模拟 AI 答案尚未确认。
            run_id = service.create_and_execute_run(service.submit(self._trusted_submission(service, submission)))  # SPDX-License-Identifier: MIT | 执行经可信上传但问卷待确认的提交。
            run = service.get_run(run_id)  # SPDX-License-Identifier: MIT | 读取运行终态。
            self.assertEqual(run["status"], "needs_creator_action")  # SPDX-License-Identifier: MIT | 确认运行停在创作者行动状态。
            self.assertIsNone(run["report"])  # SPDX-License-Identifier: MIT | 确认没有生成假评分报告。
            with self.assertRaises(ValueError):  # SPDX-License-Identifier: MIT | 待创作者修改的冻结提交不能原地重试。
                service.retry_run(run_id)  # SPDX-License-Identifier: MIT | 尝试错误重试待补充运行。

    def test_uploaded_artifact_ids_build_trusted_submission_manifest(self) -> None:  # SPDX-License-Identifier: MIT | 验证客户端无需手工复制上传哈希和解析状态。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化带上传和持久化的应用服务。
            upload = service.ingest_artifact_base64({"project_id": "seed-strong", "filename": "方案.txt", "kind": "design_document", "content_base64": base64.b64encode("核心循环与制作范围".encode("utf-8")).decode("ascii")})  # SPDX-License-Identifier: MIT | 通过正式 Base64 用例安全接收方案文件。
            submission = self._submission()  # SPDX-License-Identifier: MIT | 创建包含完整创作者确认问卷的提交。
            submission.pop("artifacts", None)  # SPDX-License-Identifier: MIT | 模拟客户端不手工组装可信文件清单。
            submission["artifact_ids"] = [upload["artifact_id"]]  # SPDX-License-Identifier: MIT | 只引用上传接口返回的资料标识。
            submission_id = service.submit(submission)  # SPDX-License-Identifier: MIT | 从服务端记录构建并冻结提交。
            frozen = service.repository.get_submission(submission_id)  # SPDX-License-Identifier: MIT | 读取持久化提交快照。
            self.assertEqual(frozen["artifacts"], [upload["submission_artifact"]])  # SPDX-License-Identifier: MIT | 确认可信清单与上传结果完全一致。

    def test_client_supplied_manifest_is_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证客户端不能伪造可信资料状态。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            with self.assertRaises(ValueError):  # SPDX-License-Identifier: MIT | 预期缺少服务端资料标识时拒绝提交。
                service.submit(self._submission())  # SPDX-License-Identifier: MIT | 尝试提交伪造哈希和 ready 状态的客户端清单。

    def test_artifact_order_is_preserved_and_duplicates_rejected(self) -> None:  # SPDX-License-Identifier: MIT | 验证资料清单顺序稳定且标识唯一。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            first = service.ingest_artifact_base64({"project_id": "seed-strong", "filename": "一.txt", "kind": "design_document", "content_base64": base64.b64encode(b"first").decode("ascii")})  # SPDX-License-Identifier: MIT | 上传第一份方案文件。
            second = service.ingest_artifact_base64({"project_id": "seed-strong", "filename": "二.txt", "kind": "design_document", "content_base64": base64.b64encode(b"second").decode("ascii")})  # SPDX-License-Identifier: MIT | 上传第二份方案文件。
            records = service.repository.get_artifacts((second["artifact_id"], first["artifact_id"]))  # SPDX-License-Identifier: MIT | 以反向顺序读取资料。
            self.assertEqual([item["artifact_id"] for item in records], [second["artifact_id"], first["artifact_id"]])  # SPDX-License-Identifier: MIT | 确认仓库严格保持调用顺序。
            with self.assertRaises(ValueError):  # SPDX-License-Identifier: MIT | 重复标识会破坏清单唯一语义。
                service.repository.get_artifacts((first["artifact_id"], first["artifact_id"]))  # SPDX-License-Identifier: MIT | 尝试重复引用同一资料。

    def test_run_cannot_be_claimed_twice_or_retry_nonretryable_failure(self) -> None:  # SPDX-License-Identifier: MIT | 验证运行状态机拒绝重复领取和错误重试。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            submission_id = service.repository.create_submission({"project_id": "state-test", "version": "1", "title": "状态测试"})  # SPDX-License-Identifier: MIT | 创建仅用于状态机测试的冻结提交。
            run_id = service.repository.create_run(submission_id)  # SPDX-License-Identifier: MIT | 创建排队运行。
            service.repository.claim_run(run_id)  # SPDX-License-Identifier: MIT | 第一次合法领取运行。
            with self.assertRaises(ValueError):  # SPDX-License-Identifier: MIT | 运行中任务不能被第二个工作线程领取。
                service.repository.claim_run(run_id)  # SPDX-License-Identifier: MIT | 尝试重复领取同一运行。
            service.repository.fail_run(run_id, "invalid_fixture", "不可重试测试失败", False)  # SPDX-License-Identifier: MIT | 将处理中运行标记为不可重试失败。
            with self.assertRaises(ValueError):  # SPDX-License-Identifier: MIT | 不可重试失败必须创建新提交或人工处置。
                service.retry_run(run_id)  # SPDX-License-Identifier: MIT | 尝试违反 retryable 标记重试。

    def test_interrupted_run_recovery_adds_audit_event(self) -> None:  # SPDX-License-Identifier: MIT | 验证启动恢复不会留下审计断层。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理服务数据目录。
            service = GameRatingApplicationService(Path(directory))  # SPDX-License-Identifier: MIT | 初始化完整应用服务。
            submission_id = service.repository.create_submission({"project_id": "recover-test", "version": "1", "title": "恢复测试"})  # SPDX-License-Identifier: MIT | 创建状态机测试提交。
            run_id = service.repository.create_run(submission_id)  # SPDX-License-Identifier: MIT | 创建排队运行。
            service.repository.claim_run(run_id)  # SPDX-License-Identifier: MIT | 模拟工作线程领取后进程中断。
            self.assertEqual(service.repository.recover_interrupted_runs(), 1)  # SPDX-License-Identifier: MIT | 确认恢复一个中断运行。
            run = service.get_run(run_id)  # SPDX-License-Identifier: MIT | 读取恢复后的运行状态。
            self.assertEqual(run["status"], "failed")  # SPDX-License-Identifier: MIT | 确认中断运行变为可重试失败。
            self.assertTrue(run["error"]["retryable"])  # SPDX-License-Identifier: MIT | 确认恢复错误允许安全重试。
            events = service.repository.list_audit(run_id)  # SPDX-License-Identifier: MIT | 读取完整恢复审计链。
            self.assertEqual([item["event_type"] for item in events], ["run.created", "run.claimed", "run.failed"])  # SPDX-License-Identifier: MIT | 确认中断恢复追加失败事件。

class HttpApiTests(unittest.TestCase):  # SPDX-License-Identifier: MIT | 验证真实 HTTP 鉴权和核心路由。
    def test_frontend_shell_is_public_but_api_remains_protected(self) -> None:  # SPDX-License-Identifier: MIT | 验证前端可加载且业务 API 仍要求令牌。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理 API 数据目录。
            token = "test-token-123456789"  # SPDX-License-Identifier: MIT | 配置满足最小长度的测试令牌。
            server = create_server("127.0.0.1", 0, Path(directory), token)  # SPDX-License-Identifier: MIT | 在随机空闲端口创建真实服务。
            thread = threading.Thread(target=server.serve_forever, daemon=True)  # SPDX-License-Identifier: MIT | 在测试后台线程处理请求。
            thread.start()  # SPDX-License-Identifier: MIT | 启动真实 HTTP 服务。
            base = f"http://127.0.0.1:{server.server_address[1]}"  # SPDX-License-Identifier: MIT | 获取操作系统分配端口。
            try:  # SPDX-License-Identifier: MIT | 始终在测试结束关闭服务。
                with urlopen(base + "/", timeout=3) as response:  # SPDX-License-Identifier: MIT | 无令牌读取不含项目数据的前端外壳。
                    html = response.read().decode("utf-8")  # SPDX-License-Identifier: MIT | 解析前端 UTF-8 页面内容。
                    content_security_policy = response.headers.get("Content-Security-Policy", "")  # SPDX-License-Identifier: MIT | 读取前端内容安全策略。
                self.assertIn("GameForge", html)  # SPDX-License-Identifier: MIT | 确认返回真实产品前端而非占位页。
                self.assertIn("default-src 'self'", content_security_policy)  # SPDX-License-Identifier: MIT | 确认前端限制同源资源加载。
                with urlopen(base + "/app.js", timeout=3) as response:  # SPDX-License-Identifier: MIT | 无令牌读取同源前端交互脚本。
                    script = response.read().decode("utf-8")  # SPDX-License-Identifier: MIT | 解析前端 JavaScript 内容。
                self.assertIn("/v1/artifacts", script)  # SPDX-License-Identifier: MIT | 确认前端连接真实上传 API。
                self.assertIn("/v1/knowledge-base", script)  # SPDX-License-Identifier: MIT | 确认前端与后端类型知识库合同真实耦合。
                self.assertIn("buildGenreEditor", script)  # SPDX-License-Identifier: MIT | 确认类型知识库使用引导式控件而非要求用户猜代码。
                with self.assertRaises(HTTPError) as context:  # SPDX-License-Identifier: MIT | 预期业务 API 仍拒绝匿名请求。
                    urlopen(base + "/health", timeout=3)  # SPDX-License-Identifier: MIT | 发起未授权健康请求。
                self.assertEqual(context.exception.code, 401)  # SPDX-License-Identifier: MIT | 确认前端公开没有放松 API 鉴权。
            finally:  # SPDX-License-Identifier: MIT | 无论断言结果都关闭 HTTP 服务。
                server.shutdown()  # SPDX-License-Identifier: MIT | 停止后台请求循环。
                server.server_close()  # SPDX-License-Identifier: MIT | 释放随机测试端口。
                thread.join(timeout=3)  # SPDX-License-Identifier: MIT | 等待测试线程退出。
    def test_health_requires_token_and_questionnaire_is_available(self) -> None:  # SPDX-License-Identifier: MIT | 验证 API 默认拒绝匿名访问。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理 API 数据目录。
            token = "test-token-123456789"  # SPDX-License-Identifier: MIT | 配置满足最小长度的测试令牌。
            server = create_server("127.0.0.1", 0, Path(directory), token)  # SPDX-License-Identifier: MIT | 在随机空闲端口创建真实服务。
            thread = threading.Thread(target=server.serve_forever, daemon=True)  # SPDX-License-Identifier: MIT | 在测试后台线程处理请求。
            thread.start()  # SPDX-License-Identifier: MIT | 启动真实 HTTP 服务。
            base = f"http://127.0.0.1:{server.server_address[1]}"  # SPDX-License-Identifier: MIT | 获取操作系统分配端口。
            try:  # SPDX-License-Identifier: MIT | 始终在测试结束关闭服务。
                with self.assertRaises(HTTPError) as context:  # SPDX-License-Identifier: MIT | 预期匿名健康请求被拒绝。
                    urlopen(base + "/health", timeout=3)  # SPDX-License-Identifier: MIT | 发起未授权 GET 请求。
                self.assertEqual(context.exception.code, 401)  # SPDX-License-Identifier: MIT | 确认匿名请求返回 401。
                request = Request(base + "/v1/questionnaire", headers={"Authorization": f"Bearer {token}"})  # SPDX-License-Identifier: MIT | 创建带 Bearer Token 的问卷请求。
                with urlopen(request, timeout=3) as response:  # SPDX-License-Identifier: MIT | 发起已授权真实 HTTP 请求。
                    payload = json.loads(response.read().decode("utf-8"))  # SPDX-License-Identifier: MIT | 解析问卷 JSON 响应。
                self.assertGreater(len(payload["questions"]), 10)  # SPDX-License-Identifier: MIT | 确认服务返回完整问卷而非占位符。
                knowledge_request = Request(base + "/v1/knowledge-base", headers={"Authorization": f"Bearer {token}"})  # SPDX-License-Identifier: MIT | 创建带 Bearer Token 的知识库读取请求。
                with urlopen(knowledge_request, timeout=3) as response:  # SPDX-License-Identifier: MIT | 读取版本化游戏类型评分规则。
                    knowledge = json.loads(response.read().decode("utf-8"))  # SPDX-License-Identifier: MIT | 解析类型基线和评分逻辑 JSON。
                self.assertGreaterEqual(len(knowledge["profiles"]), 20)  # SPDX-License-Identifier: MIT | 确认知识库覆盖主要市场游戏类型而非占位资料。
            finally:  # SPDX-License-Identifier: MIT | 无论断言结果都关闭 HTTP 服务。
                server.shutdown()  # SPDX-License-Identifier: MIT | 停止后台请求循环。
                server.server_close()  # SPDX-License-Identifier: MIT | 释放随机测试端口。
                thread.join(timeout=3)  # SPDX-License-Identifier: MIT | 等待测试线程退出。

    def test_post_requires_json_content_type(self) -> None:  # SPDX-License-Identifier: MIT | 验证 POST 请求拒绝媒体类型混淆。
        with TemporaryDirectory() as directory:  # SPDX-License-Identifier: MIT | 创建自动清理 API 数据目录。
            token = "test-token-123456789"  # SPDX-License-Identifier: MIT | 配置满足最小长度的测试令牌。
            server = create_server("127.0.0.1", 0, Path(directory), token)  # SPDX-License-Identifier: MIT | 在随机空闲端口创建真实服务。
            thread = threading.Thread(target=server.serve_forever, daemon=True)  # SPDX-License-Identifier: MIT | 在测试后台线程处理请求。
            thread.start()  # SPDX-License-Identifier: MIT | 启动真实 HTTP 服务。
            base = f"http://127.0.0.1:{server.server_address[1]}"  # SPDX-License-Identifier: MIT | 获取操作系统分配端口。
            try:  # SPDX-License-Identifier: MIT | 始终在测试结束关闭服务。
                request = Request(base + "/v1/submissions", data=b"{}", headers={"Authorization": f"Bearer {token}", "Content-Type": "text/plain"}, method="POST")  # SPDX-License-Identifier: MIT | 构造错误媒体类型的已授权请求。
                with self.assertRaises(HTTPError) as context:  # SPDX-License-Identifier: MIT | 预期请求合同校验失败。
                    urlopen(request, timeout=3)  # SPDX-License-Identifier: MIT | 发起真实 POST 请求。
                self.assertEqual(context.exception.code, 400)  # SPDX-License-Identifier: MIT | 确认媒体类型错误返回 400。
            finally:  # SPDX-License-Identifier: MIT | 无论断言结果都关闭 HTTP 服务。
                server.shutdown()  # SPDX-License-Identifier: MIT | 停止后台请求循环。
                server.server_close()  # SPDX-License-Identifier: MIT | 释放随机测试端口。
                thread.join(timeout=3)  # SPDX-License-Identifier: MIT | 等待测试线程退出。

if __name__ == "__main__":  # SPDX-License-Identifier: MIT | 允许直接执行服务层测试。
    unittest.main()  # SPDX-License-Identifier: MIT | 启动标准库测试运行器。
