// SPDX-License-Identifier: MIT | 本文件新增真人评分门槛逻辑采用 MIT 许可，未引入 GPL 代码。
const state = {
  view: "home",
  grade: "S",
  projectFilter: "全部项目",
  assetTab: "创作项目",
  activeRoleIndex: 0,
  wished: new Set(["星环余烬"]),
};

const HUMAN_REVIEW_PROGRESS_THRESHOLD = 80; // SPDX-License-Identifier: MIT | 真人评分最低完成度固定为 80%。

const roles = ["创作者", "能力人才", "投资参与者", "玩家"];

const games = [
  {
    id: "ember-ring",
    title: "星环余烬",
    english: "EMBER RING",
    grade: "S",
    rank: "月榜 #01",
    genre: ["动作 Roguelite", "Demo", "PC"],
    dna: "高压近战 × 元素融合 × 20 分钟构筑循环",
    score: "9.2",
    wishes: "18.4k",
    color: "#d8ff58",
    cover: "linear-gradient(145deg,#272f1d,#0b0d0c 62%)",
    art: "radial-gradient(circle at 72% 32%, #d8ff58 0 5%, transparent 6%), radial-gradient(circle at 72% 32%, transparent 0 18%, #657928 19% 21%, transparent 22%), linear-gradient(125deg, transparent 48%, #90ac37 49% 51%, transparent 52%)",
  },
  {
    id: "neon-tide",
    title: "霓潮协议",
    english: "NEON TIDE",
    grade: "S",
    rank: "月榜 #02",
    genre: ["叙事解谜", "正式版", "PC"],
    dna: "城市记忆 × 非线性调查 × 多结局因果网",
    score: "9.0",
    wishes: "11.7k",
    color: "#59ddff",
    cover: "linear-gradient(145deg,#132b33,#0d1014 66%)",
    art: "linear-gradient(90deg, transparent 34%, #59ddff 35% 37%, transparent 38%), linear-gradient(20deg, transparent 57%, #8d72ff 58% 61%, transparent 62%), radial-gradient(ellipse at 50% 110%, #295f6d 0 28%, transparent 29%)",
  },
  {
    id: "moss-oracle",
    title: "苔原神谕",
    english: "MOSS ORACLE",
    grade: "S",
    rank: "年榜 #08",
    genre: ["经营模拟", "正式版", "移动端"],
    dna: "生态经营 × 温和叙事 × 社区共同决策",
    score: "8.9",
    wishes: "9.5k",
    color: "#56e29f",
    cover: "linear-gradient(145deg,#173328,#0b1210 68%)",
    art: "radial-gradient(ellipse at 28% 42%, #56e29f 0 8%, transparent 9%), radial-gradient(ellipse at 62% 68%, #2a7452 0 15%, transparent 16%), linear-gradient(160deg, transparent 52%, #3b8a65 53% 56%, transparent 57%)",
  },
  {
    id: "paper-moon",
    title: "纸月旅人",
    english: "PAPER MOON",
    grade: "S",
    rank: "新品 #03",
    genre: ["平台冒险", "Demo", "PC"],
    dna: "折纸世界 × 重力切换 × 无对白叙事",
    score: "8.8",
    wishes: "7.2k",
    color: "#ffad58",
    cover: "linear-gradient(145deg,#3a291d,#130f0d 68%)",
    art: "linear-gradient(35deg, transparent 42%, #ffad58 43% 48%, transparent 49%), linear-gradient(145deg, transparent 52%, #8d72ff 53% 56%, transparent 57%), radial-gradient(circle at 73% 28%, #ffe0ae 0 8%, transparent 9%)",
  },
  {
    id: "gravity-mail",
    title: "引力邮局",
    english: "GRAVITY POST",
    grade: "A",
    rank: "月榜 #05",
    genre: ["休闲解谜", "正式版", "移动端"],
    dna: "星球投递 × 轨道计算 × 轻量收集",
    score: "8.6",
    wishes: "6.4k",
    color: "#8d72ff",
    cover: "linear-gradient(145deg,#26203f,#0d0d13 68%)",
    art: "radial-gradient(circle at 35% 36%, #8d72ff 0 7%, transparent 8%), radial-gradient(circle at 65% 63%, #ff6cae 0 10%, transparent 11%), radial-gradient(ellipse at 50% 50%, transparent 0 28%, #6a55c9 29% 31%, transparent 32%)",
  },
  {
    id: "deep-bloom",
    title: "深海花期",
    english: "DEEP BLOOM",
    grade: "A",
    rank: "新品 #06",
    genre: ["探索生存", "Demo", "PC"],
    dna: "深海基地 × 生物共生 × 无战斗探索",
    score: "8.4",
    wishes: "5.8k",
    color: "#59ddff",
    cover: "linear-gradient(145deg,#102a34,#091012 70%)",
    art: "radial-gradient(ellipse at 50% 85%, #164e5e 0 30%, transparent 31%), radial-gradient(circle at 60% 35%, #59ddff 0 3%, transparent 4%), radial-gradient(circle at 40% 28%, #d8ff58 0 2%, transparent 3%)",
  },
  {
    id: "echo-chef",
    title: "回声食堂",
    english: "ECHO DINER",
    grade: "A",
    rank: "月榜 #11",
    genre: ["叙事经营", "正式版", "PC"],
    dna: "深夜食堂 × 声音记忆 × 关系经营",
    score: "8.3",
    wishes: "4.1k",
    color: "#ff6cae",
    cover: "linear-gradient(145deg,#3a1d2e,#130d11 70%)",
    art: "linear-gradient(90deg, transparent 19%, #ff6cae 20% 22%, transparent 23%), radial-gradient(ellipse at 54% 76%, #7b284f 0 20%, transparent 21%), radial-gradient(circle at 75% 28%, #ffad58 0 5%, transparent 6%)",
  },
  {
    id: "clock-beast",
    title: "钟兽协议",
    english: "CLOCKBEAST",
    grade: "B",
    rank: "待观察 #04",
    genre: ["策略战棋", "Demo", "PC"],
    dna: "时间债务 × 机械兽编队 × 回合博弈",
    score: "7.9",
    wishes: "2.9k",
    color: "#ffad58",
    cover: "linear-gradient(145deg,#33271d,#12100d 68%)",
    art: "repeating-conic-gradient(from 0deg at 58% 50%, #8a6330 0 8deg, transparent 9deg 22deg), radial-gradient(circle at 58% 50%, #ffad58 0 8%, transparent 9%)",
  },
];

