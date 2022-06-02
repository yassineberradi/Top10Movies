import os
import requests

THEMOVIEDB_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
API_KEY = os.environ.get("api_key")
HEADERS = {
        "api_key": API_KEY,
    }
MOVIE_DB_API_KEY = "GET YOUR API KEY FROM themoviedb.org"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


class DataManager:
    def __init__(self):
        self.data_raw = None

    def get_data(self, name):
        param = {
            "api_key": API_KEY,
            "query": name
        }
        self.data_raw = requests.get(THEMOVIEDB_ENDPOINT, params=param, headers=HEADERS).json()
        return self.data_raw['results']

