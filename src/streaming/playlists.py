"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""

class Playlist:
    def __init__(self, playlist_id, name, owner):
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks = []

    def add_track(self, track):
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id):
        self.tracks = [t for t in self.tracks if t.track_id != track_id]


class CollaborativePlaylist(Playlist):
    def __init__(self, playlist_id, name, owner):
        super().__init__(playlist_id, name, owner)
        self.contributors = [owner]

    def add_contributor(self, user):
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user):
        if user != self.owner and user in self.contributors:
            self.contributors.remove(user)