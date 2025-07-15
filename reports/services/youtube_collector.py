import os
from googleapiclient.discovery import build
from django.conf import settings

class YouTubeCollector:
    def __init__(self):
        api_key = settings.YOUTUBE_API_KEY
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY is not set in settings.")
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_channel_details_by_name(self, channel_name):
        try:
            # First, search for the channel to get its ID
            search_request = self.youtube.search().list(
                q=channel_name,
                part='id',
                type='channel',
                maxResults=1
            )
            search_response = search_request.execute()
            items = search_response.get('items', [])
            if not items:
                return {"error": f"Channel '{channel_name}' not found."}
            
            channel_id = items[0]['id']['channelId']

            # Then, get channel details using the ID
            channel_request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            channel_data = channel_response.get('items', [{}])[0]

            if channel_data:
                uploads_playlist_id = channel_data.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
                if uploads_playlist_id:
                    # Get top 10 videos by view count from the uploads playlist
                    top_videos = self.get_playlist_videos(uploads_playlist_id, max_results=10)
                    channel_data['top_videos'] = top_videos
            
            return channel_data

        except Exception as e:
            print(f"Error getting YouTube channel details for '{channel_name}': {e}")
            return {"error": str(e)}

    def get_playlist_videos(self, playlist_id, max_results=10):
        videos = []
        next_page_token = None
        while True:
            playlist_items_request = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=min(max_results, 50), # Max 50 per request
                pageToken=next_page_token
            )
            playlist_items_response = playlist_items_request.execute()

            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items_response.get('items', []) if item['snippet']['resourceId']['kind'] == 'youtube#video']
            
            if video_ids:
                video_details = self.get_video_details(video_ids)
                for detail in video_details:
                    video_info = {
                        'title': detail['snippet']['title'],
                        'viewCount': int(detail['statistics'].get('viewCount', 0)),
                        'likeCount': int(detail['statistics'].get('likeCount', 0)),
                        'commentCount': int(detail['statistics'].get('commentCount', 0)),
                        'videoId': detail['id']
                    }
                    # Get comments for each video
                    video_info['comments'] = self.get_comments(detail['id'], max_results=50) # Limit comments to 50 per video
                    videos.append(video_info)
            
            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_results:
                break
        
        # Sort by viewCount to get top videos
        videos.sort(key=lambda x: x['viewCount'], reverse=True)
        return videos[:max_results]

    def search_videos(self, query, max_results=10):
        try:
            request = self.youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=max_results
            )
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            print(f"Error searching YouTube videos: {e}")
            return []

    def get_video_details(self, video_ids):
        if not video_ids:
            return []
        try:
            request = self.youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            )
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            print(f"Error getting YouTube video details: {e}")
            return []

    def get_comments(self, video_id, max_results=100):
        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=max_results
            )
            response = request.execute()
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt']
                })
            return comments
        except Exception as e:
            # Silently fail for comments as they are not always enabled
            # print(f"Error getting YouTube comments for video {video_id}: {e}")
            return []