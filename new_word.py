import random
from common import *


def clear_screen_by_scroll(lines=40):
    """通过打印多个换行实现终端下翻，不清除历史"""
    print("\n" * lines)


def get_unlearned_words(word_dict, learned_words):
    """返回未学过的单词列表（英文，中文）"""
    unlearned = []
    for word, meaning in word_dict.items():
        if word not in learned_words:
            unlearned.append((word, meaning))
    return unlearned


def run_new_words_session(current_day):
    """
    执行新词学习会话
    current_day: 当前学习天数，用于设置 last_review
    """
    # 加载数据
    word_dict = load_wordlist()
    config = load_config()
    user_data = load_user_data()

    daily_new_words = config["daily_new_words"]
    learned_words = user_data.get("learned_words", {})

    # 检查是否有未完成的队列
    pending = user_data.get("pending_new_words", [])
    if pending:
        print(f"检测到未完成的新词学习，共 {len(pending)} 个单词待学完。")
        test_queue = pending
    else:
        # 抽取新词
        unlearned = get_unlearned_words(word_dict, learned_words)
        if not unlearned:
            print("所有单词都已学过！无需学习新词。")
            return
        # 随机抽取 daily_new_words 个（不超过总数）
        n = min(daily_new_words, len(unlearned))
        test_queue = random.sample(unlearned, n)
        print(f"今日新词 {n} 个：{', '.join(w for w, _ in test_queue)}")

    # 开始多轮测试
    round_num = 1
    while test_queue:
        clear_screen_by_scroll(40)
        print(f"=== 第 {round_num} 轮 ===")
        next_round = []
        for word, meaning in test_queue:
            # 显示英文，等待用户输入
            user_input = input(f"\n单词: {word}\n认识吗？(y/n): ").strip().lower()
            if user_input in ("y", "yes", "是"):
                # 认识：移入已学库
                learned_words[word] = (
                    {
                        "last_review": current_day,
                        "recognized_count": 1,
                    }
                    if round_num != 1
                    else {
                        "last_review": current_day,
                        "recognized_count": 1000,  # 设置一个很大的数, 让学习前认识的词几乎不可能被抽取
                    }
                )
                print(f"✓ {word} 已掌握")
            else:
                # 不认识：显示中文
                print(f"✗ {word} 的意思是：{meaning}")
                # 放回下一轮
                next_round.append((word, meaning))
        # 更新待测队列
        test_queue = next_round
        round_num += 1

        # 保存进度（以便中断恢复）
        user_data["learned_words"] = learned_words
        user_data["pending_new_words"] = test_queue
        save_user_data(user_data)

        # 需要回车确认, 防止最后一个单词示意被翻走
        input("\n本轮结束，按回车键继续下一轮...")

    # 全部学完，清除 pending
    user_data["pending_new_words"] = []
    save_user_data(user_data)
    print("\n🎉 今日新词全部学会！")


# 如果直接运行脚本
if __name__ == "__main__":
    # 需要传入当前天数（可以从 user_data 中读取）
    data = load_user_data()
    current_day = data.get("current_day", 1)
    run_new_words_session(current_day)
