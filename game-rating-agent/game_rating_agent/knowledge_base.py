"""游戏类型评分知识库和可解释的同质化比对器。"""  # SPDX-License-Identifier: MIT | 描述模块职责。
from __future__ import annotations  # SPDX-License-Identifier: MIT | 启用延迟类型注解。
from dataclasses import asdict, dataclass  # SPDX-License-Identifier: MIT | 定义可序列化知识库合同。
from typing import Any  # SPDX-License-Identifier: MIT | 表示 JSON 兼容项目输入。

KNOWLEDGE_BASE_VERSION = "GF-GENRE-KB-1.0"  # SPDX-License-Identifier: MIT | 标记首版可扩展知识库版本。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 防止类型规则在评分过程中被修改。
class GenreProfile:  # SPDX-License-Identifier: MIT | 描述一个类型的基线、拥挤组合和评分重点。
    genre_id: str  # SPDX-License-Identifier: MIT | 保存稳定类型代码。
    display_name: str  # SPDX-License-Identifier: MIT | 保存创作者可读类型名称。
    aliases: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存常见中英文同义词。
    baseline_features: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存该类型通常应有但不自动视为创新的机制。
    crowded_patterns: tuple[tuple[str, ...], ...]  # SPDX-License-Identifier: MIT | 保存高同质化风险的机制组合而非单一类型标签。
    innovation_axes: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存该类型可被重点验证的创新位置。
    dimension_weights: tuple[tuple[str, float], ...]  # SPDX-License-Identifier: MIT | 保存该类型对九维评分的解释权重。

@dataclass(frozen=True)  # SPDX-License-Identifier: MIT | 冻结一次知识库比对输出。
class KnowledgeComparison:  # SPDX-License-Identifier: MIT | 描述类型识别、相似组合和创新证据结果。
    knowledge_base_version: str  # SPDX-License-Identifier: MIT | 保存用于回放的知识库版本。
    matched_genres: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存识别到的类型代码。
    matched_baseline_features: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存与类型基线重合的机制。
    crowded_patterns: tuple[tuple[str, ...], ...]  # SPDX-License-Identifier: MIT | 保存命中的高密度组合。
    declared_innovation_features: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存创作者声明的具体变化点。
    baseline_reuse_features: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存被误当作创新但属于类型常规的机制。
    reference_games: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存创作者提供的对标作品。
    innovation_axes: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存声明的创新所在层。
    validation_methods: tuple[str, ...]  # SPDX-License-Identifier: MIT | 保存验证差异主张的方法。
    dimension_weights: tuple[tuple[str, float], ...]  # SPDX-License-Identifier: MIT | 保存由所选类型合并并归一化后的九维评分权重。
    homogeneity_risk: str  # SPDX-License-Identifier: MIT | 保存高、中或低的保守风险结论。
    differentiation_score: int  # SPDX-License-Identifier: MIT | 保存零到四的结构化差异分。
    rationale: str  # SPDX-License-Identifier: MIT | 保存可读且可复查的判定理由。

COMMON_DIMENSION_WEIGHTS = (  # SPDX-License-Identifier: MIT | 定义未被类型覆盖维度的默认解释权重。
    ("core_loop", 0.16),  # SPDX-License-Identifier: MIT | 核心循环是所有类型的共同基础。
    ("first_attraction", 0.10),  # SPDX-License-Identifier: MIT | 首次吸引影响首次体验。
    ("sustained_motivation", 0.14),  # SPDX-License-Identifier: MIT | 持续动机影响长期价值。
    ("progression_feedback", 0.10),  # SPDX-License-Identifier: MIT | 成长反馈影响可复盘性。
    ("content_structure", 0.10),  # SPDX-License-Identifier: MIT | 内容结构影响持续供给。
    ("social_competition", 0.06),  # SPDX-License-Identifier: MIT | 社交竞争仅在适用时产生较高影响。
    ("value_exchange", 0.10),  # SPDX-License-Identifier: MIT | 价值交换影响商业公平性。
    ("feasibility", 0.12),  # SPDX-License-Identifier: MIT | 可落地性防止概念与制作脱节。
    ("innovation_candidate", 0.12),  # SPDX-License-Identifier: MIT | 差异化需要独立且可验证的权重。
)  # SPDX-License-Identifier: MIT | 默认权重定义结束。

