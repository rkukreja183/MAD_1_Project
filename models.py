from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db=SQLAlchemy()

class User(db.Model, UserMixin):
   user_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
   user_name=db.Column(db.String(),unique=True,nullable=False)
   password=db.Column(db.String(),nullable=False)
   creator_id=db.Column(db.Integer(),db.ForeignKey('artist.artist_id'),nullable=True)
   playlists=db.relationship('Playlistuser',backref="by_user")
   liked_songs=db.relationship('Songs',backref='liked_by', secondary='likes')
   rated_songs=db.relationship('Songs',backref='rated_by', secondary='rating')
   def get_id(self):
        return str(self.user_id)
   #it is a child of parent class db.model

class Artist(db.Model):
    artist_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    artist_user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),unique=True,nullable=False)
    artist_name=db.Column(db.String(),nullable=False)
    blacklisted=db.Column(db.Boolean(),default=False)
    songs=db.relationship('Songs',backref="song_by")
    albums=db.relationship('Album',backref="owner")

class Album(db.Model):
   album_id=db.Column(db.Integer(),primary_key=True)
   album_name=db.Column(db.String(),nullable=False)
   artist_id=db.Column(db.Integer(),db.ForeignKey('artist.artist_id'),nullable=False)
   flag=db.Column(db.Boolean, default=False)
   songs=db.relationship('Songs',backref='from_album')

class Songs(db.Model):
   song_id=db.Column(db.Integer(),primary_key=True)
   song_name=db.Column(db.String(),nullable=False)  
   singer=db.Column(db.Integer(),db.ForeignKey('artist.artist_id'),nullable=False)
   album=db.Column(db.Integer(),db.ForeignKey('album.album_id'),nullable=True)
   lyrics=db.Column(db.Text(),nullable=False)
   genre=db.Column(db.String(),nullable=False)
   total_rating=db.Column(db.Integer(),default=0)
   song_path=db.Column(db.String(),nullable=False)
   timestamp=db.Column(db.DateTime, default=datetime.utcnow)
   poster=db.Column(db.String(),nullable=False)
   flag=db.Column(db.Boolean, default=False)
   plays=db.Column(db.Integer(), default=0)

class Likes(db.Model):
   relationship_id=db.Column(db.Integer(),primary_key=True,autoincrement=True) 
   l_user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False)
   l_song_id=db.Column(db.Integer(),db.ForeignKey('songs.song_id'),nullable=False) 

class Rating(db.Model):
   rating_id=db.Column(db.Integer(),primary_key=True,autoincrement=True) 
   r_user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False)
   r_song_id=db.Column(db.Integer(),db.ForeignKey('songs.song_id'),nullable=False)
   rating=db.Column(db.Integer(),default=0)

class Playlist(db.Model):
   relationship_id=db.Column(db.Integer(),primary_key=True)
   playlist_id=db.Column(db.Integer(),db.ForeignKey('playlistuser.p_id'),nullable=False)
   p_song_id=db.Column(db.Integer(),db.ForeignKey('songs.song_id'),nullable=False)

class Playlistuser(db.Model):
   p_id=db.Column(db.Integer(),primary_key=True) 
   p_user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False) 
   playlist_name=db.Column(db.String(),nullable=False) 
   songs=db.relationship('Songs',backref="in_playlists",secondary="playlist")