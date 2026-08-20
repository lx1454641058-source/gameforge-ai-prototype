"""使用 SQLite 保存提交、运行、报告、错误和审计事件。"""  # SPDX-License-Identifier: MIT | 描述持久化模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from datetime import datetime, timezone  # SPDX-License-Identifier: MIT | 生成统一 UTC 审计时间。
from pathlib import Path  # SPDX-License-Identifier: MIT | 安全处理数据库路径。
from typing import Any, Iterator  # SPDX-License-Identifier: MIT | 表示 JSON 兼容数据和连接迭代器。
from contextlib import contextmanager  # SPDX-License-Identifier: MIT | 确保 SQLite 事务结束后显式关闭连接。
import json  # SPDX-License-Identifier: MIT | 保存结构化提交和报告。
import sqlite3  # SPDX-License-Identifier: MIT | 使用标准库实现单机 MVP 持久化。
import uuid  # SPDX-License-Identifier: MIT | 生成提交和审计标识。

TERMINAL_STATUSES = {"completed", "failed", "needs_creator_action"}  # SPDX-License-Identifier: MIT | 定义不应继续自动推进的运行状态。

class AgentRepository:  # SPDX-License-Identifier: MIT | 管理可恢复运行和不可覆盖审计记录。
    def __init__(self, database_path: Path) -> None:  # SPDX-License-Identifier: MIT | 配置 SQLite 数据库文件。
        self.database_path = database_path.resolve()  # SPDX-License-Identifier: MIT | 固定绝对数据库路径。
        self.database_path.parent.mkdir(parents=True, exist_ok=True)  # SPDX-License-Identifier: MIT | 创建数据库父目录。
        self._initialize()  # SPDX-License-Identifier: MIT | 创建首次运行所需表结构。

    def create_submission(self, payload: dict[str, Any]) -> str:  # SPDX-License-Identifier: MIT | 保存创作者提交版本而不覆盖历史。
        submission_id = f"sub_{uuid.uuid4().hex}"  # SPDX-License-Identifier: MIT | 生成提交唯一标识。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成统一创建时间。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在事务中写入提交和审计。
            connection.execute("INSERT INTO submissions(id, project_id, project_version, payload_json, created_at) VALUES (?, ?, ?, ?, ?)", (submission_id, str(payload.get("project_id") or ""), str(payload.get("version") or ""), self._json(payload), now))  # SPDX-License-Identifier: MIT | 保存完整提交快照。
            self._audit_connection(connection, "submission.created", submission_id, {"project_id": payload.get("project_id"), "version": payload.get("version")})  # SPDX-License-Identifier: MIT | 记录提交创建审计。
        return submission_id  # SPDX-License-Identifier: MIT | 返回提交标识。

    def save_artifact(self, artifact: dict[str, Any]) -> None:  # SPDX-License-Identifier: MIT | 保存隔离资料元数据和有限提取文本。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在事务中保存资料记录和审计。
            connection.execute("INSERT INTO artifacts(id, project_id, payload_json, created_at) VALUES (?, ?, ?, ?)", (str(artifact["artifact_id"]), str(artifact["project_id"]), self._json(artifact), self._now()))  # SPDX-License-Identifier: MIT | 使用系统资料标识避免覆盖。
            self._audit_connection(connection, "artifact.created", str(artifact["artifact_id"]), {"project_id": artifact["project_id"], "sha256": artifact["sha256"], "parse_status": artifact["parse_status"]})  # SPDX-License-Identifier: MIT | 记录不含正文的资料接收审计。

    def get_artifacts(self, artifact_ids: tuple[str, ...]) -> tuple[dict[str, Any], ...]:  # SPDX-License-Identifier: MIT | 按本次请求标识读取已隔离资料。
        if not artifact_ids:  # SPDX-License-Identifier: MIT | 空列表无需查询数据库。
            return ()  # SPDX-License-Identifier: MIT | 返回空资料集合。
        if len(set(artifact_ids)) != len(artifact_ids):  # SPDX-License-Identifier: MIT | 拒绝同一资料标识被重复引用。
            raise ValueError("资料标识不能重复")  # SPDX-License-Identifier: MIT | 保证清单顺序和哈希语义唯一。
        placeholders = ",".join("?" for _ in artifact_ids)  # SPDX-License-Identifier: MIT | 为参数化 IN 查询生成占位符。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 创建短生命周期读取连接。
            rows = connection.execute(f"SELECT payload_json FROM artifacts WHERE id IN ({placeholders})", artifact_ids).fetchall()  # SPDX-License-Identifier: MIT | 只插入占位符数量并参数化所有值。
        records_by_id = {str(record.get("artifact_id")): record for record in (json.loads(row["payload_json"]) for row in rows)}  # SPDX-License-Identifier: MIT | 按系统资料标识建立服务端可信记录映射。
        if len(records_by_id) != len(artifact_ids):  # SPDX-License-Identifier: MIT | 防止调用方引用不存在或未授权资料。
            raise KeyError("一个或多个资料标识不存在")  # SPDX-License-Identifier: MIT | 返回明确资料引用错误。
        return tuple(records_by_id[artifact_id] for artifact_id in artifact_ids)  # SPDX-License-Identifier: MIT | 严格保持调用方声明的资料清单顺序。

    def get_submission(self, submission_id: str) -> dict[str, Any] | None:  # SPDX-License-Identifier: MIT | 读取冻结提交快照。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 创建短生命周期读取连接。
            row = connection.execute("SELECT payload_json FROM submissions WHERE id = ?", (submission_id,)).fetchone()  # SPDX-License-Identifier: MIT | 使用参数化查询读取提交。
        return json.loads(row["payload_json"]) if row else None  # SPDX-License-Identifier: MIT | 返回提交或空值。

    def create_run(self, submission_id: str) -> str:  # SPDX-License-Identifier: MIT | 创建可独立重试的新 Agent 运行。
        run_id = f"run_{uuid.uuid4().hex}"  # SPDX-License-Identifier: MIT | 生成服务层运行标识。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成运行创建时间。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在事务中创建运行。
            exists = connection.execute("SELECT 1 FROM submissions WHERE id = ?", (submission_id,)).fetchone()  # SPDX-License-Identifier: MIT | 验证提交存在。
            if not exists:  # SPDX-License-Identifier: MIT | 拒绝不存在的提交引用。
                raise KeyError(f"提交不存在：{submission_id}")  # SPDX-License-Identifier: MIT | 返回领域错误。
            connection.execute("INSERT INTO runs(id, submission_id, status, attempt, created_at, updated_at) VALUES (?, ?, 'queued', 0, ?, ?)", (run_id, submission_id, now, now))  # SPDX-License-Identifier: MIT | 保存排队状态运行。
            self._audit_connection(connection, "run.created", run_id, {"submission_id": submission_id})  # SPDX-License-Identifier: MIT | 记录运行创建审计。
        return run_id  # SPDX-License-Identifier: MIT | 返回服务层运行标识。

    def claim_run(self, run_id: str) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 将排队或失败运行标记为处理中。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成状态更新时间。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 使用事务防止并发重复领取。
            row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()  # SPDX-License-Identifier: MIT | 读取当前运行状态。
            if row is None:  # SPDX-License-Identifier: MIT | 拒绝未知运行标识。
                raise KeyError(f"运行不存在：{run_id}")  # SPDX-License-Identifier: MIT | 返回领域错误。
            error = json.loads(row["error_json"]) if row["error_json"] else {}  # SPDX-License-Identifier: MIT | 读取失败重试属性而不信任调用方。
            retryable_failure = row["status"] == "failed" and error.get("retryable") is True  # SPDX-License-Identifier: MIT | 只有显式可重试失败允许再次领取。
            if row["status"] != "queued" and not retryable_failure:  # SPDX-License-Identifier: MIT | 拒绝运行中、完成、待创作者行动和不可重试失败。
                raise ValueError(f"当前运行状态不能领取：{row['status']}")  # SPDX-License-Identifier: MIT | 返回明确状态机错误。
            cursor = connection.execute("UPDATE runs SET status = 'running', attempt = attempt + 1, error_json = NULL, updated_at = ? WHERE id = ? AND status = ?", (now, run_id, row["status"]))  # SPDX-License-Identifier: MIT | 使用条件更新原子阻止两个工作线程重复领取。
            if cursor.rowcount != 1:  # SPDX-License-Identifier: MIT | 并发竞争失败时不得继续执行同一运行。
                raise ValueError("运行已被其他工作线程领取")  # SPDX-License-Identifier: MIT | 返回可观察的并发状态冲突。
            self._audit_connection(connection, "run.claimed", run_id, {"previous_status": row["status"], "attempt": row["attempt"] + 1})  # SPDX-License-Identifier: MIT | 记录运行领取审计。
        return self.get_run(run_id) or {}  # SPDX-License-Identifier: MIT | 返回更新后的运行快照。

    def complete_run(self, run_id: str, report: dict[str, Any]) -> None:  # SPDX-License-Identifier: MIT | 原子保存成功报告和完成状态。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成完成时间。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在同一事务保存报告和审计。
            cursor = connection.execute("UPDATE runs SET status = 'completed', report_json = ?, error_json = NULL, updated_at = ? WHERE id = ? AND status = 'running'", (self._json(report), now, run_id))  # SPDX-License-Identifier: MIT | 只允许处理中运行保存不可变诊断报告快照。
            if cursor.rowcount != 1:  # SPDX-License-Identifier: MIT | 拒绝越级完成或覆盖终态运行。
                raise ValueError("只有 running 状态可以完成")  # SPDX-License-Identifier: MIT | 返回明确状态机约束。
            self._audit_connection(connection, "run.completed", run_id, {"assessment_result": report.get("rating", {}).get("assessment_result")})  # SPDX-License-Identifier: MIT | 记录完成结论审计。

    def require_creator_action(self, run_id: str, issues: tuple[str, ...]) -> None:  # SPDX-License-Identifier: MIT | 保存可由创作者补充解决的输入阻塞。
        self._set_error(run_id, "needs_creator_action", {"issues": issues})  # SPDX-License-Identifier: MIT | 记录结构化问卷确认问题。

    def fail_run(self, run_id: str, code: str, message: str, retryable: bool) -> None:  # SPDX-License-Identifier: MIT | 保存失败原因和重试属性。
        self._set_error(run_id, "failed", {"code": code, "message": message, "retryable": retryable})  # SPDX-License-Identifier: MIT | 记录不生成假报告的失败状态。

    def get_run(self, run_id: str) -> dict[str, Any] | None:  # SPDX-License-Identifier: MIT | 读取运行状态、报告和错误。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 创建短生命周期读取连接。
            row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()  # SPDX-License-Identifier: MIT | 使用参数化查询读取运行。
        if row is None:  # SPDX-License-Identifier: MIT | 未找到时返回空值供 API 转 404。
            return None  # SPDX-License-Identifier: MIT | 返回未知运行。
        return {"run_id": row["id"], "submission_id": row["submission_id"], "status": row["status"], "attempt": row["attempt"], "report": json.loads(row["report_json"]) if row["report_json"] else None, "error": json.loads(row["error_json"]) if row["error_json"] else None, "created_at": row["created_at"], "updated_at": row["updated_at"]}  # SPDX-License-Identifier: MIT | 返回 API 友好的运行对象。

    def list_audit(self, entity_id: str) -> list[dict[str, Any]]:  # SPDX-License-Identifier: MIT | 读取某提交或运行的完整审计时间线。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 创建短生命周期读取连接。
            rows = connection.execute("SELECT event_type, payload_json, created_at FROM audit_events WHERE entity_id = ? ORDER BY sequence ASC", (entity_id,)).fetchall()  # SPDX-License-Identifier: MIT | 按稳定序号读取审计事件。
        return [{"event_type": row["event_type"], "payload": json.loads(row["payload_json"]), "created_at": row["created_at"]} for row in rows]  # SPDX-License-Identifier: MIT | 返回结构化审计时间线。

    def recover_interrupted_runs(self) -> int:  # SPDX-License-Identifier: MIT | 将进程中断时的 running 任务恢复为 failed 可重试状态。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成恢复时间。
        error_payload = {"code": "worker_interrupted", "message": "上次执行被中断，可安全重试", "retryable": True}  # SPDX-License-Identifier: MIT | 生成标准恢复错误对象。
        error_json = self._json(error_payload)  # SPDX-License-Identifier: MIT | 序列化恢复错误供运行表保存。
        recovered = 0  # SPDX-License-Identifier: MIT | 初始化成功恢复数量。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在单一事务恢复未完成运行并追加审计。
            rows = connection.execute("SELECT id FROM runs WHERE status = 'running'").fetchall()  # SPDX-License-Identifier: MIT | 固定本次需要恢复的运行集合。
            for row in rows:  # SPDX-License-Identifier: MIT | 逐个执行条件更新和审计。
                cursor = connection.execute("UPDATE runs SET status = 'failed', error_json = ?, updated_at = ? WHERE id = ? AND status = 'running'", (error_json, now, row["id"]))  # SPDX-License-Identifier: MIT | 只恢复仍处于运行中的任务。
                if cursor.rowcount == 1:  # SPDX-License-Identifier: MIT | 仅为实际发生的状态变化记录事件。
                    self._audit_connection(connection, "run.failed", str(row["id"]), error_payload)  # SPDX-License-Identifier: MIT | 补齐进程中断恢复的运行审计链。
                    recovered += 1  # SPDX-License-Identifier: MIT | 累加已恢复运行数量。
        return recovered  # SPDX-License-Identifier: MIT | 返回恢复运行数量供启动日志使用。

    def _set_error(self, run_id: str, status: str, error: dict[str, Any]) -> None:  # SPDX-License-Identifier: MIT | 原子保存运行错误状态。
        now = self._now()  # SPDX-License-Identifier: MIT | 生成失败更新时间。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在同一事务保存错误和审计。
            cursor = connection.execute("UPDATE runs SET status = ?, error_json = ?, report_json = NULL, updated_at = ? WHERE id = ? AND status = 'running'", (status, self._json(error), now, run_id))  # SPDX-License-Identifier: MIT | 只允许处理中运行转入错误终态且不带伪报告。
            if cursor.rowcount != 1:  # SPDX-License-Identifier: MIT | 拒绝不存在运行或终态覆盖。
                raise ValueError("只有 running 状态可以写入失败或创作者行动")  # SPDX-License-Identifier: MIT | 返回明确状态机约束。
            self._audit_connection(connection, f"run.{status}", run_id, error)  # SPDX-License-Identifier: MIT | 记录失败或创作者行动审计。

    def _initialize(self) -> None:  # SPDX-License-Identifier: MIT | 创建单机 MVP 数据表和索引。
        with self._connect() as connection:  # SPDX-License-Identifier: MIT | 在首次连接中应用幂等 DDL。
            connection.execute("PRAGMA journal_mode = WAL")  # SPDX-License-Identifier: MIT | 仅在初始化时启用 WAL，避免并发请求重复切换日志模式造成锁竞争。
            connection.execute("CREATE TABLE IF NOT EXISTS submissions(id TEXT PRIMARY KEY, project_id TEXT NOT NULL, project_version TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL)")  # SPDX-License-Identifier: MIT | 创建提交版本表。
            connection.execute("CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, project_id TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL)")  # SPDX-License-Identifier: MIT | 创建隔离资料元数据表。
            connection.execute("CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, submission_id TEXT NOT NULL REFERENCES submissions(id), status TEXT NOT NULL, attempt INTEGER NOT NULL, report_json TEXT, error_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")  # SPDX-License-Identifier: MIT | 创建可恢复 Agent 运行表。
            connection.execute("CREATE TABLE IF NOT EXISTS audit_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL, event_type TEXT NOT NULL, entity_id TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL)")  # SPDX-License-Identifier: MIT | 创建不可覆盖审计事件表。
            connection.execute("CREATE INDEX IF NOT EXISTS idx_runs_submission ON runs(submission_id)")  # SPDX-License-Identifier: MIT | 加速按提交读取运行历史。
            connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_id, sequence)")  # SPDX-License-Identifier: MIT | 加速按实体读取审计时间线。

    @contextmanager  # SPDX-License-Identifier: MIT | 将连接生命周期限定在单次数据库操作内。
    def _connect(self) -> Iterator[sqlite3.Connection]:  # SPDX-License-Identifier: MIT | 创建并在使用后关闭数据库连接。
        connection = sqlite3.connect(self.database_path, timeout=10)  # SPDX-License-Identifier: MIT | 创建具有锁等待上限的连接。
        connection.row_factory = sqlite3.Row  # SPDX-License-Identifier: MIT | 允许按列名读取查询结果。
        connection.execute("PRAGMA foreign_keys = ON")  # SPDX-License-Identifier: MIT | 强制运行引用有效提交。
        try:  # SPDX-License-Identifier: MIT | 保证成功提交、异常回滚并最终释放文件句柄。
            with connection:  # SPDX-License-Identifier: MIT | 使用 SQLite 原生事务上下文管理提交和回滚。
                yield connection  # SPDX-License-Identifier: MIT | 向单次仓库操作提供已配置连接。
        finally:  # SPDX-License-Identifier: MIT | 无论操作成功或失败都执行资源清理。
            connection.close()  # SPDX-License-Identifier: MIT | 显式释放 Windows 数据库文件句柄。

    def _audit_connection(self, connection: sqlite3.Connection, event_type: str, entity_id: str, payload: dict[str, Any]) -> None:  # SPDX-License-Identifier: MIT | 在调用方事务中追加审计事件。
        connection.execute("INSERT INTO audit_events(id, event_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?)", (f"aud_{uuid.uuid4().hex}", event_type, entity_id, self._json(payload), self._now()))  # SPDX-License-Identifier: MIT | 追加不可覆盖审计事实。

    def _json(self, payload: Any) -> str:  # SPDX-License-Identifier: MIT | 生成稳定 UTF-8 JSON 文本。
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))  # SPDX-License-Identifier: MIT | 规范化对象便于比较和审计。

    def _now(self) -> str:  # SPDX-License-Identifier: MIT | 生成带时区 UTC 时间字符串。
        return datetime.now(timezone.utc).isoformat()  # SPDX-License-Identifier: MIT | 返回 ISO 8601 UTC 时间。
