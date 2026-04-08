from common import *

if __name__ == "__main__":
    user_data = load_user_data()
    user_data["current_day"] = user_data.get("current_day") + 1
    save_user_data(user_data)
    print(f"当前学习天数已更新为第 {user_data['current_day']} 天")
