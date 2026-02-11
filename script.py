import requests
import pandas as pd
import time

API_KEY = "9a89b06d71262c1f7f0a3f710ba4fd2a4032df5acdf73332a97284bb26edce12"
TARGET = 50

SEARCH_QUERIES = [
    "hospital",
    "clinic",
    "medical center",
    "pharmacy",
    "healthcare"
]

def get_google_maps_results():
    collected = []
    seen = set()
    next_page_token = None
    query_index = 0

    while len(collected) < TARGET:
        params = {
            "engine": "google_maps",
            "q": SEARCH_QUERIES[query_index],
            "ll": "@25.2854,51.5310,11z",  # 🔹 wider radius
            "hl": "en",
            "type": "search",
            "api_key": API_KEY
        }

        if next_page_token:
            params["next_page_token"] = next_page_token

        response = requests.get(
            "https://serpapi.com/search.json",
            params=params,
            timeout=30
        )
        data = response.json()

        results = data.get("local_results", [])
        if not results:
            # move to next query if current exhausted
            query_index += 1
            next_page_token = None

            if query_index >= len(SEARCH_QUERIES):
                break

            continue

        for place in results:
            name = place.get("title")
            if not name or name in seen:
                continue

            seen.add(name)

            collected.append({
                "Company Name": name,
                "Website": place.get("website", "N/A"),
                "Phone": place.get("phone", "N/A"),
                "Address": place.get("address", "N/A"),
                "Rating": place.get("rating", "N/A"),
            })

            if len(collected) == TARGET:
                return collected  

        next_page_token = data.get("serpapi_pagination", {}).get("next_page_token")

        if not next_page_token:
            query_index += 1

        time.sleep(2)  # ⏱ mandatory for SerpAPI

    return collected


def main():
    print("[INFO] Collecting 50 healthcare businesses from Google Maps (Qatar)")
    records = get_google_maps_results()

    if len(records) < TARGET:
        raise RuntimeError(
            f"Only {len(records)} businesses found. "
            "Google Maps did not return enough data."
        )

    df = pd.DataFrame(records)
    df.to_csv(
        "qatar_healthcare_companies.csv",
        index=False,
        encoding="utf-8"
    )

    print(f"[DONE] Saved {len(df)} businesses  qatar_healthcare_companies.csv")


if __name__ == "__main__":
    main()
