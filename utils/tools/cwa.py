import ssl
import aiohttp
import certifi
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("CWA_KEY")

ssl_context = ssl.create_default_context(cafile=certifi.where())

locationNames = ['嘉義縣', '新北市', '嘉義市', '新竹縣', '新竹市', '臺北市', '臺南市', '宜蘭縣', '苗栗縣', '雲林縣', '花蓮縣', '臺中市', '臺東縣', '桃園市', '南投縣', '高雄市', '金門縣', '屏東縣', '基隆市', '澎湖縣', '彰化縣', '連江縣']
elementNames = {
    "MinT": "最低溫度",
    "MaxT": "最高溫度",
    "PoP": "降雨機率",
    "CI": "降雨量",
    "Wx": "天氣現象"
}

# F-C0032-001 今明36小時天氣預報
async def get_forcast_36h(locationName):
    # 檢查locationName是否正確
    if locationName not in locationNames:
        return { "status": "error", "status_code": 404, "response": F"Error: {locationName} is not a valid location name." }

    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": KEY,
        "locationName": locationName
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as resp:
            if resp.status != 200:
                print(F"Error: {resp.status}")
                return { "status": "error", "status_code": resp.status }
            results = await resp.json()
            return {"status": "success", "results": results["records"]["location"][0]["weatherElement"]}


# E-A0015-001 顯著有感地震報告
async def get_remarkable_earthquake(limit=1):
    url = F"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
    params = {
        "Authorization": KEY,
        "limit": limit,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as resp:
            # 檢查伺服器回傳的狀態碼是否為 200
            if resp.status != 200:
                print(F"Error: {resp.status}")
                return { "status": "error", "status_code": resp.status }

            results = await resp.json()

            # 簡化震度資料
            for record in results["records"]["Earthquake"]:
                record["MaxIntensity"] = {} # 建立最大震度

                # 僅保留最大震度
                for s in record["Intensity"]["ShakingArea"]:
                    if "最大震度" in s["AreaDesc"]:
                        record["MaxIntensity"][s["AreaDesc"]]= s["CountyName"]

                del record["Intensity"] # 刪除原震度資料

            return results["records"]["Earthquake"]

# W-C0033-001 天氣特報-各別縣市地區目前之天氣警特報情形
async def get_weather_warning_by_location(locationName):
    url = F"https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001"
    params = {
        "Authorization": KEY,
        "locationName": locationName
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as resp:
            # 檢查伺服器回傳的狀態碼是否為 200
            if resp.status != 200:
                print(F"Error: {resp.status}")
                return { "status": "error", "status_code": resp.status }
            results = await resp.json()

            return results["records"]["location"]

# W-C0033-002 天氣特報-各別天氣警特報之內容及所影響之區域
async def get_weather_warning():
    url = F"https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-002"
    params = {
        "Authorization": KEY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as resp:
            # 檢查伺服器回傳的狀態碼是否為 200
            if resp.status != 200:
                print(F"Error: {resp.status}")
                return { "status": "error", "status_code": resp.status }
            results = await resp.json()

            # 整理過長資料(受影響區域)
            for record in results["records"]["record"]:
                new_affectedAreas = []
                affectedAreas = record["hazardConditions"]["hazards"]["hazard"][0]["info"]["affectedAreas"]["location"]
                for area in affectedAreas:
                    new_affectedAreas.append(area["locationName"])

                record["affectedAreas"] = new_affectedAreas
                del record["hazardConditions"] # 刪除原資料

            return results["records"]["record"]

# O-A0003-001 現在天氣觀測報告-有人氣象站資料
async def get_current_weather(locationName):
    county_to_station = {
        "基隆市": "基隆",
        "臺北市": "臺北",
        "新北市": "新北",
        "桃園市": "新屋",
        "新竹市": "新竹",
        "苗栗縣": "後龍",
        "臺中市": "臺中",
        "彰化縣": "田中",
        "南投縣": "日月潭",
        "雲林縣": "古坑",
        "嘉義市": "嘉義",
        "嘉義縣": "嘉義",
        "臺南市": "臺南",
        "高雄市": "高雄",
        "屏東縣": "恆春",
        "花蓮縣": "花蓮",
        "臺東縣": "臺東",
        "宜蘭縣": "宜蘭",
        "澎湖縣": "澎湖",
        "金門縣": "金門",
        "連江縣": "馬祖",
        "東沙島": "東沙島",
        "南沙島": "南沙島"
    }

    url = F"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
    params = {
        "Authorization": KEY,
        "StationName": county_to_station[locationName]
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as resp:
            # 檢查伺服器回傳的狀態碼是否為 200
            if resp.status != 200:
                print(F"Error: {resp.status}")
                return { "status": "error", "status_code": resp.status }
            results = await resp.json()

            return results["records"]