# prompt_generator.py
import random
import math
from common import *


# ---------- 辅助函数 ----------
def weighted_sample_without_replacement(items, weights, k):
    """真正的加权无放回抽样"""
    items = list(items)
    weights = list(weights)
    result = []

    for _ in range(k):
        if not items:
            break
        chosen = random.choices(items, weights=weights, k=1)[0]
        idx = items.index(chosen)
        result.append(chosen)
        # 移除已选中的
        items.pop(idx)
        weights.pop(idx)

    return result


def compute_forgetting_probability(
    delta_t, base_halflife, recognized_count, growth_factor
):
    """
    计算遗忘概率
    delta_t: 距离上次复习的天数
    base_halflife: 基础半衰期(天)
    recognized_count: 累计认识次数
    growth_factor: 每次认识后半衰期的增长系数
    """
    # 个性化半衰期：基础半衰期 * (1 + growth_factor * (recognized_count - 1))
    effective_halflife = base_halflife * (1 + growth_factor * (recognized_count - 1))
    # 避免除零, 设置上限(可选, 365天足够长)
    effective_halflife = min(effective_halflife, 365)
    if delta_t <= 0:
        return 1.0
    return math.pow(2, -delta_t / effective_halflife)


def select_review_words(
    learned_words,
    current_day,
    base_halflife,
    growth_factor,
    target_count,
    all_words_dict,
):
    """
    从已学单词中根据遗忘概率加权随机抽样, 返回选中的单词列表(包含英文和中文)
    learned_words: 用户数据中的 learned_words 字典
    current_day: 当前学习天数
    base_halflife: 基础半衰期
    growth_count: 半衰期增长系数
    target_count: 需要抽取的单词数量
    all_words_dict: 完整单词表 {word: meaning}
    """
    candidates = []
    weights = []
    for word, info in learned_words.items():
        # 只选择还在单词表中的单词(防止单词表更新后已学词被删除)
        if word not in all_words_dict:
            continue
        delta_t = current_day - info.get("last_review")
        rec_count = info.get("recognized_count")
        p = compute_forgetting_probability(
            delta_t, base_halflife, rec_count, growth_factor
        )
        candidates.append(word)
        weights.append(p)

    if not candidates:
        return []
    # 如果候选词不足 target_count, 则全部返回
    n = min(target_count, len(candidates))
    selected = weighted_sample_without_replacement(candidates, weights=weights, k=n)

    # 返回单词及其释义
    return [(word, all_words_dict[word]) for word in selected[:target_count]]


def build_prompt(selected_words_with_meanings):
    """
    根据选中的单词列表生成提示词
    selected_words_with_meanings: [(word, meaning), ...]
    """
    if not selected_words_with_meanings:
        return "No words to review today. Please learn some new words first."

    words_lines = []
    for word, _ in selected_words_with_meanings:
        words_lines.append(f"- {word}")
    words_list_str = "\n".join(words_lines)

    prompt = f"""Write a simple English story that MUST include ALL the words below (and you should **bold** them) :

{words_list_str}

The story should be natural and coherent. 
Only output the story, without extra explanations."""

    return prompt


# ---------- 主入口函数 ----------
def generate_today_prompt():
    """
    生成今天的复习故事提示词
    返回 (prompt, selected_words) 其中 selected_words 为 [(word, meaning), ...]
    """
    # 加载数据
    word_dict = load_wordlist()
    config = load_config()
    user_data = load_user_data()

    current_day = user_data["current_day"]
    learned_words = user_data["learned_words"]

    # 获取配置
    daily_review_words = config["daily_review_words"]
    base_halflife = config["forgetting_curve_halflife"]
    growth_factor = config["halflife_growth_factor"]

    # 根据当前天数动态调整 daily_review_words(每 review_words_growth_days 天 +1)
    growth_days = config["review_words_growth_days"]
    if growth_days > 0:
        extra = (current_day - 1) // growth_days
        daily_review_words = daily_review_words + extra

    # 抽取复习单词
    selected = select_review_words(
        learned_words,
        current_day,
        base_halflife,
        growth_factor,
        daily_review_words,
        word_dict,
    )

    # 更新复习单词
    updated = False
    for word, _ in selected:
        learned_words[word]["recognized_count"] = (
            learned_words[word].get("recognized_count") + 1
        )
        learned_words[word]["last_review"] = current_day
        updated = True
    if updated:
        user_data["learned_words"] = learned_words
        save_user_data(user_data)

    # 生成提示词
    prompt = build_prompt(selected)

    return prompt, selected


# 如果直接运行此脚本, 可以测试
if __name__ == "__main__":
    prompt, words = generate_today_prompt()
    print("===== 提示词 =====")
    print(prompt)
    print("\n===== 选中的单词 =====")
    for w, m in words:
        print(f"{w}: {m}")
