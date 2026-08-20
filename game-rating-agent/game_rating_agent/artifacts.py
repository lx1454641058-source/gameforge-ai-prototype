"""上传资料的安全接收、签名检查、隔离存储和有限文本提取。"""  # SPDX-License-Identifier: MIT | 描述文件接收模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import asdict, dataclass  # SPDX-License-Identifier: MIT | 定义可序列化资料记录。
from hashlib import sha256  # SPDX-License-Identifier: MIT | 生成内容寻址哈希。
from pathlib import Path  # SPDX-License-Identifier: MIT | 安全处理隔离存储路径。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容元数据。
from xml.etree import ElementTree  # SPDX-License-Identifier: MIT | 从 DOCX OOXML 提取纯文本。
from zipfile import BadZipFile, ZipFile  # SPDX-License-Identifier: MIT | 检查 DOCX 和 Demo ZIP 结构。
import json  # SPDX-License-Identifier: MIT | 验证 JSON 方案文件并生成元数据。
import os  # SPDX-License-Identifier: MIT | 使用排他方式写入隔离文件。
import re  # SPDX-License-Identifier: MIT | 清洗原始文件名。
import uuid  # SPDX-License-Identifier: MIT | 生成不受用户控制的存储名称。

ALLOWED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md", ".json", ".png", ".jpg", ".jpeg", ".mp4", ".webm", ".zip"}  # SPDX-License-Identifier: MIT | 只允许当前业务必要的资料格式。
TEXT_EXTENSIONS = {".txt", ".md", ".json"}  # SPDX-License-Identifier: MIT | 定义可在本地安全读取的纯文本格式。
KIND_EXTENSIONS = {"design_document": {".docx", ".pdf", ".txt", ".md", ".json"}, "pitch_deck": {".docx", ".pdf"}, "spreadsheet": {".json"}, "image": {".png", ".jpg", ".jpeg"}, "video": {".mp4", ".webm"}, "demo_build": {".zip"}, "source_snapshot": {".zip"}, "other": ALLOWED_EXTENSIONS}  # SPDX-License-Identifier: MIT | 绑定业务资料类型与实际文件格式，防止普通文本冒充 Demo。
MAX_FILENAME_LENGTH = 180  # SPDX-License-Identifier: MIT | 限制用户文件名长度。
MAX_ZIP_ENTRIES = 10000  # SPDX-License-Identifier: MIT | 限制压缩包条目数量以防资源耗尽。
MAX_ZIP_EXPANDED_BYTES = 2 * 1024 * 1024 * 1024  # SPDX-License-Identifier: MIT | 限制 Demo 压缩包声明解压总量为 2GB。
MAX_COMPRESSION_RATIO = 100.0  # SPDX-License-Identifier: MIT | 拒绝异常高压缩比压缩炸弹。
MAX_EXTRACTED_TEXT = 500000  # SPDX-License-Identifier: MIT | 限制送入问卷提取器的文本长度。

class ArtifactValidationError(ValueError):  # SPDX-License-Identifier: MIT | 表示用户可修复的上传校验失败。
    pass  # SPDX-License-Identifier: MIT | 使用父类消息承载明确失败原因。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结已接收资料记录。
class StoredArtifact:  # SPDX-License-Identifier: MIT | 描述隔离存储中的方案文件或 Demo。
    artifact_id: str  # SPDX-License-Identifier: MIT | 保存系统生成资料标识。
    project_id: str  # SPDX-License-Identifier: MIT | 保存资料所属项目。
    kind: str  # SPDX-License-Identifier: MIT | 保存设计文档或 Demo 等业务类型。
    original_filename: str  # SPDX-License-Identifier: MIT | 保存清洗后的展示文件名。
    stored_filename: str  # SPDX-License-Identifier: MIT | 保存系统生成的非公开存储名。
    extension: str  # SPDX-License-Identifier: MIT | 保存规范化扩展名。
    sha256: str  # SPDX-License-Identifier: MIT | 保存文件内容哈希。
    byte_size: int  # SPDX-License-Identifier: MIT | 保存文件大小。
    parse_status: str  # SPDX-License-Identifier: MIT | 保存 ready、unsupported 或 rejected 前状态。
    extracted_text: str  # SPDX-License-Identifier: MIT | 保存有限纯文本而不执行任何嵌入内容。
    security_notes: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存安全检查与能力限制说明。

    def manifest_record(self) -> dict[str, str]:  # SPDX-License-Identifier: MIT | 转换为评分提交需要的资料清单记录。
        return {"artifact_id": self.artifact_id, "kind": self.kind, "filename": self.original_filename, "sha256": self.sha256, "parse_status": self.parse_status}  # SPDX-License-Identifier: MIT | 返回不暴露存储路径的资料索引。

    def to_dict(self, include_text: bool = False) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 转换为安全 API 响应。
        payload = asdict(self)  # SPDX-License-Identifier: MIT | 展开不可变资料记录。
        payload.pop("stored_filename", None)  # SPDX-License-Identifier: MIT | 防止 API 暴露内部存储名称。
        if not include_text:  # SPDX-License-Identifier: MIT | 默认不返回可能包含敏感信息的提取文本。
            payload.pop("extracted_text", None)  # SPDX-License-Identifier: MIT | 移除提取正文。
        return payload  # SPDX-License-Identifier: MIT | 返回安全资料元数据。

