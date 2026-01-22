import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv

# Make sure we can find the 'skills' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skills.google_maps import GoogleMapsAgent

def main():
    # 1. Start the system
    load_dotenv()
    print(">>> Starting the AI Agent...")

    maps_agent = GoogleMapsAgent()

    # 2. Set the task (Now it is fixed here, later we will use Prompts)
    target_city = "Boulder, CO"
    target_category = "Coffee Shop"
    query = f"{target_category} in {target_city}"

    print(f">>> The Agent is looking for: {query}")

    # 3. Use the tools (Skills)
    # Note: If you do not have the API Key in .env, you will get nothing
    raw_results = maps_agent.search_places(query)
    print(f">>> Found {len(raw_results)} places.")

    # 4. Process the data
    processed_data = []
    for place in raw_results:
        # Get more details for this place
        details = maps_agent.get_place_details(place['place_id'])

        # Make the data look like the NETS database
        row = {
            "Company": details.get('name'),
            "Address": details.get('formatted_address'),
            "City": "Boulder",
            "Tags": ", ".join(details.get('types', [])),
            "PlaceID": place['place_id']
        }
        processed_data.append(row)

    # 5. Save the result
    if processed_data:
        # Make sure the 'data' folder exists
        os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)
        output_path = os.path.join(os.path.dirname(__file__), '../data/synthetic_business.csv')

        df = pd.DataFrame(processed_data)
        df.to_csv(output_path, index=False)
        print(f">>> Success! Data saved to {output_path}")
        print(df.head())
    else:
        print(">>> No data found (Did you put your API Key in .env?).")

if __name__ == "__main__":
    main()