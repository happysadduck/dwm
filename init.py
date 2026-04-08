# init.py
import json
import shutil
from pathlib import Path
from datetime import datetime

# 默认配置文件内容
DEFAULT_SETTINGS = {
    "daily_new_words": 10,
    "daily_review_words": 5,
    "review_words_growth_days": 3,
    "forgetting_curve_halflife": 3.0,
    "halflife_growth_factor": 0.5,
}

# 默认用户数据文件内容
DEFAULT_USER_DATA = {"current_day": 0, "learned_words": {}}


def backup_file(file_path: Path):
    """如果文件存在, 则备份为 文件名_时间戳.backup.json"""
    if file_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.backup"
        backup_path = file_path.parent / backup_name
        shutil.copy2(file_path, backup_path)
        print(f"已备份: {file_path.name} -> {backup_name}")
        return True
    return False


def write_default_file(file_path: Path, default_content, is_json=True):
    """写入默认内容到文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(default_content, f, indent=2, ensure_ascii=False)
    print(f"已创建: {file_path.name}")


def init():
    # 当前工作目录(脚本所在目录)
    base_dir = Path.cwd()
    settings_path = base_dir / "settings.json"
    user_data_path = base_dir / "user_data.json"

    print("=== 初始化单词学习系统 ===")

    # 处理 settings.json
    if settings_path.exists():
        print(f"发现已存在的 {settings_path.name}, 执行备份...")
        backup_file(settings_path)
    write_default_file(settings_path, DEFAULT_SETTINGS)

    # 处理 user_data.json
    if user_data_path.exists():
        print(f"发现已存在的 {user_data_path.name}, 执行备份...")
        backup_file(user_data_path)
    write_default_file(user_data_path, DEFAULT_USER_DATA)

    print("初始化完成. ")


if __name__ == "__main__":
    init()