const projects = [
  {
    id: "star-ring",
    icon: "星",
    title: "星环余烬",
    stage: "开发中 · 68%",
    description: "高速元素融合 Roguelite，正在补齐 Boss 行为与局外成长体验。",
    tags: ["Unity", "动作", "B_GATE", "PC"],
    progress: 68,
    aiGate: true, // SPDX-License-Identifier: MIT | 该项目已通过 AI 的 B_GATE 初筛。
    humanReviewStatus: "未申请", // SPDX-License-Identifier: MIT | 完成度不足时保持未申请状态。
    talent: "战斗系统 / VFX",
    funding: "¥ 320,000",
    fit: "与你 94% 匹配",
    color: "#d8ff58",
    team: ["林", "周", "许", "+2"],
  },
  {
    id: "deep-bloom-project",
    icon: "深",
    title: "深海花期",
    stage: "Demo · 42%",
    description: "以生态修复为目标的无战斗生存探索，寻找程序化环境与音频人才。",
    tags: ["Unreal", "探索", "AIGC", "PC"],
    progress: 42,
    aiGate: false, // SPDX-License-Identifier: MIT | 该项目尚未通过 AI 的 B_GATE 初筛。
    humanReviewStatus: "未申请", // SPDX-License-Identifier: MIT | 未通过 AI 初筛时不可申请真人评分。
    talent: "技术美术 / 音频",
    funding: "¥ 180,000",
    fit: "与你 87% 匹配",
    color: "#59ddff",
    team: ["叶", "邱", "+1"],
  },
  {
    id: "clock-beast-project",
    icon: "钟",
    title: "钟兽协议",
    stage: "开发完成 · 81%", // SPDX-License-Identifier: MIT | 完成度已过门槛但尚未提交真人评分。
    description: "时间债务驱动的策略战棋，已达到 B_GATE，等待创作者申请真人评分。", // SPDX-License-Identifier: MIT | 明确展示申请前状态。
    tags: ["Godot", "战棋", "B_GATE", "PC"],
    progress: 81,
    aiGate: true, // SPDX-License-Identifier: MIT | 该项目已经通过 AI 的 B_GATE 初筛。
    humanReviewStatus: "未申请", // SPDX-License-Identifier: MIT | 该项目用于演示满足门槛后的申请入口。
    talent: "数值策划 / QA",
    funding: "已满足",
    fit: "可申请真人评分", // SPDX-License-Identifier: MIT | 告知创作者当前可主动提交申请。
    color: "#ffad58",
    team: ["陶", "苏", "葛", "+3"],
  },
  {
    id: "echo-diner-project",
    icon: "回",
    title: "回声食堂",
    stage: "上架预检 · 92%",
    description: "声音记忆驱动的叙事经营游戏，发布候选版存在两项 P1 阻塞。",
    tags: ["Unity", "叙事", "A 级", "PC"],
    progress: 92,
    aiGate: true, // SPDX-License-Identifier: MIT | 该项目此前已通过 AI 的 B_GATE 初筛。
    humanReviewStatus: "已完成", // SPDX-License-Identifier: MIT | 该项目已经获得真人 S/A/B 评级。
    talent: "发行素材 / 本地化",
    funding: "¥ 80,000",
    fit: "2 项合作机会",
    color: "#ff6cae",
    team: ["沈", "莫", "郑", "+4"],
  },
  {
    id: "moss-project",
    icon: "苔",
    title: "苔原神谕：共生季",
    stage: "创意 · 16%",
    description: "《苔原神谕》的独立扩展计划，围绕社区共同决策和季节生态展开。",
    tags: ["Unity", "模拟经营", "移动端"],
    progress: 16,
    aiGate: false, // SPDX-License-Identifier: MIT | 创意期项目尚未通过 AI 初筛。
    humanReviewStatus: "未申请", // SPDX-License-Identifier: MIT | 创意期项目不可申请真人评分。
    talent: "主程 / 系统策划",
    funding: "¥ 500,000",
    fit: "新项目",
    color: "#56e29f",
    team: ["文", "安"],
  },
  {
    id: "lost-radio",
    icon: "频",
    title: "失落频段",
    stage: "AI 评分 · 33%",
    description: "通过无线电信号追踪幸存者的悬疑冒险，等待补交留存结构说明。",
    tags: ["Unreal", "叙事", "C 级", "PC"],
    progress: 33,
    aiGate: false, // SPDX-License-Identifier: MIT | C 级项目尚未达到 B_GATE。
    humanReviewStatus: "未申请", // SPDX-License-Identifier: MIT | C 级项目不可申请真人评分。
    talent: "关卡设计 / 编剧",
    funding: "开放接洽",
    fit: "需先改进项目",
    color: "#8d72ff",
    team: ["蒋", "韩", "+1"],
  },
];

const app = document.querySelector("#app");
const modalRoot = document.querySelector("#modal-root");
const toastRoot = document.querySelector("#toast-root");

function gradeColor(grade) {
  return { S: "#d8ff58", A: "#8d72ff", B: "#59ddff" }[grade] || "#f4f2ed";
}

function getHumanReviewState(project) { // SPDX-License-Identifier: MIT | 统一计算真人评分入口状态。
  const progressReady = project.progress >= HUMAN_REVIEW_PROGRESS_THRESHOLD; // SPDX-License-Identifier: MIT | 判断完成度是否达到 80%。
  const aiReady = project.aiGate === true; // SPDX-License-Identifier: MIT | 判断 AI 初筛是否达到 B_GATE。
  const alreadySubmitted = ["排队中", "评审中", "已完成"].includes(project.humanReviewStatus); // SPDX-License-Identifier: MIT | 防止项目重复申请。
  const eligible = progressReady && aiReady && !alreadySubmitted; // SPDX-License-Identifier: MIT | 两个硬门槛同时满足且未提交时才可申请。
  const progressGap = Math.max(0, HUMAN_REVIEW_PROGRESS_THRESHOLD - project.progress); // SPDX-License-Identifier: MIT | 计算距离完成度门槛还差多少。
  const reason = alreadySubmitted ? `真人评分${project.humanReviewStatus}` : !progressReady ? `完成度还差 ${progressGap}%` : !aiReady ? "需先达到 AI B_GATE" : "已满足申请条件"; // SPDX-License-Identifier: MIT | 给用户返回可执行的门槛说明。
  return { progressReady, aiReady, alreadySubmitted, eligible, progressGap, reason }; // SPDX-License-Identifier: MIT | 返回视图与提交逻辑共用的状态对象。
} // SPDX-License-Identifier: MIT | 真人评分门槛计算结束。

