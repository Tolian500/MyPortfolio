from bs4 import BeautifulSoup
import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth



# date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
print(f"client = {os.environ.get('SpotifyCID')}")
print(f"secret = {os.environ.get('SpotifyCS')}")


def get_songs(date: str):
    response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
    soup = BeautifulSoup(response.text, 'html.parser')
    song_names_spans = soup.select("li ul li h3")
    song_authors_spans = soup.find_all(name="span", class_="a-no-trucate")
    song_names = [song.getText().strip() for song in song_names_spans]
    song_authors = [song.getText().strip() for song in song_authors_spans]
    songs_dict = {author: name for author, name in zip(song_authors, song_names)}
    return songs_dict





def loggin_sp():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-public",
            redirect_uri="http://example.com",
            client_id=os.environ.get('SpotifyCID'),
            client_secret=os.environ.get('SpotifyCS'),
            show_dialog=True,
            cache_path="token.txt",
            username='Hits Playlist Bot'
        )
    )
    return sp


def get_songs_list(songs: dict, date: str):
    sp = loggin_sp()
    song_uris = []
    year = date.split("-")[0]
    for author in songs:
        result = sp.search(q=f"track:{songs[author]} year:{year}", type="track")
        # print(result)
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
            # print("🟢")
        except IndexError:
            result = sp.search(q=f"track:{songs[author]} artist:{author}", type="track")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
                # print("🟢")
            except IndexError:
                pass
                # print(f"🔴 {songs[author]} by {author} doesn't exist on Spotify. Skipped.")
    return song_uris


def create_playlist(date: str, songs_list, name:str):
    sp = loggin_sp()
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=f"{name}'s Playlist of: {date}", public=True)
    sp.playlist_add_items(playlist_id=playlist["id"], items=songs_list)
    playlist_url = playlist["external_urls"]["spotify"]
    print(f"Playlist URL: {playlist_url}")
    return playlist_url


test_date = '2010-01-01'
def find_and_generate_playlist(name:str, date:str):
    return create_playlist(date, get_songs_list(get_songs(date), date), name)
