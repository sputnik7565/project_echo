import os
import requests
import json
from django.conf import settings

class NaverCollector:
    def __init__(self):
        self.client_id = settings.NAVER_CLIENT_ID
        self.client_secret = settings.NAVER_CLIENT_SECRET
        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID or NAVER_CLIENT_SECRET is not set in settings.")
        self.datalab_headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        self.shopping_headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        self.datalab_url = "https://openapi.naver.com/v1/datalab/search"
        self.shopping_url = "https://openapi.naver.com/v1/search/shop.json"

    def get_search_trends(self, keywords, start_date, end_date, time_unit="date"):
        results = {}
        for keyword_group in keywords:
            if not isinstance(keyword_group, list) or len(keyword_group) > 5:
                raise ValueError("Each keyword group must be a list of up to 5 keywords.")

            body = {
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": time_unit,
                "keywordGroups": [
                    {
                        "groupName": keyword_group[0],
                        "keywords": keyword_group
                    }
                ]
            }
            try:
                response = requests.post(self.datalab_url, headers=self.datalab_headers, data=json.dumps(body))
                response.raise_for_status()
                data = response.json()
                results[keyword_group[0]] = data
            except requests.exceptions.RequestException as e:
                print(f"Error collecting Naver search trends for {keyword_group}: {e}")
                results[keyword_group[0]] = {"error": str(e)}
        return results

    def search_shopping(self, query, display=10):
        params = {
            'query': query,
            'display': display
        }
        try:
            response = requests.get(self.shopping_url, headers=self.shopping_headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching Naver Shopping for '{query}': {e}")
            return {"error": str(e)}