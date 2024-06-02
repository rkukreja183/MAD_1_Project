from flask import Flask,flash, render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,login_user,logout_user,login_required,current_user
from flask_restful import Api, Resource, reqparse
from datetime import datetime, timedelta
import time
import os
import matplotlib.pyplot as plt 
from models import *

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.sqlite3"
app.config['SECRET_KEY']='mysecretkey'
login_manager=LoginManager(app)

api=Api(app)
db.init_app(app)
app.app_context().push()

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(user_id)

@app.route('/',methods=['GET'])
def welcome():
    if request.method=='GET':
        return render_template('login_register.html')

@app.route('/login',methods=['GET','POST']) 
def log_user():
    if request.method=="POST":
        user_name=request.form.get('user_name')
        password=request.form.get('password')
        user=User.query.filter_by(user_name=user_name).first()
        status1=True
        status2=True
        if user==None: 
          status1=False 
          return render_template('user_login_page.html',status1=status1)
        else:
           if user.password==password:
            login_user(user)
            return redirect(url_for('user_homepage',user_id=user.user_id))
           else:
             status2=False
             return render_template('user_login_page.html',status2=status2)
    return render_template('user_login_page.html')

@app.route('/register',methods=['GET','POST'])
def register_user():
    status=True
    if request.method=='POST':
        user_name=request.form.get('user_name')
        password=request.form.get('password')
        user_exists=User.query.filter_by(user_name=user_name).all()
        if len(user_exists)==0:
            user=User(user_name=user_name,password=password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        else:
            status=False
            return render_template('user_register_page.html',status=status)
    return render_template('user_register_page.html',status=status)

@app.route('/logout',methods=['GET'])
def logout():
   logout_user()
   return redirect(url_for('log_user'))

@app.route('/company_policies',methods=['GET','POST'])
@login_required
def company_policies():
   return render_template('company_policies.html') 

@app.route('/app_admin_login', methods=['GET','POST'])
def app_admin_login():
   if request.method=='POST':
      admin_pass=request.form.get('admin_password')
      admin_name=request.form.get('admin_name')
      if admin_name=="admin1" and admin_pass=="admin756":
         return redirect(url_for('admin_dashboard',p=""))
      else:
         status=False
         return render_template('admin_login.html',status=status)
   return render_template('admin_login.html')

def create_pie():
    plt.clf()
    plt.switch_backend('Agg')
    genres=['Pop','Jazz','Classical','R&B','Rock','Electronic/Dance','HipHop','Country','Soul','Indie']
    pop=0
    jazz=0
    classical=0
    rb=0
    rock=0
    ed=0
    hiphop=0
    country=0
    soul=0
    indie=0
    songs=Songs.query.all()
    for song in songs:
       if song.genre=='Pop':
          pop+=1
       elif song.genre=='Jazz':
          jazz+=1
       elif song.genre=='Classical_music':
          classical+=1
       elif song.genre=='R&B':
          rb+=1
       elif song.genre=='Rock':
          rock+=1   
       elif song.genre=='Electronic':
          ed+=1
       elif song.genre=='HipHop':
          hiphop+=1
       elif song.genre=='Country':
          country+=1
       elif song.genre=='Soul':
          soul+=1
       else:
          indie+=1     
    num_songs=[]
    num_songs.extend([pop,jazz,classical,rb,rock,ed,hiphop,country,soul,indie])
    plt.pie(num_songs, labels=genres,autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Genre-wise distribution of songs')
    pie_filename = "pie.png"
    pie_path = os.path.join(app.static_folder, 'admin', pie_filename)
    if os.path.exists(pie_path):
       os.remove(pie_path)
    plt.savefig((pie_path))
    return pie_path

def create_graph():
   plt.clf()
   plt.switch_backend('Agg')
   one_week=datetime.now()-timedelta(weeks=1)
   today=datetime.now()
   songs=Songs.query.filter(Songs.timestamp>=one_week).all()
   dates=[]
   date_counts={}
   current_date = one_week
   while current_date <= today:
    dates.append(current_date.date())
    current_date += timedelta(days=1)
   for date in dates:
      date_counts[date]=0
      for song in songs:
         song_date=song.timestamp.date()
         if song_date==date:
            date_counts[date]+=1     
   print(date_counts)            
   x_values=formatted_dates = [date.strftime('%Y-%m-%d') for date in date_counts.keys()]
   y_values=[date_counts[date] for date in dates]
   plt.plot(x_values, y_values, marker='o', linestyle='-')
   plt.title('Uploads over last week')
   plt.xlabel('Date')
   plt.ylabel('Songs Count')
   plt.xticks(rotation=45, ha="right")
   plt.tight_layout()
   graph_filename = "graph.png"
   graph_path = os.path.join(app.static_folder, 'admin', graph_filename)
   if os.path.exists(graph_path):
      os.remove(graph_path)
   plt.savefig((graph_path))
   return graph_path


@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
   songs=Songs.query.all()
   albums=Album.query.all()
   users=User.query.all()
   artists=Artist.query.all()
   p=request.args.get('p')
   create_pie()
   create_graph()
   pie_url='/static/admin/pie.png'
   graph_url='/static/admin/graph.png'
   if p=="" or p=='top_songs':
     top_songs=Songs.query.order_by(Songs.total_rating.desc()).limit(7).all() 
     return render_template('admin_dashboard.html', songs=songs,albums=albums,users=users,artists=artists, top_songs=top_songs,p=p,pie_url=pie_url, graph_url=graph_url)      
   if p=="mostplayed":
      mostplayed_songs=Songs.query.order_by(Songs.plays.desc()).limit(7).all()          
      return render_template('admin_dashboard.html', songs=songs,albums=albums,users=users,artists=artists,mostplayed_songs=mostplayed_songs, p=p, pie_url=pie_url,graph_url=graph_url)

@app.route('/show_admin', methods=['GET'])
def show_admin():
   parameter=request.args.get('parameter')
   if parameter=='songs':
      results=Songs.query.all()
   elif parameter=="albums":
      results=Album.query.all()
   else:
      results=Artist.query.all()   
   return render_template('show_admin.html',results=results, parameter=parameter)

@app.route('/flag_song/<int:song_id>', methods=['GET','POST'])
def flag_song(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   song.flag=True
   db.session.commit()
   results=Songs.query.all()
   return redirect(url_for('show_admin',parameter="songs"))

@app.route('/unflag_song/<int:song_id>', methods=['GET','POST'])
def unflag_song(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   song.flag=False
   db.session.commit()
   results=Songs.query.all()
   return redirect(url_for('show_admin',parameter="songs"))

@app.route('/admin_play_song/<int:song_id>', methods=['GET','POST'])
def admin_play_song(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   song_file='/static/' + song.song_path
   return render_template('admin_song_page.html',song=song,song_file=song_file)

@app.route('/admin_view_artist/<int:artist_id>',methods=['GET','POST'])
def admin_view_artist(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   return render_template('admin_view_artist.html',artist=artist)

@app.route('/admin_view_album/<int:album_id>',methods=['GET','POST'])
def admin_view_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   return render_template('admin_view_album.html',album=album)

@app.route('/flag_album/<int:album_id>', methods=['GET','POST'])
def flag_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   album.flag=True
   db.session.commit()
   return redirect(url_for('show_admin',parameter="albums"))

@app.route('/unflag_album/<int:album_id>', methods=['GET','POST'])
def unflag_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   album.flag=False
   db.session.commit()
   return redirect(url_for('show_admin',parameter="albums"))

@app.route('/blacklist/<int:artist_id>',methods=['GET','POST'])
def blacklist_artist(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   artist.blacklisted=True
   db.session.commit()
   return redirect(url_for('show_admin',parameter="creators"))

@app.route('/deblacklist/<int:artist_id>',methods=['GET','POST'])
def deblacklist_artist(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   artist.blacklisted=False
   db.session.commit()
   return redirect(url_for('show_admin',parameter="creators"))

@app.route('/search_by_admin', methods=['GET','POST'])
def search_by_admin():
   if request.method=="POST":
      admin_search=request.form.get('admin_search')
      song_results=Songs.query.filter(Songs.song_name.like(f'%{admin_search}%')).all()
      artist_results=Artist.query.filter(Artist.artist_name.like(f'%{admin_search}%')).all()
      album_results=Album.query.filter(Album.album_name.like(f'%{admin_search}%')).all()
      if admin_search=="":
         song_results=[]
         artist_results=[]
         album_results=[]
      return render_template('admin_search_page.html',songs=song_results,artists=artist_results,albums=album_results)
   
@app.route('/logout_admin', methods=['GET'])   
def logout_admin():
   return redirect('/')

@app.route('/homepage/<int:user_id>',methods=['GET','POST'])
@login_required
def user_homepage(user_id):
    user=User.query.filter_by(user_id=int(user_id)).first()
    songs=Songs.query.all()
    top_songs=[]
    top_songs=Songs.query.order_by(Songs.total_rating.desc()).limit(7).all()
    return render_template('user_home.html',user=user,top_songs=top_songs)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
   if request.method=='POST':
      password=request.form.get('password')
      if password is not None:
         status=True
         current_user.password=password   
         db.session.commit() 
      return render_template('profile.html', status=status)      
   return render_template('profile.html')

@app.route('/create_playlist/<int:user_id>',methods=['GET','POST'])
@login_required
def create_playlist(user_id):
   status=True
   songs=Songs.query.all()
   user=User.query.filter_by(user_id=user_id).first()
   if request.method=='POST':
      playlist_name=request.form.get('playlist_name')     
      playlist_songs=request.form.getlist('playlist_songs')
      playlist_of_user=Playlistuser(p_user_id=user.user_id, playlist_name=playlist_name)
      db.session.add(playlist_of_user)
      db.session.commit()
      for song_id in playlist_songs:
         song_in_playlist=Playlist(playlist_id=playlist_of_user.p_id,p_song_id=int(song_id))
         db.session.add(song_in_playlist)
         db.session.commit()
      return redirect(url_for('view_playlist',p_id=playlist_of_user.p_id))
   return render_template('create_playlist.html',songs=songs,user=user)

@app.route('/view_playlist/<int:p_id>',methods=['GET','POST'])
@login_required
def view_playlist(p_id):
    playlist=Playlistuser.query.filter_by(p_id=p_id).first()
    return render_template('playlist_page.html',playlist=playlist)

@app.route('/delete_playlist/<int:p_id>',methods=['GET'])
@login_required
def delete_playlist(p_id):
   playlist=Playlistuser.query.filter_by(p_id=p_id).first()
   db.session.delete(playlist)
   db.session.commit()   
   return redirect(url_for('user_homepage',user_id=playlist.p_user_id))    

@app.route('/delete_from_playlist/<int:p_id>/<int:song_id>',methods=['GET','POST'])
@login_required
def delete_song_from_playlist(p_id,song_id):
   playlist=Playlistuser.query.filter_by(p_id=p_id).first()
   for song in playlist.songs:
      if song.song_id==song_id:
         playlist.songs.remove(song)
         db.session.commit()
   return redirect(url_for('view_playlist',p_id=p_id))   

@app.route('/add_to_playlist/<int:p_id>',methods=['GET','POST'])  
@login_required
def add_to_playlist(p_id):
   playlist=Playlistuser.query.filter_by(p_id=p_id).first()
   song_id_in_playlist=[]
   for song in playlist.songs:
      song_id_in_playlist.append(song.song_id)
   songs=Songs.query.all()  
   status=True 
   if len(playlist.songs)==len(songs):
      status=False          
   if request.method=='POST':
      songs_to_add=request.form.getlist('songs_to_add')
      for song_id in songs_to_add:
         if int(song_id) in song_id_in_playlist:
            continue
         else:
            add_relation=Playlist(playlist_id=playlist.p_id,p_song_id=int(song_id))
            db.session.add(add_relation)
      db.session.commit()  
      return redirect(url_for('view_playlist',p_id=playlist.p_id)) 
   return render_template('add_to_playlist.html',songs=songs,playlist=playlist,status=status)

@app.route('/like_song/<int:song_id>', methods=['GET'])
@login_required
def like_song(song_id):
  song=Songs.query.filter_by(song_id=song_id).first()
  user=current_user
  if song not in user.liked_songs:
      user.liked_songs.append(song)
      db.session.commit()
  return redirect(url_for('user_homepage',user_id=user.user_id))  

@app.route('/unlike_song/<int:song_id>', methods=['GET'])
@login_required
def unlike_song(song_id):
  song=Songs.query.filter_by(song_id=song_id).first()
  user=current_user
  for song in user.liked_songs:
     if song==song:
         user.liked_songs.remove(song)
         db.session.commit()
  return redirect(url_for('user_homepage',user_id=user.user_id))

@app.route('/rate_song/<int:song_id>',methods=['POST'])
@login_required
def rate_song(song_id):
   user=current_user
   song=Songs.query.filter_by(song_id=song_id).first()
   rating=request.form.get('rating')
   rating_exists=Rating.query.filter_by(r_user_id=user.user_id,r_song_id=song_id).first()
   if rating_exists:
      if rating_exists.rating!=rating:
         rating_exists.rating=rating
         db.session.commit()
   else:
      new_rating=Rating(r_user_id=user.user_id,r_song_id=song_id,rating=rating)
      db.session.add(new_rating)
      db.session.commit()
   rating_list=Rating.query.filter_by(r_song_id=song_id).all()
   raters=len(rating_list)
   rating_amt=0
   for rating in rating_list:
      rating_amt+=rating.rating
   total_rating=round(rating_amt/raters)
   song.total_rating=total_rating
   db.session.commit() 
   return redirect(url_for('song_page',song_id=song_id))   

@app.route('/search',methods=['GET','POST'])
@login_required
def search_for():
   if request.method=='POST':
      search_value=request.form.get('search_value')
      song_results=Songs.query.filter(Songs.song_name.like(f'%{search_value}%')).all()
      artist_results=Artist.query.filter(Artist.artist_name.like(f'%{search_value}%')).all()
      album_results=Album.query.filter(Album.album_name.like(f'%{search_value}%')).all()
      if search_value=="":
         song_results=[]
         artist_results=[]
         album_results=[]
      return render_template('search_page.html',songs=song_results,artists=artist_results,albums=album_results)
   if request.method=='GET':
      all_artists=Artist.query.limit(10).all()
      all_songs=Songs.query.limit(10).all()
      all_albums=Album.query.limit(10).all()
      all_genres=['Pop','Jazz','Classical','R&B','Rock','Electronic/Dance','HipHop','Country','Soul','Indie']
      song_results=None
      artist_results=None
      album_results=None
      return render_template('search_page.html',songs=song_results,artists=artist_results,albums=album_results,all_songs=all_songs,all_albums=all_albums,all_artists=all_artists,all_genres=all_genres)

@app.route('/genre/<genre>', methods=['GET','POST'])
def genre_page(genre):
   songs=Songs.query.all()
   genre_songs=[]
   for song in songs:
      if song.genre==genre:
         genre_songs.append(song)
   return render_template('genre_page.html', genre_songs=genre_songs, genre=genre)      

@app.route('/show_all', methods=['GET'])
@login_required
def show_all():
   parameter=request.args.get('parameter')
   if parameter=='songs':
      all_results=Songs.query.all()
   elif parameter=='artists':
      all_results=Artist.query.all()
   else:
      all_results=Album.query.all()  
   return render_template('all_results.html',all_results=all_results,parameter=parameter)    


@app.route('/song/<int:song_id>',methods=['GET'])
@login_required
def song_page(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   song_file='/static/' + song.song_path 
   poster_file='/static/' + song.poster
   if current_user.creator_id!=song.singer:
      song.plays+=1
   db.session.commit()
   return render_template('song_page.html',song=song,song_file=song_file, poster_file=poster_file)

@app.route('/artist/<artist_id>',methods=['GET'])
@login_required
def artist_page(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   artist_songs=artist.songs.copy()
   top_songs=Songs.query.filter_by(singer=artist_id).order_by(Songs.total_rating.desc()).limit(5).all()
   return render_template('artist_page.html',artist=artist, top_songs=top_songs)

@app.route('/album/<album_id>',methods=['GET'])
@login_required
def album_page(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   return render_template('album_page.html',album=album)

@app.route('/creator_registration/<int:user_id>',methods=['GET'])
@login_required
def creator_registration(user_id):
   user=User.query.filter_by(user_id=user_id).first()
   artist=Artist(artist_name=user.user_name,artist_user_id=user.user_id)
   db.session.add(artist)
   db.session.commit()
   artist=Artist.query.filter_by(artist_name=user.user_name).first()
   user.creator_id=artist.artist_id
   db.session.commit()
   return redirect(url_for('creator_page',artist_id=artist.artist_id))

@app.route('/creator_page/<int:artist_id>',methods=['GET','POST'])
@login_required
def creator_page(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   artist_singles=[]
   for song in artist.songs:
      if song.album is None:
         artist_singles.append(song)
   return render_template('creator_page.html',artist=artist,artist_singles=artist_singles)

@app.route('/upload/<int:artist_id>',methods=['GET','POST'])
@login_required
def upload(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   artist_albums=[]
   for album in artist.albums:
      artist_albums.append(album.album_name)
   if request.method=='POST':
      status1=True
      song_name=request.form.get('song_name')
      song_option=request.form.get('song_option')
      lyrics=request.form.get('lyrics')
      genre=request.form.get('genre')
      audio=request.files['audio_file']
      poster=request.files['poster_file']
      poster_name=poster.filename
      audio_filename=audio.filename
      if song_option==None:
         status1=False
         return render_template('upload_song.html',artist=artist,status1=status1)##try to retain the previous values
      else:
         if song_option=='album':
            album_name=request.form.get('album_name') 
            status2=True
            if album_name=="":
              status2=False 
              return render_template('upload_song.html',artist=artist,status2=status2)
            else:
              if album_name not in artist_albums:
                  album=Album(album_name=album_name,artist_id=artist.artist_id)
                  db.session.add(album)
                  db.session.commit()
              album=Album.query.filter_by(artist_id=artist.artist_id,album_name=album_name).first()
              song=Songs(song_name=song_name,singer=artist.artist_id,album=album.album_id,lyrics=lyrics,genre=genre,song_path=audio_filename,poster=poster_name)
              db.session.add(song)
              db.session.commit()
              audio.save(os.path.join('static', audio_filename))
              poster.save(os.path.join('static',poster_name))
              return redirect(url_for('creator_page',artist_id=artist.artist_id))
         else:
            song=Songs(song_name=song_name,lyrics=lyrics,singer=artist.artist_id,genre=genre,song_path=audio_filename,poster=poster_name)  
            db.session.add(song)
            db.session.commit() 
            audio.save(os.path.join('static', audio_filename))
            poster.save(os.path.join('static',poster_name))
            return redirect(url_for('creator_page',artist_id=artist.artist_id))
                 
   return render_template('upload_song.html',artist=artist)

@app.route('/update_song/<int:song_id>',methods=['GET','POST'])
@login_required
def update_song(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   if request.method=="POST":
      song_name=request.form.get('song_name')
      lyrics=request.form.get('lyrics')
      genre=request.form.get('genre')
      if song_name!="":
         song.song_name=song_name
      if lyrics!="":
         song.lyrics=lyrics
      if genre!="":
        song.genre=genre
      db.session.commit() 
      return redirect(url_for('creator_page',artist_id=song.singer))     
   return render_template('update_song.html',song=song)

@app.route('/delete_song/<int:song_id>', methods=['GET'])
@login_required
def delete_song(song_id):
   song=Songs.query.filter_by(song_id=song_id).first()
   filename=song.song_path
   file_path=os.path.join('static', filename)
   os.remove(file_path)
   singer=song.singer
   db.session.delete(song)
   db.session.commit()
   return redirect(url_for('creator_page',artist_id=singer))

@app.route('/view_album/<int:album_id>',methods=['GET','POST'])
@login_required
def view_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   return render_template('view_album.html',album=album)

@app.route('/delete_from_album/<int:album_id>/<int:song_id>',methods=['GET'])
@login_required
def delete_from_album(album_id,song_id):
   album=Album.query.filter_by(album_id=album_id).first()
   for song in album.songs:
      if song.song_id==song_id:
         album.songs.remove(song)
   db.session.commit()
   return redirect(url_for('view_album',album_id=album.album_id))

@app.route('/delete_album/<int:album_id>',methods=['GET'])
@login_required
def delete_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   artist_id=album.artist_id
   db.session.delete(album)
   db.session.commit()
   return redirect(url_for('creator_page',artist_id=artist_id))

@app.route('/create_album/<int:artist_id>',methods=['GET','POST'])
@login_required
def create_album(artist_id):
   artist=Artist.query.filter_by(artist_id=artist_id).first()
   status=True     
   if request.method=='POST':
      album_name=request.form.get('album_name')  
      album_songs=request.form.getlist('album_songs')  
      for album in artist.albums:
         if album.album_name==album_name:
            status=False
            return render_template('create_album.html',artist=artist,artist_songs=artist.songs,status=status)   
      album=Album(album_name=album_name,artist_id=artist_id)
      db.session.add(album)
      db.session.commit()
      if len(album_songs)!=0:
            for song_id in album_songs:
               song=Songs.query.filter_by(song_id=int(song_id)).first()
               album.songs.append(song)
            db.session.commit()
      return redirect(url_for('view_album',album_id=album.album_id))      
   return render_template('create_album.html',artist=artist,artist_songs=artist.songs,status=status)

@app.route('/add_to_album/<int:album_id>',methods=['GET','POST'])
@login_required
def add_to_album(album_id):
   album=Album.query.filter_by(album_id=album_id).first()
   songs_available=[]
   for song in album.owner.songs:
      if song.album!=album.album_id:
         songs_available.append(song)
   if request.method=='POST':
      album_name=request.form.get('album_name')
      if album_name!='':
         album.album_name=album_name
      songs_to_add=request.form.getlist('songs_to_add')
      for song_id in songs_to_add:
         song=Songs.query.filter_by(song_id=int(song_id)).first()
         album.songs.append(song)
      db.session.commit()
      return redirect(url_for('view_album',album_id=album_id))      
   return render_template('add_to_album.html',album=album,songs_available=songs_available)



# ----------------------------------------------------------------------------API STARTS-------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

parser=reqparse.RequestParser()
parser.add_argument("song_name",type=str)
parser.add_argument("song_singer",type=int)
parser.add_argument("song_album",type=str)
parser.add_argument("song_lyrics",type=str)
parser.add_argument("song_genre",type=str)
parser.add_argument("song_path",type=str)
parser.add_argument("song_poster",type=str)

class SongApi(Resource):
    def get(self):
        songs=Songs.query.all()
        all_songs={}
        i=1
        for song in songs:
            current_song={}
            current_song['song_id']=song.song_id
            current_song['song_name']=song.song_name
            current_song['artist_name']=song.song_by.artist_name
            current_song['album']=song.album
            current_song['lyrics']=song.lyrics
            current_song['genre']=song.genre
            current_song['streams']=song.plays
            current_song['rating']=song.total_rating
            all_songs[f'song_{i}']=current_song
            i+=1
        return all_songs,200    

    def delete(self,song_id):
        song=Songs.query.filter_by(song_id=song_id).first()
        if song is None:
            return {'message':'Song not found'}, 404
        else:
            db.session.delete(song)
            db.session.commit()
            return {'message':'Song Successfully deleted'},200
    
    def post(self):
        args=parser.parse_args()
        song_name=args.get('song_name')
        singer=args.get('song_singer')
        album=args.get('song_album')
        lyrics=args.get('song_lyrics')
        genre=args.get('song_genre')
        song_path=args.get('song_path')
        song_poster=args.get('song_poster')
        artist_ids_tuples=Artist.query.with_entities(Artist.artist_id).all()
        artist_ids=[]
        for tuple in artist_ids_tuples:
           artist_ids.append(tuple[0])
        genres=['Pop','Jazz','Classical','R&B','Rock','Electronic/Dance','HipHop','Country','Soul','Indie']
        if song_name==None or singer==None or lyrics==None or genre==None or song_path==None or song_poster==None:
            return {'message':'Some parameters missing'},400
        if song_name=='' or lyrics=='' or song_path=="" or song_poster=='':
           return {'message':'Parameters cannot be blank'},400
        if singer not in artist_ids:
            return {'message':'Artist not found'},400
        if genre not in genres:
            return {'message':'Incorrect Genre'},400
        song=Songs(song_name=song_name,singer=singer,album=album,lyrics=lyrics,genre=genre,song_path=song_path,poster=song_poster)
        db.session.add(song)
        db.session.commit()
        return {'message':'Song successfully added'},200
    
    def put(self,song_id):
       song=Songs.query.filter_by(song_id=song_id).first()
       args=parser.parse_args()
       genres=['Pop','Jazz','Classical','R&B','Rock','Electronic/Dance','HipHop','Country','Soul','Indie']
       if song is None:
          return {'message':'Song does not exist'},400
       song_name=args.get('song_name')
       lyrics=args.get('song_lyrics')
       genre=args.get('song_genre')
       if song_name==None and lyrics==None and genre==None:
          return {'message':'Bad Request'},400
       if song_name is not None:
           if song_name=="":
              return {'message':'Song name cannot be blank'},400
           else:
              song.song_name=song_name
       if lyrics is not None:
           if lyrics=="":
              return {'message':'Lyrics cannot be blank'},400
           else:
            song.lyrics=lyrics
       if genre is not None:
           if genre not in genres:
              return {'message':'Incorrect Genre'},400
           else:
              song.genre=genre
       db.session.commit()
       return {'message':'Song Successfully Updated'},200     
    
api.add_resource(SongApi,'/api/all_songs', '/api/add_song', '/api/update_song/<int:song_id>', '/api/delete_song/<int:song_id>')

parser.add_argument("playlist_name",type=str)
parser.add_argument("playlist_songs",type=list, location='json')

class PlaylistApi(Resource):
   def get(self,user_id):
      user=User.query.filter_by(user_id=user_id).first()
      if user is None:
         return {'message':'User does not exist'}
      all_playlists={}
      j=1
      if len(user.playlists)==0:
         return {'message':'User Does not have any Playlists'}
      for playlist in user.playlists:
         current_playlist={}
         i=1
         for song in playlist.songs:
            current_playlist[f'song_{i}']={'song_id':song.song_id,'song_name':song.song_name}
            i+=1
         all_playlists[f'playlist_{j}']=current_playlist   
         j+=1
      return all_playlists,200   

   def delete(self,user_id,playlist_id):
      user=User.query.filter_by(user_id=user_id).first()
      if user is None:
         return {'message':'User does not exist'},404
      if len(user.playlists)==0:
         return {'message':'User Does not have any Playlists'},400
      playlist=Playlistuser.query.filter_by(p_id=playlist_id).first()
      if playlist==None:
         return {'message':'Playlist does not exist'},404
      if playlist.p_user_id!=user_id:
         return {'message': f'{playlist} does not belong to {user}'},400
      db.session.delete(playlist)
      db.session.commit()
      return {'message':'Deleted Successfully'},200

   def post(self,user_id):
      user=User.query.filter_by(user_id=user_id).first()
      args=parser.parse_args()
      if user is None:
         return {'message':'User does not exist'},404
      playlist_name=args.get('playlist_name')
      playlist_songs=args.get('playlist_songs')
      if playlist_name is None or playlist_name=="":
         return {'message':'Provide a valid playlist name'}
      playlist=Playlistuser(p_user_id=user_id,playlist_name=playlist_name)
      db.session.add(playlist)
      db.session.commit()
      if playlist_songs is None:
         return {'message':'Playlist created with zero songs'}
      wrong_song_ids=[]
      for song_id in playlist_songs:
         if type(song_id)=='str':
            wrong_song_ids.append(song_id)
            continue
         song=Songs.query.filter_by(song_id=song_id).first()
         if song is None:
           wrong_song_ids.append(song_id)
         else:
            playlist.songs.append(song)
         db.session.commit()
      if len(wrong_song_ids)==len(playlist_songs):
         return {'message':'Playlist created but no songs added as incorrect song ids provided'}    
      if len(wrong_song_ids)!=0:
         return {'message':f'Playlist created. Wrong Song Ids:{wrong_song_ids}'}      
      else:
         return {'message':f'Playlist created. All provided songs added successfully'}

   def put(self,user_id,playlist_id):
      user=User.query.filter_by(user_id=user_id).first()
      args=parser.parse_args()
      playlist_songs=args.get('playlist_songs')
      if user is None:
         return {'message':'User does not exist'},404
      playlist=Playlistuser.query.filter_by(p_id=playlist_id).first()
      if playlist==None:
         return {'message':'Playlist does not exist'},404
      if playlist.p_user_id!=user_id:
         return {'message': f'{playlist} does not belong to {user}'},400
      playlist_song_ids=[]
      for song in playlist.songs:
         playlist_song_ids.append(song.song_id)
      if playlist_songs is None:
         return {'message':'Bad Request'},400
      wrong_song_ids=[]
      already_in_playlist=[]
      for song_id in playlist_songs:
         if type(song_id)==str:
              wrong_song_ids.append(song_id)
              continue
         song=Songs.query.filter_by(song_id=song_id).first()
         if song is None:
           wrong_song_ids.append(song_id)
           continue
         if song_id in playlist_song_ids:
            already_in_playlist.append(song_id)
         else:
            playlist.songs.append(song)
            db.session.commit()
      if len(wrong_song_ids)==len(playlist_songs):
         return {'message':'Incorrect song ids provided'}       
      if len(wrong_song_ids)!=0 and 0<len(already_in_playlist)<len(playlist_songs):
         return {'message':f'Songs added to playlist. Wrong song ids:{wrong_song_ids}. Songs already in playlist:{already_in_playlist}'} ,200
      elif len(already_in_playlist)==len(playlist_songs):
           return {'message':'All songs already in Playlist'},200
      else:
         return {'message':'All songs provided added to playlist'},200 
      

api.add_resource(PlaylistApi,'/api/all_playlists/<int:user_id>', '/api/delete_playlist/<int:user_id>/<int:playlist_id>', '/api/create_playlist/<int:user_id>','/api/update_playlist/<int:user_id>/<int:playlist_id>')


class UserApi(Resource):
   def get(self):
      users=User.query.all()
      all_users={}
      i=1
      for user in users:
         current_user={}
         current_user['user_id']=user.user_id
         current_user['user_name']=user.user_name
         current_user['creator_id']=user.creator_id
         all_users[f'user_{i}']=current_user
         i+=1
      return all_users,200 

api.add_resource(UserApi,'/api/all_users')


parser.add_argument("album_name",type=str)
parser.add_argument("album_songs",type=list,location='json')

class AlbumApi(Resource):
   def get(self):
      albums=Album.query.all()
      all_albums={}
      i=1
      for album in albums:
         current_album={}
         current_album['album_id']=album.album_id
         current_album['album_name']=album.album_name
         current_album['artist_name']=album.owner.artist_name
         current_album['songs']={}
         j=1
         for song in album.songs:
            current_song={}
            current_song['song_id']=song.song_id
            current_song['song_name']=song.song_name
            current_album['songs'][f'song_{j}']=current_song
            j+=1
         all_albums[f'album_{i}']=current_album
         i+=1
      return all_albums

   def delete(self,album_id):
      album=Album.query.filter_by(album_id=album_id).first()
      if album is None:
         return {'message':'Album Does not exist'},404
      db.session.delete(album)
      db.session.commit()
      return {'message':'Successfully Deleted'},200

   def post(self,artist_id):
      artist=Artist.query.filter_by(artist_id=artist_id).first()
      if artist==None:
         return {'message':'Artist does not exist'},404
      args=parser.parse_args()
      album_name=args.get('album_name')
      album_songs=args.get('album_songs')
      for album in artist.albums:
         if album.album_name==album_name:
            return {'message':'Album Name exists'}
      album=Album(album_name=album_name,artist_id=artist_id)  
      db.session.add(album) 
      db.session.commit()
      if album_songs==None:
         return {'message':'Album created with 0 songs'},200
      wrong_song_ids=[]
      for song_id in album_songs:
         if type(song_id)=='str':
            wrong_song_ids.append(song_id)
            continue
         song=Songs.query.filter_by(song_id=song_id).first()
         if song==None:
            wrong_song_ids.append(song_id)
            continue
         if song.singer!=artist_id:
            wrong_song_ids.append(song_id)
            continue
         album.songs.append(song)
         db.session.commit()
      if len(wrong_song_ids)==len(album_songs):
         return {'message':'Album created but no songs added as incorrect song ids provided'},200
      if len(wrong_song_ids)!=0:
         return {'message':f'Album Created Successfully. Wrong song Ids provided:{wrong_song_ids}'} ,200  
      else:
         return {'message':f'Album Created Successfully. All songs added to album'},200

   def put(self,artist_id,album_id):
      args=parser.parse_args()
      artist=Artist.query.filter_by(artist_id=artist_id).first()
      if artist==None:
         return {'message':'Artist does not exist'},404
      album=Album.query.filter_by(album_id=album_id).first()
      if album is None:
         return {'message':'Album Does not exist'},404
      if album not in artist.albums:
         return {'message':f'{album} does not belong to {artist}'},400
      album_songs=args.get('album_songs')
      wrong_song_ids=[]
      already_album_songs=[]
      for song_id in album_songs:
         if type(song_id)=='str':
            wrong_song_ids.append(song_id)
            continue
         song=Songs.query.filter_by(song_id=song_id).first()
         if song==None:
            wrong_song_ids.append(song_id)
            continue
         if song.singer!=artist_id:
            wrong_song_ids.append(song_id)
            continue
         if song in album.songs:
            already_album_songs.append(song)
            continue
         album.songs.append(song)
         db.session.commit()
      if len(wrong_song_ids)==len(album_songs):
         return {'message':'Incorrect song ids provided'}       
      if len(wrong_song_ids)!=0 and 0<len(already_album_songs)<len(album_songs):
         return {'message':f'Songs added to album. Wrong song ids:{wrong_song_ids}. Songs already in album:{already_album_songs}'} ,200
      if len(wrong_song_ids)!=0 and len(already_album_songs)==0:
         return {'message':f'Songs added to album. Wrong song ids:{wrong_song_ids}.'} ,200
      elif len(already_album_songs)==len(album_songs):
           return {'message':'All songs already in album'},200
      else:
         return {'message':'All songs provided added to album'},200 





api.add_resource(AlbumApi,'/api/all_albums','/api/delete_album/<int:album_id>','/api/create_album/<int:artist_id>','/api/update_album/<int:artist_id>/<int:album_id>')          





















app.run(debug=True,port=8080)