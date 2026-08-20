"""游戏评分 Agent 命令行入口。"""  # SPDX-License-Identifier: MIT | 描述模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
import argparse  # SPDX-License-Identifier: MIT | 解析命令行参数。
import json  # SPDX-License-Identifier: MIT | 读取项目输入并输出报告。
from pathlib import Path  # SPDX-License-Identifier: MIT | 安全处理本地输入路径。
from .agent import GameRatingAgent  # SPDX-License-Identifier: MIT | 调用评分 Agent 内核。

def main() -> int:  # SPDX-License-Identifier: MIT | 执行命令行评分流程。
    parser = argparse.ArgumentParser(description="运行 GameForge 游戏评分 Agent")  # SPDX-License-Identifier: MIT | 创建命令行解析器。
    parser.add_argument("input", type=Path, help="UTF-8 JSON 项目表单路径")  # SPDX-License-Identifier: MIT | 接收待评分项目文件。
    parser.add_argument("--output", type=Path, help="可选的 JSON 报告输出路径")  # SPDX-License-Identifier: MIT | 支持保存结构化报告。
    args = parser.parse_args()  # SPDX-License-Identifier: MIT | 解析用户参数。
    project = json.loads(args.input.read_text(encoding="utf-8"))  # SPDX-License-Identifier: MIT | 读取并解析本地 UTF-8 JSON。
    result = GameRatingAgent().run(project).to_dict()  # SPDX-License-Identifier: MIT | 执行离线可复现评分。
    report = json.dumps(result, ensure_ascii=False, indent=2)  # SPDX-License-Identifier: MIT | 生成便于审核的 JSON 文本。
    if args.output:  # SPDX-License-Identifier: MIT | 仅在用户指定时写入报告文件。
        args.output.write_text(report + "\n", encoding="utf-8")  # SPDX-License-Identifier: MIT | 以 UTF-8 保存结构化报告。
    else:  # SPDX-License-Identifier: MIT | 未指定输出路径时写到标准输出。
        print(report)  # SPDX-License-Identifier: MIT | 便于管道或人工查看结果。
    return 0  # SPDX-License-Identifier: MIT | 表示命令成功完成。

if __name__ == "__main__":  # SPDX-License-Identifier: MIT | 仅在直接执行模块时启动 CLI。
    raise SystemExit(main())  # SPDX-License-Identifier: MIT | 将返回值传递给操作系统。
