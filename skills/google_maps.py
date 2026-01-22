
import googlemaps
import os
from dotenv import load_dotenv

# 加载 .env 里的 API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GoogleMapsAgent:
    def __init__(self):
        if not API_KEY:
            print("⚠️ Warning: GOOGLE_MAPS_API_KEY not found in .env")
            self.client = None
        else:
            self.client = googlemaps.Client(key=API_KEY)

    def search_places(self, query, location=None):
        """
        模拟在 Google Maps 上搜索。
        """
        if not self.client:
            return []

        try:
            # Places API Text Search
            results = self.client.places(query=query)
            if results['status'] == 'OK':
                return results['results']
            else:
                return []
        except Exception as e:
            print(f"Error searching Google Maps: {e}")
            return []

    def get_place_details(self, place_id):
        """
        获取某个地点的详细信息
        """
        if not self.client:
            return {}

        try:
            # 获取具体字段：名字, 格式化地址, 电话, 类型, 永久关闭状态
            result = self.client.place(place_id=place_id, fields=['name', 'formatted_address', 'formatted_phone_number', 'types', 'permanently_closed'])
            return result.get('result', {})
        except Exception as e:
            print(f"Error getting details: {e}")
            return {}

# 测试代码 (只有直接运行此文件时才会执行)
if __name__ == "__main__":
    agent = GoogleMapsAgent()
    print(agent.search_places("Coffee shops in Boulder, CO"))