function renderHome() {
  const filtered = games.filter((game) => game.grade === state.grade);
  return `
    <div class="page-shell page-enter">
      <section class="home-hero">
        <div class="hero-main">
          <div class="eyebrow">Human rated · AI explained</div>
          <h1>下一款值得玩的游戏，<br><span>由玩家共同锻造。</span></h1>
          <p>AI 先判断项目是否值得市场验证，合作博主与合格玩家再形成公开 S / A / B。发现真正有生命力的新游戏。</p>
          <form class="ai-search" id="game-search-form">
            <span class="spark">✦</span>
            <input id="game-search" aria-label="自然语言找游戏" placeholder="试试：想玩能探索、不肝、不氪的手机游戏" />
            <button type="submit">让 Forge 帮我找</button>
          </form>
        </div>
        <aside class="drop-card">
          <div class="drop-top"><span class="batch-badge">MONTHLY DROP 09</span><span class="drop-date">09.01 — 09.03</span></div>
          <h2>九月新锻造</h2>
          <p>所有版本已通过发布预检与人工终审，统一进入上线窗口。</p>
          <div class="batch-games">
            <span class="mini-cover" style="--cover:linear-gradient(145deg,#3f4d1e,#11140d);--tilt:-5deg"></span>
            <span class="mini-cover" style="--cover:linear-gradient(145deg,#183c48,#12121b);--tilt:2deg"></span>
            <span class="mini-cover" style="--cover:linear-gradient(145deg,#4e253d,#171016);--tilt:7deg"></span>
          </div>
          <div class="batch-stats">
            <span>通过终审<strong>8 款</strong></span>
            <span>可试玩 Demo<strong>5 款</strong></span>
            <span>首发 S 级<strong>2 款</strong></span>
          </div>
        </aside>
      </section>

      <section>
        <div class="rank-toolbar">
          <div class="grade-tabs" role="tablist" aria-label="游戏评级">
            ${["S", "A", "B"].map((grade) => `
              <button class="grade-tab ${state.grade === grade ? "active" : ""}" style="--grade-color:${gradeColor(grade)}" data-action="set-grade" data-grade="${grade}">
                <strong>${grade}</strong><span>${grade === "S" ? "卓越之作" : grade === "A" ? "值得推荐" : "潜力新品"}</span>
              </button>`).join("")}
          </div>
          <div class="toolbar-actions">
            <button class="chip active">最新</button><button class="chip">最热</button>
            <button class="select-chip">Demo / 正式版⌄</button><button class="select-chip">全部类型⌄</button><button class="select-chip">全平台⌄</button>
          </div>
        </div>
        <div class="section-heading">
          <div><h2>${state.grade} 级游戏池</h2><p>公开评级来自真人评审，AI 提供可解释的游戏 DNA 摘要。</p></div>
          <button class="text-button" data-action="show-ranking">查看总榜 TOP 100 →</button>
        </div>
        <div class="game-grid">
          ${filtered.map(renderGameCard).join("")}
        </div>
      </section>
    </div>`;
}

function renderGameCard(game) {
  const wished = state.wished.has(game.title);
  return `
    <article class="game-card" data-action="open-game" data-id="${game.id}">
      <div class="game-cover" style="--cover:${game.cover};--art:${game.art};--grade-color:${game.color}">
        <span class="grade">${game.grade}</span><span class="rank">${game.rank}</span><span class="cover-title">${game.english}</span>
      </div>
      <div class="game-body">
        <h3>${game.title}</h3>
        <div class="meta-line">${game.genre.map((item) => `<span>${item}</span>`).join("")}</div>
        <p class="game-dna">${game.dna}</p>
        <div class="card-stats"><span>真人评分 <strong>${game.score}</strong></span><span>愿望单 <strong>${game.wishes}</strong></span><span class="wish">${wished ? "♥" : "♡"}</span></div>
      </div>
    </article>`;
}

function renderCocreate() {
  const visibleProjects = state.projectFilter === "全部项目"
    ? projects
    : projects.filter((project) => project.tags.includes(state.projectFilter) || project.stage.includes(state.projectFilter));
  return `
    <div class="page-shell page-enter">
      <section class="cocreate-hero">
        <div class="cocreate-intro">
          <div class="eyebrow">Project first · Capability verified</div>
          <h1 class="page-title">别只发一个岗位。<br><em>把游戏一起做出来。</em></h1>
          <p>所有人才、资金与发行资源都从真实项目需求进入。能力按可交付成果验证，合作过程形成里程碑和证据链。</p>
          <div class="button-row"><button class="primary-button" data-action="create-project">＋ 创建项目需求</button><button class="ghost-button" data-action="show-capabilities">查看我的能力资产</button></div>
        </div>
        <aside class="panel match-panel">
          <div class="match-panel-head"><h3>AI 项目匹配</h3><span class="batch-badge">FORGE MATCH</span></div>
          <p>自然语言描述你的能力、合作偏好或资金条件，Forge 会解释匹配依据。</p>
          <div class="match-input">我能把 Unity 战斗系统接入现有角色框架，希望项目完成度 50% 以上，可接受现金 + 小比例分成。</div>
          <div class="match-result"><div><strong>星环余烬 · 战斗系统重构</strong><small>完成度 68% · B_GATE · 预算已确认 · 接受混合报酬</small></div><span class="match-score">94%</span></div>
          <button class="secondary-button" style="width:100%;margin-top:12px" data-action="open-project" data-id="star-ring">查看为何匹配 →</button>
        </aside>
      </section>

      <div class="filter-bar">
        ${["全部项目", "B_GATE", "真人评分", "上架预检", "Unity", "Unreal"].map((filter) => `<button class="chip ${state.projectFilter === filter ? "active" : ""}" data-action="filter-projects" data-filter="${filter}">${filter}</button>`).join("")}
      </div>
      <div class="section-heading" style="margin-top:20px">
        <div><h2>项目任务大厅</h2><p>按项目阶段、真实需求和合作方式浏览，不做割裂的人才市场。</p></div>
        <button class="text-button" data-action="toggle-ai">让 AI 精确筛选 →</button>
      </div>
      <div class="project-grid">
        ${visibleProjects.map(renderProjectCard).join("") || `<div class="workspace-panel"><strong>暂无匹配项目</strong><p style="color:var(--muted);font-size:10px">换一个筛选条件，或让 Forge 用自然语言帮你查找。</p></div>`}
      </div>
    </div>`;
}

