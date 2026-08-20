"""评分 Agent 与人才能力 Agent 的端到端能力推荐示例。"""  # SPDX-License-Identifier: MIT | 描述示例用途。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
import json  # SPDX-License-Identifier: MIT | 读取提交并输出推荐摘要。
from pathlib import Path  # SPDX-License-Identifier: MIT | 安全定位示例文件。
from game_rating_agent import CapabilityRecord, CreatorAssessmentPipeline, InMemoryTalentCapabilityAgent, TalentProfile  # SPDX-License-Identifier: MIT | 导入跨 Agent 公共合同。
from game_rating_agent.diagnosis import DiagnosticPlanner  # SPDX-License-Identifier: MIT | 注入人才能力 Agent 网关。

ROOT = Path(__file__).resolve().parent  # SPDX-License-Identifier: MIT | 获取示例目录绝对路径。
PROFILES = (  # SPDX-License-Identifier: MIT | 构造已通过人才能力 Agent 认证的种子档案。
    TalentProfile("talent-qa", "循证测试者", (CapabilityRecord("qa.game_test_plan", "L3", ("pc", "unity"), ("assessment-101", "integration-44"), True, "2030-12-31", 0.94, "CAP-RUBRIC-2.0"), CapabilityRecord("qa.repro_regression", "L2", ("pc",), ("assessment-102",), True, "2030-12-31", 0.91, "CAP-RUBRIC-2.0"), CapabilityRecord("qa.platform_compatibility", "L2", ("windows",), ("assessment-103",), False, "2030-12-31", 0.88, "CAP-RUBRIC-2.0")), ("cash", "revenue_share"), True),  # SPDX-License-Identifier: MIT | 定义覆盖三项 QA 能力的人才。
    TalentProfile("talent-audio", "声音构筑者", (CapabilityRecord("audio.interactive_feedback", "L3", ("wwise", "unity"), ("assessment-201",), True, "2030-12-31", 0.96, "CAP-RUBRIC-2.0"), CapabilityRecord("audio.engine_integration", "L2", ("unity",), ("assessment-202",), True, "2030-12-31", 0.92, "CAP-RUBRIC-2.0")), ("cash",), True),  # SPDX-License-Identifier: MIT | 定义覆盖两项音频能力的人才。
)  # SPDX-License-Identifier: MIT | 种子人才档案结束。

def main() -> None:  # SPDX-License-Identifier: MIT | 执行跨 Agent 能力推荐示例。
    submission = json.loads((ROOT / "creator_submission.json").read_text(encoding="utf-8"))  # SPDX-License-Identifier: MIT | 读取创作者完整提交。
    submission["questionnaire"]["collaboration_preferences"] = {"value": ["cash", "revenue_share"], "source": "creator", "confidence": 1.0, "evidence_refs": [], "creator_confirmed": True}  # SPDX-License-Identifier: MIT | 声明项目可接受的合作方式。
    capability_agent = InMemoryTalentCapabilityAgent(PROFILES)  # SPDX-License-Identifier: MIT | 创建人才能力 Agent 参考实现。
    planner = DiagnosticPlanner(capability_gateway=capability_agent)  # SPDX-License-Identifier: MIT | 连接评分诊断与人才能力网关。
    report = CreatorAssessmentPipeline(planner=planner).run(submission)  # SPDX-License-Identifier: MIT | 执行上传到人才推荐的完整链路。
    output = ROOT / "talent_match.report.json"  # SPDX-License-Identifier: MIT | 定义跨 Agent 报告输出路径。
    output.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")  # SPDX-License-Identifier: MIT | 保存含能力包和候选解释的完整报告。
    print(json.dumps({"capability_count": len(report.capability_requirements), "recommendations": [item.display_name for item in report.talent_match.recommendations], "output": str(output)}, ensure_ascii=False))  # SPDX-License-Identifier: MIT | 输出便于审核的执行摘要。

if __name__ == "__main__":  # SPDX-License-Identifier: MIT | 仅在直接执行示例时启动。
    main()  # SPDX-License-Identifier: MIT | 运行跨 Agent 能力推荐示例。
