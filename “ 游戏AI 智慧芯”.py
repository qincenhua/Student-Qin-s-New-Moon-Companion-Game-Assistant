# main.py
import intent_recognition as ir
import image_recognition as irg
import openai_interaction as oai
import utilities as ut
import time
import pyautogui  # 用于模拟键鼠操作，需要安装
import asyncio  # 用于异步处理
import concurrent.futures  # 用于多线程处理

# 定义意图类别和对应的处理函数
INTENT_CATEGORIES = {
    "查询信息": {
        "keywords": ["查询", "了解", "知道", "查找"],
        "function": lambda query: asyncio.run(oai.get_information_async(query))
    },
    "执行操作": {
        "keywords": ["执行", "操作", "进行", "开展"],
        "function": lambda operation: asyncio.run(oai.perform_operation_async(operation))
    },
    "解决问题": {
        "keywords": ["解决", "处理", "应对", "克服"],
        "function": lambda problem: asyncio.run(oai.solve_problem_async(problem))
    },
    "获取建议": {
        "keywords": ["建议", "意见", "参考", "提议"],
        "function": lambda topic: asyncio.run(oai.give_advice_async(topic))
    },
    "游戏操作": {
        "keywords": ["打开游戏", "玩游戏", "启动游戏"],
        "function": lambda game_name: asyncio.run(operate_game_async(game_name))
    }
}

async def operate_game_async(game_name):
    """
    异步处理游戏操作

    参数:
    game_name (str): 游戏名称

    返回:
    str: 操作结果的描述
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        game_icon = await asyncio.get_event_loop().run_in_executor(executor, irg.find_game_icon, game_name)
        if game_icon:
            # 模拟鼠标点击游戏图标
            pyautogui.click(game_icon)
            time.sleep(5)  # 等待游戏窗口加载

            # 查找开始游戏按钮的位置
            start_button = await asyncio.get_event_loop().run_in_executor(executor, irg.find_start_button)
            if start_button:
                pyautogui.click(start_button)
                time.sleep(10)  # 等待进入游戏

                # 查找类似门的元素并点击
                door_element = await asyncio.get_event_loop().run_in_executor(executor, irg.find_door_element)
                if door_element:
                    pyautogui.click(door_element)
                    time.sleep(10)  # 等待操作完成
                    return f"已为您在游戏{game_name}中进行相应操作。"
                else:
                    return f"未找到游戏{game_name}中的门元素。"
            else:
                return f"未找到游戏{game_name}的开始游戏按钮。"
        else:
            return f"未在桌面上找到游戏{game_name}的图标。"

conversation_history = []
while True:
    user_input = input("您: ")
    if user_input.lower() == "q":
        response = await oai.get_response_async("与用户进行交流", conversation_history)
        print("AI: ", response)
        conversation_history.append(user_input)
        conversation_history.append(response)
    else:
        intent = ir.analyze_user_input(user_input)
        if intent == "未知意图":
            response = "抱歉，我不太理解您的需求，您可以尝试询问查询信息、执行操作、解决问题等。"
        else:
            response = await INTENT_CATEGORIES[intent]["function"](user_input)
        print("AI: ", response)
        conversation_history.append(user_input)
        conversation_history.append(response)