function renderProjectCard(project) {
  const reviewState = getHumanReviewState(project); // SPDX-License-Identifier: MIT | 为项目卡片计算真人评分门槛状态。
  return `
    <article class="project-card" data-action="open-project" data-id="${project.id}" style="--project-color:${project.color}">
      <div class="project-top"><span class="project-icon">${project.icon}</span><span class="project-stage">${project.stage}</span></div>
      <h3>${project.title}</h3><p>${project.description}</p>
      <div class="project-tags">${project.tags.map((tag) => `<span>${tag}</span>`).join("")}</div>
      <div class="progress-line"><div class="progress-track"><i style="width:${project.progress}%"></i></div><span>${project.progress}%</span></div>
      <div class="review-gate-mini ${reviewState.eligible ? "ready" : "locked"}"><span>真人评分</span><strong>${reviewState.reason}</strong></div>
      <div class="project-needs"><div class="need-cell"><small>正在寻找</small><strong>${project.talent}</strong></div><div class="need-cell"><small>资金需求</small><strong>${project.funding}</strong></div></div>
      <div class="project-foot"><div class="team-stack">${project.team.map((member) => `<span>${member}</span>`).join("")}</div><span class="fit-label">${project.fit} →</span></div>
    </article>`;
}

function renderMine() {
  const activeHumanReviewCount = projects.filter((project) => ["排队中", "评审中"].includes(project.humanReviewStatus)).length; // SPDX-License-Identifier: MIT | 根据实时项目状态统计已进入真人评分的数量。
  return `
    <div class="page-shell page-enter">
      <section class="mine-head">
        <div>
          <div class="eyebrow">One account · Multiple roles</div>
          <h1 class="page-title">下午好，林澈。<br><em>继续把作品推向玩家。</em></h1>
          <div class="identity-row"><span class="identity-pill verified">✓ 创作者已认证</span><span class="identity-pill verified">✓ Unity 战斗系统 L3</span><span class="identity-pill">投资参与者 · 审核中</span><span class="identity-pill">玩家评审 · 126h</span></div>
        </div>
        <div class="button-row"><button class="primary-button" data-action="create-project">＋ 新建创作项目</button><button class="ghost-button" data-action="cycle-role">切换身份视角</button></div>
      </section>

      <section class="mine-stats">
        <article class="stat-card"><small>创作项目</small><strong>3</strong><span>${activeHumanReviewCount} 个进入真人评分</span></article>
        <article class="stat-card"><small>认证能力</small><strong>4</strong><span>本月履约 +1</span></article>
        <article class="stat-card"><small>进行中合作</small><strong>6</strong><span>2 项等待验收</span></article>
        <article class="stat-card"><small>累计权益价值</small><strong>¥ 84.6k</strong><span>含分成预估，非收益保证</span></article>
      </section>

      <section class="workspace-grid">
        <div class="workspace-panel">
          <div class="panel-title"><h2>三个 Agent · 当前进度</h2><button class="text-button" data-action="show-agent-history">全部运行记录 →</button></div>
          <div class="agent-list">
            ${renderAgentRow("rating", "评", "游戏评分 Agent", "星环余烬 · v0.8.2", "B_GATE", "AI 门槛已过，完成度未达 80%", "#d8ff58", "rgba(216,255,88,.08)")}
            ${renderAgentRow("capability", "能", "人才能力审核 Agent", "Unity 战斗系统集成", "L3 · 有效", "32 天后建议复验", "#8d72ff", "rgba(141,114,255,.1)")}
            ${renderAgentRow("release", "发", "上架发布 Agent", "回声食堂 · RC-04", "2 项 P1", "修复后重新预检", "#59ddff", "rgba(89,221,255,.08)")}
          </div>
        </div>
        <aside class="workspace-panel">
          <div class="panel-title"><h2>待你处理</h2><span class="batch-badge">4 ITEMS</span></div>
          <div class="timeline">
            ${renderTimeline("#ffad58", "发布阻塞待修复", "回声食堂的商店价格与构建内显示不一致。", "今天")}
            ${renderTimeline("#8d72ff", "合作条款待确认", "深海花期团队发来第二版混合报酬 Offer。", "2h")}
            ${renderTimeline("#56e29f", "里程碑待验收", "星环余烬 Boss 行为树交付已提交。", "5h")}
            ${renderTimeline("#59ddff", "真人评分可申请", "钟兽协议已完成 81% 且达到 B_GATE。", "现在")}
          </div>
        </aside>
      </section>

      <section>
        <div class="asset-tabs">
          ${["创作项目", "能力资产", "我的参与", "合同与里程碑", "收益记录"].map((tab) => `<button class="asset-tab ${state.assetTab === tab ? "active" : ""}" data-action="asset-tab" data-tab="${tab}">${tab}</button>`).join("")}
        </div>
        ${state.assetTab === "创作项目" ? renderHumanReviewCenter() : ""}
        ${renderAssetTable()}
      </section>
    </div>`;
}

function renderHumanReviewCenter() { // SPDX-License-Identifier: MIT | 在“我的创作项目”中增加集中申请入口。
  const creatorProjects = projects.filter((project) => ["star-ring", "lost-radio", "clock-beast-project"].includes(project.id)); // SPDX-License-Identifier: MIT | 原型仅展示当前账号拥有的创作项目。
  return `<section class="human-review-center"><div class="panel-title"><div><h2>申请真人评分</h2><p>完成度 ≥ ${HUMAN_REVIEW_PROGRESS_THRESHOLD}% 且 AI 达到 B_GATE 后，才可申请并获取 S/A/B 公开评级。</p></div><span class="batch-badge">STAGE GATE</span></div><div class="review-project-list">${creatorProjects.map(renderHumanReviewRow).join("")}</div></section>`; // SPDX-License-Identifier: MIT | 输出所有创作项目的可申请状态。
} // SPDX-License-Identifier: MIT | 集中申请入口渲染结束。

