
import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv

# 确保能引用到 skills 文件夹
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skills.google_maps import GoogleMapsAgent

def main():
    # 1. 初始化
    load_dotenv()
    print(">>> Initializing Synthetic Urban Intelligence Agent...")

    maps_agent = GoogleMapsAgent()

    # 2. 设定任务 (这里暂时写死，后面我们会从 Prompt 读入)
    target_city = "Boulder, CO"
    target_category = "Coffee Shop"
    query = f"{target_category} in {target_city}"

    print(f">>> Agent is searching for: {query}")

    # 3. 执行工具调用 (Skills)
    # 注意：如果你没有配置 API Key，这里会返回空列表
    raw_results = maps_agent.search_places(query)
    print(f">>> Found {len(raw_results)} candidates.")

    # 4. 数据处理 (简单的 ETL)
    processed_data = []
    for place in raw_results:
        # 模拟获取详情
        details = maps_agent.get_place_details(place['place_id'])

        # 映射到简单的 NETS 结构
        row = {
            "Company": details.get('name'),
            "Address": details.get('formatted_address'),
            "City": "Boulder",
            "Tags": ", ".join(details.get('types', [])),
            "PlaceID": place['place_id']
        }
        processed_data.append(row)

    # 5. 输出结果
    if processed_data:
        # 确保 data 目录存在
        os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)
        output_path = os.path.join(os.path.dirname(__file__), '../data/synthetic_business.csv')

        df = pd.DataFrame(processed_data)
        df.to_csv(output_path, index=False)
        print(f">>> Success! Data saved to {output_path}")
        print(df.head())
    else:
        print(">>> No data found (Did you add your API Key to .env?).")

if __name__ == "__main__":
    main()