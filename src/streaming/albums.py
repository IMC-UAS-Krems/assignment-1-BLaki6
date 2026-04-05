"""
albums.py
---------
Implement the Album class for collections of AlbumTrack objects.

Classes to implement:
  - Album
"""

class Album:
    def __init__(self, album_id, title, artist, release_year):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks = []

    def add_track(self, track):
        self.tracks.append(track)
        track.album = self