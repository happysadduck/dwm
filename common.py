import csv
import json
from pathlib import Path

# ---------- 路径配置 ----------
WORDLIST_PATH = Path("wordlist/vocab.csv")
CONFIG_PATH = Path("config/settings.json")
USER_DATA_PATH = Path("user_data.json")


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
    if "halflife_growth_factor" not in config:
        config["halflife_growth_factor"] = 0.5
    return config


def load_user_data():
    """加载用户学习进度，若文件不存在则创建默认结构"""
    if not USER_DATA_PATH.exists():
        default_data = {
            "current_day": 1,
            "learned_words": {},  # {word: {"last_review": int, "recognized_count": int}}
            "pending_new_words": [],  # 存储待测队列 [(word, meaning), ...]
        }
        save_user_data(default_data)
        return default_data
    with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(data):
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
