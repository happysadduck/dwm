# common.py
import csv
import json
from pathlib import Path

# ---------- 路径配置(所有文件在程序同级目录)----------
WORDLIST_PATH = Path("vocab.csv")
CONFIG_PATH = Path("settings.json")
USER_DATA_PATH = Path("user_data.json")


def load_wordlist():
    """加载CSV单词表, 返回 {word: meaning} 字典.
    如果文件不存在/ 缺少列或为空, 直接抛出异常.
    """
    if not WORDLIST_PATH.exists():
        raise FileNotFoundError(f"单词表文件 {WORDLIST_PATH} 不存在, 请准备 vocab.csv")

    word_dict = {}
    with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "word" not in reader.fieldnames or "meaning" not in reader.fieldnames:
            raise ValueError("单词表 CSV 必须包含 'word' 和 'meaning' 列")
        for row in reader:
            word = row["word"].strip().lower()
            meaning = row["meaning"].strip()
            if word and meaning:
                word_dict[word] = meaning
    if not word_dict:
        raise ValueError("单词表为空或格式错误")
    return word_dict


def load_config():
    """加载配置文件, 文件不存在或 JSON 无效时直接抛出异常"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件 {CONFIG_PATH} 不存在, 请运行 init.py 初始化")
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件 {CONFIG_PATH} 格式错误(无效 JSON): {e}")

    # 检查必要字段
    required = [
        "daily_new_words",
        "daily_review_words",
        "review_words_growth_days",
        "forgetting_curve_halflife",
        "halflife_growth_factor",
    ]
    for key in required:
        if key not in config:
            raise KeyError(f"配置文件缺少字段: {key}")
    return config


def load_user_data():
    """加载用户数据文件, 文件不存在或 JSON 无效时直接抛出异常"""
    if not USER_DATA_PATH.exists():
        raise FileNotFoundError(
            f"用户数据文件 {USER_DATA_PATH} 不存在, 请运行 init.py 初始化"
        )
    try:
        with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"用户数据文件 {USER_DATA_PATH} 格式错误(无效 JSON): {e}")

    # 检查必要字段
    required_fields = ["current_day", "learned_words"]
    for field in required_fields:
        if field not in data:
            raise KeyError(f"用户数据文件缺少字段: {field}")
    if not isinstance(data["learned_words"], dict):
        raise TypeError("learned_words 必须是字典")
    return data


def save_user_data(data):
    """保存用户数据到文件"""
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