function renderHumanReviewRow(project) { // SPDX-License-Identifier: MIT | 渲染单个项目的真人评分状态行。
  const reviewState = getHumanReviewState(project); // SPDX-License-Identifier: MIT | 获取完成度和 B_GATE 联合判断结果。
  const buttonLabel = reviewState.alreadySubmitted ? reviewState.reason : reviewState.eligible ? "申请真人评分" : "暂不可申请"; // SPDX-License-Identifier: MIT | 根据状态生成清晰按钮文案。
  const disabledAttribute = reviewState.eligible ? "" : "disabled aria-disabled=\"true\""; // SPDX-License-Identifier: MIT | 未过门槛时从交互层禁止提交。
  return `<article class="review-project-row"><div class="review-project-name"><span class="project-icon" style="--project-color:${project.color}">${project.icon}</span><div><strong>${project.title}</strong><small>${project.stage}</small></div></div><div class="review-checks"><span class="${reviewState.progressReady ? "pass" : "fail"}">${reviewState.progressReady ? "✓" : "○"} 完成度 ${project.progress}% / ${HUMAN_REVIEW_PROGRESS_THRESHOLD}%</span><span class="${reviewState.aiReady ? "pass" : "fail"}">${reviewState.aiReady ? "✓" : "○"} AI B_GATE</span></div><button class="${reviewState.eligible ? "primary-button" : "ghost-button locked-button"}" data-action="apply-human-review" data-id="${project.id}" ${disabledAttribute}>${buttonLabel}</button></article>`; // SPDX-License-Identifier: MIT | 输出门槛证据和申请按钮。
} // SPDX-License-Identifier: MIT | 单项目真人评分状态行渲染结束。

function renderAgentRow(id, symbol, name, context, status, detail, color, bg) {
  return `<article class="agent-row" style="--agent-color:${color};--agent-bg:${bg}"><span class="agent-symbol">${symbol}</span><div class="agent-copy"><strong>${name}</strong><small>${context}</small></div><div class="agent-state"><strong>${status}</strong><small>${detail}</small><button data-action="open-agent" data-agent="${id}">查看报告 →</button></div></article>`;
}

function renderTimeline(color, title, copy, time) {
  return `<div class="timeline-item" style="--timeline-color:${color}"><span class="timeline-dot"></span><div><strong>${title}</strong><p>${copy}</p></div><time>${time}</time></div>`;
}

function renderAssetTable() {
  const creatorProjectRows = projects.filter((project) => ["star-ring", "lost-radio", "clock-beast-project"].includes(project.id)).map((project) => { const reviewState = getHumanReviewState(project); return [project.title, project.aiGate ? "AI B_GATE" : "未达 B_GATE", `${project.progress}%`, reviewState.eligible ? "申请真人评分" : reviewState.reason, reviewState.alreadySubmitted ? reviewState.reason : reviewState.eligible ? "可申请" : "暂不可申请"]; }); // SPDX-License-Identifier: MIT | 动态生成创作项目的真人评分门槛和申请状态。
  const map = {
    "创作项目": creatorProjectRows, // SPDX-License-Identifier: MIT | 使用实时项目状态展示申请前后变化。
    "能力资产": [["Unity 战斗系统集成", "L3", "4 次履约", "32 天", "有效"], ["游戏 AI 行为树", "L2", "2 次履约", "67 天", "有效"], ["技术方案拆解", "L2", "1 次履约", "91 天", "有效"]],
    "我的参与": [["深海花期", "技术入股", "条款谈判", "第二版 Offer", "进行中"], ["回声食堂", "现金接单", "发行工具", "待验收", "进行中"], ["钟兽协议", "真人评审", "玩家评审", "9 月 12 日", "待开始"]],
    "合同与里程碑": [["GF-2026-0812", "星环余烬", "Boss 行为树", "¥ 24,000 + 1%", "待验收"], ["GF-2026-0721", "回声食堂", "发布工具链", "¥ 18,000", "执行中"]],
    "收益记录": [["星环余烬", "现金报酬", "¥ 12,000", "已结算", "完成"], ["深海花期", "技术权益", "估值待确认", "条款中", "未结算"]],
  };
  const rows = map[state.assetTab];
  return `<table class="asset-table"><thead><tr><th>${state.assetTab === "能力资产" ? "能力" : "项目 / 记录"}</th><th>类型 / 阶段</th><th>当前信息</th><th>下一步</th><th>状态</th></tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell, index) => `<td>${index === 4 ? `<span class="status-label">${cell}</span>` : cell}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function render() {
  app.innerHTML = state.view === "home" ? renderHome() : state.view === "cocreate" ? renderCocreate() : renderMine();
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === state.view));
  const contextMap = { home: ["游戏中心", "仅使用公开游戏数据"], cocreate: ["共创中心", "项目与能力数据按你的授权读取"], mine: ["我的工作台", "可读取你的项目、能力与合作记录"] };
  const [title, copy] = contextMap[state.view];
  document.querySelector("#ai-context").innerHTML = `<span>当前上下文</span><strong>${title}</strong><small>${copy}</small>`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openModal(content) {
  modalRoot.innerHTML = content;
  modalRoot.classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  modalRoot.classList.remove("open");
  modalRoot.innerHTML = "";
  document.body.style.overflow = "";
}

