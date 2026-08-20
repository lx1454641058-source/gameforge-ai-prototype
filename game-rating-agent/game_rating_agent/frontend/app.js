"use strict"; // SPDX-License-Identifier: MIT | 启用严格 JavaScript 语义。
const state = { token: "", questions: [], knowledgeBase: { version: "", profiles: [] }, answers: {}, artifacts: [], runId: "", submissionId: "", run: null }; // SPDX-License-Identifier: MIT | 保存当前标签页内的问卷、知识库与诊断会话状态。
const byId = (id) => document.getElementById(id); // SPDX-License-Identifier: MIT | 提供稳定的元素标识查询助手。
const connectionForm = byId("connectionForm"); // SPDX-License-Identifier: MIT | 缓存连接表单元素。
const apiToken = byId("apiToken"); // SPDX-License-Identifier: MIT | 缓存令牌输入元素。
const projectId = byId("projectId"); // SPDX-License-Identifier: MIT | 缓存项目标识输入元素。
const projectVersion = byId("projectVersion"); // SPDX-License-Identifier: MIT | 缓存项目版本输入元素。
const projectTitle = byId("projectTitle"); // SPDX-License-Identifier: MIT | 缓存项目名称输入元素。
const designFiles = byId("designFiles"); // SPDX-License-Identifier: MIT | 缓存方案资料输入元素。
const demoFiles = byId("demoFiles"); // SPDX-License-Identifier: MIT | 缓存 Demo 文件输入元素。
const artifactList = byId("artifactList"); // SPDX-License-Identifier: MIT | 缓存上传资料列表容器。
const prefillButton = byId("prefillButton"); // SPDX-License-Identifier: MIT | 缓存问卷代填按钮。
const questionList = byId("questionList"); // SPDX-License-Identifier: MIT | 缓存动态问卷容器。
const questionProgress = byId("questionProgress"); // SPDX-License-Identifier: MIT | 缓存问卷进度文本。
const confirmFilledButton = byId("confirmFilledButton"); // SPDX-License-Identifier: MIT | 缓存批量确认按钮。
const runButton = byId("runButton"); // SPDX-License-Identifier: MIT | 缓存运行诊断按钮。
const reportContent = byId("reportContent"); // SPDX-License-Identifier: MIT | 缓存报告内容容器。
const refreshButton = byId("refreshButton"); // SPDX-License-Identifier: MIT | 缓存运行刷新按钮。
const auditButton = byId("auditButton"); // SPDX-License-Identifier: MIT | 缓存审计按钮。
const auditDialog = byId("auditDialog"); // SPDX-License-Identifier: MIT | 缓存审计对话框。
const auditContent = byId("auditContent"); // SPDX-License-Identifier: MIT | 缓存审计事件容器。
const toast = byId("toast"); // SPDX-License-Identifier: MIT | 缓存状态提示容器。
let toastTimer = 0; // SPDX-License-Identifier: MIT | 保存当前提示自动隐藏定时器。
const stageOptions = [["idea", "只有想法"], ["concept", "已有概念方案"], ["pre_prototype", "正在验证核心玩法"], ["prototype", "已有可玩原型"], ["vertical_slice", "已有代表最终品质的试玩片段"], ["alpha", "内部测试版"], ["beta", "公开测试版"], ["release_candidate", "准备发布的候选版本"]]; // SPDX-License-Identifier: MIT | 用创作者能直接判断的自然中文表达服务端制作阶段。
const businessOptions = [["buyout", "买断"], ["iap", "内购"], ["ads", "广告"], ["subscription", "订阅"], ["dlc", "DLC"], ["noncommercial", "非商业"]]; // SPDX-License-Identifier: MIT | 定义服务端支持的商业模式选项。
const objectExamples = { team: { size: 1, roles: ["独立创作者"], availability: "每周 20 小时" }, schedule: { planning_status: "preliminary", months: 12, budget: 500000, available_funding: 200000 }, progression_feedback: { mode: "in_match", in_match_progression: ["经济扩张", "科技升级"], meta_progression: [], feedback_signals: ["单位解锁", "地图控制变化"], decision_tradeoffs: "科技投入会延迟当前兵力", failure_learning: "战报和回放解释失败原因" }, production_feasibility: { scope_bounded: true, technical_path_known: true, platform_constraints_known: true, prototype_validation_plan: true, critical_dependencies: ["引擎性能"], unresolved_high_risks: [], blocking_constraints: [] }, social_competition: { not_applicable_reason: "首版为单人游戏，不需要社交竞争。" }, module_status: { core_design: "in_progress", prototype: "missing", ux: "missing", art: "missing", audio: "missing", qa: "missing", store_assets: "missing", compliance: "missing" } }; // SPDX-License-Identifier: MIT | 提供复杂对象题的可编辑 JSON 示例。
const teamRoleOptions = ["独立创作者", "策划/产品", "程序/技术", "用户体验/交互", "美术", "音频", "测试/质量保障", "发行运营", "合规/隐私"]; // SPDX-License-Identifier: MIT | 使用中文能力名称定义个人与专业团队共用的快速选择项。
const planningStatusOptions = [["not_planned", "尚未规划"], ["preliminary", "已有初步计划"], ["confirmed", "已确认计划"]]; // SPDX-License-Identifier: MIT | 定义投入计划成熟度选项并允许明确回答不知道。
const moduleDefinitions = [["core_design", "核心设计与规则"], ["prototype", "可运行原型"], ["ux", "用户体验与新手引导"], ["art", "美术资产"], ["audio", "音频与反馈"], ["qa", "测试与质量保障"], ["store_assets", "商店素材"], ["compliance", "合规与隐私"]]; // SPDX-License-Identifier: MIT | 定义第十六题全部生产模块的稳定代码与纯中文名称。
const moduleStatusOptions = [["missing", "暂无"], ["planned", "已规划"], ["documented", "已形成文档"], ["in_progress", "进行中"], ["ready", "已完成/可用"], ["validated", "已验证"]]; // SPDX-License-Identifier: MIT | 定义模块状态的渐进式成熟度枚举。
const innovationAxisOptions = [["core_loop", "核心循环"], ["decision_structure", "决策结构"], ["build_interaction", "构筑交互"], ["progression", "成长系统"], ["content_generation", "内容生成"], ["social_structure", "社交结构"], ["value_exchange", "价值交换"], ["presentation", "表现方式"], ["accessibility", "可访问性"]]; // SPDX-License-Identifier: MIT | 定义前后端一致的创新位置代码与中文名称。
const innovationAxisTokens = { ability: "能力", accessibility: "可访问性", agency: "主导权", asymmetry: "不对称", authenticity: "真实性", boss: "首领", build: "构筑", card: "卡牌", career: "生涯", causality: "因果", challenge: "挑战", character: "角色", chart: "谱面", chemistry: "氛围", choice: "选择", collection: "收集", combat: "战斗", comeback: "逆转", condition: "条件", consequence: "后果", construction: "建造", content: "内容", cooperation: "协作", core: "核心", creator: "创作", crisis: "危机", customization: "自定义", decision: "决策", depth: "深度", diplomacy: "外交", discovery: "探索", draft: "选取", driving: "驾驶", economy: "经济", emergence: "涌现", encounter: "遭遇", endgame: "后期", energy: "能量", experience: "体验", expression: "表达", fair: "公平", failure: "失败", fear: "恐惧", feedback: "反馈", feel: "手感", fun: "乐趣", game: "博弈", generation: "生成", goal: "目标", growth: "成长", hero: "英雄", hint: "提示", identity: "特色", information: "信息", input: "操作", interaction: "交互", knowledge: "知识", learning: "学习", level: "关卡", loop: "循环", loot: "战利品", management: "经营", map: "地图", match: "对局", meaningful: "有意义", memory: "记忆", merge: "合成", mission: "任务", movement: "移动", music: "音乐", narrative: "叙事", neutral: "中立博弈", objective: "目标", order: "订单", pacing: "节奏", party: "队伍", player: "玩家", planning: "规划", presentation: "表现", pressure: "压力", progression: "成长", psychological: "心理", raid: "突袭", readability: "可读性", reactivity: "反应", recovery: "恢复", replay: "重复游玩", respect: "尊重", revive: "复活", reward: "奖励", risk: "风险", rivalry: "对抗", round: "回合", route: "路线", rule: "规则", run: "单局", safety: "安全", session: "会话", simulation: "模拟", social: "社交", solution: "解法", spectator: "观战", sport: "体育", story: "故事", structure: "结构", survival: "生存", synergy: "协同", system: "系统", tactics: "战术", team: "团队", teaching: "教学", threat: "威胁", time: "时间", track: "赛道", tradeoff: "取舍", training: "训练", turn: "回合", unit: "单位", urban: "城市", value: "价值", victory: "胜利", world: "世界" }; // SPDX-License-Identifier: MIT | 将类型知识库全部创新位置的组成词转换为中文，防止新手看到下划线英文代码。
const validationMethodOptions = [["playtest", "目标玩家试玩"], ["interview", "玩家访谈"], ["survey", "结构化问卷"], ["telemetry", "行为数据埋点"], ["prototype_comparison", "两版原型对比"], ["market_test", "小规模市场测试"]]; // SPDX-License-Identifier: MIT | 用自然中文定义差异化验证方式并隐藏技术缩写。
const dimensionNames = { core_loop: "核心循环", first_attraction: "首次吸引", sustained_motivation: "持续动机", progression_feedback: "成长反馈", content_structure: "内容结构", social_competition: "社交竞争", value_exchange: "价值交换", feasibility: "产品可实现性", innovation_candidate: "创新候选" }; // SPDX-License-Identifier: MIT | 将九维代码映射为中文名称并区分产品实现与资源准备。
const featureNames = { ability_gating: "能力解锁区域", aim_combat: "瞄准射击", auto_battle: "自动战斗", backtracking: "获得能力后返回旧区域", base_building: "基地建设", base_destruction: "摧毁敌方基地", beat_timing: "节拍操作", boss_encounter: "首领战", boss_learning: "通过失败学习首领机制", branching_story: "分支剧情", card_draw: "抽牌", character_growth: "角色成长", character_interaction: "角色互动", character_route: "角色路线", checkpoint: "检查点", checkpoint_loss: "死亡损失与检查点", city_growth: "城市发展", collection_progress: "收集进度", combo: "连招", competitive_match: "竞技对局", crafting: "制作合成", creative_tools: "创作工具", daily_tasks: "每日任务", deck_building: "牌组构筑", dialogue: "对话", dialogue_choice: "对话选择", difficulty_curve: "难度曲线", difficulty_levels: "难度分级", dodge_timing: "闪避时机", economy_stash: "局外仓库经济", emergent_events: "系统涌现事件", encounter_choice: "遭遇选择", endgame_loop: "后期循环", ending_collection: "结局收集", enemy_farming: "刷怪获取资源", energy_cost: "能量费用", energy_limit: "行动能量限制", environmental_exploration: "环境探索", environmental_story: "环境叙事", expand: "领土扩张", expansion: "经营扩张", exploit: "资源利用", exploration: "探索", explore: "地图探索", exterminate: "消灭对手", feedback_loop: "操作反馈循环", grid_positioning: "网格站位", hero_collection: "角色收集", hero_roles: "英雄分工", infrastructure: "基础设施", interconnected_map: "互联地图", item_build: "装备构筑", jump_control: "跳跃控制", jump_scare: "惊吓触发", lane_control: "兵线控制", lap_competition: "圈速竞争", large_match: "大规模对局", last_team_standing: "最后存活队伍", level_sequence: "关卡序列", limited_resources: "有限资源决策", loadout: "战前配置", local_or_online_multiplayer: "本地或在线多人", loot_extraction: "携带战利品撤离", loot_hunt: "战利品追求", loot_search: "搜索物资", loss_on_death: "死亡损失", match_rules: "比赛规则", matchmaking: "匹配", merge_items: "物品合成", minigames: "小游戏组合", mission_objective: "任务目标", move_list: "招式表", movement_challenge: "移动挑战", note_chart: "音符谱面", offline_rewards: "离线收益", open_ended_goals: "开放目标", open_world_exploration: "开放世界探索", optimization: "经营优化", party_members: "队伍成员", performance_score: "表现评分", permadeath: "单局死亡重置", player_agency: "玩家自主选择", population_management: "人口管理", power_growth: "战力成长", precision_timing: "精确时机", problem_solving: "问题求解", production_chain: "生产链", pvpve: "玩家与环境混合对抗", quest_progression: "任务推进", race_track: "赛道", raid_session: "突袭对局", randomized_builds: "随机构筑", reading_progression: "阅读推进", real_time_combat: "即时战斗", resource_flow: "资源流转", resource_gathering: "资源采集", resource_management: "资源管理", round_match: "回合对战", rule_learning: "规则学习", run_based: "单局跑局", season_progression: "赛季进程", short_round: "短回合", short_session: "短时体验", shrinking_zone: "安全区收缩", simple_controls: "简单操作", skill_build: "技能构筑", skill_timing: "技能时机", social_reaction: "社交反应", song_selection: "歌曲选择", spacing: "距离控制", staff_management: "人员管理", stamina_combat: "精力战斗", story_chapters: "剧情章节", survival_meter: "生存指标", system_simulation: "系统模拟", task_order: "任务排序", team_control: "队伍控制", team_objective: "团队目标", teamfight: "团战", technology_tree: "科技树", tension_cycle: "紧张与缓解循环", terrain_use: "地形利用", threat_avoidance: "威胁躲避", time_trial: "计时挑战", turn_based_combat: "回合战斗", turn_order: "行动顺序", unit_roles: "单位分工", vehicle_control: "载具操控", vehicle_tuning: "载具改装", zoning: "区域规划", elemental_fusion: "元素融合", dynamic_enemy_response: "敌人动态响应", stat_upgrade: "数值升级", macro_intervention: "宏观干预", autonomous_civilization: "文明自主演化", explainable_history_chain: "可解释历史因果链" }; // SPDX-License-Identifier: MIT | 将知识库常规机制和常见创新机制翻译为新手可理解的中文。
const internalNames = { critical_fields_complete: "关键信息完整", core_loop_defined: "核心循环已定义", stage_evidence_consistent: "制作阶段与证据一致", basic_product_feasibility: "产品基本可实现", basic_feasibility: "产品基本可实现", cash: "资金", people: "团队能力", production: "制作资源", external_services: "外部服务", P0: "立即处理", P1: "下一阶段前处理", P2: "后续优化", L1: "入门能力", L2: "可独立执行", L3: "熟练负责", L4: "专家能力" }; // SPDX-License-Identifier: MIT | 将硬门槛、资源类别、优先级和能力等级内部代码转换为中文。
function genreName(genreId) { const profile = state.knowledgeBase.profiles.find((item) => item.genre_id === genreId); return profile?.display_name || "其他游戏类型"; } // SPDX-License-Identifier: MIT | 优先使用知识库中文类型名并隐藏内部代码。
function featureName(featureId) { return featureNames[String(featureId)] || (String(featureId).includes("_") ? "项目自定义机制" : String(featureId)); } // SPDX-License-Identifier: MIT | 将机制代码转换为中文并对未知内部代码安全降级。
function optionName(value, options) { return new Map(options).get(String(value)) || String(value); } // SPDX-License-Identifier: MIT | 将稳定枚举代码转换为中文选项名。
function innovationAxisName(value) { const stableName = new Map(innovationAxisOptions).get(String(value)); const tokens = String(value).split("_"); const translated = tokens.map((token) => innovationAxisTokens[token]); return stableName || (translated.every(Boolean) ? translated.join("") : "其他关键体验差异"); } // SPDX-License-Identifier: MIT | 将任何已登记创新位置转换为中文并对未知值安全降级而不泄露内部代码。
function friendlyText(value) { let output = String(value ?? ""); const replacements = { ...dimensionNames, ...internalNames, ...featureNames }; Object.entries(replacements).sort((left, right) => right[0].length - left[0].length).forEach(([code, label]) => { output = output.replaceAll(code, label); }); return output.replaceAll("B_GATE", "进入真人验证候选"); } // SPDX-License-Identifier: MIT | 在新手报告中翻译内部维度、门槛、机制和结论代码。
function create(tag, className = "", text = "") { // SPDX-License-Identifier: MIT | 创建只使用文本节点的安全 DOM 元素。
    const element = document.createElement(tag); // SPDX-License-Identifier: MIT | 创建指定类型的页面元素。
    if (className) element.className = className; // SPDX-License-Identifier: MIT | 在提供类名时设置样式类。
    if (text !== "") element.textContent = String(text); // SPDX-License-Identifier: MIT | 使用 textContent 防止服务端数据形成 HTML 注入。
    return element; // SPDX-License-Identifier: MIT | 返回构造完成的页面元素。
} // SPDX-License-Identifier: MIT | 结束安全元素创建助手。
function showToast(message, isError = false) { // SPDX-License-Identifier: MIT | 向用户和辅助技术播报异步状态。
    window.clearTimeout(toastTimer); // SPDX-License-Identifier: MIT | 取消上一条提示的隐藏定时器。
    toast.textContent = message; // SPDX-License-Identifier: MIT | 使用纯文本显示状态消息。
    toast.className = `toast visible${isError ? " error" : ""}`; // SPDX-License-Identifier: MIT | 根据结果设置提示视觉状态。
    toastTimer = window.setTimeout(() => { toast.className = "toast"; }, 4200); // SPDX-License-Identifier: MIT | 在足够阅读时间后隐藏提示。
} // SPDX-License-Identifier: MIT | 结束状态提示函数。
async function api(path, options = {}) { // SPDX-License-Identifier: MIT | 调用同源 Agent JSON API。
    const headers = { Authorization: `Bearer ${state.token}`, ...(options.headers || {}) }; // SPDX-License-Identifier: MIT | 为每次请求添加当前内存中的 Bearer Token。
    if (options.body !== undefined) headers["Content-Type"] = "application/json"; // SPDX-License-Identifier: MIT | 对带请求体操作声明严格 JSON 媒体类型。
    const response = await fetch(path, { ...options, headers, cache: "no-store" }); // SPDX-License-Identifier: MIT | 禁止缓存并发送同源请求。
    const payload = await response.json().catch(() => ({ error: "invalid_json_response" })); // SPDX-License-Identifier: MIT | 安全解析 JSON 或生成可诊断的降级错误。
    if (!response.ok) throw new Error(payload.message || payload.error || `请求失败：${response.status}`); // SPDX-License-Identifier: MIT | 将非成功响应转换为可显示异常。
    return payload; // SPDX-License-Identifier: MIT | 返回解析后的结构化响应。
} // SPDX-License-Identifier: MIT | 结束 API 调用助手。
function unlock(id) { // SPDX-License-Identifier: MIT | 开放完成前置条件的工作面板。
    const panel = byId(id); // SPDX-License-Identifier: MIT | 查找目标工作面板。
    panel.classList.remove("locked"); // SPDX-License-Identifier: MIT | 移除视觉和交互锁定状态。
    panel.setAttribute("aria-disabled", "false"); // SPDX-License-Identifier: MIT | 向辅助技术声明面板可用。
} // SPDX-License-Identifier: MIT | 结束面板开放函数。
connectionForm.addEventListener("submit", async (event) => { // SPDX-License-Identifier: MIT | 处理 Agent 连接与问卷合同读取。
    event.preventDefault(); // SPDX-License-Identifier: MIT | 阻止浏览器执行传统表单导航。
    if (!connectionForm.reportValidity()) return; // SPDX-License-Identifier: MIT | 在字段无效时保留原生可访问提示。
    state.token = apiToken.value; // SPDX-License-Identifier: MIT | 只把令牌保存到当前页面内存。
    try { // SPDX-License-Identifier: MIT | 捕获连接或鉴权失败。
        const [health, questionnaire, knowledgeBase] = await Promise.all([api("/health"), api("/v1/questionnaire"), api("/v1/knowledge-base")]); // SPDX-License-Identifier: MIT | 并行验证服务并读取前端消费的问卷与类型知识库合同。
        state.questions = questionnaire.questions || []; // SPDX-License-Identifier: MIT | 保存服务端返回的版本化问题列表。
        state.knowledgeBase = knowledgeBase && Array.isArray(knowledgeBase.profiles) ? knowledgeBase : { version: "", profiles: [] }; // SPDX-License-Identifier: MIT | 保存后端签发的类型规则并对异常响应安全降级。
        byId("connectionPill").classList.add("connected"); // SPDX-License-Identifier: MIT | 更新全局连接视觉状态。
        byId("connectionText").textContent = "评分助手已连接"; // SPDX-License-Identifier: MIT | 面向新手只显示连接结果并隐藏内部服务版本。
        unlock("upload"); // SPDX-License-Identifier: MIT | 开放资料上传步骤。
        renderQuestions(); // SPDX-License-Identifier: MIT | 预先渲染空问卷方便创作者查看结构。
        showToast(`连接成功，已读取 ${state.questions.length} 个问题和 ${state.knowledgeBase.profiles.length} 个类型规则。`); // SPDX-License-Identifier: MIT | 播报前后端两个合同都已加载。
        byId("upload").scrollIntoView({ behavior: "smooth", block: "start" }); // SPDX-License-Identifier: MIT | 将视图移动到下一操作步骤。
    } catch (error) { // SPDX-License-Identifier: MIT | 处理连接、网络或令牌错误。
        state.token = ""; // SPDX-License-Identifier: MIT | 连接失败后立即清除内存令牌。
        showToast(error.message, true); // SPDX-License-Identifier: MIT | 显示不含堆栈的连接错误。
    } // SPDX-License-Identifier: MIT | 结束连接异常处理。
}); // SPDX-License-Identifier: MIT | 结束连接表单监听器。
designFiles.addEventListener("change", () => uploadSelectedFiles(designFiles.files, "design_document")); // SPDX-License-Identifier: MIT | 上传新选择的方案资料。
demoFiles.addEventListener("change", () => uploadSelectedFiles(demoFiles.files, "demo_build")); // SPDX-License-Identifier: MIT | 上传新选择的 Demo ZIP。
async function uploadSelectedFiles(fileList, kind) { // SPDX-License-Identifier: MIT | 顺序上传用户选择的受支持文件。
    const files = Array.from(fileList || []); // SPDX-License-Identifier: MIT | 将只读文件列表转换为稳定数组。
    if (!files.length) return; // SPDX-License-Identifier: MIT | 没有文件时不执行网络操作。
    for (const file of files) { // SPDX-License-Identifier: MIT | 逐个处理文件以展示明确状态。
        try { // SPDX-License-Identifier: MIT | 隔离单个文件失败避免中断整个选择。
            showToast(`正在上传：${file.name}`); // SPDX-License-Identifier: MIT | 播报当前上传文件名称。
            const content = await fileToBase64(file); // SPDX-License-Identifier: MIT | 将文件编码为 Agent API 所需 Base64。
            const result = await api("/v1/artifacts", { method: "POST", body: JSON.stringify({ project_id: projectId.value.trim(), filename: file.name, kind, content_base64: content }) }); // SPDX-License-Identifier: MIT | 通过可信上传接口发送文件和业务类型。
            state.artifacts.push({ ...result, local_kind: kind }); // SPDX-License-Identifier: MIT | 保存服务端签发的资料标识和安全状态。
            renderArtifacts(); // SPDX-License-Identifier: MIT | 立即刷新资料清单。
            showToast(`已安全接收：${file.name}`); // SPDX-License-Identifier: MIT | 播报单个文件接收成功。
        } catch (error) { // SPDX-License-Identifier: MIT | 处理文件读取或上传校验错误。
            showToast(`${file.name}：${error.message}`, true); // SPDX-License-Identifier: MIT | 显示具体文件失败原因。
        } // SPDX-License-Identifier: MIT | 结束单个文件异常处理。
    } // SPDX-License-Identifier: MIT | 结束选择文件遍历。
    designFiles.value = ""; // SPDX-License-Identifier: MIT | 清空方案输入以允许重新选择同名文件。
    demoFiles.value = ""; // SPDX-License-Identifier: MIT | 清空 Demo 输入以允许重新选择同名文件。
} // SPDX-License-Identifier: MIT | 结束文件上传函数。
function fileToBase64(file) { // SPDX-License-Identifier: MIT | 读取浏览器文件并返回纯 Base64 内容。
    return new Promise((resolve, reject) => { // SPDX-License-Identifier: MIT | 将 FileReader 回调转换为 Promise。
        const reader = new FileReader(); // SPDX-License-Identifier: MIT | 创建浏览器文件读取器。
        reader.onerror = () => reject(new Error("浏览器读取文件失败")); // SPDX-License-Identifier: MIT | 将本地读取失败转换为明确异常。
        reader.onload = () => resolve(String(reader.result).split(",", 2)[1] || ""); // SPDX-License-Identifier: MIT | 移除 Data URL 前缀并返回 Base64 数据。
        reader.readAsDataURL(file); // SPDX-License-Identifier: MIT | 在不修改本地文件的情况下读取内容。
    }); // SPDX-License-Identifier: MIT | 结束文件读取 Promise。
} // SPDX-License-Identifier: MIT | 结束 Base64 编码助手。
function renderArtifacts() { // SPDX-License-Identifier: MIT | 安全显示服务端确认的资料列表。
    artifactList.replaceChildren(); // SPDX-License-Identifier: MIT | 清除旧资料列表节点。
    if (!state.artifacts.length) artifactList.append(create("p", "empty-state", "尚未选择资料。")); // SPDX-License-Identifier: MIT | 在无资料时显示空状态。
    state.artifacts.forEach((artifact, index) => { // SPDX-License-Identifier: MIT | 遍历每个可信资料记录。
        const row = create("div", "artifact-row"); // SPDX-License-Identifier: MIT | 创建单个资料行。
        const detail = create("div"); // SPDX-License-Identifier: MIT | 创建资料名称和标识容器。
        detail.append(create("strong", "", artifact.original_filename), create("small", "", `${artifact.artifact_id} · ${(artifact.byte_size / 1024).toFixed(1)} KB`)); // SPDX-License-Identifier: MIT | 显示服务端清洗文件名、标识和大小。
        const status = create("span", "tag", artifact.parse_status); // SPDX-License-Identifier: MIT | 显示资料解析状态。
        const remove = create("button", "remove-button", "移除"); // SPDX-License-Identifier: MIT | 创建仅移除本次引用的操作按钮。
        remove.type = "button"; // SPDX-License-Identifier: MIT | 防止移除按钮提交外层表单。
        remove.addEventListener("click", () => { state.artifacts.splice(index, 1); renderArtifacts(); }); // SPDX-License-Identifier: MIT | 从当前提交引用中移除资料并刷新视图。
        row.append(detail, status, remove); // SPDX-License-Identifier: MIT | 组合资料行全部内容。
        artifactList.append(row); // SPDX-License-Identifier: MIT | 将资料行添加到列表。
    }); // SPDX-License-Identifier: MIT | 结束资料列表遍历。
    const hasDesign = state.artifacts.some((item) => ["design_document", "pitch_deck", "spreadsheet"].includes(item.kind)); // SPDX-License-Identifier: MIT | 判断是否已有规则要求的方案类文件。
    prefillButton.disabled = !hasDesign; // SPDX-License-Identifier: MIT | 仅在存在方案资料后开放问卷代填。
} // SPDX-License-Identifier: MIT | 结束资料列表渲染。
prefillButton.addEventListener("click", async () => { // SPDX-License-Identifier: MIT | 处理基于资料生成问卷草稿操作。
    prefillButton.disabled = true; // SPDX-License-Identifier: MIT | 防止用户重复发起代填请求。
    try { // SPDX-License-Identifier: MIT | 捕获代填服务错误。
        const result = await api("/v1/questionnaire/prefill", { method: "POST", body: JSON.stringify({ artifact_ids: state.artifacts.map((item) => item.artifact_id), creator_values: {} }) }); // SPDX-License-Identifier: MIT | 只传递本次可信资料标识生成问卷草稿。
        state.answers = result.answers || {}; // SPDX-License-Identifier: MIT | 保存带来源和证据的代填答案信封。
        unlock("questionnaire"); // SPDX-License-Identifier: MIT | 开放问卷审核步骤。
        renderQuestions(); // SPDX-License-Identifier: MIT | 用代填结果重新生成动态问卷。
        showToast(`问卷草稿已生成：${result.prefiller_version}`); // SPDX-License-Identifier: MIT | 播报实际使用的代填器版本。
        byId("questionnaire").scrollIntoView({ behavior: "smooth", block: "start" }); // SPDX-License-Identifier: MIT | 将视图移动到问卷步骤。
    } catch (error) { // SPDX-License-Identifier: MIT | 处理代填、网络或服务配置错误。
        showToast(error.message, true); // SPDX-License-Identifier: MIT | 显示可操作的代填失败消息。
    } finally { // SPDX-License-Identifier: MIT | 无论结果都恢复按钮可用性判断。
        renderArtifacts(); // SPDX-License-Identifier: MIT | 根据当前方案资料恢复代填按钮状态。
    } // SPDX-License-Identifier: MIT | 结束代填请求清理。
}); // SPDX-License-Identifier: MIT | 结束问卷代填按钮监听器。
function renderQuestions() { // SPDX-License-Identifier: MIT | 按服务端问卷合同安全生成表单控件。
    questionList.replaceChildren(); // SPDX-License-Identifier: MIT | 清除旧问卷节点和监听器。
    state.questions.forEach((question, index) => { // SPDX-License-Identifier: MIT | 按服务端稳定顺序遍历问题。
        const answer = state.answers[question.question_id] || { value: null, source: "creator", confidence: 1, evidence_refs: [], creator_confirmed: false }; // SPDX-License-Identifier: MIT | 读取代填答案或建立空创作者答案。
        state.answers[question.question_id] = answer; // SPDX-License-Identifier: MIT | 确保所有登记题目都有答案信封。
        const card = create("section", "question-card"); // SPDX-License-Identifier: MIT | 创建单个问题卡片。
        const meta = create("div", "question-meta"); // SPDX-License-Identifier: MIT | 创建问题说明容器。
        meta.append(create("span", "tag", `${String(index + 1).padStart(2, "0")} · ${question.section}${question.required ? " · 必填" : ""}`), create("h3", "", question.prompt), create("p", "", question.purpose)); // SPDX-License-Identifier: MIT | 显示问题分组、要求、正文和用途。
        const control = create("div", "question-control"); // SPDX-License-Identifier: MIT | 创建答案编辑和确认容器。
        const input = buildQuestionInput(question, answer); // SPDX-License-Identifier: MIT | 根据题型创建可访问控件。
        const confirmation = create("div", "confirm-row"); // SPDX-License-Identifier: MIT | 创建答案溯源和确认行。
        const source = create("span", "", `来源：${sourceName(answer.source)} · 置信 ${Number(answer.confidence || 0).toFixed(2)}`); // SPDX-License-Identifier: MIT | 显示答案来源和提取置信度。
        const checkLabel = create("label", "confirm-check"); // SPDX-License-Identifier: MIT | 创建创作者确认标签。
        const checkbox = create("input"); // SPDX-License-Identifier: MIT | 创建创作者确认复选框。
        checkbox.type = "checkbox"; // SPDX-License-Identifier: MIT | 设置复选框控件类型。
        checkbox.checked = answer.creator_confirmed === true; // SPDX-License-Identifier: MIT | 回显当前创作者确认状态。
        checkbox.addEventListener("change", () => { answer.creator_confirmed = checkbox.checked; updateProgress(); }); // SPDX-License-Identifier: MIT | 保存确认变化并刷新问卷进度。
        checkLabel.append(checkbox, document.createTextNode("我已核对并确认")); // SPDX-License-Identifier: MIT | 为复选框提供可见文字标签。
        confirmation.append(source, checkLabel); // SPDX-License-Identifier: MIT | 组合答案来源与确认控件。
        control.append(input, confirmation); // SPDX-License-Identifier: MIT | 组合答案编辑和元数据。
        card.append(meta, control); // SPDX-License-Identifier: MIT | 组合完整问题卡片。
        questionList.append(card); // SPDX-License-Identifier: MIT | 将问题卡片加入问卷。
    }); // SPDX-License-Identifier: MIT | 结束问卷问题遍历。
    confirmFilledButton.disabled = state.questions.length === 0; // SPDX-License-Identifier: MIT | 有问题时开放批量确认按钮。
    updateProgress(); // SPDX-License-Identifier: MIT | 计算并显示初始问卷完成度。
} // SPDX-License-Identifier: MIT | 结束动态问卷渲染。
function markGuidedAnswerEdited(container, answer, value) { // SPDX-License-Identifier: MIT | 将引导式编辑器的值同步到统一答案信封。
    answer.value = value; // SPDX-License-Identifier: MIT | 保存引导式控件生成的结构化对象或无效高级文本。
    answer.source = "creator"; // SPDX-License-Identifier: MIT | 将引导式编辑标记为创作者直接输入。
    answer.confidence = 1; // SPDX-License-Identifier: MIT | 对创作者直接编辑使用确定来源置信度。
    answer.evidence_refs = []; // SPDX-License-Identifier: MIT | 清除修改后不再可靠的自动提取引用。
    answer.creator_confirmed = false; // SPDX-License-Identifier: MIT | 修改答案后要求创作者重新确认。
    const parent = container.closest(".question-control"); // SPDX-License-Identifier: MIT | 查找当前问题容器以更新确认与来源状态。
    const checkbox = parent?.querySelector('.confirm-check input[type="checkbox"]'); // SPDX-License-Identifier: MIT | 查找当前问题的确认复选框。
    const source = parent?.querySelector(".confirm-row > span"); // SPDX-License-Identifier: MIT | 查找当前问题的来源说明文本。
    if (checkbox) checkbox.checked = false; // SPDX-License-Identifier: MIT | 在答案变化后取消视觉确认状态。
    if (source) source.textContent = "来源：创作者 · 置信 1.00"; // SPDX-License-Identifier: MIT | 在答案变化后刷新来源说明。
    updateProgress(); // SPDX-License-Identifier: MIT | 更新问卷填写与关键确认进度。
} // SPDX-License-Identifier: MIT | 结束引导式答案同步助手。
function commitGuidedObject(container, answer, value, jsonEditor) { // SPDX-License-Identifier: MIT | 提交有效对象并同步专业 JSON 编辑器。
    markGuidedAnswerEdited(container, answer, value); // SPDX-License-Identifier: MIT | 将当前结构化对象写入统一答案状态。
    if (jsonEditor && document.activeElement !== jsonEditor) jsonEditor.value = JSON.stringify(value, null, 2); // SPDX-License-Identifier: MIT | 在非高级编辑状态下回显最新 JSON。
} // SPDX-License-Identifier: MIT | 结束有效对象提交助手。
function addAdvancedJsonEditor(container, question, answer, syncSimple) { // SPDX-License-Identifier: MIT | 为专业用户添加可展开 JSON 编辑能力。
    const details = create("details", "advanced-json"); // SPDX-License-Identifier: MIT | 创建默认折叠的渐进披露容器。
    const summary = create("summary", "", "专业团队数据格式（新手无需打开）"); // SPDX-License-Identifier: MIT | 使用中文说明并保持技术参数默认折叠。
    const hint = create("p", "editor-hint", "只适合需要批量导入数据的专业团队；修改后会同步到上方简单表单。"); // SPDX-License-Identifier: MIT | 用新手能理解的语言解释高级编辑器用途。
    const textarea = create("textarea", "json-editor"); // SPDX-License-Identifier: MIT | 创建专业 JSON 多行编辑器。
    const error = create("p", "editor-error"); // SPDX-License-Identifier: MIT | 创建就近显示的 JSON 格式错误区域。
    textarea.value = formatAnswerValue(question, answer.value); // SPDX-License-Identifier: MIT | 回显已有结构化答案。
    textarea.placeholder = JSON.stringify(objectExamples[question.question_id] || { note: "请使用 JSON 对象" }, null, 2); // SPDX-License-Identifier: MIT | 提供合法 JSON 示例而不要求新手阅读。
    textarea.setAttribute("aria-label", `${question.prompt}（专业 JSON）`); // SPDX-License-Identifier: MIT | 为高级编辑器提供独立可访问名称。
    textarea.addEventListener("input", () => { // SPDX-License-Identifier: MIT | 解析专业用户输入并同步快速表单。
        const raw = textarea.value.trim(); // SPDX-License-Identifier: MIT | 读取并清理高级 JSON 文本。
        if (!raw) { error.textContent = ""; syncSimple({}); markGuidedAnswerEdited(container, answer, null); return; } // SPDX-License-Identifier: MIT | 允许清空答案并同步空状态。
        try { // SPDX-License-Identifier: MIT | 捕获高级 JSON 解析错误。
            const parsed = JSON.parse(raw); // SPDX-License-Identifier: MIT | 使用浏览器原生解析器读取 JSON。
            if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("object_required"); // SPDX-License-Identifier: MIT | 限制高级答案必须为 JSON 对象。
            error.textContent = ""; // SPDX-License-Identifier: MIT | 清除已修复的格式错误。
            syncSimple(parsed); // SPDX-License-Identifier: MIT | 将专业答案同步到快速控件。
            markGuidedAnswerEdited(container, answer, parsed); // SPDX-License-Identifier: MIT | 保存解析后的专业对象。
        } catch { // SPDX-License-Identifier: MIT | 处理 JSON 不完整或非对象输入。
            error.textContent = "JSON 格式暂不正确，请检查引号、逗号和大括号。"; // SPDX-License-Identifier: MIT | 提供紧邻输入框的可操作错误信息。
            markGuidedAnswerEdited(container, answer, raw); // SPDX-License-Identifier: MIT | 保留原始文本并阻止无效对象提交。
        } // SPDX-License-Identifier: MIT | 结束高级 JSON 解析分支。
    }); // SPDX-License-Identifier: MIT | 结束高级 JSON 输入监听器。
    details.append(summary, hint, textarea, error); // SPDX-License-Identifier: MIT | 组合专业模式的说明、输入和错误提示。
    container.append(details); // SPDX-License-Identifier: MIT | 将专业模式附加到引导式编辑器底部。
    return textarea; // SPDX-License-Identifier: MIT | 返回 JSON 编辑器供快速表单反向同步。
} // SPDX-License-Identifier: MIT | 结束专业 JSON 编辑器构造函数。
function createGuidedHeader(title, hint) { // SPDX-License-Identifier: MIT | 创建引导式问题的标题与一句话提示。
    const header = create("div", "guided-header"); // SPDX-License-Identifier: MIT | 创建引导式编辑器说明容器。
    header.append(create("strong", "", title), create("p", "editor-hint", hint)); // SPDX-License-Identifier: MIT | 添加短标题和面向新手的简短说明。
    return header; // SPDX-License-Identifier: MIT | 返回引导式说明容器。
} // SPDX-License-Identifier: MIT | 结束引导式说明构造函数。
function createQuickButton(label, action) { // SPDX-License-Identifier: MIT | 创建不提交表单的快捷预设按钮。
    const button = create("button", "quick-button", label); // SPDX-License-Identifier: MIT | 创建紧凑的次级操作按钮。
    button.type = "button"; // SPDX-License-Identifier: MIT | 防止快捷按钮提交外层问卷表单。
    button.addEventListener("click", action); // SPDX-License-Identifier: MIT | 绑定本地预设应用逻辑。
    return button; // SPDX-License-Identifier: MIT | 返回配置完成的快捷按钮。
} // SPDX-License-Identifier: MIT | 结束快捷按钮构造函数。
function innovationAxisChoicesForCurrentGenres() { // SPDX-License-Identifier: MIT | 从后端类型规则生成当前项目相关的创新位置选项。
    const labels = new Map(innovationAxisOptions); // SPDX-License-Identifier: MIT | 建立常用创新位置代码到中文名称的映射。
    const genreIds = new Set(Array.isArray(state.answers.genre_ids?.value) ? state.answers.genre_ids.value : []); // SPDX-License-Identifier: MIT | 读取当前已选择的游戏类型代码。
    const axes = state.knowledgeBase.profiles.filter((profile) => genreIds.has(profile.genre_id)).flatMap((profile) => profile.innovation_axes || []); // SPDX-License-Identifier: MIT | 汇总后端为所选类型登记的创新验证位置。
    const uniqueAxes = [...new Set(axes)]; // SPDX-License-Identifier: MIT | 去除混合类型间重复的创新位置。
    return (uniqueAxes.length ? uniqueAxes : innovationAxisOptions.map(([value]) => value)).map((value) => [value, labels.get(value) || innovationAxisName(value)]); // SPDX-License-Identifier: MIT | 优先展示类型相关位置并将所有未知显示代码翻译为中文名称。
} // SPDX-License-Identifier: MIT | 结束类型相关创新位置选项生成函数。
function buildGenreEditor(question, answer) { // SPDX-License-Identifier: MIT | 使用后端知识库构建可多选游戏类型编辑器。
    const container = create("div", "guided-editor knowledge-editor"); // SPDX-License-Identifier: MIT | 创建类型知识库引导式编辑器根容器。
    const fieldset = create("fieldset", "choice-fieldset"); // SPDX-License-Identifier: MIT | 创建语义化类型复选组。
    const grid = create("div", "choice-grid genre-grid"); // SPDX-License-Identifier: MIT | 创建可扫描的类型选项网格。
    const selected = new Set(Array.isArray(answer.value) ? answer.value : []); // SPDX-License-Identifier: MIT | 回显现有类型代码并支持 AI 代填候选。
    const inputs = new Map(); // SPDX-License-Identifier: MIT | 保存类型代码到复选框的映射。
    const profiles = Array.isArray(state.knowledgeBase.profiles) ? state.knowledgeBase.profiles : []; // SPDX-License-Identifier: MIT | 只使用后端知识库合同返回的类型资料。
    profiles.forEach((profile) => { // SPDX-License-Identifier: MIT | 为每个已登记类型创建复选项。
        const label = create("label", "choice-option genre-option"); // SPDX-License-Identifier: MIT | 创建一个类型选择卡片。
        const input = create("input"); // SPDX-License-Identifier: MIT | 创建类型复选框。
        const text = create("span"); // SPDX-License-Identifier: MIT | 创建类型名称与代码容器。
        input.type = "checkbox"; // SPDX-License-Identifier: MIT | 允许混合类型项目选择多个类型。
        input.value = String(profile.genre_id || ""); // SPDX-License-Identifier: MIT | 使用后端签发的稳定类型代码。
        input.checked = selected.has(input.value); // SPDX-License-Identifier: MIT | 回显当前已选择类型。
        text.append(create("strong", "", profile.display_name || "其他游戏类型")); // SPDX-License-Identifier: MIT | 新手界面只显示中文类型名，稳定代码保留在提交值中。
        inputs.set(input.value, input); // SPDX-License-Identifier: MIT | 登记复选框供数量限制和答案收集。
        label.append(input, text); // SPDX-License-Identifier: MIT | 组合可访问类型复选项。
        grid.append(label); // SPDX-License-Identifier: MIT | 将类型卡片加入网格。
    }); // SPDX-License-Identifier: MIT | 结束类型资料遍历。
    const commit = (changedInput) => { // SPDX-License-Identifier: MIT | 将类型选择同步到问卷答案并执行数量限制。
        const values = [...inputs].filter(([, input]) => input.checked).map(([genreId]) => genreId); // SPDX-License-Identifier: MIT | 收集当前全部已选择类型代码。
        if (values.length > 3) { changedInput.checked = false; showToast("最多选择 3 个最主要的游戏类型。", true); return; } // SPDX-License-Identifier: MIT | 防止泛化标签过多稀释类型评分逻辑。
        markGuidedAnswerEdited(container, answer, values); // SPDX-License-Identifier: MIT | 写入与后端列表合同一致的类型答案。
        renderQuestions(); // SPDX-License-Identifier: MIT | 重新生成依赖类型的玩法机制和创新位置控件并保留统一答案状态。
    }; // SPDX-License-Identifier: MIT | 结束类型答案提交函数。
    inputs.forEach((input) => input.addEventListener("change", () => commit(input))); // SPDX-License-Identifier: MIT | 在每个类型选择变化时同步答案。
    fieldset.append(create("legend", "", "选择 1-3 个最符合的游戏类型"), create("p", "editor-hint", "混合类型可以多选；请先选择最主要的类型。"), grid); // SPDX-License-Identifier: MIT | 新手界面隐藏知识库版本并保留必要选择说明。
    container.append(createGuidedHeader("从评分知识库选择类型", "选择后，下一题会自动给出该类型的常规机制和高密度组合提示。"), fieldset); // SPDX-License-Identifier: MIT | 组合类型知识库编辑器。
    return container; // SPDX-License-Identifier: MIT | 返回类型引导式编辑器。
} // SPDX-License-Identifier: MIT | 结束类型知识库编辑器构造函数。
function buildGameplayFeatureEditor(question, answer) { // SPDX-License-Identifier: MIT | 将类型基线候选和自由机制列表耦合为一个结构化编辑器。
    const container = create("div", "guided-editor knowledge-editor"); // SPDX-License-Identifier: MIT | 创建玩法机制知识库编辑器根容器。
    const suggestions = create("div", "feature-suggestions"); // SPDX-License-Identifier: MIT | 创建由所选类型动态生成的机制候选区。
    const customInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建只填写项目自定义中文机制的输入框。
    const selected = new Set((Array.isArray(answer.value) ? answer.value : []).filter((value) => Object.hasOwn(featureNames, value))); // SPDX-License-Identifier: MIT | 将知识库已知机制保存为内部选择状态而不在新手界面显示代码。
    const initialCustom = (Array.isArray(answer.value) ? answer.value : []).filter((value) => !Object.hasOwn(featureNames, value)); // SPDX-License-Identifier: MIT | 将知识库外机制作为创作者自定义中文内容回显。
    customInput.id = "answer-gameplay_features"; // SPDX-License-Identifier: MIT | 保留稳定元素标识供测试和辅助技术使用。
    customInput.value = initialCustom.join("\n"); // SPDX-License-Identifier: MIT | 回显项目自定义机制而不暴露内部英文代码。
    customInput.placeholder = "补充项目独有玩法，每行一项；例如：棋子自主演化、因果链复盘"; // SPDX-License-Identifier: MIT | 使用中文自然语言提示补充独有机制。
    customInput.setAttribute("aria-label", "补充项目独有玩法"); // SPDX-License-Identifier: MIT | 为自定义机制输入提供新手可理解的名称。
    const customValues = () => customInput.value.split(/\r?\n|，|,/).map((item) => item.trim()).filter(Boolean); // SPDX-License-Identifier: MIT | 将中文换行或逗号输入转换为稳定列表。
    const currentValues = () => [...selected, ...customValues()]; // SPDX-License-Identifier: MIT | 合并内部知识库选择与创作者自定义机制用于提交。
    const commit = () => markGuidedAnswerEdited(container, answer, currentValues()); // SPDX-License-Identifier: MIT | 将合并后的机制列表同步到统一答案信封。
    const renderSuggestions = () => { // SPDX-License-Identifier: MIT | 按当前类型选择重新生成常规机制和拥挤组合提示。
        suggestions.replaceChildren(); // SPDX-License-Identifier: MIT | 清除旧类型对应的候选节点。
        const genreIds = new Set(Array.isArray(state.answers.genre_ids?.value) ? state.answers.genre_ids.value : []); // SPDX-License-Identifier: MIT | 读取当前已确认前的类型选择状态。
        const profiles = state.knowledgeBase.profiles.filter((profile) => genreIds.has(profile.genre_id)); // SPDX-License-Identifier: MIT | 找出当前项目使用的类型资料。
        if (!profiles.length) { suggestions.append(create("p", "editor-note", "请先在上一题选择游戏类型，系统会在这里展示常规机制。")); return; } // SPDX-License-Identifier: MIT | 在未选类型时提供明确下一步。
        const baseline = [...new Set(profiles.flatMap((profile) => profile.baseline_features || []))].sort(); // SPDX-License-Identifier: MIT | 合并混合类型的全部常规机制并去重。
        const crowded = profiles.flatMap((profile) => profile.crowded_patterns || []); // SPDX-License-Identifier: MIT | 汇总所选类型的高密度机制组合。
        const buttonRow = create("div", "quick-actions feature-buttons"); // SPDX-License-Identifier: MIT | 创建常规机制快捷按钮区。
        baseline.forEach((featureId) => { // SPDX-License-Identifier: MIT | 为每项类型常规机制创建可切换按钮。
            const button = createQuickButton(featureName(featureId), () => { // SPDX-License-Identifier: MIT | 使用中文机制名创建将机制加入或移出答案的快捷操作。
                if (selected.has(featureId)) selected.delete(featureId); else selected.add(featureId); // SPDX-License-Identifier: MIT | 在内部选择状态中切换常规机制而不暴露代码。
                commit(); // SPDX-License-Identifier: MIT | 同步更新后的结构化机制答案。
                renderSuggestions(); // SPDX-License-Identifier: MIT | 更新按钮选中状态和组合提示。
            }); // SPDX-License-Identifier: MIT | 结束机制按钮切换逻辑。
            if (selected.has(featureId)) button.classList.add("selected"); // SPDX-License-Identifier: MIT | 对已选择机制显示明确选中状态。
            buttonRow.append(button); // SPDX-License-Identifier: MIT | 将机制按钮加入候选区。
        }); // SPDX-License-Identifier: MIT | 结束常规机制候选遍历。
        const crowdedText = crowded.length ? crowded.map((pattern) => pattern.map(featureName).join(" + ")).join("；") : "当前类型没有登记常见的高同质化组合"; // SPDX-License-Identifier: MIT | 将拥挤机制组合翻译为创作者可读中文提示。
        suggestions.append(create("strong", "", "点击选择项目实际采用的类型常规机制"), buttonRow, create("p", "editor-note", `高同质化组合提示：${crowdedText}`)); // SPDX-License-Identifier: MIT | 同时展示基线选择与同质化风险组合。
    }; // SPDX-License-Identifier: MIT | 结束机制候选渲染函数。
    suggestions.id = "knowledgeFeatureSuggestions"; // SPDX-License-Identifier: MIT | 提供跨问题刷新使用的稳定容器标识。
    suggestions.refreshSuggestions = renderSuggestions; // SPDX-License-Identifier: MIT | 登记仅作用于当前编辑器的刷新函数。
    customInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在中文自定义机制变化时同步答案。
    container.append(createGuidedHeader("选择已有玩法，再补充项目独有玩法", "常规玩法本身不扣分；系统会结合具体差异和验证证据判断同质化风险。"), suggestions, customInput); // SPDX-License-Identifier: MIT | 组合中文类型基线与自然语言自定义机制输入。
    renderSuggestions(); // SPDX-License-Identifier: MIT | 首次渲染当前类型对应的机制候选。
    return container; // SPDX-License-Identifier: MIT | 返回玩法机制知识库编辑器。
} // SPDX-License-Identifier: MIT | 结束玩法机制知识库编辑器构造函数。
function buildKnowledgeOptionEditor(question, answer, options, title, hint) { // SPDX-License-Identifier: MIT | 为创新位置和验证方式创建前后端一致的多选编辑器。
    const container = create("div", "guided-editor knowledge-editor"); // SPDX-License-Identifier: MIT | 创建知识库枚举编辑器根容器。
    const fieldset = create("fieldset", "choice-fieldset"); // SPDX-License-Identifier: MIT | 创建语义化枚举复选组。
    const grid = create("div", "choice-grid"); // SPDX-License-Identifier: MIT | 创建枚举选项网格。
    const current = new Set(Array.isArray(answer.value) ? answer.value : []); // SPDX-License-Identifier: MIT | 回显已有结构化多选值。
    const inputs = new Map(); // SPDX-License-Identifier: MIT | 保存枚举代码到复选框映射。
    options.forEach(([value, labelText]) => { // SPDX-License-Identifier: MIT | 为每个前后端稳定代码创建选项。
        const label = create("label", "choice-option"); // SPDX-License-Identifier: MIT | 创建单个枚举复选项。
        const input = create("input"); // SPDX-License-Identifier: MIT | 创建枚举复选框。
        const text = create("span"); // SPDX-License-Identifier: MIT | 创建中文名称和代码容器。
        input.type = "checkbox"; // SPDX-License-Identifier: MIT | 允许选择多个创新位置或验证方式。
        input.value = value; // SPDX-License-Identifier: MIT | 保存稳定后端代码。
        input.checked = current.has(value); // SPDX-License-Identifier: MIT | 回显当前值。
        text.append(document.createTextNode(labelText)); // SPDX-License-Identifier: MIT | 新手界面只展示中文名称，稳定代码保留在控件值中。
        inputs.set(value, input); // SPDX-License-Identifier: MIT | 登记复选框供答案收集。
        label.append(input, text); // SPDX-License-Identifier: MIT | 组合完整复选项。
        grid.append(label); // SPDX-License-Identifier: MIT | 将选项加入网格。
    }); // SPDX-License-Identifier: MIT | 结束知识库枚举遍历。
    const commit = () => markGuidedAnswerEdited(container, answer, [...inputs].filter(([, input]) => input.checked).map(([value]) => value)); // SPDX-License-Identifier: MIT | 将已选稳定代码同步到后端列表合同。
    inputs.forEach((input) => input.addEventListener("change", commit)); // SPDX-License-Identifier: MIT | 在任一枚举选择变化时更新答案。
    fieldset.append(create("legend", "", title), create("p", "editor-hint", hint), grid); // SPDX-License-Identifier: MIT | 组合枚举标题、说明和选项。
    container.append(fieldset); // SPDX-License-Identifier: MIT | 将枚举复选组加入编辑器。
    return container; // SPDX-License-Identifier: MIT | 返回知识库枚举编辑器。
} // SPDX-License-Identifier: MIT | 结束知识库枚举编辑器构造函数。
function buildProgressionFeedbackEditor(question, answer) { // SPDX-License-Identifier: MIT | 构建不偏向局外成长的分层成长反馈编辑器。
    const container = create("div", "guided-editor"); // SPDX-License-Identifier: MIT | 创建成长反馈引导式编辑器根容器。
    const current = answer.value && typeof answer.value === "object" && !Array.isArray(answer.value) ? answer.value : {}; // SPDX-License-Identifier: MIT | 安全读取已有结构化成长反馈。
    const modeLabel = create("label", "guided-field guided-wide"); // SPDX-License-Identifier: MIT | 创建成长时间尺度选择标签。
    const modeSelect = create("select"); // SPDX-License-Identifier: MIT | 创建局内、局外、混合或无成长选择器。
    const grid = create("div", "guided-grid"); // SPDX-License-Identifier: MIT | 创建分层成长机制输入网格。
    const inMatchInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建单局内成长机制列表输入。
    const metaInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建局间或长期成长机制列表输入。
    const signalsInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建反馈信号列表输入。
    const tradeoffsInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建成长选择与取舍说明输入。
    const failureInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建失败学习与复盘说明输入。
    let jsonEditor = null; // SPDX-License-Identifier: MIT | 保存成长反馈专业 JSON 编辑器引用。
    modeSelect.append(new Option("请选择", ""), new Option("主要发生在单局内", "in_match"), new Option("主要发生在局间/局外", "meta"), new Option("局内与局外都有", "hybrid"), new Option("没有数值成长，但有技能学习", "none")); // SPDX-License-Identifier: MIT | 提供覆盖 RTS、Roguelite、RPG 和纯技巧游戏的时间尺度。
    modeSelect.id = "answer-progression-mode"; // SPDX-License-Identifier: MIT | 提供成长时间尺度稳定控件标识。
    inMatchInput.id = "answer-progression-in-match"; // SPDX-License-Identifier: MIT | 提供局内成长稳定控件标识。
    metaInput.id = "answer-progression-meta"; // SPDX-License-Identifier: MIT | 提供局外成长稳定控件标识。
    signalsInput.id = "answer-progression-signals"; // SPDX-License-Identifier: MIT | 提供成长反馈信号稳定控件标识。
    tradeoffsInput.id = "answer-progression-tradeoffs"; // SPDX-License-Identifier: MIT | 提供成长取舍稳定控件标识。
    failureInput.id = "answer-progression-failure"; // SPDX-License-Identifier: MIT | 提供失败学习稳定控件标识。
    modeSelect.value = typeof current.mode === "string" ? current.mode : ""; // SPDX-License-Identifier: MIT | 回显当前成长时间尺度。
    inMatchInput.value = Array.isArray(current.in_match_progression) ? current.in_match_progression.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显局内经济、科技、兵力或构筑进程。
    metaInput.value = Array.isArray(current.meta_progression) ? current.meta_progression.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显局间解锁或长期进程。
    signalsInput.value = Array.isArray(current.feedback_signals) ? current.feedback_signals.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显视觉、音频、数值或状态反馈。
    tradeoffsInput.value = typeof current.decision_tradeoffs === "string" ? current.decision_tradeoffs : ""; // SPDX-License-Identifier: MIT | 回显成长选择如何影响策略。
    failureInput.value = typeof current.failure_learning === "string" ? current.failure_learning : ""; // SPDX-License-Identifier: MIT | 回显失败、回退和复盘机制。
    [[inMatchInput, "单局内成长（每行一项）", "例如：采集资源、扩张基地、科技升级、单位解锁、地图控制"], [metaInput, "局间/局外成长（没有可留空）", "例如：角色解锁、永久能力、剧情章节、账号等级"], [signalsInput, "玩家怎样感知成长（每行一项）", "例如：新单位可用、建筑外观变化、伤害反馈、地图优势、因果报告"], [tradeoffsInput, "成长如何改变选择或产生取舍？", "例如：先升科技会牺牲当前兵力，但打开新的战术路线"], [failureInput, "失败后怎样理解原因并调整？", "例如：战报、回放、伤害来源、资源曲线或重试提示"]].forEach(([input, labelText, placeholder]) => { const label = create("label", "guided-field"); input.placeholder = placeholder; label.append(create("span", "", labelText), input); grid.append(label); }); // SPDX-License-Identifier: MIT | 为不同类型游戏提供对应证据入口而不强迫填写局外成长。
    modeLabel.append(create("span", "", "成长反馈主要发生在哪里？"), modeSelect, create("small", "", "即时战略可选“单局内”；没有局外成长不会因此扣分。")); // SPDX-License-Identifier: MIT | 明确 RTS 等游戏的局内成长属于完整成长反馈。
    const listValue = (input) => input.value.split(/\r?\n|，|,/).map((item) => item.trim()).filter(Boolean); // SPDX-License-Identifier: MIT | 将换行或逗号输入转换为稳定字符串列表。
    const collect = () => ({ mode: modeSelect.value || "unknown", in_match_progression: listValue(inMatchInput), meta_progression: listValue(metaInput), feedback_signals: listValue(signalsInput), decision_tradeoffs: tradeoffsInput.value.trim(), failure_learning: failureInput.value.trim() }); // SPDX-License-Identifier: MIT | 将快速表单转换为后端分层成长反馈合同。
    const commit = () => commitGuidedObject(container, answer, collect(), jsonEditor); // SPDX-License-Identifier: MIT | 提交当前分层成长反馈对象。
    [modeSelect, inMatchInput, metaInput, signalsInput, tradeoffsInput, failureInput].forEach((input) => input.addEventListener(input === modeSelect ? "change" : "input", commit)); // SPDX-License-Identifier: MIT | 在任一成长反馈字段变化时同步答案。
    container.append(createGuidedHeader("分别描述局内与局外成长", "评分看所选时间尺度中的成长机制、反馈信号、策略取舍和失败学习，不按字数，也不默认要求局外系统。"), modeLabel, grid); // SPDX-License-Identifier: MIT | 组合成长反馈的新手路径。
    const syncSimple = (value) => { modeSelect.value = typeof value.mode === "string" ? value.mode : ""; inMatchInput.value = Array.isArray(value.in_match_progression) ? value.in_match_progression.join("\n") : ""; metaInput.value = Array.isArray(value.meta_progression) ? value.meta_progression.join("\n") : ""; signalsInput.value = Array.isArray(value.feedback_signals) ? value.feedback_signals.join("\n") : ""; tradeoffsInput.value = typeof value.decision_tradeoffs === "string" ? value.decision_tradeoffs : ""; failureInput.value = typeof value.failure_learning === "string" ? value.failure_learning : ""; }; // SPDX-License-Identifier: MIT | 将专业 JSON 反向同步到分层成长快速控件。
    jsonEditor = addAdvancedJsonEditor(container, question, answer, syncSimple); // SPDX-License-Identifier: MIT | 添加成长反馈专业 JSON 编辑入口。
    return container; // SPDX-License-Identifier: MIT | 返回分层成长反馈编辑器。
} // SPDX-License-Identifier: MIT | 结束分层成长反馈编辑器构造函数。
function buildProductionFeasibilityEditor(question, answer) { // SPDX-License-Identifier: MIT | 构建与当前团队资金分离的产品可实现性编辑器。
    const container = create("div", "guided-editor"); // SPDX-License-Identifier: MIT | 创建产品可实现性引导式编辑器根容器。
    const current = answer.value && typeof answer.value === "object" && !Array.isArray(answer.value) ? answer.value : {}; // SPDX-License-Identifier: MIT | 安全读取已有产品可实现性对象。
    const checksGrid = create("div", "choice-grid"); // SPDX-License-Identifier: MIT | 创建四类实现证据复选区域。
    const listGrid = create("div", "guided-grid"); // SPDX-License-Identifier: MIT | 创建依赖和风险列表输入区域。
    const checkDefinitions = [["scope_bounded", "首发范围有明确上限"], ["technical_path_known", "主要技术路径已明确"], ["platform_constraints_known", "目标平台约束已核对"], ["prototype_validation_plan", "关键未知有原型验证计划"]]; // SPDX-License-Identifier: MIT | 定义不涉及当前人数和资金的四项可实现性证据。
    const checkInputs = new Map(); // SPDX-License-Identifier: MIT | 保存产品可实现性代码到复选框的映射。
    const dependenciesInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建关键外部依赖列表输入。
    const risksInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建未解决高风险列表输入。
    const blockersInput = create("textarea"); // SPDX-License-Identifier: MIT | 创建明确硬阻断列表输入。
    let jsonEditor = null; // SPDX-License-Identifier: MIT | 保存产品可实现性专业 JSON 编辑器引用。
    checkDefinitions.forEach(([key, labelText]) => { const label = create("label", "choice-option"); const input = create("input"); input.type = "checkbox"; input.id = `answer-production-${key.replaceAll("_", "-")}`; input.checked = current[key] === true; checkInputs.set(key, input); label.append(input, create("span", "", labelText)); checksGrid.append(label); }); // SPDX-License-Identifier: MIT | 创建带稳定标识的范围、技术、平台和验证四项可核对证据。
    dependenciesInput.id = "answer-production-dependencies"; // SPDX-License-Identifier: MIT | 提供关键依赖稳定控件标识。
    risksInput.id = "answer-production-risks"; // SPDX-License-Identifier: MIT | 提供未解决高风险稳定控件标识。
    blockersInput.id = "answer-production-blockers"; // SPDX-License-Identifier: MIT | 提供硬阻断稳定控件标识。
    dependenciesInput.value = Array.isArray(current.critical_dependencies) ? current.critical_dependencies.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显引擎、第三方服务或外部内容依赖。
    risksInput.value = Array.isArray(current.unresolved_high_risks) ? current.unresolved_high_risks.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显性能、规模、算法或内容产能高风险。
    blockersInput.value = Array.isArray(current.blocking_constraints) ? current.blocking_constraints.join("\n") : ""; // SPDX-License-Identifier: MIT | 回显无法绕过的物理、平台或政策阻断。
    [[dependenciesInput, "关键依赖（每行一项）", "例如：引擎大规模单位性能、第三方服务器、授权内容；没有可留空"], [risksInput, "尚未解决的高风险（每行一项）", "例如：千单位同屏性能尚未验证；没有可留空"], [blockersInput, "当前方案的明确硬阻断（每行一项）", "只有确定无法绕过时才填；普通缺团队或缺资金不要填在这里"]].forEach(([input, labelText, placeholder]) => { const label = create("label", "guided-field"); input.placeholder = placeholder; label.append(create("span", "", labelText), input); listGrid.append(label); }); // SPDX-License-Identifier: MIT | 将依赖、高风险和硬阻断清楚分开。
    const listValue = (input) => input.value.split(/\r?\n|，|,/).map((item) => item.trim()).filter(Boolean); // SPDX-License-Identifier: MIT | 将多行实现风险输入转换为稳定列表。
    const collect = () => ({ ...Object.fromEntries([...checkInputs].map(([key, input]) => [key, input.checked])), critical_dependencies: listValue(dependenciesInput), unresolved_high_risks: listValue(risksInput), blocking_constraints: listValue(blockersInput) }); // SPDX-License-Identifier: MIT | 将快速表单转换为产品可实现性合同。
    const commit = () => commitGuidedObject(container, answer, collect(), jsonEditor); // SPDX-License-Identifier: MIT | 提交当前产品可实现性对象。
    checkInputs.forEach((input) => input.addEventListener("change", commit)); // SPDX-License-Identifier: MIT | 在任一实现证据变化时同步答案。
    [dependenciesInput, risksInput, blockersInput].forEach((input) => input.addEventListener("input", commit)); // SPDX-License-Identifier: MIT | 在依赖或风险变化时同步答案。
    container.append(createGuidedHeader("只判断游戏本身能不能做出来", "请假设能获得合适团队与足够资金；当前缺人、缺钱会进入下方资源缺口报告，不会降低这一维分数。"), checksGrid, listGrid); // SPDX-License-Identifier: MIT | 明确产品可实现性与资源准备度的边界。
    const syncSimple = (value) => { checkInputs.forEach((input, key) => { input.checked = value[key] === true; }); dependenciesInput.value = Array.isArray(value.critical_dependencies) ? value.critical_dependencies.join("\n") : ""; risksInput.value = Array.isArray(value.unresolved_high_risks) ? value.unresolved_high_risks.join("\n") : ""; blockersInput.value = Array.isArray(value.blocking_constraints) ? value.blocking_constraints.join("\n") : ""; }; // SPDX-License-Identifier: MIT | 将专业 JSON 反向同步到产品可实现性快速控件。
    jsonEditor = addAdvancedJsonEditor(container, question, answer, syncSimple); // SPDX-License-Identifier: MIT | 添加产品可实现性专业 JSON 编辑入口。
    return container; // SPDX-License-Identifier: MIT | 返回产品可实现性编辑器。
} // SPDX-License-Identifier: MIT | 结束产品可实现性编辑器构造函数。
function buildTeamEditor(question, answer) { // SPDX-License-Identifier: MIT | 构建适合个人与专业团队的团队情况编辑器。
    const container = create("div", "guided-editor"); // SPDX-License-Identifier: MIT | 创建团队引导式编辑器根容器。
    const current = answer.value && typeof answer.value === "object" && !Array.isArray(answer.value) ? answer.value : {}; // SPDX-License-Identifier: MIT | 安全读取已有团队对象。
    const quick = create("div", "quick-actions"); // SPDX-License-Identifier: MIT | 创建团队常用预设操作区。
    const grid = create("div", "guided-grid"); // SPDX-License-Identifier: MIT | 创建团队基础字段网格。
    const sizeLabel = create("label", "guided-field"); // SPDX-License-Identifier: MIT | 创建人数输入标签。
    const sizeInput = create("input"); // SPDX-License-Identifier: MIT | 创建团队人数数值输入框。
    const availabilityLabel = create("label", "guided-field"); // SPDX-License-Identifier: MIT | 创建投入时间输入标签。
    const availabilityInput = create("input"); // SPDX-License-Identifier: MIT | 创建投入时间文本输入框。
    const rolesFieldset = create("fieldset", "choice-fieldset"); // SPDX-License-Identifier: MIT | 创建语义化已覆盖能力复选组。
    const rolesLegend = create("legend", "", "目前已覆盖哪些能力？"); // SPDX-License-Identifier: MIT | 为团队能力复选组提供问题说明。
    const rolesGrid = create("div", "choice-grid"); // SPDX-License-Identifier: MIT | 创建团队能力选项网格。
    const roleInputs = new Map(); // SPDX-License-Identifier: MIT | 保存能力名称到复选框的映射用于同步。
    let jsonEditor = null; // SPDX-License-Identifier: MIT | 保存专业 JSON 编辑器以便快速表单反向同步。
    sizeInput.type = "number"; // SPDX-License-Identifier: MIT | 限制团队人数为数值输入。
    sizeInput.min = "1"; // SPDX-License-Identifier: MIT | 防止填写零人或负数团队。
    sizeInput.step = "1"; // SPDX-License-Identifier: MIT | 限制人数按整数递增。
    sizeInput.value = Number.isFinite(Number(current.size)) && Number(current.size) > 0 ? String(Number(current.size)) : ""; // SPDX-License-Identifier: MIT | 回显有效团队人数。
    sizeInput.placeholder = "例如：1"; // SPDX-License-Identifier: MIT | 提供个人创作者人数示例。
    availabilityInput.value = typeof current.availability === "string" ? current.availability : ""; // SPDX-License-Identifier: MIT | 回显团队可投入时间说明。
    availabilityInput.placeholder = "例如：每周 20 小时；不确定可填待确认"; // SPDX-License-Identifier: MIT | 允许新手明确回答不确定。
    sizeLabel.append(create("span", "", "当前总人数"), sizeInput); // SPDX-License-Identifier: MIT | 组合团队人数标签与输入。
    availabilityLabel.append(create("span", "", "团队可投入时间"), availabilityInput); // SPDX-License-Identifier: MIT | 组合投入时间标签与输入。
    grid.append(sizeLabel, availabilityLabel); // SPDX-License-Identifier: MIT | 将基础团队字段加入网格。
    teamRoleOptions.forEach((role) => { // SPDX-License-Identifier: MIT | 为每种团队能力创建可访问复选项。
        const label = create("label", "choice-option"); // SPDX-License-Identifier: MIT | 创建单个能力选项标签。
        const input = create("input"); // SPDX-License-Identifier: MIT | 创建能力复选框。
        input.type = "checkbox"; // SPDX-License-Identifier: MIT | 设置能力选择为可多选复选框。
        input.value = role; // SPDX-License-Identifier: MIT | 保存稳定中文能力名称。
        input.checked = Array.isArray(current.roles) && current.roles.includes(role); // SPDX-License-Identifier: MIT | 回显已有能力选择。
        roleInputs.set(role, input); // SPDX-License-Identifier: MIT | 登记能力复选框供预设和高级同步使用。
        label.append(input, document.createTextNode(role)); // SPDX-License-Identifier: MIT | 组合能力复选框与可见文字。
        rolesGrid.append(label); // SPDX-License-Identifier: MIT | 将能力选项加入网格。
    }); // SPDX-License-Identifier: MIT | 结束团队能力选项构造。
    rolesFieldset.append(rolesLegend, create("p", "editor-hint", "可多选；没有团队时选择“独立创作者”。"), rolesGrid); // SPDX-License-Identifier: MIT | 组合能力问题、提示和选项。
    const collect = () => ({ size: sizeInput.value ? Number(sizeInput.value) : null, roles: [...roleInputs].filter(([, input]) => input.checked).map(([role]) => role), availability: availabilityInput.value.trim() || "待确认" }); // SPDX-License-Identifier: MIT | 将快速团队控件转换为后端兼容对象。
    const commit = () => commitGuidedObject(container, answer, collect(), jsonEditor); // SPDX-License-Identifier: MIT | 提交当前团队快速表单对象。
    const setPreset = (size, roles, availability) => { sizeInput.value = String(size); availabilityInput.value = availability; roleInputs.forEach((input, role) => { input.checked = roles.includes(role); }); commit(); }; // SPDX-License-Identifier: MIT | 应用个人或团队快捷预设并立即保存。
    quick.append(createQuickButton("我是个人创作者", () => setPreset(1, ["独立创作者"], "待确认")), createQuickButton("3 人小团队示例", () => setPreset(3, ["策划/产品", "程序/技术", "美术"], "待确认"))); // SPDX-License-Identifier: MIT | 提供两种常见团队起点降低首次填写成本。
    sizeInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在人数变化时同步结构化答案。
    availabilityInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在投入时间变化时同步结构化答案。
    roleInputs.forEach((input) => input.addEventListener("change", commit)); // SPDX-License-Identifier: MIT | 在能力选择变化时同步结构化答案。
    container.append(createGuidedHeader("快速填写团队情况", "先选择一个常见情况，再按实际情况微调；不知道的内容可以填“待确认”。"), quick, grid, rolesFieldset); // SPDX-License-Identifier: MIT | 组合团队编辑器的新手路径。
    const syncSimple = (value) => { sizeInput.value = Number(value.size) > 0 ? String(Number(value.size)) : ""; availabilityInput.value = typeof value.availability === "string" ? value.availability : ""; roleInputs.forEach((input, role) => { input.checked = Array.isArray(value.roles) && value.roles.includes(role); }); }; // SPDX-License-Identifier: MIT | 将专业团队 JSON 反向同步到快速控件。
    jsonEditor = addAdvancedJsonEditor(container, question, answer, syncSimple); // SPDX-License-Identifier: MIT | 添加团队专业 JSON 编辑入口。
    return container; // SPDX-License-Identifier: MIT | 返回团队引导式编辑器。
} // SPDX-License-Identifier: MIT | 结束团队编辑器构造函数。
function buildScheduleEditor(question, answer) { // SPDX-License-Identifier: MIT | 构建允许未知状态的周期与资金编辑器。
    const container = create("div", "guided-editor"); // SPDX-License-Identifier: MIT | 创建投入引导式编辑器根容器。
    const current = answer.value && typeof answer.value === "object" && !Array.isArray(answer.value) ? answer.value : {}; // SPDX-License-Identifier: MIT | 安全读取已有投入对象。
    const statusLabel = create("label", "guided-field guided-wide"); // SPDX-License-Identifier: MIT | 创建计划成熟度选择标签。
    const statusSelect = create("select"); // SPDX-License-Identifier: MIT | 创建计划成熟度选择器。
    const grid = create("div", "guided-grid three-columns"); // SPDX-License-Identifier: MIT | 创建周期与资金三列网格。
    const monthsInput = create("input"); // SPDX-License-Identifier: MIT | 创建开发周期数值输入。
    const budgetInput = create("input"); // SPDX-License-Identifier: MIT | 创建总预算数值输入。
    const fundingInput = create("input"); // SPDX-License-Identifier: MIT | 创建已落实资金数值输入。
    let jsonEditor = null; // SPDX-License-Identifier: MIT | 保存投入专业 JSON 编辑器引用。
    statusSelect.append(new Option("请选择", "")); // SPDX-License-Identifier: MIT | 提供未选择占位选项。
    planningStatusOptions.forEach(([value, label]) => statusSelect.append(new Option(label, value))); // SPDX-License-Identifier: MIT | 添加中文计划成熟度选项。
    statusSelect.value = typeof current.planning_status === "string" ? current.planning_status : ""; // SPDX-License-Identifier: MIT | 回显已有计划成熟度。
    [[monthsInput, "开发周期（月）", current.months, "例如：12"], [budgetInput, "计划总预算（元）", current.budget, "不知道可留空"], [fundingInput, "已落实资金（元）", current.available_funding, "没有资金填 0"]].forEach(([input, labelText, value, placeholder]) => { input.type = "number"; input.min = "0"; input.step = "1"; input.value = typeof value === "number" && Number.isFinite(value) ? String(value) : ""; input.placeholder = placeholder; const label = create("label", "guided-field"); label.append(create("span", "", labelText), input); grid.append(label); }); // SPDX-License-Identifier: MIT | 配置周期、预算和资金字段并加入网格。
    statusLabel.append(create("span", "", "目前的计划状态"), statusSelect, create("small", "", "尚未规划也可以正常提交，评分助手会把它列为待补项。")); // SPDX-License-Identifier: MIT | 组合计划状态字段和纯中文新手说明。
    const numberOrNull = (input) => input.value === "" ? null : Number(input.value); // SPDX-License-Identifier: MIT | 将空数值保留为未知而非错误地转换为零。
    const collect = () => ({ planning_status: statusSelect.value || "not_planned", months: numberOrNull(monthsInput), budget: numberOrNull(budgetInput), available_funding: numberOrNull(fundingInput) }); // SPDX-License-Identifier: MIT | 将快速投入控件转换为后端兼容对象。
    const commit = () => commitGuidedObject(container, answer, collect(), jsonEditor); // SPDX-License-Identifier: MIT | 提交当前投入快速表单对象。
    statusSelect.addEventListener("change", () => { if (statusSelect.value === "not_planned") { monthsInput.value = ""; budgetInput.value = ""; if (fundingInput.value === "") fundingInput.value = "0"; } commit(); }); // SPDX-License-Identifier: MIT | 在暂无计划时清除推测数字并保留零资金表达。
    monthsInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在周期变化时同步结构化答案。
    budgetInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在预算变化时同步结构化答案。
    fundingInput.addEventListener("input", commit); // SPDX-License-Identifier: MIT | 在已落实资金变化时同步结构化答案。
    container.append(createGuidedHeader("快速填写周期与资金", "只填已经知道的数字；不知道就留空，系统不会替你估算现金缺口。"), statusLabel, grid, create("p", "editor-note", "“总预算”是完成当前范围预计需要的钱；“已落实资金”是现在确定可用于项目的钱。")); // SPDX-License-Identifier: MIT | 组合投入编辑器的新手路径和概念解释。
    const syncSimple = (value) => { statusSelect.value = typeof value.planning_status === "string" ? value.planning_status : ""; monthsInput.value = typeof value.months === "number" ? String(value.months) : ""; budgetInput.value = typeof value.budget === "number" ? String(value.budget) : ""; fundingInput.value = typeof value.available_funding === "number" ? String(value.available_funding) : ""; }; // SPDX-License-Identifier: MIT | 将专业投入 JSON 反向同步到快速控件。
    jsonEditor = addAdvancedJsonEditor(container, question, answer, syncSimple); // SPDX-License-Identifier: MIT | 添加投入专业 JSON 编辑入口。
    return container; // SPDX-License-Identifier: MIT | 返回投入引导式编辑器。
} // SPDX-License-Identifier: MIT | 结束投入编辑器构造函数。
function buildModuleStatusEditor(question, answer) { // SPDX-License-Identifier: MIT | 构建生产模块状态矩阵与快捷预设。
    const container = create("div", "guided-editor"); // SPDX-License-Identifier: MIT | 创建模块状态引导式编辑器根容器。
    const current = answer.value && typeof answer.value === "object" && !Array.isArray(answer.value) ? answer.value : {}; // SPDX-License-Identifier: MIT | 安全读取已有模块状态对象。
    const quick = create("div", "quick-actions"); // SPDX-License-Identifier: MIT | 创建模块状态快捷操作区。
    const matrix = create("div", "module-matrix"); // SPDX-License-Identifier: MIT | 创建模块状态表格式矩阵。
    const statusSelects = new Map(); // SPDX-License-Identifier: MIT | 保存模块代码到状态选择器的映射。
    let jsonEditor = null; // SPDX-License-Identifier: MIT | 保存模块专业 JSON 编辑器引用。
    moduleDefinitions.forEach(([key, labelText]) => { // SPDX-License-Identifier: MIT | 为八个生产模块创建状态选择器。
        const row = create("label", "module-row"); // SPDX-License-Identifier: MIT | 创建单个模块状态行。
        const select = create("select"); // SPDX-License-Identifier: MIT | 创建模块成熟度选择器。
        select.append(new Option("请选择", "")); // SPDX-License-Identifier: MIT | 允许尚未说明的模块状态。
        moduleStatusOptions.forEach(([value, label]) => select.append(new Option(label, value))); // SPDX-License-Identifier: MIT | 添加统一模块成熟度选项。
        select.value = typeof current[key] === "string" ? current[key] : ""; // SPDX-License-Identifier: MIT | 回显已有模块状态。
        statusSelects.set(key, select); // SPDX-License-Identifier: MIT | 登记模块状态选择器供预设和同步使用。
        row.append(create("span", "", labelText), select); // SPDX-License-Identifier: MIT | 组合模块名称与状态选择器。
        matrix.append(row); // SPDX-License-Identifier: MIT | 将模块状态行加入矩阵。
    }); // SPDX-License-Identifier: MIT | 结束模块状态行构造。
    const collect = () => Object.fromEntries([...statusSelects].map(([key, select]) => [key, select.value || "missing"])); // SPDX-License-Identifier: MIT | 将模块矩阵转换为完整后端状态对象。
    const commit = () => commitGuidedObject(container, answer, collect(), jsonEditor); // SPDX-License-Identifier: MIT | 提交当前模块状态对象。
    const setStatuses = (values) => { statusSelects.forEach((select, key) => { select.value = values[key] || "missing"; }); commit(); }; // SPDX-License-Identifier: MIT | 应用完整模块预设并立即保存。
    quick.append(createQuickButton("一键全部暂无", () => setStatuses(Object.fromEntries(moduleDefinitions.map(([key]) => [key, "missing"])))), createQuickButton("套用可玩原型阶段示例", () => setStatuses({ core_design: "documented", prototype: "ready", ux: "planned", art: "planned", audio: "missing", qa: "planned", store_assets: "missing", compliance: "planned" }))); // SPDX-License-Identifier: MIT | 提供新手最常用的空状态与可玩原型状态预设。
    statusSelects.forEach((select) => select.addEventListener("change", commit)); // SPDX-License-Identifier: MIT | 在任一模块状态变化时同步结构化答案。
    container.append(createGuidedHeader("逐项选择制作状态", "没有开始就选“暂无”；只有经过试玩、测试或审核的成果才选“已验证”。"), quick, matrix); // SPDX-License-Identifier: MIT | 组合模块状态编辑器的新手路径。
    const syncSimple = (value) => { statusSelects.forEach((select, key) => { select.value = typeof value[key] === "string" ? value[key] : ""; }); }; // SPDX-License-Identifier: MIT | 将专业模块 JSON 反向同步到状态矩阵。
    jsonEditor = addAdvancedJsonEditor(container, question, answer, syncSimple); // SPDX-License-Identifier: MIT | 添加模块专业 JSON 编辑入口。
    return container; // SPDX-License-Identifier: MIT | 返回模块状态引导式编辑器。
} // SPDX-License-Identifier: MIT | 结束模块状态编辑器构造函数。
function buildQuestionInput(question, answer) { // SPDX-License-Identifier: MIT | 根据问卷类型构造可编辑控件。
    if (question.question_id === "genre_ids") return buildGenreEditor(question, answer); // SPDX-License-Identifier: MIT | 使用后端类型知识库渲染游戏类型复选项。
    if (question.question_id === "gameplay_features") return buildGameplayFeatureEditor(question, answer); // SPDX-License-Identifier: MIT | 使用所选类型基线辅助填写实际玩法机制。
    if (question.question_id === "innovation_axes") return buildKnowledgeOptionEditor(question, answer, innovationAxisChoicesForCurrentGenres(), "创新发生在哪些设计位置？", "选项来自当前游戏类型的知识库规则；只改题材或美术包装时不要选择核心循环。 "); // SPDX-License-Identifier: MIT | 使用后端类型资料动态生成稳定创新位置代码。
    if (question.question_id === "validation_methods") return buildKnowledgeOptionEditor(question, answer, validationMethodOptions, "准备怎样验证玩家感受到了差异？", "可多选；没有验证计划时保持为空，评分助手会按未知处理。 "); // SPDX-License-Identifier: MIT | 使用稳定验证方式代码替代自由拼写并隐藏英文产品名。
    if (question.question_id === "progression_feedback") return buildProgressionFeedbackEditor(question, answer); // SPDX-License-Identifier: MIT | 为成长反馈使用局内、局外和混合模式引导编辑器。
    if (question.question_id === "production_feasibility") return buildProductionFeasibilityEditor(question, answer); // SPDX-License-Identifier: MIT | 为产品可实现性使用与团队资金分离的引导编辑器。
    if (question.question_id === "team") return buildTeamEditor(question, answer); // SPDX-License-Identifier: MIT | 为第十三题使用团队引导式编辑器。
    if (question.question_id === "schedule") return buildScheduleEditor(question, answer); // SPDX-License-Identifier: MIT | 为第十四题使用投入引导式编辑器。
    if (question.question_id === "module_status") return buildModuleStatusEditor(question, answer); // SPDX-License-Identifier: MIT | 为第十六题使用模块状态矩阵。
    let input; // SPDX-License-Identifier: MIT | 声明即将创建的控件变量。
    if (question.question_id === "development_stage" || question.question_id === "business_model") { // SPDX-License-Identifier: MIT | 对规则枚举使用选择器避免拼写错误。
        input = create("select"); // SPDX-License-Identifier: MIT | 创建枚举选择控件。
        input.append(new Option("请选择", "")); // SPDX-License-Identifier: MIT | 添加未填写占位选项。
        const options = question.question_id === "development_stage" ? stageOptions : businessOptions; // SPDX-License-Identifier: MIT | 选择对应规则枚举集合。
        options.forEach(([value, label]) => input.append(new Option(label, value))); // SPDX-License-Identifier: MIT | 仅展示自然中文标签并把稳定代码保留在不可见选项值中。
        input.value = typeof answer.value === "string" ? answer.value : ""; // SPDX-License-Identifier: MIT | 回显有效字符串枚举答案。
    } else if (question.answer_type === "boolean") { // SPDX-License-Identifier: MIT | 为布尔问题创建三态选择器。
        input = create("select"); // SPDX-License-Identifier: MIT | 创建布尔选择控件。
        input.append(new Option("请选择", ""), new Option("是", "true"), new Option("否", "false")); // SPDX-License-Identifier: MIT | 添加未知、是和否选项。
        input.value = answer.value === true ? "true" : answer.value === false ? "false" : ""; // SPDX-License-Identifier: MIT | 回显布尔答案或未知状态。
    } else { // SPDX-License-Identifier: MIT | 为文本、列表和对象问题创建多行编辑器。
        input = create("textarea"); // SPDX-License-Identifier: MIT | 创建适合长答案的多行控件。
        input.value = formatAnswerValue(question, answer.value); // SPDX-License-Identifier: MIT | 将结构化答案转换为可编辑文本。
        input.placeholder = placeholderFor(question); // SPDX-License-Identifier: MIT | 提供类型和格式示例。
    } // SPDX-License-Identifier: MIT | 结束问题控件类型分支。
    input.id = `answer-${question.question_id}`; // SPDX-License-Identifier: MIT | 设置稳定控件标识方便调试和自动化。
    input.setAttribute("aria-label", question.prompt); // SPDX-License-Identifier: MIT | 为动态控件提供可访问名称。
    input.addEventListener("input", () => { // SPDX-License-Identifier: MIT | 将用户编辑同步到答案信封。
        answer.value = parseInputValue(question, input.value); // SPDX-License-Identifier: MIT | 按登记题型解析当前控件值。
        answer.source = "creator"; // SPDX-License-Identifier: MIT | 用户修改后将答案来源标记为创作者。
        answer.confidence = 1; // SPDX-License-Identifier: MIT | 创作者直接输入使用确定来源置信度。
        answer.evidence_refs = []; // SPDX-License-Identifier: MIT | 用户改写后清除不再保证适用的 AI 资料引用。
        answer.creator_confirmed = false; // SPDX-License-Identifier: MIT | 修改答案后要求重新确认。
        const parent = input.closest(".question-control"); // SPDX-License-Identifier: MIT | 获取当前问题控件容器以局部更新元数据。
        const checkbox = parent?.querySelector('.confirm-check input[type="checkbox"]'); // SPDX-License-Identifier: MIT | 查找当前答案确认复选框。
        const source = parent?.querySelector(".confirm-row > span"); // SPDX-License-Identifier: MIT | 查找当前答案来源说明。
        if (checkbox) checkbox.checked = false; // SPDX-License-Identifier: MIT | 在编辑后立即取消视觉确认状态。
        if (source) source.textContent = "来源：创作者 · 置信 1.00"; // SPDX-License-Identifier: MIT | 在编辑后立即更新答案来源说明。
        updateProgress(); // SPDX-License-Identifier: MIT | 在不重建控件的情况下刷新问卷进度。
    }); // SPDX-License-Identifier: MIT | 结束答案编辑监听器。
    return input; // SPDX-License-Identifier: MIT | 返回完成配置的答案控件。
} // SPDX-License-Identifier: MIT | 结束问题控件构造函数。
function formatAnswerValue(question, value) { // SPDX-License-Identifier: MIT | 将答案值转换为控件文本。
    if (value === null || value === undefined) return ""; // SPDX-License-Identifier: MIT | 未知答案显示为空输入。
    if (question.answer_type === "list") return Array.isArray(value) ? value.join("\n") : ""; // SPDX-License-Identifier: MIT | 将列表按每行一项展示。
    if (question.answer_type === "object") return typeof value === "object" ? JSON.stringify(value, null, 2) : ""; // SPDX-License-Identifier: MIT | 将对象格式化为可读 JSON。
    return String(value); // SPDX-License-Identifier: MIT | 将普通文本或数字转换为字符串。
} // SPDX-License-Identifier: MIT | 结束答案格式化函数。
function parseInputValue(question, value) { // SPDX-License-Identifier: MIT | 按问题类型解析用户输入。
    if (question.answer_type === "boolean") return value === "true" ? true : value === "false" ? false : null; // SPDX-License-Identifier: MIT | 将选择器字符串转为 JSON 布尔值。
    if (question.answer_type === "list") return value.split(/\r?\n|，|,/).map((item) => item.trim()).filter(Boolean); // SPDX-License-Identifier: MIT | 将换行或逗号分隔文本解析为非空字符串列表。
    if (question.answer_type === "object") { try { return value.trim() ? JSON.parse(value) : null; } catch { return value; } } // SPDX-License-Identifier: MIT | 将有效 JSON 解析为对象并保留无效文本供客户端校验。
    if (question.answer_type === "number") return value.trim() === "" ? null : Number(value); // SPDX-License-Identifier: MIT | 将数值输入转换为 JSON 数字。
    return value.trim(); // SPDX-License-Identifier: MIT | 对普通文本去除首尾空白。
} // SPDX-License-Identifier: MIT | 结束答案解析函数。
function placeholderFor(question) { // SPDX-License-Identifier: MIT | 为不同题型生成清晰输入说明。
    if (question.question_id === "genre_ids") return "请选择上方中文游戏类型"; // SPDX-License-Identifier: MIT | 避免向新手展示内部类型代码。
    if (question.question_id === "gameplay_features") return "每行填写一个实际玩法"; // SPDX-License-Identifier: MIT | 使用中文自然语言说明玩法输入格式。
    if (question.question_id === "innovation_features") return "每行一个具体变化，例如：元素组合会改变敌人的行为"; // SPDX-License-Identifier: MIT | 用中文实例说明具体创新机制。
    if (question.question_id === "validation_methods") return "请选择上方中文验证方式"; // SPDX-License-Identifier: MIT | 避免向新手展示内部验证代码。
    if (question.answer_type === "list") return "每行填写一项"; // SPDX-License-Identifier: MIT | 说明列表题输入格式。
    if (question.answer_type === "object") return JSON.stringify(objectExamples[question.question_id] || { note: "请使用 JSON 对象" }, null, 2); // SPDX-License-Identifier: MIT | 提供对象题合法 JSON 示例。
    return "请填写具体、可验证的答案"; // SPDX-License-Identifier: MIT | 提供普通文本题通用提示。
} // SPDX-License-Identifier: MIT | 结束占位提示函数。
function sourceName(source) { // SPDX-License-Identifier: MIT | 将答案来源代码转换为中文标签。
    return { creator: "创作者", ai_prefill: "智能助手代填", document_extract: "方案提取", demo_extract: "可运行版本提取" }[source] || "未知"; // SPDX-License-Identifier: MIT | 返回登记来源名称或未知降级值。
} // SPDX-License-Identifier: MIT | 结束来源名称函数。
function runStatusName(status) { // SPDX-License-Identifier: MIT | 将运行状态内部代码转换为创作者可理解的中文。
    return { pending: "等待处理", running: "正在分析", completed: "诊断完成", needs_creator_action: "需要补充资料", failed: "本次诊断未完成" }[status] || "状态暂不可用"; // SPDX-License-Identifier: MIT | 返回登记状态名称并避免直接泄露接口代码。
} // SPDX-License-Identifier: MIT | 结束运行状态名称函数。
function hasValue(value) { // SPDX-License-Identifier: MIT | 判断答案是否具有可提交内容。
    if (typeof value === "string") return value.trim().length > 0; // SPDX-License-Identifier: MIT | 纯空白字符串不算已填写。
    if (Array.isArray(value)) return value.length > 0; // SPDX-License-Identifier: MIT | 非空列表算已填写。
    if (value && typeof value === "object") return Object.keys(value).length > 0; // SPDX-License-Identifier: MIT | 非空对象算已填写。
    return value === true || value === false || typeof value === "number"; // SPDX-License-Identifier: MIT | 保留合法布尔值和数字零。
} // SPDX-License-Identifier: MIT | 结束答案存在性判断。
function updateProgress() { // SPDX-License-Identifier: MIT | 更新问卷填写和关键确认完成度。
    const filled = state.questions.filter((question) => hasValue(state.answers[question.question_id]?.value)).length; // SPDX-License-Identifier: MIT | 统计全部已填写问题数量。
    const required = state.questions.filter((question) => question.required); // SPDX-License-Identifier: MIT | 收集所有服务端标记的关键问题。
    const confirmed = required.filter((question) => hasValue(state.answers[question.question_id]?.value) && state.answers[question.question_id]?.creator_confirmed === true).length; // SPDX-License-Identifier: MIT | 统计已填写且确认的关键答案。
    questionProgress.textContent = `已填写 ${filled}/${state.questions.length} · 关键确认 ${confirmed}/${required.length}`; // SPDX-License-Identifier: MIT | 显示可理解的问卷完成进度。
    runButton.disabled = !state.artifacts.length || confirmed !== required.length; // SPDX-License-Identifier: MIT | 关键答案全部确认后才开放诊断提交。
} // SPDX-License-Identifier: MIT | 结束问卷进度更新。
confirmFilledButton.addEventListener("click", () => { // SPDX-License-Identifier: MIT | 批量确认当前所有已填写答案。
    state.questions.forEach((question) => { if (hasValue(state.answers[question.question_id]?.value)) state.answers[question.question_id].creator_confirmed = true; }); // SPDX-License-Identifier: MIT | 只确认具有实际内容的答案。
    renderQuestions(); // SPDX-License-Identifier: MIT | 刷新全部确认控件和进度。
    showToast("已确认所有当前已填写答案；后续修改会自动取消对应确认。 "); // SPDX-License-Identifier: MIT | 解释批量确认的后续行为。
}); // SPDX-License-Identifier: MIT | 结束批量确认按钮监听器。
runButton.addEventListener("click", async () => { // SPDX-License-Identifier: MIT | 提交冻结输入并执行评分诊断。
    const validationError = validateSubmission(); // SPDX-License-Identifier: MIT | 在网络请求前执行可操作的客户端验证。
    if (validationError) { showToast(validationError, true); return; } // SPDX-License-Identifier: MIT | 验证失败时停止提交并提示用户。
    runButton.disabled = true; // SPDX-License-Identifier: MIT | 防止重复创建提交和运行。
    try { // SPDX-License-Identifier: MIT | 捕获提交或评分执行错误。
        const submission = await api("/v1/submissions", { method: "POST", body: JSON.stringify({ project_id: projectId.value.trim(), version: projectVersion.value.trim(), title: projectTitle.value.trim(), artifact_ids: state.artifacts.map((item) => item.artifact_id), questionnaire: state.answers }) }); // SPDX-License-Identifier: MIT | 创建只引用可信资料标识的冻结提交。
        state.submissionId = submission.submission_id; // SPDX-License-Identifier: MIT | 保存不可变提交标识用于状态展示。
        showToast("答案已提交，评分助手正在生成诊断。 "); // SPDX-License-Identifier: MIT | 用自然中文播报评分运行已开始。
        const run = await api("/v1/runs", { method: "POST", body: JSON.stringify({ submission_id: state.submissionId }) }); // SPDX-License-Identifier: MIT | 创建并同步执行一次评分运行。
        state.runId = run.run_id; // SPDX-License-Identifier: MIT | 保存运行标识用于刷新和审计。
        state.run = run; // SPDX-License-Identifier: MIT | 保存当前运行快照。
        unlock("report"); // SPDX-License-Identifier: MIT | 开放诊断报告步骤。
        refreshButton.disabled = false; // SPDX-License-Identifier: MIT | 开放运行状态刷新。
        auditButton.disabled = false; // SPDX-License-Identifier: MIT | 开放运行审计查询。
        renderRun(run); // SPDX-License-Identifier: MIT | 根据终态或错误渲染报告。
        byId("report").scrollIntoView({ behavior: "smooth", block: "start" }); // SPDX-License-Identifier: MIT | 将视图移动到报告步骤。
    } catch (error) { // SPDX-License-Identifier: MIT | 处理服务端输入阻塞或执行失败。
        showToast(error.message, true); // SPDX-License-Identifier: MIT | 显示可修复错误而不暴露堆栈。
        runButton.disabled = false; // SPDX-License-Identifier: MIT | 允许用户修正后重新提交。
    } // SPDX-License-Identifier: MIT | 结束运行异常处理。
}); // SPDX-License-Identifier: MIT | 结束诊断运行按钮监听器。
function validateSubmission() { // SPDX-License-Identifier: MIT | 检查提交前端可发现的合同错误。
    if (!projectId.value.trim() || !projectVersion.value.trim() || !projectTitle.value.trim()) return "请完整填写记录编号、方案版本和项目名称。"; // SPDX-License-Identifier: MIT | 检查冻结提交基础标识。
    if (!state.artifacts.some((item) => ["design_document", "pitch_deck", "spreadsheet"].includes(item.kind))) return "至少上传一份方案文件。"; // SPDX-License-Identifier: MIT | 检查规则要求的方案资料。
    for (const question of state.questions) { // SPDX-License-Identifier: MIT | 遍历问卷执行题型与确认校验。
        const answer = state.answers[question.question_id]; // SPDX-License-Identifier: MIT | 读取当前题目答案信封。
        if (question.required && (!hasValue(answer?.value) || answer?.creator_confirmed !== true)) return `关键答案尚未填写并确认：${question.prompt}`; // SPDX-License-Identifier: MIT | 阻止未确认关键答案进入评分。
        if (question.answer_type === "object" && hasValue(answer?.value) && (typeof answer.value !== "object" || Array.isArray(answer.value))) return `对象题必须填写有效 JSON：${question.prompt}`; // SPDX-License-Identifier: MIT | 阻止无效 JSON 对象题提交。
    } // SPDX-License-Identifier: MIT | 结束问卷合同校验。
    return ""; // SPDX-License-Identifier: MIT | 返回空字符串表示客户端验证通过。
} // SPDX-License-Identifier: MIT | 结束提交验证函数。
refreshButton.addEventListener("click", async () => { // SPDX-License-Identifier: MIT | 刷新当前评分运行状态。
    if (!state.runId) return; // SPDX-License-Identifier: MIT | 没有运行标识时不发送请求。
    try { state.run = await api(`/v1/runs/${encodeURIComponent(state.runId)}`); renderRun(state.run); showToast("运行状态已刷新。 "); } catch (error) { showToast(error.message, true); } // SPDX-License-Identifier: MIT | 读取运行、刷新报告并处理查询错误。
}); // SPDX-License-Identifier: MIT | 结束运行刷新监听器。
auditButton.addEventListener("click", async () => { // SPDX-License-Identifier: MIT | 查询并显示当前运行审计时间线。
    if (!state.runId) return; // SPDX-License-Identifier: MIT | 没有运行标识时不发送请求。
    try { const result = await api(`/v1/runs/${encodeURIComponent(state.runId)}/audit`); renderAudit(result.events || []); auditDialog.showModal(); } catch (error) { showToast(error.message, true); } // SPDX-License-Identifier: MIT | 加载审计事件、打开对话框并处理错误。
}); // SPDX-License-Identifier: MIT | 结束审计按钮监听器。
byId("closeAuditButton").addEventListener("click", () => auditDialog.close()); // SPDX-License-Identifier: MIT | 允许用户关闭审计对话框。
function renderRun(run) { // SPDX-License-Identifier: MIT | 根据运行状态渲染诊断报告或阻塞信息。
    reportContent.replaceChildren(); // SPDX-License-Identifier: MIT | 清除旧报告内容。
    if (run.status !== "completed" || !run.report) { // SPDX-License-Identifier: MIT | 对未完成或失败运行显示结构化状态。
        const placeholder = create("div", "report-placeholder"); // SPDX-License-Identifier: MIT | 创建运行状态占位区域。
        const statusName = runStatusName(run.status); // SPDX-License-Identifier: MIT | 读取当前运行状态的中文显示名称。
        placeholder.append(create("span", "", statusName), create("strong", "", `运行状态：${statusName}`), create("p", "", formatRunError(run.error))); // SPDX-License-Identifier: MIT | 显示状态和创作者可操作错误。
        reportContent.append(placeholder); // SPDX-License-Identifier: MIT | 将状态占位加入报告。
        showToast(run.status === "needs_creator_action" ? "资料或问卷需要修改，请创建新提交。" : `运行状态：${statusName}`, run.status === "failed"); // SPDX-License-Identifier: MIT | 播报运行终态语义。
        return; // SPDX-License-Identifier: MIT | 未完成运行不继续渲染评分报告。
    } // SPDX-License-Identifier: MIT | 结束非完成状态分支。
    renderReport(run.report); // SPDX-License-Identifier: MIT | 渲染完整诊断报告。
    showToast(`诊断完成：${run.report.rating.assessment_result}`); // SPDX-License-Identifier: MIT | 播报最终初筛结论。
} // SPDX-License-Identifier: MIT | 结束运行渲染函数。
function formatRunError(error) { // SPDX-License-Identifier: MIT | 将结构化运行错误转换为可读文字。
    if (!error) return "评分助手正在处理或尚未返回详细信息。"; // SPDX-License-Identifier: MIT | 为无错误详情状态提供纯中文降级说明。
    if (Array.isArray(error.issues)) return error.issues.join("；"); // SPDX-License-Identifier: MIT | 合并待创作者行动问题列表。
    return error.message || error.code || JSON.stringify(error); // SPDX-License-Identifier: MIT | 选择明确错误说明或结构化降级文本。
} // SPDX-License-Identifier: MIT | 结束运行错误格式化。
function renderReport(report) { // SPDX-License-Identifier: MIT | 使用安全 DOM 节点展示完整 Agent 诊断结果。
    const rating = report.rating || {}; // SPDX-License-Identifier: MIT | 读取评分部分并提供空对象降级。
    const hero = create("section", "report-hero"); // SPDX-License-Identifier: MIT | 创建评分结论摘要区。
    const badge = create("div", "rating-badge", rating.assessment_result || "?"); // SPDX-License-Identifier: MIT | 显示初筛等级而不冒充 BAS 分数。
    const summary = create("div"); // SPDX-License-Identifier: MIT | 创建评分文字摘要容器。
    summary.append(create("h3", "", reportTitle(rating.assessment_result)), create("p", "", `项目 ${rating.project_id || "-"} · 版本 ${rating.project_version || "-"}`)); // SPDX-License-Identifier: MIT | 新手摘要只显示项目和版本，内部规则版本移入折叠信息。
    const metrics = create("div", "metric-row"); // SPDX-License-Identifier: MIT | 创建关键指标行。
    metrics.append(create("span", "metric", `资料可靠度 ${Math.round(Number(rating.confidence || 0) * 100)}%`), create("span", "metric", `人工复核 ${rating.needs_human_review ? "需要" : "暂不需要"}`), create("span", "metric", `真人评分申请 ${rating.human_review_ready ? "已达到基础条件" : "暂不可申请"}`)); // SPDX-License-Identifier: MIT | 同时清楚展示真人评分的独立完成度资格，避免创作者把自动诊断与 BAS 混淆。
    summary.append(metrics); // SPDX-License-Identifier: MIT | 将指标加入摘要。
    hero.append(badge, summary); // SPDX-License-Identifier: MIT | 组合评分摘要区。
    reportContent.append(hero); // SPDX-License-Identifier: MIT | 将评分摘要加入报告。
    const grid = create("div", "report-grid"); // SPDX-License-Identifier: MIT | 创建报告双栏内容网格。
    const comparison = rating.knowledge_comparison || {}; // SPDX-License-Identifier: MIT | 读取类型知识库比对结果并提供空对象降级。
    const crowdedPatterns = (comparison.crowded_patterns || []).map((pattern) => Array.isArray(pattern) ? pattern.map(featureName).join(" + ") : featureName(pattern)); // SPDX-License-Identifier: MIT | 将命中的机制组合转换为中文可读文本。
    const weightSummary = (comparison.dimension_weights || []).map((pair) => Array.isArray(pair) ? `${dimensionNames[pair[0]] || pair[0]} ${Math.round(Number(pair[1]) * 100)}%` : String(pair)); // SPDX-License-Identifier: MIT | 将当前类型的动态九维权重转换为百分比摘要。
    const comparisonItems = [`匹配类型：${(comparison.matched_genres || []).map(genreName).join("、") || "尚未识别"}`, `同质化风险：${comparison.homogeneity_risk || "未知"}；差异候选分：${comparison.differentiation_score ?? "-"}/4`, `采用的类型常规玩法：${(comparison.matched_baseline_features || []).map(featureName).join("、") || "暂未识别"}`, `命中常见同质化组合：${crowdedPatterns.join("；") || "没有"}`, `项目声明的差异机制：${(comparison.declared_innovation_features || []).map(featureName).join("、") || "尚未填写"}`, `其中属于类型常规的机制：${(comparison.baseline_reuse_features || []).map(featureName).join("、") || "没有"}`, `对标作品：${(comparison.reference_games || []).join("、") || "尚未填写"}`, `验证方式：${(comparison.validation_methods || []).map((item) => optionName(item, validationMethodOptions)).join("、") || "尚未填写"}`, `本类型评分重点：${weightSummary.join("；") || "各维度采用默认权重"}`]; // SPDX-License-Identifier: MIT | 使用中文类型、机制和验证方式生成新手可读的知识库比对说明。
    grid.append(renderTextList("类型知识库与同质化比对", comparisonItems, true)); // SPDX-License-Identifier: MIT | 将类型、相似组合、创新候选和权重展示在报告首位。
    grid.append(renderDna(rating.game_dna || {})); // SPDX-License-Identifier: MIT | 加入九维评分分区。
    const readiness = rating.resource_readiness || {}; // SPDX-License-Identifier: MIT | 读取不计入九维的当前资源准备度。
    grid.append(renderTextList("当前资源准备度（不计入九维）", [`准备度 ${readiness.score ?? 0}/4`, readiness.rationale || "团队、周期和资金信息尚未填写；这不会改变游戏本身的产品可实现性分数。"], true)); // SPDX-License-Identifier: MIT | 明确展示缺人缺钱只用于缺口诊断。
    const priorityActions = [...new Set([...(rating.blocking_issues || []), ...(rating.improvement_actions || []).map((item) => String(item).replace(/^修复：/, ""))])]; // SPDX-License-Identifier: MIT | 合并阻塞和行动并移除重复的“修复”前缀。
    grid.append(renderTextList("优先改进", priorityActions, false)); // SPDX-License-Identifier: MIT | 只向新手展示去重后的可执行改进列表。
    grid.append(renderCardSection("缺失制作模块", report.missing_modules || [], (item) => [item.name, `${item.priority} · ${item.reason}`])); // SPDX-License-Identifier: MIT | 加入缺失模块诊断。
    grid.append(renderCardSection("团队角色缺口", report.missing_roles || [], (item) => [item.role, `${item.priority} · ${item.timing} · ${item.engagement}`])); // SPDX-License-Identifier: MIT | 加入团队角色诊断。
    grid.append(renderCardSection("能力需求", report.capability_requirements || [], (item) => [item.name, `${friendlyText(item.minimum_level)} · ${item.integration_context}`], true)); // SPDX-License-Identifier: MIT | 新手界面隐藏内部能力代码，只展示能力等级和使用场景。
    grid.append(renderCardSection("投入缺口", report.investment_needs || [], (item) => [internalNames[item.category] || item.category, `${formatMoney(item.amount_gap, item.unit)} · ${item.reason}`])); // SPDX-License-Identifier: MIT | 使用中文类别展示创作者数字计算的投入差额。
    grid.append(renderTimelineSection("制作路线", report.production_roadmap || [], true)); // SPDX-License-Identifier: MIT | 加入完整生产阶段路线。
    Object.entries(report.release_roadmap || {}).forEach(([platform, steps]) => grid.append(renderTimelineSection(`${platform.toUpperCase()} 上架路线`, steps || [], true))); // SPDX-License-Identifier: MIT | 按目标平台加入上架步骤。
    grid.append(renderTextList("假设与能力边界", [...(report.assumptions || []), ...(rating.limitations || [])], true)); // SPDX-License-Identifier: MIT | 加入未知假设和评分能力边界。
    const professional = create("details", "report-section full advanced-json"); // SPDX-License-Identifier: MIT | 创建默认折叠的专业运行信息区域。
    professional.append(create("summary", "", "专业信息与内部编号"), renderTextList("内部记录", [`评分规则：${rating.rubric_version || "-"}`, `知识库：${comparison.knowledge_base_version || "-"}`, `运行编号：${rating.run_id || state.runId}`, comparison.rationale || "暂无内部比对说明"], true)); // SPDX-License-Identifier: MIT | 将规则版本、运行编号和内部比对参数移出新手主视图。
    grid.append(professional); // SPDX-License-Identifier: MIT | 将折叠专业信息加入报告末尾。
    reportContent.append(grid); // SPDX-License-Identifier: MIT | 将全部报告分区加入页面。
} // SPDX-License-Identifier: MIT | 结束完整报告渲染。
function reportTitle(result) { // SPDX-License-Identifier: MIT | 将初筛代码转换为不夸大的中文说明。
    return { D: "基础门槛未通过", C: "可继续补强与验证", B_GATE: "可以进入下一轮真人验证" }[result] || "诊断结果"; // SPDX-License-Identifier: MIT | 使用创作者能理解的语言解释三类内部结论。
} // SPDX-License-Identifier: MIT | 结束报告标题函数。
function renderDna(dna) { // SPDX-License-Identifier: MIT | 创建九维评分可视化分区。
    const section = create("section", "report-section"); // SPDX-License-Identifier: MIT | 创建九维报告分区。
    section.append(create("h3", "", "游戏九维结构")); // SPDX-License-Identifier: MIT | 添加九维分区标题。
    const list = create("div", "dna-list"); // SPDX-License-Identifier: MIT | 创建九维条目列表。
    Object.entries(dna).forEach(([name, score]) => { // SPDX-License-Identifier: MIT | 遍历每个稳定维度分数。
        const item = create("div", "dna-item"); // SPDX-License-Identifier: MIT | 创建单个维度行。
        const bar = create("div", "bar"); // SPDX-License-Identifier: MIT | 创建分数比例轨道。
        const fill = create("span"); // SPDX-License-Identifier: MIT | 创建分数比例填充。
        fill.style.width = `${Math.max(0, Math.min(4, Number(score))) * 25}%`; // SPDX-License-Identifier: MIT | 将零到四分安全转换为百分比宽度。
        bar.append(fill); // SPDX-License-Identifier: MIT | 将分数填充加入轨道。
        item.append(create("span", "", dimensionNames[name] || name), bar, create("b", "", score)); // SPDX-License-Identifier: MIT | 组合维度名称、进度和分数。
        list.append(item); // SPDX-License-Identifier: MIT | 将维度行加入九维列表。
    }); // SPDX-License-Identifier: MIT | 结束维度分数遍历。
    section.append(list); // SPDX-License-Identifier: MIT | 将九维列表加入分区。
    return section; // SPDX-License-Identifier: MIT | 返回九维评分分区。
} // SPDX-License-Identifier: MIT | 结束九维分区渲染。
function renderTextList(title, items, full) { // SPDX-License-Identifier: MIT | 创建纯文本诊断列表分区。
    const section = create("section", `report-section${full ? " full" : ""}`); // SPDX-License-Identifier: MIT | 创建可选全宽报告分区。
    section.append(create("h3", "", title)); // SPDX-License-Identifier: MIT | 添加列表分区标题。
    const list = create("ul", "list-clean"); // SPDX-License-Identifier: MIT | 创建语义化无序列表。
    (items.length ? items : ["暂无"]).forEach((item) => list.append(create("li", "", friendlyText(item)))); // SPDX-License-Identifier: MIT | 翻译内部代码后使用纯文本显示每个诊断条目。
    section.append(list); // SPDX-License-Identifier: MIT | 将列表加入报告分区。
    return section; // SPDX-License-Identifier: MIT | 返回纯文本报告分区。
} // SPDX-License-Identifier: MIT | 结束文本列表渲染。
function renderCardSection(title, items, mapper, full = false) { // SPDX-License-Identifier: MIT | 创建结构化诊断卡片分区。
    const section = create("section", `report-section${full ? " full" : ""}`); // SPDX-License-Identifier: MIT | 创建可选全宽卡片分区。
    section.append(create("h3", "", title)); // SPDX-License-Identifier: MIT | 添加卡片分区标题。
    const list = create("div", "card-list"); // SPDX-License-Identifier: MIT | 创建卡片列表容器。
    if (!items.length) list.append(create("p", "empty-state", "当前没有识别到该类缺口。")); // SPDX-License-Identifier: MIT | 在无缺口时显示明确空状态。
    items.forEach((item) => { const [name, detail] = mapper(item); const card = create("div", "mini-card"); card.append(create("strong", "", friendlyText(name)), create("p", "", friendlyText(detail))); list.append(card); }); // SPDX-License-Identifier: MIT | 翻译内部代码后使用文本节点生成结构化诊断卡片。
    section.append(list); // SPDX-License-Identifier: MIT | 将卡片列表加入报告分区。
    return section; // SPDX-License-Identifier: MIT | 返回卡片报告分区。
} // SPDX-License-Identifier: MIT | 结束卡片分区渲染。
function renderTimelineSection(title, steps, full) { // SPDX-License-Identifier: MIT | 创建制作或上架流程时间线分区。
    const section = create("section", `report-section${full ? " full" : ""}`); // SPDX-License-Identifier: MIT | 创建可选全宽时间线分区。
    section.append(create("h3", "", title)); // SPDX-License-Identifier: MIT | 添加时间线标题。
    const timeline = create("div", "timeline"); // SPDX-License-Identifier: MIT | 创建时间线容器。
    steps.forEach((step, index) => { const item = create("div", "timeline-item"); const copy = create("div"); copy.append(create("strong", "", friendlyText(step.name)), create("p", "", friendlyText(step.objective)), create("p", "", `完成标准：${friendlyText((step.exit_criteria || []).join("；"))}`)); item.append(create("span", "timeline-index", step.order || index + 1), copy); timeline.append(item); }); // SPDX-License-Identifier: MIT | 使用中文友好文本显示流程名称、目标和完成标准。
    section.append(timeline); // SPDX-License-Identifier: MIT | 将时间线加入报告分区。
    return section; // SPDX-License-Identifier: MIT | 返回流程时间线分区。
} // SPDX-License-Identifier: MIT | 结束时间线分区渲染。
function formatMoney(amount, unit) { // SPDX-License-Identifier: MIT | 格式化投入差额并保留服务端币种。
    if (amount === null || amount === undefined) return "金额待补充"; // SPDX-License-Identifier: MIT | 未知金额明确显示为待补充。
    return `${new Intl.NumberFormat("zh-CN").format(Number(amount))} ${unit || ""}`.trim(); // SPDX-License-Identifier: MIT | 使用中文数字分组格式显示金额。
} // SPDX-License-Identifier: MIT | 结束金额格式化。
function renderAudit(events) { // SPDX-License-Identifier: MIT | 安全渲染追加式运行审计事件。
    auditContent.replaceChildren(); // SPDX-License-Identifier: MIT | 清除旧审计事件节点。
    if (!events.length) auditContent.append(create("p", "empty-state", "暂无审计事件。")); // SPDX-License-Identifier: MIT | 在无事件时显示明确空状态。
    events.forEach((event) => { const card = create("div", "audit-event"); card.append(create("strong", "", event.event_type), create("p", "", event.created_at), create("p", "", JSON.stringify(event.payload))); auditContent.append(card); }); // SPDX-License-Identifier: MIT | 使用纯文本显示事件类型、时间和结构化载荷。
} // SPDX-License-Identifier: MIT | 结束审计事件渲染。
renderArtifacts(); // SPDX-License-Identifier: MIT | 初始化资料列表空状态和按钮状态。
