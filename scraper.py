import requests
from bs4 import BeautifulSoup
import json

def fetch_pricing():
    url = 'https://aws.amazon.com/bedrock/pricing/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Filter sections containing 'On-Demand and Batch pricing'
    sections = soup.find_all("div", class_="lb-row lb-row-max-large lb-snap lb-gutter-mid")
    pricing_data = {}
    
    for section in sections:
        if 'On-Demand and Batch pricing' in section.text:
            table = section.find("table")
            rows = table.find('tbody').find_all('tr')[1:]  # Skip the header
            for row in rows:
                columns = row.find_all('td')
                if len(columns) > 2:  # Ensure there are three columns for pricing
                    model_name = columns[0].text.strip()
                    input_price = columns[1].text.strip()
                    output_price = columns[2].text.strip()
                    pricing_data[model_name] = {
                        "Price per 1,000 input tokens": input_price,
                        "Price per 1,000 output tokens": output_price
                    }

    # Save the collected data
    with open('pricing_data_on_demand_batch.json', 'w') as f:
        json.dump(pricing_data, f, indent=4)

if __name__ == "__main__":
    fetch_pricing()
