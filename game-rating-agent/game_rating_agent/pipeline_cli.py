"""创作者提交到完整诊断报告的命令行入口。"""  # SPDX-License-Identifier: MIT | 描述端到端 CLI 职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
import argparse  # SPDX-License-Identifier: MIT | 解析命令行参数。
import json  # SPDX-License-Identifier: MIT | 读取提交并输出诊断报告。
from pathlib import Path  # SPDX-License-Identifier: MIT | 安全处理本地文件路径。
from .intake import SubmissionNotReadyError  # SPDX-License-Identifier: MIT | 输出评分前确认问题。
from .pipeline import CreatorAssessmentPipeline  # SPDX-License-Identifier: MIT | 调用完整创作者诊断流水线。

def main() -> int:  # SPDX-License-Identifier: MIT | 执行端到端诊断命令。
    parser = argparse.ArgumentParser(description="运行 GameForge 创作者游戏诊断流水线")  # SPDX-License-Identifier: MIT | 创建命令行解析器。
    parser.add_argument("submission", type=Path, help="包含资料清单和问卷的 UTF-8 JSON")  # SPDX-License-Identifier: MIT | 接收完整创作者提交文件。
    parser.add_argument("--output", type=Path, required=True, help="完整诊断报告 JSON 输出路径")  # SPDX-License-Identifier: MIT | 要求明确保存完整报告。
    args = parser.parse_args()  # SPDX-License-Identifier: MIT | 解析用户参数。
    submission = json.loads(args.submission.read_text(encoding="utf-8"))  # SPDX-License-Identifier: MIT | 读取并解析创作者提交。
    try:  # SPDX-License-Identifier: MIT | 捕获评分前确认阻塞并返回结构化错误。
        report = CreatorAssessmentPipeline().run(submission).to_dict()  # SPDX-License-Identifier: MIT | 执行上传、问卷、评分和诊断。
    except SubmissionNotReadyError as error:  # SPDX-License-Identifier: MIT | 处理尚未满足评分条件的提交。
        print(json.dumps({"status": "needs_creator_action", "issues": error.issues}, ensure_ascii=False, indent=2))  # SPDX-License-Identifier: MIT | 告知创作者需要补充或确认的内容。
        return 2  # SPDX-License-Identifier: MIT | 使用独立退出码表示可修复的输入阻塞。
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")  # SPDX-License-Identifier: MIT | 保存完整 UTF-8 诊断报告。
    print(json.dumps({"status": "completed", "result": report["rating"]["assessment_result"], "output": str(args.output)}, ensure_ascii=False))  # SPDX-License-Identifier: MIT | 输出便于自动化读取的完成摘要。
    return 0  # SPDX-License-Identifier: MIT | 表示端到端诊断成功完成。

if __name__ == "__main__":  # SPDX-License-Identifier: MIT | 仅在直接执行模块时启动 CLI。
    raise SystemExit(main())  # SPDX-License-Identifier: MIT | 将返回值传递给操作系统。
