# prompt_generator.py
import csv
import json
import random
import math
from pathlib import Path

# ---------- 路径配置 ----------
WORDLIST_PATH = Path("wordlist/vocab.csv")
CONFIG_PATH = Path("config/settings.json")
USER_DATA_PATH = Path("user_data.json")


# ---------- 辅助函数 ----------
def load_wordlist():
    """加载CSV单词表，返回 {word: meaning} 字典"""
    word_dict = {}
    with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row["word"].strip().lower()
            meaning = row["meaning"].strip()
            if word and meaning:
                word_dict[word] = meaning
    return word_dict


def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    # 确保必要字段存在
    required = [
        "daily_new_words",
        "daily_review_words",
        "review_words_growth_days",
        "forgetting_curve_halflife",
    ]
    for key in required:
        if key not in config:
            raise KeyError(f"配置文件缺少字段: {key}")
    return config


def load_user_data():
    """加载用户学习进度，若文件不存在则创建默认结构"""
    if not USER_DATA_PATH.exists():
        default_data = {
            "current_day": 1,
            "learned_words": {},  # {word: {"last_review": int, "recognized_count": int}}
        }
        save_user_data(default_data)
        return default_data
    with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(data):
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compute_forgetting_probability(delta_t, halflife):
    """
    计算遗忘概率 p = 2^(-delta_t / halflife)
    delta_t: 距离上次复习的天数
    halflife: 半衰期（天）
    """
    if delta_t <= 0:
        return 1.0  # 今天刚复习过，权重设为1（保证有机会被抽到，但实际概率会由抽样算法处理）
    return math.pow(2, -delta_t / halflife)


def select_review_words(
    learned_words, current_day, halflife, target_count, all_words_dict
):
    """
    从已学单词中根据遗忘概率加权随机抽样，返回选中的单词列表（包含英文和中文）
    learned_words: 用户数据中的 learned_words 字典
    current_day: 当前学习天数
    halflife: 半衰期
    target_count: 需要抽取的单词数量
    all_words_dict: 完整单词表 {word: meaning}
    """
    candidates = []
    weights = []
    for word, info in learned_words.items():
        # 只选择还在单词表中的单词（防止单词表更新后已学词被删除）
        if word not in all_words_dict:
            continue
        delta_t = current_day - info["last_review"]
        p = compute_forgetting_probability(delta_t, halflife)
        candidates.append(word)
        weights.append(p)

    if len(candidates) == 0:
        return []  # 没有已学单词

    # 如果候选词不足 target_count，则全部返回
    n = min(target_count, len(candidates))
    selected = random.choices(candidates, weights=weights, k=n)
    # 去重（random.choices 可能有重复，但概率很低，k一般小于候选数，但为了安全）
    selected = list(dict.fromkeys(selected))
    # 若去重后数量不足，再补充（简单处理：从剩余候选词中随机补全）
    if len(selected) < n:
        remaining = [w for w in candidates if w not in selected]
        extra = random.sample(remaining, min(n - len(selected), len(remaining)))
        selected.extend(extra)

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
    for word, meaning in selected_words_with_meanings:
        words_lines.append(f"- {word} ({meaning})")
    words_list_str = "\n".join(words_lines)

    prompt = f"""Write a short English story that MUST include ALL the words below:

{words_list_str}

The story should be natural and coherent. Do NOT limit the length; write as much as needed to make it interesting.
Only output the story, without extra explanations."""

    return prompt


def generate_today_prompt():
    """
    主入口：生成今天的复习故事提示词
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
    halflife = config["forgetting_curve_halflife"]

    # 根据当前天数动态调整 daily_review_words（每 review_words_growth_days 天 +1）
    growth_days = config["review_words_growth_days"]
    if growth_days > 0:
        extra = (current_day - 1) // growth_days
        daily_review_words = min(
            daily_review_words + extra, len(word_dict)
        )  # 不超过总词数

    # 抽取复习单词
    selected = select_review_words(
        learned_words, current_day, halflife, daily_review_words, word_dict
    )

    # 生成提示词
    prompt = build_prompt(selected)

    return prompt, selected


# 如果直接运行此脚本，可以测试
if __name__ == "__main__":
    prompt, words = generate_today_prompt()
    print("===== 提示词 =====")
    print(prompt)
    print("\n===== 选中的单词 =====")
    for w, m in words:
        print(f"{w}: {m}")
