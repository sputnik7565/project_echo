import matplotlib
matplotlib.use('Agg')
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from django.conf import settings

def generate_wordcloud(text, filename):
    # 한글 폰트 경로 설정 (macOS 기준, 다른 OS는 경로 변경 필요)
    # 시스템에 설치된 한글 폰트 경로를 확인하여 사용하세요.
    # 예: /System/Library/Fonts/AppleSDGothicNeo.ttc (macOS)
    # 예: C:/Windows/Fonts/malgun.ttf (Windows)
    # 예: /usr/share/fonts/truetype/nanum/NanumGothic.ttf (Ubuntu)
    font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc' # macOS 예시

    if not os.path.exists(font_path):
        print(f"Warning: Font file not found at {font_path}. Wordcloud might not display Korean correctly.")
        # Fallback to a default font if the specified font is not found
        font_path = None # Let WordCloud try to find a default font

    wordcloud = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color='white',
        max_words=100,
        collocations=False # 중복 단어 제거
    ).generate(text)

    # 이미지 저장 경로 설정
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        os.makedirs(media_root)
    
    image_path = os.path.join(media_root, 'wordclouds', filename)
    if not os.path.exists(os.path.dirname(image_path)):
        os.makedirs(os.path.dirname(image_path))

    wordcloud.to_file(image_path)
    return os.path.join('wordclouds', filename)