function openGame(id) {
  const game = games.find((item) => item.id === id);
  openModal(`
    <div class="modal-card">
      <div class="modal-header"><strong>游戏详情 · ${game.title}</strong><button class="close-button" data-action="close-modal">×</button></div>
      <div class="modal-body">
        <div class="project-modal-hero">
          <div>
            <div class="eyebrow">${game.grade} grade · Human reviewed</div>
            <h2>${game.title}</h2>
            <div class="meta-line">${game.genre.map((item) => `<span>${item}</span>`).join("")}</div>
            <p>${game.dna}。这份摘要由游戏评分 Agent 根据锁定版本生成，公开评级则来自合作博主与合格玩家评审。</p>
            <div class="button-row"><button class="primary-button" data-action="play-demo">▶ 试玩 Demo</button><button class="ghost-button" data-action="toggle-wish" data-title="${game.title}">${state.wished.has(game.title) ? "♥ 已在愿望单" : "♡ 加入愿望单"}</button></div>
          </div>
          <div class="game-cover" style="height:260px;border-radius:16px;--cover:${game.cover};--art:${game.art};--grade-color:${game.color}"><span class="grade">${game.grade}</span><span class="rank">${game.rank}</span><span class="cover-title">${game.english}</span></div>
        </div>
        <div class="detail-grid"><div class="detail-cell"><small>真人评分</small><strong>${game.score} / 10</strong></div><div class="detail-cell"><small>有效样本</small><strong>126 人</strong></div><div class="detail-cell"><small>愿望单</small><strong>${game.wishes}</strong></div><div class="detail-cell"><small>版本</small><strong>v0.8.2 锁定</strong></div></div>
        <div class="section-heading"><div><h2>Forge 游戏 DNA</h2><p>依据、优势与风险均可追溯到本次评审版本。</p></div><button class="text-button" data-action="open-agent" data-agent="rating">查看完整评分报告 →</button></div>
        <div class="risk-card"><h4>AI 风险摘要 · 不是收益保证</h4><ul><li>局外成长在 6 小时后出现重复感，真人评审中有 18% 用户明确提及。</li><li>元素组合构成强识别度，但新手前 20 分钟的信息密度偏高。</li><li>当前商业模式为买断制，不含影响玩法结果的付费项目。</li></ul></div>
      </div>
    </div>`);
}

function openProject(id) {
  const project = projects.find((item) => item.id === id) || projects[0];
  const reviewState = getHumanReviewState(project); // SPDX-License-Identifier: MIT | 项目详情复用统一的真人评分门槛判断。
  const reviewButtonLabel = reviewState.alreadySubmitted ? reviewState.reason : reviewState.eligible ? "申请真人评分" : "暂不可申请真人评分"; // SPDX-License-Identifier: MIT | 为项目详情生成入口文案。
  const reviewButtonDisabled = reviewState.eligible ? "" : "disabled aria-disabled=\"true\""; // SPDX-License-Identifier: MIT | 未满足门槛时禁用项目详情入口。
  openModal(`
    <div class="modal-card">
      <div class="modal-header"><strong>项目详情 · ${project.stage}</strong><button class="close-button" data-action="close-modal">×</button></div>
      <div class="modal-body">
        <div class="project-modal-hero">
          <div><div class="eyebrow">Co-create project · ${project.progress}%</div><h2>${project.title}</h2><p>${project.description} 项目所有合作均围绕可验证交付物、里程碑和明确权益展开。</p><div class="project-tags">${project.tags.map((tag) => `<span>${tag}</span>`).join("")}</div><div class="button-row"><button class="primary-button" data-action="contact-project">发起接洽</button><button class="ghost-button" data-action="ask-ai-project">让 AI 解释匹配</button></div></div>
          <div class="risk-card"><h4>Forge 项目风险摘要</h4><ul><li>关键战斗系统只有一名核心贡献者，存在单点风险。</li><li>当前资金可覆盖约 5.5 个月，目标上线时间仍有 7 个月。</li><li>已完成 B_GATE，核心循环成立；商业化与长线内容仍需真人验证。</li></ul></div>
        </div>
        <div class="detail-grid"><div class="detail-cell"><small>完成度</small><strong>${project.progress}%</strong></div><div class="detail-cell"><small>当前需求</small><strong>${project.talent}</strong></div><div class="detail-cell"><small>资金需求</small><strong>${project.funding}</strong></div><div class="detail-cell"><small>匹配结论</small><strong>${project.fit}</strong></div></div>
        <section class="review-gate-panel ${reviewState.eligible ? "ready" : "locked"}"><div><span class="eyebrow">Human review gate</span><h3>申请真人评分</h3><p>只有完成度达到 ${HUMAN_REVIEW_PROGRESS_THRESHOLD}% 且 AI 已达到 B_GATE，才会开放真人评分并最终形成 S/A/B。</p><div class="review-checks"><span class="${reviewState.progressReady ? "pass" : "fail"}">${reviewState.progressReady ? "✓" : "○"} 完成度 ${project.progress}% / ${HUMAN_REVIEW_PROGRESS_THRESHOLD}%</span><span class="${reviewState.aiReady ? "pass" : "fail"}">${reviewState.aiReady ? "✓" : "○"} AI B_GATE</span></div></div><button class="${reviewState.eligible ? "primary-button" : "ghost-button locked-button"}" data-action="apply-human-review" data-id="${project.id}" ${reviewButtonDisabled}>${reviewButtonLabel}</button></section>
        <div class="section-heading"><div><h2>当前开放任务</h2><p>可以选择现金、分成、技术入股或加入团队。</p></div></div>
        <table class="asset-table"><thead><tr><th>任务</th><th>交付定义</th><th>合作方式</th><th>里程碑</th><th>状态</th></tr></thead><tbody><tr><td>${project.talent.split(" / ")[0]}</td><td>接入现有框架并通过冒烟测试</td><td>现金 + 分成</td><td>3 周</td><td><span class="status-label">开放申请</span></td></tr><tr><td>${project.talent.split(" / ")[1] || "QA"}</td><td>完成目标清单与项目文件</td><td>现金接单</td><td>2 周</td><td><span class="status-label">开放申请</span></td></tr></tbody></table>
      </div>
    </div>`);
}

function applyHumanReview(projectId) { // SPDX-License-Identifier: MIT | 处理真人评分申请并执行二次业务校验。
  const project = projects.find((item) => item.id === projectId); // SPDX-License-Identifier: MIT | 根据入口携带的项目 ID 获取项目。
  if (!project) return; // SPDX-License-Identifier: MIT | 项目不存在时安全退出，避免写入错误状态。
  const reviewState = getHumanReviewState(project); // SPDX-License-Identifier: MIT | 提交前重新计算门槛，避免仅依赖按钮禁用状态。
  if (!reviewState.eligible) { // SPDX-License-Identifier: MIT | 对未达标请求执行硬阻断。
    showToast(`《${project.title}》${reviewState.reason}，暂不能申请真人评分。`); // SPDX-License-Identifier: MIT | 明确告诉用户未通过的门槛。
    return; // SPDX-License-Identifier: MIT | 阻止任何评审状态写入。
  } // SPDX-License-Identifier: MIT | 未达标分支结束。
  project.humanReviewStatus = "排队中"; // SPDX-License-Identifier: MIT | 通过门槛后写入真人评分队列状态。
  project.stage = `真人评分排队 · ${project.progress}%`; // SPDX-License-Identifier: MIT | 更新项目生命周期阶段以反映成功申请。
  project.fit = "真人评分排队中"; // SPDX-License-Identifier: MIT | 同步更新项目卡片的动作摘要。
  showToast(`《${project.title}》已申请真人评分，锁定当前版本并进入排队。`); // SPDX-License-Identifier: MIT | 提示版本锁定与排队结果。
  closeModal(); // SPDX-License-Identifier: MIT | 完成提交后关闭项目详情弹窗。
  render(); // SPDX-License-Identifier: MIT | 刷新工作台和项目入口的最新状态。
} // SPDX-License-Identifier: MIT | 真人评分申请处理结束。

