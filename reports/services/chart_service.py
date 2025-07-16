import os
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
from django.conf import settings
from django.utils import timezone
import pandas as pd

class ChartService:
    def __init__(self, brand_name):
        self.brand_name = brand_name
        self.charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(self.charts_dir, exist_ok=True)
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'Noto Sans KR' # Adjust as needed for your OS
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 12 # Default font size
        plt.rcParams['axes.titlesize'] = 14 # Title font size
        plt.rcParams['axes.labelsize'] = 12 # Axis label font size
        plt.rcParams['xtick.labelsize'] = 10 # X-tick label size
        plt.rcParams['ytick.labelsize'] = 10 # Y-tick label size
        plt.rcParams['legend.fontsize'] = 10 # Legend font size

    def _save_matplotlib_chart(self, fig, chart_type, brand_name):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = f"{chart_type}_{brand_name}_{timestamp}.png"
        filepath = os.path.join(self.charts_dir, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)
        return os.path.join(settings.MEDIA_URL, 'charts', filename)

    def generate_naver_search_trend_chart(self, client_data, competitor_data, client_name, competitor_name):
        try:
            client_df = pd.DataFrame(client_data['results'][0]['data'])
            competitor_df = pd.DataFrame(competitor_data['results'][0]['data'])
            
            # Ensure 'period' is in datetime format for sorting
            client_df['period'] = pd.to_datetime(client_df['period'])
            competitor_df['period'] = pd.to_datetime(competitor_df['period'])

            # Sort by period to ensure correct chart display
            client_df = client_df.sort_values(by='period')
            competitor_df = competitor_df.sort_values(by='period')

            labels = client_df['period'].dt.strftime('%Y-%m-%d').tolist()
            client_ratios = client_df['ratio'].tolist()
            competitor_ratios = competitor_df['ratio'].tolist()

            # Chart.js data
            chartjs_data = {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': client_name,
                            'data': client_ratios,
                            'borderColor': '#4A90E2',
                            'fill': False
                        },
                        {
                            'label': competitor_name,
                            'data': competitor_ratios,
                            'borderColor': '#E57373',
                            'fill': False
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': '네이버 검색량 트렌드 비교',
                            'font': {'size': 16}
                        }
                    },
                    'scales': {
                        'x': {
                            'title': {
                                'display': True,
                                'text': '기간'
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': '상대적 검색량'
                            }
                        }
                    }
                }
            }

            # Matplotlib image
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(client_df['period'], client_df['ratio'], label=client_name, color='#4A90E2', linewidth=2)
            ax.plot(competitor_df['period'], competitor_df['ratio'], label=competitor_name, color='#E57373', linewidth=2)
            ax.set_title('네이버 검색량 트렌드 비교', fontsize=16, pad=20)
            ax.set_xlabel('기간')
            ax.set_ylabel('상대적 검색량')
            ax.legend(frameon=False)
            ax.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            matplotlib_image_path = self._save_matplotlib_chart(fig, 'naver_search_trend', self.brand_name)

            return {
                'chartjs_data': chartjs_data,
                'image_path': matplotlib_image_path
            }
        except (KeyError, IndexError) as e:
            print(f"Chart Error (Naver Search): Invalid data structure - {e}")
            return None

    def generate_youtube_subscriber_chart(self, client_stats, competitor_stats, client_name, competitor_name):
        try:
            client_subscribers = int(client_stats.get('subscriberCount', 0))
            competitor_subscribers = int(competitor_stats.get('subscriberCount', 0))

            # Chart.js data
            chartjs_data = {
                'type': 'bar',
                'data': {
                    'labels': [client_name, competitor_name],
                    'datasets': [
                        {
                            'label': '구독자 수',
                            'data': [client_subscribers, competitor_subscribers],
                            'backgroundColor': ['#4A90E2', '#E57373']
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'YouTube 구독자 수 비교',
                            'font': {'size': 16}
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': '구독자 수'
                            }
                        }
                    }
                }
            }

            # Matplotlib image
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar([client_name, competitor_name], [client_subscribers, competitor_subscribers], color=['#4A90E2', '#E57373'])
            ax.set_title('YouTube 구독자 수 비교', fontsize=16, pad=20)
            ax.set_ylabel('구독자 수')
            plt.tight_layout()
            matplotlib_image_path = self._save_matplotlib_chart(fig, 'youtube_subscriber', self.brand_name)

            return {
                'chartjs_data': chartjs_data,
                'image_path': matplotlib_image_path
            }
        except (KeyError, IndexError) as e:
            print(f"Chart Error (YouTube Subscriber): Invalid data structure - {e}")
            return None

    def generate_youtube_view_chart(self, client_stats, competitor_stats, client_name, competitor_name):
        try:
            client_views = int(client_stats.get('viewCount', 0))
            competitor_views = int(competitor_stats.get('viewCount', 0))

            # Chart.js data
            chartjs_data = {
                'type': 'bar',
                'data': {
                    'labels': [client_name, competitor_name],
                    'datasets': [
                        {
                            'label': '총 조회수',
                            'data': [client_views, competitor_views],
                            'backgroundColor': ['#4A90E2', '#E57373']
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'YouTube 총 조회수 비교',
                            'font': {'size': 16}
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': '조회수'
                            }
                        }
                    }
                }
            }

            # Matplotlib image
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar([client_name, competitor_name], [client_views, competitor_views], color=['#4A90E2', '#E57373'])
            ax.set_title('YouTube 총 조회수 비교', fontsize=16, pad=20)
            ax.set_ylabel('조회수')
            plt.tight_layout()
            matplotlib_image_path = self._save_matplotlib_chart(fig, 'youtube_view', self.brand_name)

            return {
                'chartjs_data': chartjs_data,
                'image_path': matplotlib_image_path
            }
        except (KeyError, IndexError) as e:
            print(f"Chart Error (YouTube View): Invalid data structure - {e}")
            return None

    def generate_shopping_sov_chart(self, client_review_count, competitor_review_count, client_name, competitor_name):
        try:
            labels = [client_name, competitor_name]
            sizes = [client_review_count, competitor_review_count]
            colors = ['#4A90E2', '#E57373']

            # Only generate chart data if there's actual data to display
            if sum(sizes) == 0:
                return None

            # Chart.js data
            chartjs_data = {
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': sizes,
                        'backgroundColor': colors,
                        'hoverOffset': 4
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': '네이버 쇼핑 관심도 점유율 (리뷰 수 기반)',
                            'font': {'size': 16}
                        }
                    }
                }
            }

            # Matplotlib image
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 12})
            ax.set_title('네이버 쇼핑 관심도 점유율 (리뷰 수 기반)', fontsize=16, pad=20)
            ax.axis('equal')
            plt.tight_layout()
            matplotlib_image_path = self._save_matplotlib_chart(fig, 'shopping_sov', self.brand_name)

            return {
                'chartjs_data': chartjs_data,
                'image_path': matplotlib_image_path
            }
        except Exception as e:
            print(f"Chart Error (Shopping SOV): {e}")
            return None
