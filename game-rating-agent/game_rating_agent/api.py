"""无第三方依赖的本地 MVP HTTP API。"""  # SPDX-License-Identifier: MIT | 描述服务接口职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from http import HTTPStatus  # SPDX-License-Identifier: MIT | 使用标准 HTTP 状态码。
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # SPDX-License-Identifier: MIT | 提供并发本地 JSON API。
from pathlib import Path  # SPDX-License-Identifier: MIT | 配置应用数据目录。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 请求和响应对象。
from urllib.parse import urlparse  # SPDX-License-Identifier: MIT | 安全解析请求路径而不处理外部 URL。
import argparse  # SPDX-License-Identifier: MIT | 解析服务启动参数。
import hmac  # SPDX-License-Identifier: MIT | 使用恒定时间比较 Bearer Token。
import json  # SPDX-License-Identifier: MIT | 读取和输出 JSON 请求。
import os  # SPDX-License-Identifier: MIT | 读取 API Token 和数据目录环境配置。
from .artifacts import ArtifactValidationError  # SPDX-License-Identifier: MIT | 映射安全上传错误到 400。
from .service import GameRatingApplicationService  # SPDX-License-Identifier: MIT | 调用完整应用服务。

MAX_REQUEST_BYTES = 140 * 1024 * 1024  # SPDX-License-Identifier: MIT | 覆盖 100MB 文件 Base64 后的请求体并限制资源占用。
SERVICE_VERSION = "1.1.0"  # SPDX-License-Identifier: MIT | 标记产品可实现性、分层成长反馈和中文新手界面升级。
FRONTEND_ROOT = Path(__file__).with_name("frontend")  # SPDX-License-Identifier: MIT | 将同源前端静态资源定位到包内固定目录。
STATIC_ROUTES = {"/": ("index.html", "text/html; charset=utf-8"), "/index.html": ("index.html", "text/html; charset=utf-8"), "/styles.css": ("styles.css", "text/css; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8")}  # SPDX-License-Identifier: MIT | 只公开明确登记的前端静态文件。