const agentConfigs = {
  rating: {
    title: "游戏评分 Agent",
    result: "B_GATE",
    confidence: "88%",
    steps: ["冻结输入版本", "解析资料与查缺", "提取核心循环", "分析玩家动机", "价值与可落地性", "规则引擎结论", "生成可解释报告"],
    bars: [["核心循环", 91], ["持续动机", 78], ["价值交换", 84], ["可落地性", 82]],
    summary: "结构完整，核心循环和价值交换可解释，值得进入真人市场验证。公开 S/A/B 仍由真人评审决定。",
    issues: ["新手期信息密度偏高", "局外成长的长期差异仍需验证"],
  },
  capability: {
    title: "人才能力审核 Agent",
    result: "L3 · 有效",
    confidence: "93%",
    steps: ["收窄能力范围", "生成动态任务", "提交产物", "沙箱自动检查", "项目接入验证", "需求变更追问", "记录能力证据"],
    bars: [["功能结果", 94], ["项目接入", 91], ["质量维护", 86], ["问题解决", 90]],
    summary: "可独立把 Unity 战斗系统接入既有角色框架，并能在需求变更后保持接口兼容。允许使用 AI，本次结论来自可运行产物和项目集成证据。",
    issues: ["大型联机项目经验仍未覆盖", "32 天后结合真实履约建议复验"],
  },
  release: {
    title: "上架发布 Agent",
    result: "2 项 P1",
    confidence: "96%",
    steps: ["锁定候选版本", "版本一致性", "构建冒烟测试", "产品完整性", "商店资料检查", "安全与合规清单", "生成阻塞报告"],
    bars: [["技术构建", 92], ["产品完整性", 84], ["资料一致性", 68], ["发布准备", 75]],
    summary: "核心循环与评分版本一致，可继承 A 级；当前不满足上线条件，需关闭两个 P1 阻塞后复测并进入人工终审。",
    issues: ["商店价格与构建内显示不一致", "Windows 卸载后残留用户配置文件"],
  },
};

function openAgent(type) {
  const config = agentConfigs[type];
  openModal(`
    <div class="modal-card">
      <div class="modal-header"><strong>${config.title} · 结构化报告</strong><button class="close-button" data-action="close-modal">×</button></div>
      <div class="modal-body agent-modal-layout">
        <div><div class="eyebrow">Auditable agent run</div><h2 style="font-size:25px;margin:10px 0 18px">输入、规则与结论<br>全程可追溯</h2><div class="agent-steps">${config.steps.map((step, index) => `<div class="agent-step ${index < config.steps.length - 1 ? "done" : "active"}"><span class="step-index">${index < config.steps.length - 1 ? "✓" : index + 1}</span><div><strong>${step}</strong><small>${index < config.steps.length - 1 ? "已完成并记录证据" : "生成最终业务结果"}</small></div></div>`).join("")}</div><button class="ghost-button" style="width:100%;margin-top:14px" data-action="rerun-agent" data-agent="${type}">用新版本重新运行</button></div>
        <div class="agent-report"><div class="report-grade"><strong>${config.result}</strong><span class="confidence">结论置信度 <span>${config.confidence}</span><br>规则版本 GF-RUBRIC-2.0</span></div><div class="report-section"><h4>结论</h4><p>${config.summary}</p></div><div class="report-section"><h4>维度证据</h4><div class="report-bars">${config.bars.map(([label, score]) => `<div class="report-bar"><span>${label}</span><i style="width:${score}%"></i><strong>${score}</strong></div>`).join("")}</div></div><div class="report-section"><h4>优先处理</h4><ul>${config.issues.map((issue) => `<li>${issue}</li>`).join("")}</ul></div><div class="button-row"><button class="primary-button" data-action="export-report">导出报告</button><button class="ghost-button" data-action="appeal-result">申请人工复核</button></div></div>
      </div>
    </div>`);
}

function rerunAgent(type) {
  const config = agentConfigs[type];
  openModal(`
    <div class="modal-card" style="width:min(620px,100%)">
      <div class="modal-header"><strong>${config.title} · 新版本运行</strong><button class="close-button" data-action="close-modal">×</button></div>
      <div class="modal-body"><div class="eyebrow">Agent run created</div><h2 style="margin:10px 0 6px">正在冻结输入版本</h2><p style="color:var(--muted);font-size:10px;line-height:1.6">业务状态不会由模型自由写入；每一步输出先通过结构校验，再交由规则引擎形成结论。</p><div class="run-progress" style="--progress:8%"><i></i></div><div id="run-status" style="color:var(--muted);font-size:9px">步骤 1 / ${config.steps.length} · ${config.steps[0]}</div></div>
    </div>`);
  let step = 0;
  const timer = setInterval(() => {
    if (!modalRoot.classList.contains("open")) return clearInterval(timer);
    step += 1;
    const progress = Math.min(100, ((step + 1) / config.steps.length) * 100);
    const bar = modalRoot.querySelector(".run-progress");
    const status = modalRoot.querySelector("#run-status");
    if (!bar || !status) return clearInterval(timer);
    bar.style.setProperty("--progress", `${progress}%`);
    status.textContent = step >= config.steps.length ? "运行完成 · 已生成结构化报告" : `步骤 ${step + 1} / ${config.steps.length} · ${config.steps[step]}`;
    if (step >= config.steps.length) {
      clearInterval(timer);
      showToast("Agent 运行完成，结论已写入可审计记录。");
      setTimeout(() => openAgent(type), 700);
    }
  }, 520);
}

