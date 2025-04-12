from openai import OpenAI
import time
import json
from utils.tools import cwa
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 定義tool_calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_forcast_36h",
            "description": "查詢地方的天氣預報。",
            "parameters": {
                "type": "object",
                "properties": {
                    "locationName": {
                        "type": "string",
                        "description": "欲查詢天氣的縣市名稱，例如：臺北市。",
                    }
                },
                "required": ["locationName"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_remarkable_earthquake",
            "description": "查詢最近的顯著有感地震。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "查詢的地震數量，預設為1。"
                    }
                },
                "required": ["limit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "查詢各縣市氣象站即時觀測資料。",
            "parameters": {
                "type": "object",
                "properties": {
                    "locationName": {
                        "type": "string",
                        "description": "欲查詢天氣的縣市名稱，例如：臺北市。",
                    }
                },
                "required": ["locationName"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_warning",
            "description": "查詢最近的天氣預警。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "取得當前時間",
        }
    }
]

async def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

tools_name = {
    "get_forcast_36h": cwa.get_forcast_36h,
    "get_current_time": get_current_time,
    "get_remarkable_earthquake": cwa.get_remarkable_earthquake,
    "get_weather_warning": cwa.get_weather_warning,
    "get_current_weather": cwa.get_current_weather
}

async def tool_calling(name, args):
    if name in tools_name:
        result = await tools_name[name](**args)
        return result
    else:
        print(f"Unknown function: {name}")

async def chat(msgs):
    start = time.time()

    # 讀取對話紀錄
    with open("data/chat_history.json", "r", encoding="utf-8") as f:
        chat_history = json.load(f)

    # 加入對話紀錄(因為可能有回覆所以用迴圈)
    for msg in msgs:
        chat_history.append(msg)

    # 例外處理
    try:
        # 對Gemini發送API請求
        response = client.chat.completions.create(
            messages=chat_history, # 對話紀錄
            model="gemini-2.0-flash", # 模型
            temperature=0.7, # 創意度
            max_tokens=2048, # 最大token
            top_p=1,
            tools=tools,
            tool_choice="auto" # AI自己選擇function
        )

        assistant_resp = response.choices[0]

        used_calls = []
        # 用finish_reason檢查是否為tool_calls
        if assistant_resp.finish_reason == "tool_calls":
            calls = assistant_resp.message.tool_calls
            # 讓AI確認tools_call狀態
            chat_history.append({
                "role": "assistant",
                "tool_calls": [call.model_dump() for call in calls],
                "content": assistant_resp.message.content
            })

            for call in calls:
                used_calls.append(call.function.name)
                args = json.loads(call.function.arguments)  # 這裡把字串轉成 dict
                result = await tool_calling(call.function.name, args)
                chat_history.append({
                    "role": "function",
                    "name": call.function.name,
                    "content": json.dumps(result, ensure_ascii=False), # 把結果轉成字串
                })

            # 回傳tools_call的content
            yield {"status": "success", "response": assistant_resp.message.content, "duration": time.time() - start, "used_calls": used_calls}

            # 將結果加入對話紀錄
            response = client.chat.completions.create(
                messages=chat_history, # 對話紀錄
                model="gemini-2.0-flash", # 模型
                temperature=0.7, # 創意度
                max_tokens=2048, # 最大token
                top_p=1,
                tools=tools,
                tool_choice="auto" # AI自己選擇function
            )
            assistant_msg = response.choices[0].message.content
        else:
            assistant_msg = assistant_resp.message.content # 直接回傳訊息

        chat_history.append({
            "role": "assistant",
            "content": assistant_msg,
        })
        with open("data/chat_history.json", "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)

        yield {"status": "success", "response": assistant_msg, "duration": time.time() - start}
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}")
        yield {"status": "error","response": F"Something went wrong.", "duration": time.time() - start}

async def chat_api(msgs):
    start = time.time()

    try:
        response = client.chat.completions.create(
            messages=msgs,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
        )

        assistant_msg = response.choices[0].message.content

        return {"status": "success", "response": assistant_msg, "duration": time.time() - start}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error","response": F"Something went wrong.", "duration": time.time() - start}