class GameRatingRequestHandler(BaseHTTPRequestHandler):  # SPDX-License-Identifier: MIT | 路由问卷、上传、运行和审计 API。
    service: GameRatingApplicationService  # SPDX-License-Identifier: MIT | 由服务启动器注入共享应用服务。
    api_token: str  # SPDX-License-Identifier: MIT | 由环境或启动参数注入 Bearer Token。
    server_version = f"GameForgeRatingAgent/{SERVICE_VERSION}"  # SPDX-License-Identifier: MIT | 设置不包含 Python 版本的最小服务标识。
    sys_version = ""  # SPDX-License-Identifier: MIT | 避免默认响应暴露运行时版本。

    def do_GET(self) -> None:  # SPDX-License-Identifier: MIT | 处理健康、问卷、运行和审计读取。
        try:  # SPDX-License-Identifier: MIT | 将领域错误统一映射为 JSON 响应。
            path = urlparse(self.path).path  # SPDX-License-Identifier: MIT | 在鉴权前解析路径以允许加载不含数据的前端外壳。
            if path in STATIC_ROUTES:  # SPDX-License-Identifier: MIT | 只为登记静态路由提供前端文件。
                self._static_response(*STATIC_ROUTES[path])  # SPDX-License-Identifier: MIT | 返回同源前端并保持 API 令牌由用户输入。
                return  # SPDX-License-Identifier: MIT | 静态资源响应完成后停止路由。
            if not self._authorized():  # SPDX-License-Identifier: MIT | 所有接口包括健康检查都需要令牌。
                return  # SPDX-License-Identifier: MIT | 未授权响应已经发送。
            if path == "/health":  # SPDX-License-Identifier: MIT | 提供服务存活和版本信息。
                self._json_response(HTTPStatus.OK, {"status": "ok", "service": "game-rating-agent", "version": SERVICE_VERSION})  # SPDX-License-Identifier: MIT | 返回不含敏感配置的健康信息。
                return  # SPDX-License-Identifier: MIT | 健康检查路由结束。
            if path == "/v1/questionnaire":  # SPDX-License-Identifier: MIT | 返回客户端可渲染问卷。
                self._json_response(HTTPStatus.OK, self.service.get_questionnaire())  # SPDX-License-Identifier: MIT | 返回版本化问卷合同。
                return  # SPDX-License-Identifier: MIT | 问卷路由结束。
            if path == "/v1/knowledge-base":  # SPDX-License-Identifier: MIT | 返回游戏类型基线和评分逻辑。
                self._json_response(HTTPStatus.OK, self.service.get_knowledge_base())  # SPDX-License-Identifier: MIT | 返回版本化只读知识库合同。
                return  # SPDX-License-Identifier: MIT | 知识库读取路由结束。
            segments = [segment for segment in path.split("/") if segment]  # SPDX-License-Identifier: MIT | 将路径拆为非空段。
            if len(segments) == 3 and segments[:2] == ["v1", "runs"]:  # SPDX-License-Identifier: MIT | 匹配单个运行读取接口。
                result = self.service.get_run(segments[2])  # SPDX-License-Identifier: MIT | 读取持久化运行状态。
                self._json_response(HTTPStatus.OK if result else HTTPStatus.NOT_FOUND, result or {"error": "run_not_found"})  # SPDX-License-Identifier: MIT | 返回运行或 404。
                return  # SPDX-License-Identifier: MIT | 运行读取路由结束。
            if len(segments) == 4 and segments[:2] == ["v1", "runs"] and segments[3] == "audit":  # SPDX-License-Identifier: MIT | 匹配运行审计读取接口。
                if self.service.get_run(segments[2]) is None:  # SPDX-License-Identifier: MIT | 审计接口先确认运行确实存在。
                    self._json_response(HTTPStatus.NOT_FOUND, {"error": "run_not_found"})  # SPDX-License-Identifier: MIT | 未知运行返回一致的 404。
                    return  # SPDX-License-Identifier: MIT | 不把空事件列表伪装为存在的运行。
                self._json_response(HTTPStatus.OK, {"run_id": segments[2], "events": self.service.repository.list_audit(segments[2])})  # SPDX-License-Identifier: MIT | 返回完整运行审计时间线。
                return  # SPDX-License-Identifier: MIT | 审计路由结束。
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "route_not_found"})  # SPDX-License-Identifier: MIT | 拒绝未知 GET 路由。
        except Exception as error:  # SPDX-License-Identifier: MIT | 防止未处理异常中断工作线程。
            self._handle_error(error)  # SPDX-License-Identifier: MIT | 返回最小结构化错误。

    def do_POST(self) -> None:  # SPDX-License-Identifier: MIT | 处理上传、问卷代填、提交、运行和履约回写。
        try:  # SPDX-License-Identifier: MIT | 将领域错误统一映射为 JSON 响应。
            if not self._authorized():  # SPDX-License-Identifier: MIT | 在读取请求体前完成鉴权。
                return  # SPDX-License-Identifier: MIT | 未授权响应已经发送。
            path = urlparse(self.path).path  # SPDX-License-Identifier: MIT | 解析不含查询字符串的请求路径。
            payload = self._read_json()  # SPDX-License-Identifier: MIT | 在大小限制内读取 JSON 请求。
            if path == "/v1/artifacts":  # SPDX-License-Identifier: MIT | 接收方案、图片、视频或 Demo 文件。
                self._json_response(HTTPStatus.CREATED, self.service.ingest_artifact_base64(payload))  # SPDX-License-Identifier: MIT | 返回安全资料元数据。
                return  # SPDX-License-Identifier: MIT | 资料上传路由结束。
            if path == "/v1/questionnaire/prefill":  # SPDX-License-Identifier: MIT | 使用隔离资料生成待确认问卷草稿。
                artifact_ids = tuple(str(item) for item in payload.get("artifact_ids", []))  # SPDX-License-Identifier: MIT | 读取明确资料引用列表。
                creator_values = payload.get("creator_values") if isinstance(payload.get("creator_values"), dict) else {}  # SPDX-License-Identifier: MIT | 读取不可被 AI 覆盖的创作者事实。
                self._json_response(HTTPStatus.OK, self.service.prefill_by_artifact_ids(artifact_ids, creator_values))  # SPDX-License-Identifier: MIT | 返回带来源、置信度和确认状态的草稿。
                return  # SPDX-License-Identifier: MIT | 问卷代填路由结束。
            if path == "/v1/submissions":  # SPDX-License-Identifier: MIT | 保存创作者确认后的提交版本。
                submission_id = self.service.submit(payload)  # SPDX-License-Identifier: MIT | 持久化完整提交快照。
                self._json_response(HTTPStatus.CREATED, {"submission_id": submission_id})  # SPDX-License-Identifier: MIT | 返回提交标识。
                return  # SPDX-License-Identifier: MIT | 提交创建路由结束。
            if path == "/v1/runs":  # SPDX-License-Identifier: MIT | 创建并执行一次评分诊断运行。
                run_id = self.service.create_and_execute_run(str(payload.get("submission_id") or ""))  # SPDX-License-Identifier: MIT | 创建持久化运行并同步执行。
                self._json_response(HTTPStatus.CREATED, self.service.get_run(run_id) or {"run_id": run_id})  # SPDX-License-Identifier: MIT | 返回终态或运行标识。
                return  # SPDX-License-Identifier: MIT | 运行创建路由结束。
            if path == "/v1/capability-feedback":  # SPDX-License-Identifier: MIT | 将实际项目履约回写人才能力 Agent。
                self._json_response(HTTPStatus.OK, self.service.record_fulfillment(payload))  # SPDX-License-Identifier: MIT | 返回幂等能力反馈回执。
                return  # SPDX-License-Identifier: MIT | 履约回写路由结束。
            segments = [segment for segment in path.split("/") if segment]  # SPDX-License-Identifier: MIT | 将动态路由拆为路径段。
            if len(segments) == 4 and segments[:2] == ["v1", "runs"] and segments[3] == "retry":  # SPDX-License-Identifier: MIT | 匹配失败运行重试接口。
                self.service.retry_run(segments[2])  # SPDX-License-Identifier: MIT | 重新执行冻结提交且不覆盖完成报告。
                self._json_response(HTTPStatus.OK, self.service.get_run(segments[2]) or {"run_id": segments[2]})  # SPDX-License-Identifier: MIT | 返回重试后的运行状态。
                return  # SPDX-License-Identifier: MIT | 运行重试路由结束。
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "route_not_found"})  # SPDX-License-Identifier: MIT | 拒绝未知 POST 路由。
        except Exception as error:  # SPDX-License-Identifier: MIT | 防止未处理异常中断工作线程。
            self._handle_error(error)  # SPDX-License-Identifier: MIT | 返回最小结构化错误。

    def _authorized(self) -> bool:  # SPDX-License-Identifier: MIT | 验证 Bearer Token 而不记录令牌值。
        header = self.headers.get("Authorization", "")  # SPDX-License-Identifier: MIT | 读取授权请求头。
        expected = f"Bearer {self.api_token}"  # SPDX-License-Identifier: MIT | 构造当前服务期望值。
        if not self.api_token or not hmac.compare_digest(header.encode("utf-8"), expected.encode("utf-8")):  # SPDX-License-Identifier: MIT | 以恒定时间比较令牌并拒绝缺失服务令牌。
            self._json_response(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})  # SPDX-License-Identifier: MIT | 返回不泄露鉴权细节的 401。
            return False  # SPDX-License-Identifier: MIT | 通知路由停止处理。
        return True  # SPDX-License-Identifier: MIT | 允许处理已授权请求。

    def _read_json(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 在请求体上限内解析 JSON 对象。
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()  # SPDX-License-Identifier: MIT | 读取并规范请求媒体类型。
        if content_type != "application/json":  # SPDX-License-Identifier: MIT | 所有 POST 路由都使用严格 JSON 合同。
            raise ValueError("Content-Type 必须是 application/json")  # SPDX-License-Identifier: MIT | 阻止类型混淆请求。
        raw_length = self.headers.get("Content-Length")  # SPDX-License-Identifier: MIT | 读取请求声明长度。
        if raw_length is None:  # SPDX-License-Identifier: MIT | POST 请求必须明确长度避免无限读取。
            raise ValueError("缺少 Content-Length")  # SPDX-License-Identifier: MIT | 返回客户端请求错误。
        length = int(raw_length)  # SPDX-License-Identifier: MIT | 将长度转换为整数。
        if length < 0 or length > MAX_REQUEST_BYTES:  # SPDX-License-Identifier: MIT | 限制负数和超大请求体。
            raise ArtifactValidationError("请求体超过大小限制")  # SPDX-License-Identifier: MIT | 返回安全资源限制错误。
        raw = self.rfile.read(length)  # SPDX-License-Identifier: MIT | 只读取声明且受限的字节数量。
        payload = json.loads(raw.decode("utf-8"))  # SPDX-License-Identifier: MIT | 使用 UTF-8 解析 JSON。
        if not isinstance(payload, dict):  # SPDX-License-Identifier: MIT | 所有 API 请求必须是 JSON 对象。
            raise ValueError("请求 JSON 必须是对象")  # SPDX-License-Identifier: MIT | 返回明确客户端错误。
        return payload  # SPDX-License-Identifier: MIT | 返回结构化请求对象。

    def _json_response(self, status: HTTPStatus, payload: Any) -> None:  # SPDX-License-Identifier: MIT | 输出统一 UTF-8 JSON 响应。
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")  # SPDX-License-Identifier: MIT | 序列化响应而不输出内部对象表示。
        self.send_response(status.value)  # SPDX-License-Identifier: MIT | 写入 HTTP 状态行。
        self.send_header("Content-Type", "application/json; charset=utf-8")  # SPDX-License-Identifier: MIT | 声明 JSON 和 UTF-8 编码。
        self.send_header("Content-Length", str(len(data)))  # SPDX-License-Identifier: MIT | 声明响应体准确长度。
        self.send_header("Cache-Control", "no-store")  # SPDX-License-Identifier: MIT | 防止评分和项目数据被客户端缓存。
        self.send_header("X-Content-Type-Options", "nosniff")  # SPDX-License-Identifier: MIT | 防止响应内容类型嗅探。
        self.end_headers()  # SPDX-License-Identifier: MIT | 结束响应头。
        self.wfile.write(data)  # SPDX-License-Identifier: MIT | 写入 JSON 响应体。

    def _static_response(self, filename: str, content_type: str) -> None:  # SPDX-License-Identifier: MIT | 返回包内白名单前端资源。
        target = (FRONTEND_ROOT / filename).resolve()  # SPDX-License-Identifier: MIT | 解析固定文件名对应的绝对资源路径。
        if FRONTEND_ROOT.resolve() not in target.parents or not target.is_file():  # SPDX-License-Identifier: MIT | 防止路径逃逸并处理缺失构建资源。
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "frontend_asset_not_found"})  # SPDX-License-Identifier: MIT | 返回不泄露内部路径的 404。
            return  # SPDX-License-Identifier: MIT | 资源缺失时停止响应。
        data = target.read_bytes()  # SPDX-License-Identifier: MIT | 读取只读静态资源字节。
        self.send_response(HTTPStatus.OK.value)  # SPDX-License-Identifier: MIT | 写入静态资源成功状态。
        self.send_header("Content-Type", content_type)  # SPDX-License-Identifier: MIT | 声明登记资源的准确媒体类型。
        self.send_header("Content-Length", str(len(data)))  # SPDX-License-Identifier: MIT | 声明响应体准确长度。
        self.send_header("Cache-Control", "no-store")  # SPDX-License-Identifier: MIT | 防止共享设备缓存项目操作界面。
        self.send_header("X-Content-Type-Options", "nosniff")  # SPDX-License-Identifier: MIT | 禁止浏览器猜测资源类型。
        self.send_header("X-Frame-Options", "DENY")  # SPDX-License-Identifier: MIT | 阻止前端被第三方页面框架嵌入。
        self.send_header("Referrer-Policy", "no-referrer")  # SPDX-License-Identifier: MIT | 防止本地地址通过引用头外泄。
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")  # SPDX-License-Identifier: MIT | 限制前端只加载和连接同源资源。
        self.end_headers()  # SPDX-License-Identifier: MIT | 结束静态资源响应头。
        self.wfile.write(data)  # SPDX-License-Identifier: MIT | 写入静态资源内容。

    def _handle_error(self, error: Exception) -> None:  # SPDX-License-Identifier: MIT | 将已知领域错误映射为安全 HTTP 状态。
        if isinstance(error, KeyError):  # SPDX-License-Identifier: MIT | 未知提交、资料或运行属于资源不存在。
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found", "message": str(error)})  # SPDX-License-Identifier: MIT | 返回 404 领域错误。
        elif isinstance(error, (ArtifactValidationError, ValueError, json.JSONDecodeError, UnicodeDecodeError)):  # SPDX-License-Identifier: MIT | 上传、编码或 JSON 问题属于客户端错误。
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "invalid_request", "message": str(error)})  # SPDX-License-Identifier: MIT | 返回 400 且不含堆栈。
        elif isinstance(error, RuntimeError):  # SPDX-License-Identifier: MIT | 未配置模型或能力网关属于服务能力不可用。
            self._json_response(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "service_unavailable", "message": str(error)})  # SPDX-License-Identifier: MIT | 返回 503 集成错误。
        else:  # SPDX-License-Identifier: MIT | 未知错误不向客户端泄露内部细节。
            self._json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "internal_error"})  # SPDX-License-Identifier: MIT | 返回最小 500 响应。

    def log_message(self, format_string: str, *args: Any) -> None:  # SPDX-License-Identifier: MIT | 限制本地开发日志不输出请求头和正文。
        print(f"{self.address_string()} - {format_string % args}")  # SPDX-License-Identifier: MIT | 只记录地址和标准访问摘要。