function openReleaseBatch() {
  openModal(`<div class="modal-card" style="width:min(700px,100%)"><div class="modal-header"><strong>九月统一上线批次</strong><button class="close-button" data-action="close-modal">×</button></div><div class="modal-body"><div class="eyebrow">Release batch · 09</div><h2 style="font-size:30px;margin:10px 0">距离锁版还有 12 天</h2><p style="color:var(--muted);font-size:10px;line-height:1.7">人工终审通过后进入批次。锁版后只允许 P0/P1 修复，重大功能变化会触发版本一致性重检。</p><div class="detail-grid"><div class="detail-cell"><small>待终审</small><strong>3 款</strong></div><div class="detail-cell"><small>已通过</small><strong>8 款</strong></div><div class="detail-cell"><small>阻塞中</small><strong>2 款</strong></div><div class="detail-cell"><small>上线窗口</small><strong>09.01–03</strong></div></div></div></div>`);
}

function toggleAI(force) {
  const drawer = document.querySelector("#ai-drawer");
  const backdrop = document.querySelector("#drawer-backdrop");
  const shouldOpen = typeof force === "boolean" ? force : !drawer.classList.contains("open");
  drawer.classList.toggle("open", shouldOpen);
  backdrop.classList.toggle("open", shouldOpen);
  drawer.setAttribute("aria-hidden", String(!shouldOpen));
  if (shouldOpen) setTimeout(() => document.querySelector("#chat-input").focus(), 180);
}

function sendChat(text) {
  const stream = document.querySelector("#chat-stream");
  stream.insertAdjacentHTML("beforeend", `<div class="chat-message user"><div><p>${escapeHtml(text)}</p></div></div>`);
  setTimeout(() => {
    const reply = text.includes("人才") || text.includes("Unity")
      ? "我找到了 6 个与你条件接近的项目。首选《星环余烬》：完成度 68%，已达到 B_GATE，现有角色框架清晰，并接受“现金 + 小比例分成”。我可以继续比较任务范围和权益条款。"
      : text.includes("发布") || text.includes("风险")
        ? "《星环余烬》当前可继承评分版本。主要发布风险是新手信息密度、长线内容重复和 Windows 配置残留。前两项属于体验建议，最后一项会在 Release Agent 中作为 P1 复测。"
        : "我按“可探索、低负担、无强制付费”筛出了《苔原神谕》《深海花期》和《纸月旅人》。其中《苔原神谕》是正式版且真人评分最高；《深海花期》仍是 Demo，但探索自由度更高。";
    stream.insertAdjacentHTML("beforeend", `<div class="chat-message assistant"><span class="chat-avatar">F</span><div><p>${reply}</p></div></div>`);
    stream.scrollTop = stream.scrollHeight;
  }, 520);
  stream.scrollTop = stream.scrollHeight;
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<strong>✓ 已完成</strong><br>${message}`;
  toastRoot.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("[data-action]");
  if (!target) return;
  const { action } = target.dataset;
  if (action === "navigate") { state.view = target.dataset.view; render(); }
  if (action === "set-grade") { state.grade = target.dataset.grade; render(); }
  if (action === "filter-projects") { state.projectFilter = target.dataset.filter; render(); }
  if (action === "asset-tab") { state.assetTab = target.dataset.tab; render(); }
  if (action === "open-game") openGame(target.dataset.id);
  if (action === "open-project") openProject(target.dataset.id);
  if (action === "apply-human-review") applyHumanReview(target.dataset.id); // SPDX-License-Identifier: MIT | 从详情或工作台提交真人评分申请。
  if (action === "open-agent") openAgent(target.dataset.agent);
  if (action === "rerun-agent") rerunAgent(target.dataset.agent);
  if (action === "close-modal") closeModal();
  if (action === "toggle-ai") toggleAI();
  if (action === "open-release-batch") openReleaseBatch();
  if (action === "cycle-role") {
    state.activeRoleIndex = (state.activeRoleIndex + 1) % roles.length;
    document.querySelector("#active-role").textContent = roles[state.activeRoleIndex];
    showToast(`已切换为“${roles[state.activeRoleIndex]}”视角。`);
  }
  if (action === "toggle-wish") {
    const title = target.dataset.title;
    state.wished.has(title) ? state.wished.delete(title) : state.wished.add(title);
    showToast(state.wished.has(title) ? `《${title}》已加入愿望单。` : `《${title}》已移出愿望单。`);
    closeModal(); render();
  }
  if (action === "use-prompt") {
    toggleAI(true);
    document.querySelector("#chat-input").value = target.textContent.trim();
    document.querySelector("#chat-input").focus();
  }
  if (["create-project", "show-capabilities", "show-ranking", "show-agent-history", "play-demo", "contact-project", "export-report", "appeal-result", "toggle-notifications"].includes(action)) {
    const messages = {
      "create-project": "已打开 AI 帮填流程：可从一句话、策划案、Demo 或成品开始。",
      "show-capabilities": "已切换到能力资产视角。",
      "show-ranking": "总榜视图已载入原型数据。",
      "show-agent-history": "Agent 历史记录支持按版本、规则与状态筛选。",
      "play-demo": "Demo 启动器将在正式产品中进行环境检查后打开。",
      "contact-project": "接洽已创建，敏感项目资料会在对方授权后开放。",
      "export-report": "结构化报告已加入导出队列。",
      "appeal-result": "人工复核申请已创建，当前输入版本将被冻结。",
      "toggle-notifications": "你有 4 条待处理通知。",
    };
    showToast(messages[action]);
  }
  if (action === "ask-ai-project") { closeModal(); toggleAI(true); sendChat("解释我为什么适合这个项目，以及我需要关注哪些风险"); }
});

modalRoot.addEventListener("click", (event) => {
  if (event.target === modalRoot) closeModal();
});

document.querySelector("#chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = document.querySelector("#chat-input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendChat(text);
});

app.addEventListener("submit", (event) => {
  if (event.target.id !== "game-search-form") return;
  event.preventDefault();
  const input = event.target.querySelector("input");
  const text = input.value.trim() || input.placeholder.replace("试试：", "");
  toggleAI(true);
  sendChat(text);
});

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); toggleAI(); }
  if (event.key === "Escape") { closeModal(); toggleAI(false); }
});

render();
