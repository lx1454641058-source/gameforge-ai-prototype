"""创作者上传到完整诊断报告的端到端流水线。"""  # SPDX-License-Identifier: MIT | 描述编排模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容提交。
from .agent import GameRatingAgent  # SPDX-License-Identifier: MIT | 调用确定性评分内核。
from .diagnosis import CreatorDiagnosticReport, DiagnosticPlanner  # SPDX-License-Identifier: MIT | 调用后续诊断规划器。
from .intake import PreparedSubmission, SubmissionPreparer  # SPDX-License-Identifier: MIT | 调用上传和问卷准备器。

class CreatorAssessmentPipeline:  # SPDX-License-Identifier: MIT | 编排上传、问卷、评分和行动路线。
    def __init__(self, preparer: SubmissionPreparer | None = None, agent: GameRatingAgent | None = None, planner: DiagnosticPlanner | None = None) -> None:  # SPDX-License-Identifier: MIT | 支持替换各阶段实现。
        self.preparer = preparer or SubmissionPreparer()  # SPDX-License-Identifier: MIT | 默认使用严格问卷确认门槛。
        self.agent = agent or GameRatingAgent()  # SPDX-License-Identifier: MIT | 默认使用离线可回归评分内核。
        self.planner = planner or DiagnosticPlanner()  # SPDX-License-Identifier: MIT | 默认使用规则化诊断规划器。

    def run(self, submission: dict[str, Any]) -> CreatorDiagnosticReport:  # SPDX-License-Identifier: MIT | 执行端到端创作者诊断。
        prepared = self.preparer.prepare(submission)  # SPDX-License-Identifier: MIT | 验证上传资料和创作者确认状态。
        rating = self.agent.run(prepared.normalized_project)  # SPDX-License-Identifier: MIT | 对冻结输入运行 D、C、B_GATE 评分。
        return self.planner.build(prepared.normalized_project, rating)  # SPDX-License-Identifier: MIT | 将评分转化为制作和上架行动路线。

    def prepare_only(self, submission: dict[str, Any]) -> PreparedSubmission:  # SPDX-License-Identifier: MIT | 暴露评分前问卷和资料检查能力。
        return self.preparer.prepare(submission)  # SPDX-License-Identifier: MIT | 返回规范化输入供产品展示和确认。
