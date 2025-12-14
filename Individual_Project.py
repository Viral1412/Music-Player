import pygame
import os
import random
import mysql.connector
import time

def establishDatabaseConnection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="music_db"
        )
        print("Database connection successfully!")
        return conn
    except mysql.connector.Error as e:
        print(f"Connection Error: {e}")
        return None

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.active_track_index = -1
        self.track_list = []

    def loadTracks(self, track_data):
        self.track_list = track_data
        print("Loading tracks, Please Wait", end="")
        for _ in range(3):
            time.sleep(1)
            print(".", end="", flush=True)
        print("\nTracks successfully loaded into the player.")

    def playTrack(self, index):
        if index < 0 or index >= len(self.track_list):
            print("Invalid track index!")
            return

        trackPath = self.track_list[index][3]
        if os.path.exists(trackPath):
            pygame.mixer.music.load(trackPath)
            pygame.mixer.music.play()
            self.active_track_index = index
            print(f"Playing: {self.track_list[index][1]} by {self.track_list[index][2]}")
        else:
            print("Track file not found!")

    def nextTrack(self):
        if self.active_track_index + 1 < len(self.track_list):
            self.playTrack(self.active_track_index + 1)
        else:
            self.playTrack(0)

    def previousTrack(self):
        if self.active_track_index > 0:
            self.playTrack(self.active_track_index - 1)
        else:
            index = len(self.track_list)-1
            self.playTrack(index)

    def shuffleTracks(self):
        random.shuffle(self.track_list)
        self.active_track_index = -1
        print("Track list shuffled!")

    def stop(self):
        pygame.mixer.music.stop()
        print("Track stopped.")

    def pause(self):
        pygame.mixer.music.pause()
        print("Track paused.")

    def resume(self):
        pygame.mixer.music.unpause()
        print("Track resumed.")

def start():
    database = establishDatabaseConnection()
    if not database:
        return

    DC = database.cursor()
    player = AudioPlayer()

    while True:
        print("\n--- Audio Player Menu ---")
        print("1. Load Tracks from Database")
        print("2. Add Track to Database")
        print("3. Play Track")
        print("4. Play Next Track")
        print("5. Play Previous Track")
        print("6. Shuffle Track List")
        print("7. Like a Track")
        print("8. View Favorite Tracks")
        print("9. Stop Track")
        print("10. Pause Track")
        print("11. Resume Track")
        print("12. Exit")
        print("\n----------------------")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            DC.execute("SELECT * FROM songs")
            retrieved_tracks = DC.fetchall()
            if retrieved_tracks:
                player.loadTracks(retrieved_tracks)
            else:
                print("No tracks found in the database!")

        elif choice == "2":
            track_title = input("Enter track title: ")
            track_artist = input("Enter artist name: ")
            track_location = input("Enter file location: ")

            try:
                insert_query = "INSERT INTO songs (title, artist, file_path) VALUES (%s, %s, %s)"
                DC.execute(insert_query, (track_title, track_artist, track_location))
                database.commit()
                print("Track successfully added!")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "3":
            if not player.track_list:
                print("Please load tracks first.")
                continue

            print("\n--- Available Tracks ---")
            for track in player.track_list:
                print(f"{track[0]}. {track[1]} by {track[2]}")

            track_id = input("Enter the track ID to play: ")
            track_indexes = [track[0] for track in player.track_list]
            if int(track_id) in track_indexes:
                index_position = track_indexes.index(int(track_id))
                player.playTrack(index_position)
            else:
                print("Invalid track ID!")

        elif choice == "4":
            player.nextTrack()

        elif choice == "5":
            player.previousTrack()

        elif choice == "6":
            player.shuffleTracks()

        elif choice == "7":
            if not player.track_list:
                print("Please load tracks first.")
                continue

            print("\n--- Available Tracks ---")
            for track in player.track_list:
                print(f"{track[0]}. {track[1]} by {track[2]}")

            liked_track_id = input("Enter the track ID to like: ")
            try:
                like_query = "INSERT INTO liked_songs (song_id) VALUES (%s)"
                DC.execute(like_query, (liked_track_id,))
                database.commit()
                print("Track successfully liked!")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":
            DC.execute("""
                SELECT songs.id, songs.title, songs.artist
                FROM liked_songs
                INNER JOIN songs ON liked_songs.song_id = songs.id
            """)
            favorite_tracks = DC.fetchall()
            if favorite_tracks:
                print("\n--- Favorite Tracks ---")
                for track in favorite_tracks:
                    print(f"{track[0]}. {track[1]} by {track[2]}")
            else:
                print("No favorite tracks found!")

        elif choice == "9":
            player.stop()

        elif choice == "10":
            player.pause()

        elif choice == "11":
            player.resume()

        elif choice == "12":
            print("Quiting...")
            break

        else:
            print("Invalid choice! Please try again.")

    DC.close()
    database.close()

if __name__ == "__main__":
    start()