class ArtifactStore:  # SPDX-License-Identifier: MIT | 在 Web 根目录之外安全接收上传内容。
    def __init__(self, root: Path, max_bytes: int = 100 * 1024 * 1024) -> None:  # SPDX-License-Identifier: MIT | 配置隔离根目录和单文件大小限制。
        self.root = root.resolve()  # SPDX-License-Identifier: MIT | 固定绝对隔离存储根目录。
        self.max_bytes = max_bytes  # SPDX-License-Identifier: MIT | 保存可配置单文件上限。
        self.root.mkdir(parents=True, exist_ok=True)  # SPDX-License-Identifier: MIT | 创建隔离存储目录。

    def ingest(self, project_id: str, filename: str, kind: str, content: bytes) -> StoredArtifact:  # SPDX-License-Identifier: MIT | 验证并隔离保存一个上传文件。
        canonical_project_id = self._project_id(project_id)  # SPDX-License-Identifier: MIT | 保留创作者项目编号原文并在进入存储前验证其长度和控制字符。
        storage_project_key = self._project_storage_key(canonical_project_id)  # SPDX-License-Identifier: MIT | 为文件系统目录生成安全且不会因中文字符折叠碰撞的存储键。
        safe_name = self._safe_filename(filename)  # SPDX-License-Identifier: MIT | 清洗仅用于展示的原始文件名。
        extension = Path(safe_name).suffix.lower()  # SPDX-License-Identifier: MIT | 在解码后读取最后一个扩展名。
        if extension not in ALLOWED_EXTENSIONS:  # SPDX-License-Identifier: MIT | 使用业务格式白名单而非黑名单。
            raise ArtifactValidationError(f"不支持的文件扩展名：{extension or '无扩展名'}")  # SPDX-License-Identifier: MIT | 返回明确格式错误。
        if kind not in KIND_EXTENSIONS:  # SPDX-License-Identifier: MIT | 拒绝未登记的业务资料类型。
            raise ArtifactValidationError(f"不支持的资料类型：{kind}")  # SPDX-License-Identifier: MIT | 返回明确资料类型错误。
        if extension not in KIND_EXTENSIONS[kind]:  # SPDX-License-Identifier: MIT | 检查资料声明与实际扩展名是否相符。
            raise ArtifactValidationError(f"资料类型 {kind} 不接受文件格式 {extension}")  # SPDX-License-Identifier: MIT | 阻止以错误类型绕过阶段证据门槛。
        if not content:  # SPDX-License-Identifier: MIT | 拒绝空文件。
            raise ArtifactValidationError("上传文件为空")  # SPDX-License-Identifier: MIT | 返回空文件错误。
        if len(content) > self.max_bytes:  # SPDX-License-Identifier: MIT | 在写盘前执行大小限制。
            raise ArtifactValidationError(f"文件超过大小限制：{self.max_bytes} bytes")  # SPDX-License-Identifier: MIT | 返回大小限制错误。
        self._validate_signature(extension, content)  # SPDX-License-Identifier: MIT | 不信任客户端 Content-Type 并检查文件签名。
        security_notes = list(self._inspect_archive(extension, content))  # SPDX-License-Identifier: MIT | 检查 ZIP 路径、条目和压缩炸弹风险。
        extracted_text, parse_status, parse_notes = self._extract_text(extension, content)  # SPDX-License-Identifier: MIT | 仅执行受限静态文本提取。
        security_notes.extend(parse_notes)  # SPDX-License-Identifier: MIT | 合并提取能力限制说明。
        artifact_id = f"art_{uuid.uuid4().hex}"  # SPDX-License-Identifier: MIT | 生成不可预测资料标识。
        project_dir = (self.root / storage_project_key).resolve()  # SPDX-License-Identifier: MIT | 使用安全存储键计算项目隔离子目录。
        if self.root not in project_dir.parents:  # SPDX-License-Identifier: MIT | 再次确认项目目录位于隔离根目录内。
            raise ArtifactValidationError("项目存储路径无效")  # SPDX-License-Identifier: MIT | 阻止任何路径逃逸。
        project_dir.mkdir(parents=True, exist_ok=True)  # SPDX-License-Identifier: MIT | 创建项目隔离目录。
        stored_filename = f"{artifact_id}{extension}"  # SPDX-License-Identifier: MIT | 使用系统标识替代用户文件名。
        destination = (project_dir / stored_filename).resolve()  # SPDX-License-Identifier: MIT | 计算最终隔离文件路径。
        if project_dir not in destination.parents:  # SPDX-License-Identifier: MIT | 确认最终文件仍在项目隔离目录内。
            raise ArtifactValidationError("资料存储路径无效")  # SPDX-License-Identifier: MIT | 阻止存储路径逃逸。
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # SPDX-License-Identifier: MIT | 排他创建最小权限文件避免覆盖。
        with os.fdopen(descriptor, "wb") as handle:  # SPDX-License-Identifier: MIT | 将文件描述符交给上下文管理器。
            handle.write(content)  # SPDX-License-Identifier: MIT | 一次写入已通过校验的原始内容。
        digest = sha256(content).hexdigest()  # SPDX-License-Identifier: MIT | 计算内容哈希用于版本和去重。
        return StoredArtifact(artifact_id, canonical_project_id, kind, safe_name, stored_filename, extension, digest, len(content), parse_status, extracted_text, tuple(security_notes))  # SPDX-License-Identifier: MIT | 返回保留原项目编号且不执行文件的安全资料记录。

    def _project_id(self, value: str) -> str:  # SPDX-License-Identifier: MIT | 验证仅用于业务归属而非路径拼接的项目编号。
        project_id = str(value).strip()  # SPDX-License-Identifier: MIT | 规范化项目编号前后空白但保留中文等展示字符。
        if not project_id or len(project_id) > 120 or any(ord(character) < 32 for character in project_id):  # SPDX-License-Identifier: MIT | 拒绝空、过长或含控制字符的项目编号。
            raise ArtifactValidationError("项目编号无效或过长")  # SPDX-License-Identifier: MIT | 返回新手可理解的项目编号校验错误。
        return project_id  # SPDX-License-Identifier: MIT | 返回可在数据库和 API 合同中保持一致的原项目编号。

    def _project_storage_key(self, project_id: str) -> str:  # SPDX-License-Identifier: MIT | 为项目资料目录创建不泄露原文且无字符折叠碰撞的安全键。
        if re.fullmatch(r"[A-Za-z0-9_-]{1,80}", project_id):  # SPDX-License-Identifier: MIT | 保留既有 ASCII 编号的目录兼容性和可读性。
            return project_id  # SPDX-License-Identifier: MIT | 返回与旧版本一致的安全 ASCII 目录名。
        return f"project_{sha256(project_id.encode('utf-8')).hexdigest()}"  # SPDX-License-Identifier: MIT | 对含中文或其他安全展示字符的编号使用确定性哈希目录键。

    def _safe_filename(self, filename: str) -> str:  # SPDX-License-Identifier: MIT | 清洗仅用于显示和扩展判断的文件名。
        candidate = Path(str(filename).replace("\\", "/")).name  # SPDX-License-Identifier: MIT | 移除客户端路径部分。
        candidate = re.sub(r"[\x00-\x1f<>:\"/\\|?*]", "_", candidate).strip(" .")  # SPDX-License-Identifier: MIT | 移除控制字符和 Windows 危险字符。
        if not candidate or len(candidate) > MAX_FILENAME_LENGTH:  # SPDX-License-Identifier: MIT | 拒绝空名或异常长文件名。
            raise ArtifactValidationError("文件名无效或过长")  # SPDX-License-Identifier: MIT | 返回文件名错误。
        return candidate  # SPDX-License-Identifier: MIT | 返回清洗后的展示文件名。

    def _validate_signature(self, extension: str, content: bytes) -> None:  # SPDX-License-Identifier: MIT | 对常见二进制格式执行最小魔数检查。
        signatures = {".pdf": (b"%PDF-",), ".png": (b"\x89PNG\r\n\x1a\n",), ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",), ".docx": (b"PK\x03\x04",), ".zip": (b"PK\x03\x04",), ".webm": (b"\x1aE\xdf\xa3",)}  # SPDX-License-Identifier: MIT | 定义白名单格式的已知文件签名。
        if extension == ".mp4":  # SPDX-License-Identifier: MIT | MP4 的 ftyp 标识位于偏移四。
            if len(content) < 12 or content[4:8] != b"ftyp":  # SPDX-License-Identifier: MIT | 检查 MP4 容器品牌标识。
                raise ArtifactValidationError("MP4 文件签名不匹配")  # SPDX-License-Identifier: MIT | 拒绝伪装 MP4。
            return  # SPDX-License-Identifier: MIT | 完成 MP4 签名验证。
        expected = signatures.get(extension)  # SPDX-License-Identifier: MIT | 读取扩展名对应签名。
        if expected and not any(content.startswith(signature) for signature in expected):  # SPDX-License-Identifier: MIT | 检查内容是否匹配任一合法签名。
            raise ArtifactValidationError(f"文件内容与扩展名 {extension} 不匹配")  # SPDX-License-Identifier: MIT | 拒绝简单类型伪装。
        if extension in TEXT_EXTENSIONS and b"\x00" in content[:4096]:  # SPDX-License-Identifier: MIT | 纯文本前部不应包含空字节。
            raise ArtifactValidationError("文本文件包含二进制内容")  # SPDX-License-Identifier: MIT | 拒绝伪装纯文本。

    def _inspect_archive(self, extension: str, content: bytes) -> tuple[str, ...]:  # SPDX-License-Identifier: MIT | 静态检查 DOCX 和 Demo ZIP 而不解压执行。
        if extension not in {".docx", ".zip"}:  # SPDX-License-Identifier: MIT | 非 ZIP 容器无需压缩结构检查。
            return ()  # SPDX-License-Identifier: MIT | 返回空安全说明。
        try:  # SPDX-License-Identifier: MIT | 捕获损坏压缩包错误。
            from io import BytesIO  # SPDX-License-Identifier: MIT | 在内存中读取已受大小限制的压缩包。
            with ZipFile(BytesIO(content)) as archive:  # SPDX-License-Identifier: MIT | 只读取中央目录和指定文本条目。
                infos = archive.infolist()  # SPDX-License-Identifier: MIT | 获取压缩条目元数据。
                if len(infos) > MAX_ZIP_ENTRIES:  # SPDX-License-Identifier: MIT | 限制异常多条目的压缩包。
                    raise ArtifactValidationError("压缩包条目数量超过安全限制")  # SPDX-License-Identifier: MIT | 拒绝条目耗尽攻击。
                expanded = sum(info.file_size for info in infos)  # SPDX-License-Identifier: MIT | 计算声明解压总量。
                compressed = max(1, sum(info.compress_size for info in infos))  # SPDX-License-Identifier: MIT | 计算压缩总量并避免除零。
                if expanded > MAX_ZIP_EXPANDED_BYTES or expanded / compressed > MAX_COMPRESSION_RATIO:  # SPDX-License-Identifier: MIT | 检查体积和压缩比双重阈值。
                    raise ArtifactValidationError("压缩包疑似压缩炸弹")  # SPDX-License-Identifier: MIT | 拒绝异常压缩包。
                for info in infos:  # SPDX-License-Identifier: MIT | 检查每个条目的规范路径。
                    normalized = info.filename.replace("\\", "/")  # SPDX-License-Identifier: MIT | 统一压缩条目路径分隔符。
                    if normalized.startswith(("/", "//")) or re.match(r"^[A-Za-z]:/", normalized) or ".." in Path(normalized).parts:  # SPDX-License-Identifier: MIT | 同时检测 POSIX、UNC、Windows 盘符绝对路径和父目录逃逸。
                        raise ArtifactValidationError("压缩包包含路径穿越条目")  # SPDX-License-Identifier: MIT | 拒绝 Zip Slip 风险。
                if extension == ".docx" and "word/document.xml" not in {info.filename for info in infos}:  # SPDX-License-Identifier: MIT | DOCX 必须包含主文档部件。
                    raise ArtifactValidationError("DOCX 缺少主文档内容")  # SPDX-License-Identifier: MIT | 拒绝伪装或损坏 DOCX。
        except BadZipFile as error:  # SPDX-License-Identifier: MIT | 处理无法解析的 ZIP 容器。
            raise ArtifactValidationError("压缩包结构损坏") from error  # SPDX-License-Identifier: MIT | 返回安全的用户错误。
        return ("压缩包仅完成静态结构检查，未执行其中任何文件",)  # SPDX-License-Identifier: MIT | 明示检查边界。

    def _extract_text(self, extension: str, content: bytes) -> tuple[str, str, tuple[str, ...]]:  # SPDX-License-Identifier: MIT | 对受支持格式执行有限静态文本提取。
        if extension in {".txt", ".md"}:  # SPDX-License-Identifier: MIT | 处理 UTF-8 或可替换字符的纯文本。
            return content.decode("utf-8", errors="replace")[:MAX_EXTRACTED_TEXT], "ready", ("已提取纯文本",)  # SPDX-License-Identifier: MIT | 返回限制长度的文本。
        if extension == ".json":  # SPDX-License-Identifier: MIT | 先验证 JSON 再作为文本使用。
            decoded = content.decode("utf-8", errors="strict")  # SPDX-License-Identifier: MIT | JSON 必须是有效 UTF-8。
            json.loads(decoded)  # SPDX-License-Identifier: MIT | 拒绝语法无效 JSON。
            return decoded[:MAX_EXTRACTED_TEXT], "ready", ("已验证并提取 JSON 文本",)  # SPDX-License-Identifier: MIT | 返回有效 JSON 文本。
        if extension == ".docx":  # SPDX-License-Identifier: MIT | 从 OOXML 主文档提取可见文本节点。
            from io import BytesIO  # SPDX-License-Identifier: MIT | 在内存中读取已校验 DOCX。
            with ZipFile(BytesIO(content)) as archive:  # SPDX-License-Identifier: MIT | 只打开主文档 XML。
                xml_bytes = archive.read("word/document.xml")  # SPDX-License-Identifier: MIT | 读取已确认存在的主文档部件。
            if len(xml_bytes) > 20 * 1024 * 1024:  # SPDX-License-Identifier: MIT | 限制异常巨大的 XML 文档部件。
                raise ArtifactValidationError("DOCX 主文档内容过大")  # SPDX-License-Identifier: MIT | 防止 XML 解析资源耗尽。
            upper_xml = xml_bytes.upper()  # SPDX-License-Identifier: MIT | 规范化 XML 声明以执行不区分大小写的危险结构检查。
            if b"<!DOCTYPE" in upper_xml or b"<!ENTITY" in upper_xml:  # SPDX-License-Identifier: MIT | 拒绝 DTD 和实体声明以降低 XML 实体扩展风险。
                raise ArtifactValidationError("DOCX 主文档包含不允许的 DTD 或实体声明")  # SPDX-License-Identifier: MIT | 将恶意 XML 作为用户可修复上传错误处理。
            try:  # SPDX-License-Identifier: MIT | 将损坏 OOXML 映射为明确资料校验错误。
                root = ElementTree.fromstring(xml_bytes)  # SPDX-License-Identifier: MIT | 在体积和声明检查后解析标准 Word 主文档 XML。
            except ElementTree.ParseError as error:  # SPDX-License-Identifier: MIT | 捕获损坏或恶意 XML 语法。
                raise ArtifactValidationError("DOCX 主文档 XML 无效") from error  # SPDX-License-Identifier: MIT | 防止解析错误变成不透明服务端 500。
            text = "\n".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))  # SPDX-License-Identifier: MIT | 仅收集 Word 文本节点。
            return text[:MAX_EXTRACTED_TEXT], "ready", ("仅提取 DOCX 主文档文字；未执行宏、链接或嵌入对象",)  # SPDX-License-Identifier: MIT | 返回有限文本和边界说明。
        if extension == ".zip":  # SPDX-License-Identifier: MIT | Demo ZIP 不在业务进程中解压或执行。
            return "", "ready", ("Demo 已登记哈希和压缩结构；尚未在隔离沙箱中运行",)  # SPDX-License-Identifier: MIT | 允许作为阶段证据但披露未试玩。
        return "", "unsupported", ("当前本地内核不提取该格式正文；可后续接入受控多模态或 OCR 服务",)  # SPDX-License-Identifier: MIT | 对 PDF、图像和视频明确降级而不猜测。
