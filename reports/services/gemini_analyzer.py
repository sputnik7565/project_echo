import os
import google.generativeai as genai
import json
import re
from django.conf import settings
from datetime import datetime, timedelta

class GeminiAnalyzer:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_data(self, raw_data, client_brand, competitor_brand, target_persona_keywords):
        youtube_data = raw_data.get('youtube', {})
        naver_data = raw_data.get('naver', {})
        
        today = datetime.now()
        report_period = f"{(today - timedelta(days=7)).strftime('%Y.%m.%d')} ~ {today.strftime('%Y.%m.%d')}"

        prompt = f"""
# [Master Prompt]

## 1. Persona & Goal
You are a Chief Marketing Consultant AI for a top-tier digital agency. Your client, '{client_brand}', is a brand. Your goal is to deliver a weekly report that is insightful, actionable, and proves your agency's value. The report must be written in Korean and formatted as a single, valid JSON object.

## 2. Core Principles
- **Insight-over-Information:** Do not just list data. Provide a strong, data-backed opinion on what the data *means*.
- **Evidence-Based:** For every insight or claim, you MUST cite the source data. Use the `data_source` field for this.
- **Omit if Empty:** If the data for a specific JSON field is insufficient or unavailable, omit the field entirely from the output. Do not populate with placeholders like 'N/A' or '데이터 없음'.
- **Persona Adherence:** All persona-related insights and recommendations MUST strictly adhere to the provided `target_persona_keywords`. Do NOT introduce personas not explicitly mentioned in `target_persona_keywords`.

## 3. Input Data
- **Client:** {client_brand}
- **Competitor:** {competitor_brand}
- **Target Persona Keywords:** {target_persona_keywords} (Use these keywords ONLY for persona-related analysis and recommendations. Do NOT invent new personas.)
- **Report Period:** {report_period}
- **YouTube Raw Data:** {json.dumps(youtube_data, indent=2, ensure_ascii=False)}
- **Naver Raw Data:** {json.dumps(naver_data, indent=2, ensure_ascii=False)}

## 4. Required JSON Output Structure

{{
  "report_meta": {{
    "title": "{client_brand} 주간 디지털 퍼포먼스 리포트",
    "period": "{report_period}"
  }},
  "weekly_headline": "이번 주 가장 중요한 발견이나 성과를 한 문장으로 요약한, 시선을 사로잡는 헤드라인을 작성합니다.",
  
  "executive_summary": {{
    "title": "Executive Summary: 이번 주 핵심 요약",
    "summary_points": [
      {{
        "point": "지난 주 대비 가장 큰 성과 또는 변화를 요약합니다.",
        "data_source": "예: Naver 검색량 트렌드, YouTube 총 조회수"
      }},
      {{
        "point": "경쟁사 대비 주목할 만한 움직임을 요약합니다.",
        "data_source": "예: 경쟁사 YouTube 채널 구독자 비교, Naver 쇼핑 리뷰 수 비교"
      }},
      {{
        "point": "가장 시급하게 실행해야 할 최우선 과제 1가지를 제안합니다.",
        "data_source": "예: YouTube 댓글 분석, 경쟁사 제품 전략 분석"
      }}
    ]
  }},

  "performance_dashboard": {{
    "title": "Performance Dashboard: 성과 대시보드",
    "metrics": [
      {{
        "metric_name": "YouTube 채널 구독자",
        "value": "{youtube_data.get('client', {}).get('channel_details', {}).get('statistics', {}).get('subscriberCount', '0')} 명",
        "insight": "구독자 수 변화 추이에 대한 분석 및 평가를 제공합니다.",
        "data_source": "YouTube Channel Statistics API"
      }},
      {{
        "metric_name": "Naver 브랜드 검색량 (vs 경쟁사)",
        "value": "데이터를 기반으로 클라이언트와 경쟁사의 검색량 추이를 비교 서술합니다.",
        "insight": "검색량 변동의 원인을 유추하고, 시장 관심도 측면에서 어떤 의미가 있는지 분석합니다.",
        "data_source": "Naver DataLab Search Trends"
      }},
      {{
        "metric_name": "Naver 쇼핑 리뷰 수 (상위 10개 제품 합산)",
        "value": "클라이언트와 경쟁사 각각의 상위 10개 제품 리뷰 수를 합산하여 비교 제시합니다.",
        "insight": "리뷰 총합을 통해 시장의 관심도와 구매 전환 규모를 유추하고, 경쟁사와의 상대적 위치를 파악합니다.",
        "data_source": "Naver Shopping Search API (Review Counts)"
      }}
    ]
  }},

  "deep_dive": {{
    "title": "Deep Dive: 상세 분석 및 전략 제언",
    "sections": [
      {{
        "section_title": "YouTube 채널 분석: 무엇이 통하고, 무엇이 통하지 않았나?",
        "finding": "이번 주 발행된 콘텐츠 또는 채널 전체의 주요 성공/실패 요인을 분석합니다. 특히 조회수 상위 동영상과 하위 동영상을 비교하여 어떤 콘텐츠가 효과적이었는지 분석합니다.",
        "evidence": "클라이언트 채널의 조회수 상위 3개 동영상: {youtube_data.get('client', {}).get('channel_details', {}).get('top_videos', [])[:3]}\n경쟁사 채널의 조회수 상위 3개 동영상: {youtube_data.get('competitor', {}).get('channel_details', {}).get('top_videos', [])[:3]}",
        "recommendation": "분석에 기반하여 다음 주에 시도해볼 만한 구체적인 콘텐츠 아이디어나 개선 방안을 제안합니다.",
        "data_source": "YouTube Video Statistics & Comments"
      }},
      {{
        "section_title": "Naver 쇼핑 제품 전략 분석",
        "finding": "Naver 쇼핑 검색 결과 상위 제품들의 상품명, 가격대, 리뷰 수를 통해 현재 브랜드의 주력 제품군과 가격 전략을 분석합니다.",
        "evidence": "리뷰 수가 가장 많은 상위 3개 제품의 이름과 가격, 리뷰 수를 명시합니다. 경쟁사와 비교하여 차이점을 설명합니다.",
        "recommendation": "현재 제품 전략의 강점과 약점을 진단하고, 시장 반응(리뷰 수)을 기반으로 어떤 제품을 더 강조해야 할지 제안합니다.",
        "data_source": "Naver Shopping Search API (Products, Prices, Review Counts)"
      }},
      {{
        "section_title": "고객의 목소리(VoC) 분석: 고객은 무엇을 원하는가?",
        "finding": "YouTube 댓글에서는 고객의 구체적인 의견을, Naver 쇼핑에서는 리뷰 수를 통해 어떤 제품에 관심이 집중되는지를 파악합니다.",
        "evidence": "YouTube 댓글의 주요 키워드를 인용하고, Naver 쇼핑에서 리뷰 수가 가장 많은 상위 3개 제품을 언급합니다.",
        "recommendation": "댓글의 질적 데이터와 리뷰 수의 양적 데이터를 종합하여, 고객이 중요하게 생각하는 가치(디자인, 가격, 기능 등)를 파악하고 마케팅에 활용하는 방안을 제안합니다.",
        "data_source": "YouTube Comments, Naver Shopping Search API (Review Counts)"
      }}
    ]
  }},

  "strategic_recommendations": {{
    "title": "Action Plan: 다음 주 실행 계획",
    "recommendations": [
      {{
        "priority": "1순위",
        "action": "분석 결과에 기반한 가장 시급하고 중요한 실행 과제를 명확하게 제시합니다.",
        "rationale": "이것이 왜 1순위인지 데이터에 기반하여 논리적으로 설명합니다.",
        "expected_impact": "이 활동을 통해 기대할 수 있는 정량적/정성적 효과를 예측합니다. (예: '주력 제품군 쇼핑 검색결과 상위 노출', '특정 영상 조회수 20% 증가')"
      }},
      {{
        "priority": "2순위",
        "action": "차순위 실행 과제를 제시합니다.",
        "rationale": "이것이 왜 2순위인지 설명합니다.",
        "expected_impact": "기대 효과를 예측합니다."
      }}
    ]
  }}
}}
"""
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up the response text by removing markdown backticks for JSON
            match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if match:
                json_string = match.group(1)
            else:
                json_string = response_text
            
            report_data = json.loads(json_string)
            return report_data

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print(f"Raw response text: {response_text}")
            return {"error": f"Failed to decode Gemini response into JSON: {e}", "raw_response": response_text}
        except Exception as e:
            print(f"An unexpected error occurred in GeminiAnalyzer: {e}")
            return {"error": str(e)}