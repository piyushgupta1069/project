# app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
db = SQLAlchemy(app)

celery = Celery(app.name, broker='redis://localhost:6379/0')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    thumbnail_url = db.Column(db.String(255))


@celery.task
def fetch_videos():
    # Fetch videos from YouTube API
    api_key = os.getenv("api_key")
    search_query = "python+web+development"
    published_after = (datetime.utcnow() - timedelta(minutes=14400)).isoformat()  # Example: Fetch videos published in the last 1 day
    url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&q={search_query}&part=snippet&type=video&order=date&publishedAfter={published_after}&maxResults=10'
    response = requests.get(url)
    data = response.json().get('items', [])

    # Store fetched videos in the database
    
    for item in data:
        
        video = Video(
            title=item['snippet']['title'],
            description=item['snippet']['description'],
            published_at=datetime.fromisoformat(item['snippet']['publishedAt']),
            thumbnail_url=item['snippet']['thumbnails']['default']['url']
        )
        print(video)
        db.session.add(video)
    db.session.commit()
    return 'Fetch videos task triggered successfully!'


@app.route('/videos', methods=['GET'])
def get_videos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('search_query')

    # Fetch videos based on search query
    if search_query:
        videos_query = Video.query.filter(Video.title.ilike(f'%{search_query}%')).order_by(Video.published_at.desc())
    else:
        videos_query = Video.query.order_by(Video.published_at.desc())

    videos = videos_query.paginate(page=page, per_page=per_page, error_out=False)


    video_data = []
    for video in videos.items:
        video_data.append({
            'title': video.title,
            'description': video.description,
            'published_at': video.published_at.isoformat(),
            'thumbnail_url': video.thumbnail_url
        })

    return jsonify({
        'videos': video_data,
        'total_pages': videos.pages,
        'total_videos': videos.total
    })

if __name__ == '__main__':
    configure()
    app.run(debug=True)