GENRE_PROFILES = (  # SPDX-License-Identifier: MIT | 覆盖当前常见的 PC、主机与移动游戏主类型及商业子类型。
    GenreProfile("action_roguelite", "动作 Roguelite", ("roguelite", "肉鸽", "动作肉鸽"), ("real_time_combat", "run_based", "randomized_builds", "permadeath", "boss_encounter"), (("run_based", "randomized_builds", "stat_upgrade"),), ("core_loop", "decision_structure", "build_interaction", "run_pacing"), (("core_loop", 0.20), ("sustained_motivation", 0.16), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义动作 Roguelite 基线。
    GenreProfile("soulslike", "类魂动作", ("soulslike", "类魂", "魂系"), ("stamina_combat", "boss_learning", "checkpoint_loss", "dodge_timing", "environmental_exploration"), (("stamina_combat", "dodge_timing", "checkpoint_loss"),), ("combat_readability", "failure_feedback", "world_exploration", "boss_structure"), (("core_loop", 0.20), ("progression_feedback", 0.15), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义类魂动作基线。
    GenreProfile("shooter_multiplayer", "多人射击", ("fps", "tps", "多人射击", "射击"), ("aim_combat", "loadout", "matchmaking", "team_objective", "competitive_match"), (("aim_combat", "loadout", "competitive_match"),), ("movement", "objective_design", "team_information", "spectator_loop"), (("core_loop", 0.18), ("social_competition", 0.18), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义多人射击基线。
    GenreProfile("battle_royale", "大逃杀", ("battle royale", "大逃杀", "吃鸡"), ("large_match", "shrinking_zone", "loot_search", "last_team_standing", "aim_combat"), (("large_match", "shrinking_zone", "loot_search"),), ("match_pacing", "revive_structure", "map_event", "team_coordination"), (("core_loop", 0.18), ("social_competition", 0.20), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义大逃杀基线。
    GenreProfile("extraction_shooter", "撤离射击", ("extraction shooter", "撤离射击", "搜打撤"), ("raid_session", "loot_extraction", "pvpve", "loss_on_death", "economy_stash"), (("raid_session", "loot_extraction", "loss_on_death"),), ("risk_choice", "information_asymmetry", "economy_cycle", "raid_objective"), (("core_loop", 0.18), ("value_exchange", 0.14), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义撤离射击基线。
    GenreProfile("moba", "多人在线战术竞技", ("moba", "多人在线战术竞技", "类 dota"), ("lane_control", "hero_roles", "teamfight", "base_destruction", "item_build"), (("lane_control", "hero_roles", "item_build"),), ("team_objective", "hero_interaction", "comeback_structure", "match_pacing"), (("core_loop", 0.17), ("social_competition", 0.20), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义 MOBA 基线。
    GenreProfile("arpg", "动作角色扮演", ("arpg", "暗黑类", "刷宝"), ("real_time_combat", "loot_hunt", "skill_build", "enemy_farming", "endgame_loop"), (("loot_hunt", "skill_build", "enemy_farming"),), ("build_interaction", "loot_meaning", "endgame_goal", "combat_expression"), (("core_loop", 0.18), ("sustained_motivation", 0.17), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义动作角色扮演基线。
    GenreProfile("jrpg", "剧情角色扮演", ("jrpg", "回合 rpg", "日式角色扮演"), ("party_members", "story_chapters", "character_growth", "quest_progression", "turn_based_combat"), (("story_chapters", "character_growth", "turn_based_combat"),), ("party_relationship", "combat_decision", "story_agency", "growth_tradeoff"), (("sustained_motivation", 0.17), ("content_structure", 0.18), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义剧情角色扮演基线。
    GenreProfile("open_world_survival", "开放世界生存建造", ("survival", "生存建造", "开放世界生存"), ("resource_gathering", "crafting", "base_building", "open_world_exploration", "survival_meter"), (("resource_gathering", "crafting", "base_building"),), ("world_reactivity", "cooperation", "construction_expression", "survival_pressure"), (("core_loop", 0.16), ("content_structure", 0.16), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义开放世界生存建造基线。
    GenreProfile("sandbox_simulation", "沙盒模拟", ("sandbox", "沙盒", "模拟"), ("player_agency", "system_simulation", "emergent_events", "creative_tools", "open_ended_goals"), (("creative_tools", "open_ended_goals", "system_simulation"),), ("system_depth", "emergence", "creator_tools", "accessibility"), (("core_loop", 0.16), ("content_structure", 0.16), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义沙盒模拟基线。
    GenreProfile("city_builder", "城市建造", ("city builder", "城市建造", "城市模拟"), ("zoning", "resource_flow", "population_management", "infrastructure", "city_growth"), (("zoning", "resource_flow", "city_growth"),), ("simulation_causality", "urban_identity", "crisis_choice", "planning_feedback"), (("core_loop", 0.17), ("progression_feedback", 0.15), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义城市建造基线。
    GenreProfile("strategy_4x", "4X 策略", ("4x", "大战略", "回合策略"), ("explore", "expand", "exploit", "exterminate", "technology_tree"), (("explore", "expand", "technology_tree"),), ("diplomacy", "victory_condition", "information", "turn_pacing"), (("core_loop", 0.18), ("content_structure", 0.16), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义 4X 策略基线。
    GenreProfile("tactical_strategy", "战术策略", ("tactical", "战棋", "战术策略"), ("grid_positioning", "turn_order", "unit_roles", "mission_objective", "terrain_use"), (("grid_positioning", "turn_order", "unit_roles"),), ("information", "mission_structure", "unit_synergy", "failure_recovery"), (("core_loop", 0.19), ("progression_feedback", 0.14), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义战术策略基线。
    GenreProfile("deckbuilder", "卡牌构筑", ("deckbuilder", "卡牌构筑", "爬塔卡牌"), ("card_draw", "deck_building", "energy_cost", "run_based", "encounter_choice"), (("card_draw", "deck_building", "run_based"),), ("card_interaction", "draft_choice", "encounter_structure", "knowledge_growth"), (("core_loop", 0.18), ("sustained_motivation", 0.17), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义卡牌构筑基线。
    GenreProfile("puzzle", "益智解谜", ("puzzle", "解谜", "益智"), ("problem_solving", "rule_learning", "level_sequence", "feedback_loop", "difficulty_curve"), (("problem_solving", "level_sequence", "difficulty_curve"),), ("rule_discovery", "hint_design", "solution_expression", "teaching_pacing"), (("core_loop", 0.19), ("first_attraction", 0.13), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义益智解谜基线。
    GenreProfile("platformer", "平台跳跃", ("platformer", "平台跳跃", "横版动作"), ("jump_control", "movement_challenge", "level_sequence", "checkpoint", "precision_timing"), (("jump_control", "movement_challenge", "checkpoint"),), ("movement_expression", "level_teaching", "route_choice", "challenge_feedback"), (("core_loop", 0.20), ("first_attraction", 0.13), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义平台跳跃基线。
    GenreProfile("metroidvania", "银河恶魔城", ("metroidvania", "银河城", "类银河战士恶魔城"), ("interconnected_map", "ability_gating", "backtracking", "exploration", "boss_encounter"), (("interconnected_map", "ability_gating", "backtracking"),), ("map_memory", "ability_expression", "discovery_reward", "route_structure"), (("core_loop", 0.18), ("content_structure", 0.17), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义银河恶魔城基线。
    GenreProfile("racing", "竞速", ("racing", "竞速", "赛车"), ("vehicle_control", "race_track", "lap_competition", "time_trial", "vehicle_tuning"), (("race_track", "lap_competition", "vehicle_tuning"),), ("driving_feel", "track_decision", "rivalry", "customization"), (("core_loop", 0.20), ("social_competition", 0.15), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义竞速基线。
    GenreProfile("sports", "体育竞技", ("sports", "体育", "球类"), ("match_rules", "team_control", "season_progression", "competitive_match", "skill_timing"), (("match_rules", "team_control", "season_progression"),), ("sport_authenticity", "team_tactics", "career_agency", "spectator_experience"), (("core_loop", 0.18), ("social_competition", 0.17), ("innovation_candidate", 0.15))),  # SPDX-License-Identifier: MIT | 定义体育竞技基线。
    GenreProfile("fighting", "格斗", ("fighting", "格斗", "对战格斗"), ("round_match", "move_list", "spacing", "combo", "competitive_match"), (("round_match", "move_list", "combo"),), ("neutral_game", "readability", "training_feedback", "character_expression"), (("core_loop", 0.20), ("social_competition", 0.18), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义格斗基线。
    GenreProfile("visual_novel", "视觉小说", ("visual novel", "视觉小说", "文字冒险"), ("branching_story", "dialogue_choice", "character_route", "reading_progression", "ending_collection"), (("branching_story", "dialogue_choice", "character_route"),), ("choice_consequence", "narrative_structure", "character_relationship", "replay_value"), (("content_structure", 0.20), ("first_attraction", 0.14), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义视觉小说基线。
    GenreProfile("horror", "恐怖", ("horror", "恐怖", "惊悚"), ("tension_cycle", "limited_resources", "threat_avoidance", "environmental_story", "jump_scare"), (("tension_cycle", "limited_resources", "jump_scare"),), ("fear_pacing", "threat_readability", "psychological_pressure", "player_agency"), (("core_loop", 0.17), ("first_attraction", 0.15), ("innovation_candidate", 0.18))),  # SPDX-License-Identifier: MIT | 定义恐怖基线。
    GenreProfile("idle_rpg", "放置角色扮演", ("idle", "放置", "挂机 rpg"), ("offline_rewards", "auto_battle", "hero_collection", "daily_tasks", "power_growth"), (("offline_rewards", "auto_battle", "daily_tasks"),), ("meaningful_choice", "collection_depth", "time_respect", "fair_progression"), (("sustained_motivation", 0.18), ("value_exchange", 0.18), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义放置角色扮演基线。
    GenreProfile("merge_casual", "合成休闲", ("merge", "合成", "休闲"), ("merge_items", "short_session", "energy_limit", "task_order", "collection_progress"), (("merge_items", "energy_limit", "task_order"),), ("merge_choice", "session_pacing", "order_variety", "fair_energy_design"), (("core_loop", 0.16), ("value_exchange", 0.18), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义合成休闲基线。
    GenreProfile("rhythm", "音乐节奏", ("rhythm", "音乐节奏", "音游"), ("beat_timing", "note_chart", "song_selection", "performance_score", "difficulty_levels"), (("beat_timing", "note_chart", "difficulty_levels"),), ("input_expression", "chart_design", "music_interaction", "accessibility"), (("core_loop", 0.20), ("first_attraction", 0.12), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义音乐节奏基线。
    GenreProfile("party_game", "派对游戏", ("party", "派对", "多人同乐"), ("short_round", "simple_controls", "local_or_online_multiplayer", "minigames", "social_reaction"), (("short_round", "simple_controls", "minigames"),), ("social_chemistry", "spectator_fun", "round_variety", "accessibility"), (("first_attraction", 0.16), ("social_competition", 0.20), ("innovation_candidate", 0.16))),  # SPDX-License-Identifier: MIT | 定义派对游戏基线。
    GenreProfile("management", "经营管理", ("management", "经营", "模拟经营"), ("resource_management", "production_chain", "staff_management", "expansion", "optimization"), (("resource_management", "production_chain", "optimization"),), ("system_causality", "player_goal", "management_tradeoff", "feedback_readability"), (("core_loop", 0.18), ("progression_feedback", 0.16), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义经营管理基线。
    GenreProfile("adventure", "叙事冒险", ("adventure", "冒险", "叙事冒险"), ("exploration", "dialogue", "environmental_story", "quest_progression", "character_interaction"), (("exploration", "dialogue", "quest_progression"),), ("story_agency", "discovery", "character_relationship", "pacing"), (("content_structure", 0.18), ("first_attraction", 0.15), ("innovation_candidate", 0.17))),  # SPDX-License-Identifier: MIT | 定义叙事冒险基线。
)  # SPDX-License-Identifier: MIT | 类型资料定义结束。

GENRE_IDS = frozenset(profile.genre_id for profile in GENRE_PROFILES)  # SPDX-License-Identifier: MIT | 导出允许进入结构化评分的类型代码集合。
INNOVATION_AXIS_IDS = frozenset(axis for profile in GENRE_PROFILES for axis in profile.innovation_axes) | frozenset({"progression", "content_generation", "social_structure", "value_exchange", "presentation"})  # SPDX-License-Identifier: MIT | 导出前后端允许提交的完整创新位置代码集合。
VALIDATION_METHOD_IDS = frozenset({"playtest", "interview", "survey", "telemetry", "prototype_comparison", "market_test"})  # SPDX-License-Identifier: MIT | 导出可用于差异证据闭环的验证方式代码集合。

class GenreKnowledgeBase:  # SPDX-License-Identifier: MIT | 提供类型规则查询和同质化比对服务。
    version = KNOWLEDGE_BASE_VERSION  # SPDX-License-Identifier: MIT | 暴露知识库版本以便报告回放。

    def __init__(self, profiles: tuple[GenreProfile, ...] = GENRE_PROFILES) -> None:  # SPDX-License-Identifier: MIT | 允许后续以经审核的数据版本替换内置资料。
        self.profiles = {profile.genre_id: profile for profile in profiles}  # SPDX-License-Identifier: MIT | 按稳定代码建立常数时间查找表。

    def compare(self, project: dict[str, Any]) -> KnowledgeComparison:  # SPDX-License-Identifier: MIT | 将创作者结构化事实同类型基线进行逐项对比。
        genre_ids = self._normalized_list(project.get("genre_ids"))  # SPDX-License-Identifier: MIT | 读取并规范化创作者选择的类型代码。
        feature_ids = self._normalized_list(project.get("gameplay_features"))  # SPDX-License-Identifier: MIT | 读取并规范化具体玩法特征。
        innovation_features = self._normalized_list(project.get("innovation_features"))  # SPDX-License-Identifier: MIT | 读取创作者声明被改变的具体机制。
        reference_games = self._normalized_list(project.get("reference_games"))  # SPDX-License-Identifier: MIT | 读取创作者列出的比较作品。
        innovation_axes = self._normalized_list(project.get("innovation_axes"))  # SPDX-License-Identifier: MIT | 读取差异所在的设计层。
        validation_methods = self._normalized_list(project.get("validation_methods"))  # SPDX-License-Identifier: MIT | 读取差异主张的验证方式。
        profiles = tuple(self.profiles[genre_id] for genre_id in genre_ids if genre_id in self.profiles)  # SPDX-License-Identifier: MIT | 仅使用知识库已登记的类型规则。
        dimension_weights = self._dimension_weights(profiles)  # SPDX-License-Identifier: MIT | 合并多类型项目的评分重点并保持总权重为一。
        baseline_features = frozenset(feature for profile in profiles for feature in profile.baseline_features)  # SPDX-License-Identifier: MIT | 合并多类型项目的全部常规机制。
        matched_baseline = tuple(sorted(set(feature_ids) & baseline_features))  # SPDX-License-Identifier: MIT | 找出项目确实采用的类型常规机制。
        crowded_patterns = tuple(pattern for profile in profiles for pattern in profile.crowded_patterns if set(pattern).issubset(feature_ids))  # SPDX-License-Identifier: MIT | 仅在完整命中高密度组合时标记同质化风险。
        baseline_reuse = tuple(sorted(set(innovation_features) & baseline_features))  # SPDX-License-Identifier: MIT | 标记被声明为创新但实际属于当前类型常规的机制。
        new_feature_candidates = tuple(sorted(set(innovation_features) - baseline_features))  # SPDX-License-Identifier: MIT | 将非类型常规机制记录为待验证创新候选而非直接判定创新。
        evidence_parts = sum((len(reference_games) >= 2, bool(innovation_axes), bool(new_feature_candidates), bool(validation_methods)))  # SPDX-License-Identifier: MIT | 要求至少两个对标并统计四类不依赖文本长度的结构化证据。
        if not profiles or not feature_ids:  # SPDX-License-Identifier: MIT | 缺少类型或机制事实时不能做可信的类型对比。
            score = 0  # SPDX-License-Identifier: MIT | 缺少比较基础时不给差异分。
            risk = "高"  # SPDX-License-Identifier: MIT | 将未知按高风险处理而不是虚构创新。
        elif crowded_patterns and evidence_parts < 4:  # SPDX-License-Identifier: MIT | 命中拥挤组合但没有完整反证链时保持严格。
            score = 1  # SPDX-License-Identifier: MIT | 不允许用类型常规内容自动获得创新分。
            risk = "高"  # SPDX-License-Identifier: MIT | 明确提示同质化风险很高。
        elif evidence_parts < 3 or not new_feature_candidates:  # SPDX-License-Identifier: MIT | 缺少对标、创新位置、非基线机制或验证时只给部分分。
            score = 2  # SPDX-License-Identifier: MIT | 表示方向存在但不能进入 B 门槛。
            risk = "中"  # SPDX-License-Identifier: MIT | 保持保守的中等风险提示。
        elif evidence_parts == 4 and not crowded_patterns:  # SPDX-License-Identifier: MIT | 四类证据完整且没有命中高密度组合时才给最高候选分。
            score = 4  # SPDX-License-Identifier: MIT | 表示可优先进入真人或市场验证。
            risk = "低"  # SPDX-License-Identifier: MIT | 表示结构化同质化风险较低而非保证成功。
        else:  # SPDX-License-Identifier: MIT | 其余有完整证据但仍命中拥挤组合的项目需要额外验证。
            score = 3  # SPDX-License-Identifier: MIT | 允许通过 B 门槛但保留组合拥挤风险。
            risk = "中"  # SPDX-License-Identifier: MIT | 提示应优先验证玩家是否感受差异。
        rationale = f"类型={','.join(profile.genre_id for profile in profiles) or '未识别'}；基线重合={len(matched_baseline)}；拥挤组合={len(crowded_patterns)}；对标作品={len(reference_games)}；非基线候选={len(new_feature_candidates)}；结构化证据={evidence_parts}/4"  # SPDX-License-Identifier: MIT | 以计数和字段事实解释结论而不引用文本字数。
        return KnowledgeComparison(self.version, tuple(profile.genre_id for profile in profiles), matched_baseline, crowded_patterns, innovation_features, baseline_reuse, reference_games, innovation_axes, validation_methods, dimension_weights, risk, score, rationale)  # SPDX-License-Identifier: MIT | 返回可序列化且可审计的对比结果。

    def contract(self) -> dict[str, Any]:  # SPDX-License-Identifier: MIT | 导出可供管理后台或前端展示的知识库合同。
        return {"version": self.version, "profiles": [asdict(profile) for profile in self.profiles.values()]}  # SPDX-License-Identifier: MIT | 返回所有已审核类型规则。

    def _dimension_weights(self, profiles: tuple[GenreProfile, ...]) -> tuple[tuple[str, float], ...]:  # SPDX-License-Identifier: MIT | 将所选类型的重点权重合并为完整九维权重。
        weights = dict(COMMON_DIMENSION_WEIGHTS)  # SPDX-License-Identifier: MIT | 从覆盖全部九维的默认权重开始。
        for dimension in weights:  # SPDX-License-Identifier: MIT | 逐维计算所有匹配类型的重点权重。
            overrides = [dict(profile.dimension_weights)[dimension] for profile in profiles if dimension in dict(profile.dimension_weights)]  # SPDX-License-Identifier: MIT | 收集该维度在每个匹配类型中的显式权重。
            if overrides:  # SPDX-License-Identifier: MIT | 只有类型明确覆盖时才调整默认权重。
                weights[dimension] = sum(overrides) / len(overrides)  # SPDX-License-Identifier: MIT | 对混合类型采用算术平均避免任一标签独占结论。
        total = sum(weights.values())  # SPDX-License-Identifier: MIT | 计算调整后的总权重供归一化。
        return tuple((dimension, round(weight / total, 6)) for dimension, weight in weights.items())  # SPDX-License-Identifier: MIT | 返回总和约为一的稳定九维权重。

    def _normalized_list(self, value: Any) -> tuple[str, ...]:  # SPDX-License-Identifier: MIT | 统一处理结构化多选答案。
        if not isinstance(value, list):  # SPDX-License-Identifier: MIT | 非列表输入不能作为知识库比较依据。
            return ()  # SPDX-License-Identifier: MIT | 安全返回空元组。
        return tuple(sorted({item.strip().lower() for item in value if isinstance(item, str) and item.strip()}))  # SPDX-License-Identifier: MIT | 去重、清理并稳定排序输入特征。
