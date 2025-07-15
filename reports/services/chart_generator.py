import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import json
from django.conf import settings

def generate_naver_chart(naver_data, filename):
    labels = []
    datasets = []

    for brand_name, data_entry in naver_data.items():
        if data_entry and data_entry.get('results') and data_entry['results'][0].get('data'):
            data_points = data_entry['results'][0]['data']
            group_labels = [item['period'] for item in data_points]
            group_values = [item['ratio'] for item in data_points]

            for label in group_labels:
                if label not in labels:
                    labels.append(label)

            datasets.append({
                'label': brand_name,
                'data': group_values,
                'borderColor': getRandomColor(),
                'fill': False
            })
    
    labels.sort()

    if not datasets:
        return None

    plt.figure(figsize=(10, 6))
    for dataset in datasets:
        plt.plot(dataset['data'], label=dataset['label'], color=dataset['borderColor'])
    
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.xlabel('Date')
    plt.ylabel('Search Ratio')
    plt.title('Naver Search Trend')
    plt.legend()
    plt.tight_layout()

    image_path = os.path.join(settings.MEDIA_ROOT, 'charts', filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    plt.savefig(image_path)
    plt.close()
    return os.path.join('charts', filename)

def generate_youtube_sov_chart(youtube_data, client_brand_name, competitor_brand_name, filename):
    client_youtube_data = youtube_data.get('client', {})
    competitor_youtube_data = youtube_data.get('competitor', {})

    client_total_views = 0
    competitor_total_views = 0

    if client_youtube_data.get('videos'):
        for video in client_youtube_data['videos']:
            client_total_views += int(video['statistics'].get('viewCount', 0))

    if competitor_youtube_data.get('videos'):
        for video in competitor_youtube_data['videos']:
            competitor_total_views += int(video['statistics'].get('viewCount', 0))

    total_views = client_total_views + competitor_total_views

    if total_views == 0:
        return None

    sov_labels = []
    sov_data = []
    colors = []

    if client_total_views > 0:
        sov_labels.append(client_brand_name)
        sov_data.append((client_total_views / total_views) * 100)
        colors.append(getRandomColor())
    if competitor_total_views > 0:
        sov_labels.append(competitor_brand_name)
        sov_data.append((competitor_total_views / total_views) * 100)
        colors.append(getRandomColor())

    if not sov_data:
        return None

    plt.figure(figsize=(8, 8))
    plt.pie(sov_data, labels=sov_labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('YouTube SOV (Share of Voice)')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()

    image_path = os.path.join(settings.MEDIA_ROOT, 'charts', filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    plt.savefig(image_path)
    plt.close()
    return os.path.join('charts', filename)

def getRandomColor():
    import random
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())
