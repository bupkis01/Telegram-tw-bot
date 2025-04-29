# helper.py
# Utility functions for handling media (download photos/videos).

import os
import requests
from urllib.parse import urlparse, parse_qs

def download_media(url: str) -> str:
    """
    Download a media file from a URL and save it locally.
    Returns the local file path. Caller is responsible for deleting the file.
    """
    # Determine file extension from the URL (jpg or mp4)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if 'format' in qs:
        ext = '.' + qs['format'][0]  # e.g., '.jpg'
    else:
        # Fallback to extension from path
        path_ext = os.path.splitext(parsed.path)[1]
        ext = path_ext if path_ext else ''
    # Use a temporary filename
    local_filename = os.path.basename(parsed.path)
    if not local_filename or '.' not in local_filename:
        local_filename = f"temp_media{ext}"
    else:
        # Strip query parameters if present
        local_filename = local_filename.split('?')[0]
    # Ensure directory for downloads
    if not os.path.isdir('downloads'):
        os.mkdir('downloads')
    filepath = os.path.join('downloads', local_filename)
    # Download the file
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        # Cleanup on failure
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e
    return filepath

def extract_media_urls(tweet) -> (list, list):
    """
    Given an snscrape Tweet object, extract lists of photo URLs and video URLs.
    Returns (photos, videos). Video URLs are chosen at highest available resolution.
    """
    photos = []
    videos = []
    media = getattr(tweet, 'media', None)
    if media:
        for m in media:
            if m.type == 'photo':
                photos.append(m.fullUrl)
            elif m.type == 'video':
                # Select the highest-bitrate MP4 variant
                variants = [v for v in m.variants if v.contentType == 'video/mp4']
                if variants:
                    best = max(variants, key=lambda v: v.bitrate or 0)
                    videos.append(best.url)
    return photos, videos 