def create_server(host: str, port: int, data_root: Path, api_token: str) -> ThreadingHTTPServer:  # SPDX-License-Identifier: MIT | 创建配置完成的本地 HTTP 服务。
    service = GameRatingApplicationService.from_environment(data_root)  # SPDX-License-Identifier: MIT | 初始化上传、问卷、持久化和评分服务。
    handler = type("ConfiguredGameRatingHandler", (GameRatingRequestHandler,), {"service": service, "api_token": api_token})  # SPDX-License-Identifier: MIT | 为当前服务实例绑定依赖。
    return ThreadingHTTPServer((host, port), handler)  # SPDX-License-Identifier: MIT | 返回可启动的并发 HTTP 服务。

def main() -> int:  # SPDX-License-Identifier: MIT | 启动本地 MVP HTTP API。
    parser = argparse.ArgumentParser(description="启动 GameForge 游戏评分 Agent 本地 API")  # SPDX-License-Identifier: MIT | 创建服务启动参数解析器。
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认仅本机")  # SPDX-License-Identifier: MIT | 默认不暴露到局域网或公网。
    parser.add_argument("--port", type=int, default=8765, help="监听端口")  # SPDX-License-Identifier: MIT | 配置本地服务端口。
    parser.add_argument("--data-root", type=Path, default=Path(os.getenv("GAMEFORGE_AGENT_DATA", "./var")), help="数据库和隔离文件目录")  # SPDX-License-Identifier: MIT | 将运行数据默认保存在项目 var 目录。
    parser.add_argument("--api-token", default=os.getenv("GAMEFORGE_AGENT_TOKEN", ""), help="Bearer Token，建议使用环境变量")  # SPDX-License-Identifier: MIT | 支持环境变量注入服务令牌。
    args = parser.parse_args()  # SPDX-License-Identifier: MIT | 解析服务启动参数。
    if len(args.api_token) < 16:  # SPDX-License-Identifier: MIT | 要求非空且难以猜测的最小令牌长度。
        raise SystemExit("GAMEFORGE_AGENT_TOKEN 或 --api-token 至少需要 16 个字符")  # SPDX-License-Identifier: MIT | 拒绝无鉴权启动。
    server = create_server(args.host, args.port, args.data_root, args.api_token)  # SPDX-License-Identifier: MIT | 创建配置完成的本地服务。
    print(f"GameForge 游戏评分 Agent API 已监听 http://{args.host}:{args.port}")  # SPDX-License-Identifier: MIT | 输出不包含令牌的启动地址。
    try:  # SPDX-License-Identifier: MIT | 支持正常键盘中断退出。
        server.serve_forever()  # SPDX-License-Identifier: MIT | 持续处理本地 API 请求。
    except KeyboardInterrupt:  # SPDX-License-Identifier: MIT | 处理用户主动停止服务。
        pass  # SPDX-License-Identifier: MIT | 不输出无意义堆栈。
    finally:  # SPDX-License-Identifier: MIT | 始终关闭监听套接字。
        server.server_close()  # SPDX-License-Identifier: MIT | 释放服务端口。
    return 0  # SPDX-License-Identifier: MIT | 表示服务正常停止。

if __name__ == "__main__":  # SPDX-License-Identifier: MIT | 仅在直接执行模块时启动服务。
    raise SystemExit(main())  # SPDX-License-Identifier: MIT | 将退出码传递给操作系统。
