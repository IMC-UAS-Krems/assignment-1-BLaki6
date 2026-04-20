"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""

from datetime import datetime, timedelta
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Song
from streaming.playlists import CollaborativePlaylist


class StreamingPlatform:
    def __init__(self, name: str):
        self.name = name
        self._catalogue = {}
        self._users = {}
        self._artists = {}
        self._albums = {}
        self._playlists = {}
        self._sessions = []

        self.catalogue = self._catalogue
        self.users = self._users
        self.artists = self._artists
        self.albums = self._albums
        self.playlists = self._playlists
        self.sessions = self._sessions

    # basic helper methods (needed for tests)
    def add_user(self, user):
        self.users[user.user_id] = user

    def add_artist(self, artist):
        self.artists[artist.artist_id] = artist

    def add_album(self, album):
        self.albums[album.album_id] = album

    def add_playlist(self, playlist):
        self.playlists[playlist.playlist_id] = playlist

    def add_track(self, track):
        self.catalogue[track.track_id] = track

    def add_session(self, session):
        self.sessions.append(session)
        session.user.add_session(session)

    def record_session(self, session):
        self.add_session(session)

    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_track(self, track_id):
        return self.catalogue.get(track_id)

    def get_artist(self, artist_id):
        return self.artists.get(artist_id)

    def get_album(self, album_id):
        return self.albums.get(album_id)

    def all_users(self):
        return list(self.users.values())

    def all_tracks(self):
        return list(self.catalogue.values())

    # =========================
    # Q1
    # =========================
    def total_listening_time_minutes(self, start, end):
        """Sum listening time in minutes within a given time window."""
        total = 0
        for session in self.sessions:
            if start <= session.timestamp <= end:
                total += session.duration_listened_seconds
        return total / 60

    # =========================
    # Q2
    # =========================
    def avg_unique_tracks_per_premium_user(self, days=30):
        """Average number of unique tracks listened by PremiumUsers in last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        premium_users = [u for u in self.users.values() if isinstance(u, PremiumUser)]
        if not premium_users:
            return 0.0
        total_unique = 0
        for user in premium_users:
            tracks = set()
            for session in user.sessions:
                if session.timestamp >= cutoff:
                    tracks.add(session.track.track_id)
            total_unique += len(tracks)
        return total_unique / len(premium_users)

    # =========================
    # Q3
    # =========================
    def track_with_most_distinct_listeners(self):
        if not self.sessions:
            return None    
        track_listeners = {}    
        for session in self.sessions:
            track = session.track
            user_id = session.user.user_id    
            if track is None:
                continue            
            track_listeners.setdefault(track, set()).add(user_id)    
        if not track_listeners:
            return None    
        return max(track_listeners, key=lambda t: len(track_listeners[t]))

    # =========================
    # Q4
    # =========================
    def avg_session_duration_by_user_type(self):
        """Average session duration per user type, sorted descending."""
        data = {
            "FreeUser": [],
            "PremiumUser": [],
            "FamilyAccountUser": [],
            "FamilyMember": []
        }

        for session in self.sessions:
            user = session.user
            duration = session.duration_listened_seconds
            # group durations by user type
            if isinstance(user, FreeUser):
                data["FreeUser"].append(duration)
            elif isinstance(user, PremiumUser):
                data["PremiumUser"].append(duration)
            elif isinstance(user, FamilyAccountUser):
                data["FamilyAccountUser"].append(duration)
            elif isinstance(user, FamilyMember):
                data["FamilyMember"].append(duration)
        result = []
        for user_type, durations in data.items():
            avg = sum(durations) / len(durations) if durations else 0.0
            result.append((user_type, avg))
        # sort from highest to lowest average
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    # =========================
    # Q5
    # =========================
    def total_listening_time_underage_sub_users_minutes(self, age_threshold=18):
        """Total listening time (minutes) for underage FamilyMembers."""
        total = 0
        for session in self.sessions:
            user = session.user
            # only count underage family members
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total += session.duration_listened_seconds
        return total / 60

    # =========================
    # Q6
    # =========================
    def top_artists_by_listening_time(self, n=5):
        """Return top N artists ranked by total listening time."""
        artist_time = {}
        for session in self.sessions:
            track = session.track

            # only count Song tracks
            if isinstance(track, Song):
                artist = track.artist
                minutes = session.duration_listened_seconds / 60
                if artist not in artist_time:
                    artist_time[artist] = 0
                artist_time[artist] += minutes
        result = list(artist_time.items())
        # sort descending by listening time
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    # =========================
    # Q7
    # =========================
    def user_top_genre(self, user_id):
        """Return user's most listened genre and its percentage."""
        user = self.get_user(user_id)
        if user is None or not user.sessions:
            return None

        genre_time = {}
        total_time = 0
        for session in user.sessions:
            genre = session.track.genre
            seconds = session.duration_listened_seconds
            total_time += seconds
            if genre not in genre_time:
                genre_time[genre] = 0
            genre_time[genre] += seconds

        # find genre with max listening time
        top_genre = max(genre_time, key=lambda g: genre_time[g])
        top_time = genre_time[top_genre]
        percentage = (top_time / total_time) * 100
        return (top_genre, percentage)

    # =========================
    # Q8
    # =========================
    def collaborative_playlists_with_many_artists(self, threshold=3):
        """Return collaborative playlists with many distinct artists."""
        result = []

        for playlist in self.playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = set()
                for track in playlist.tracks:
                    # only count Song artists
                    if isinstance(track, Song):
                        artists.add(track.artist)
                if len(artists) > threshold:
                    result.append(playlist)
        return result

    # =========================
    # Q9
    # =========================
    def avg_tracks_per_playlist_type(self):
        """Average number of tracks for each playlist type."""
        normal_counts = []
        collab_counts = []
        for playlist in self.playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                collab_counts.append(len(playlist.tracks))
            else:
                normal_counts.append(len(playlist.tracks))

        def avg(lst):
            return sum(lst) / len(lst) if lst else 0.0
        return {
            "Playlist": avg(normal_counts),
            "CollaborativePlaylist": avg(collab_counts)
        }

    # =========================
    # Q10
    # =========================
    def users_who_completed_albums(self):
        """Return users who listened to all tracks of at least one album."""
        result = []
        for user in self.users.values():
            completed_albums = []
            for album in self.albums.values():
                album_track_ids = {t.track_id for t in album.tracks}
                listened_track_ids = {
                    session.track.track_id for session in user.sessions
                }
                if album_track_ids and album_track_ids.issubset(listened_track_ids):
                    completed_albums.append(album.title)
            if completed_albums:
                result.append((user, completed_albums))
        return result
