
import tkinter as tk
from tkinter import messagebox
import requests
import hashlib

# 游戏助手类
class GameAssistant:
    def __init__(self):
        self.game_name = "新月同行"
        self.user_id = None
        self.api_key = "your_secret_api_key"
        self.server_url = "https://your_real_server.com"  # 请将此修改为实际的服务器地址

    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            response = requests.post(f"{self.server_url}/auth/login", json={"username": username, "password": hashed_password})
            if response.status_code == 200:
                self.user_id = response.json()["user_id"]
                return True
            else:
                return False
        except requests.RequestException as e:
            print(f"登录时出现错误：{e}")
            return False

    def fetch_game_data(self):
        if self.user_id:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.get(f"{self.server_url}/user/{self.user_id}/game_data", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.update_player_data(data)
                    return True
                else:
                    return False
            except requests.RequestException as e:
                print(f"获取游戏数据时出现错误：{e}")
                return False

    def update_player_data(self, data):
        self.player_data = data

    def complete_daily_task(self, task_name):
        if self.user_id:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.post(f"{self.server_url}/user/{self.user_id}/update_daily_task", headers=headers, json={"task_name": task_name})
                if response.status_code == 200:
                    # 根据服务器返回的响应处理奖励和数据更新
                    return True
                else:
                    print(f"更新任务状态失败：{response.text}")
                    return False
            except requests.RequestException as e:
                print(f"更新任务状态时出现错误：{e}")
                return False
        else:
            return False

    def start_auto_battle(self):
        if self.user_id and self.check_enough_energy_for_battle():
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.post(f"{self.server_url}/user/{self.user_id}/start_auto_battle", headers=headers)
                if response.status_code == 200:
                    battle_result = response.json()
                    self.process_battle_result(battle_result)
                    return True
                else:
                    print(f"开始自动战斗失败：{response.text}")
                    return False
            except requests.RequestException as e:
                print(f"开始自动战斗时出现错误：{e}")
                return False
        else:
            messagebox.showinfo("提示", "能量不足，无法进行战斗。")
            return False

    def check_enough_energy_for_battle(self):
        return self.player_data.get("resources", {}).get("energy", 0) >= 10

    def process_battle_result(self, battle_result):
        if battle_result.get("won", False):
            messagebox.showinfo("战斗结果", "战斗胜利！")
            # 根据实际战斗结果更新玩家数据
            self.update_resources(battle_result.get("rewards", {}))
            self.player_data["battle_history"].append({
                "result": "win",
                "rewards": battle_result["rewards"]
            })
            self.player_data["energy"] -= 10
        else:
            messagebox.showinfo("战斗结果", "战斗失败。")
            self.player_data["battle_history"].append({
                "result": "loss",
                "rewards": None
            })
            self.player_data["energy"] -= 5

    def update_resources(self, rewards):
        if "currency" in rewards:
            self.player_data["resources"]["currency"] += rewards["currency"]
        if "experience" in rewards:
            self.player_data["resources"]["experience"] += rewards["experience"]
        if "materials" in rewards:
            self.player_data["resources"]["materials"].extend(rewards["materials"])

    def upgrade_character(self, character_name):
        if self.user_id:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.post(f"{self.server_url}/user/{self.user_id}/upgrade_character", headers=headers, json={"character_name": character_name})
                if response.status_code == 200:
                    # 根据服务器返回的数据更新玩家角色信息
                    return True
                else:
                    print(f"升级角色失败：{response.text}")
                    return False
            except requests.RequestException as e:
                print(f"升级角色时出现错误：{e}")
                return False
        else:
            return False

    def show_game_info(self):
        info_text = f"游戏名称: {self.game_name}\n\n玩家资源:\n"
        info_text += f" - 货币: {self.player_data['resources']['currency']}\n"
        info_text += f" - 材料: {', '.join(self.player_data['resources']['materials'])}\n"
        info_text += f" - 经验: {self.player_data['resources']['experience']}\n"
        info_text += f" - 能量: {self.player_data['resources']['energy']}\n"
        info_text += "\n角色列表:\n"
        for character in self.player_data["characters"]:
            info_text += f"- {character['name']} (等级: {character['level']})\n"
        info_text += "\n日常任务:\n"
        for task, status in self.player_data["daily_tasks"].items():
            info_text += f"- {task}: {'已完成' if status else '未完成'}\n"
        info_text += "\n周常任务:\n"
        for task, status in self.player_data["weekly_tasks"].items():
            info_text += f"- {task}: {'已完成' if status else '未完成'}\n"
        info_text += "\n主线任务进度:\n"
        for quest, progress in self.player_data["quest_progress"].items():
            info_text += f"- {quest}: {progress}\n"
        info_text += "\n卡带系统信息:\n"
        for info_key, info_value in self.card_system_info.items():
            info_text += f"{info_key}: {info_value}\n"
        info_text += "\n背包物品:\n"
        info_text += f"- {', '.join(self.player_data['inventory'])}"
        messagebox.showinfo("游戏助手 - 游戏信息", info_text)

    def check_events(self):
        if self.user_id:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.get(f"{self.server_url}/user/{self.user_id}/events", headers=headers)
                if response.status_code == 200:
                    self.events = response.json()
                    return True
                else:
                    return False
            except requests.RequestException as e:
                print(f"获取事件时出现错误：{e}")
                return False
        else:
            return False

    def simulate_gacha(self):
        if self.user_id:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.post(f"{self.server_url}/user/{self.user_id}/gacha", headers=headers)
                if response.status_code == 200:
                    gacha_result = response.json()
                    # 处理抽卡结果并更新玩家数据
                    return True
                else:
                    print(f"抽卡失败：{response.text}")
                    return False
            except requests.RequestException as e:
                print(f"抽卡时出现错误：{e}")
                return False

# 创建 GUI 类
class GameGUI:
    def __init__(self, game_assistant):
        self.game_assistant = game_assistant
        self.root = tk.Tk()
        self.root.title("新月同行 游戏助手")

        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")
        self.login_button = tk.Button(self.root, text="登录", command=self.login)

        def show_info():
            if self.game_assistant.user_id:
                self.game_assistant.show_game_info()
            else:
                messagebox.showinfo("错误", "请先登录。")

        def complete_task(task_name):
            if self.game_assistant.user_id:
                if self.game_assistant.complete_daily_task(task_name):
                    messagebox.showinfo("任务完成", f"{task_name}任务已完成。")
                else:
                    messagebox.showinfo("错误", f"无法完成{task_name}任务。")
            else:
                messagebox.showinfo("错误", "请先登录。")

        def start_battle():
            if self.game_assistant.user_id:
                if self.game_assistant.start_auto_battle():
                    messagebox.showinfo("战斗结果", "自动战斗已完成。")
                else:
                    messagebox.showinfo("错误", "无法开始自动战斗。")
            else:
                messagebox.showinfo("错误", "请先登录。")

        def upgrade_character(character_name):
            if self.game_assistant.user_id:
                if self.game_assistant.upgrade_character(character_name):
                    messagebox.showinfo("升级结果", f"{character_name}已成功升级。")
                else:
                    messagebox.showinfo("错误", f"无法升级{character_name}。")
            else:
                messagebox.showinfo("错误", "请先登录。")

        def check_events():
            if self.game_assistant.user_id:
                if self.game_assistant.check_events():
                    event_text = "当前事件：\n"
                    for event in self.game_assistant.events:
                        event_text += f"- {event['description']}\n"
                    messagebox.showinfo("事件信息", event_text)
                else:
                    messagebox.showinfo("错误", "无法获取事件信息。")
            else:
                messagebox.showinfo("错误", "请先登录。")

        def simulate_gacha():
            if self.game_assistant.user_id:
                self.game_assistant.simulate_gacha()
            else:
                messagebox.showinfo("错误", "请先登录。")

        # 创建按钮
        info_button = tk.Button(self.root, text="查看游戏信息", command=show_info)
        daily_login_button = tk.Button(self.root, text="完成每日登录", command=lambda: complete_task("daily_login"))
        main_quest_button = tk.Button(self.root, text="完成主线任务进度", command=lambda: complete_task("main_quest_progress"))
        battle_button = tk.Button(self.root, text="开始自动战斗", command=start_battle)
        upgrade_character_button = tk.Button(self.root, text="升级角色", command=lambda: upgrade_character("character_name"))
        check_events_button = tk.Button(self.root, text="查看事件", command=check_events)
        gacha_button = tk.Button(self.root, text="模拟抽卡", command=simulate_gacha)

        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)
        self.login_button.pack(pady=10)
        info_button.pack(pady=10)
        daily_login_button.pack(pady=10)
        main_quest_button.pack(pady=10)
        battle_button.pack(pady=10)
        upgrade_character_button.pack(pady=10)
        check_events_button.pack(pady=10)
        gacha_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.game_assistant.authenticate_user(username, password):
            if self.game_assistant.fetch_game_data():
                messagebox.showinfo("成功", "登录成功并获取游戏数据。")
            else:
                messagebox.showinfo("错误", "登录成功，但获取游戏数据失败。")
        else:
            messagebox.showinfo("错误", "登录失败。")

    def run(self):
        self.root.mainloop()

# 创建游戏助手实例和 GUI 实例并运行
game_assistant = GameAssistant()
game_gui = GameGUI(game_assistant)
game_gui.run()