from flask_mongoengine import MongoEngine

from .models import Item

import requests

class Item(object):
    def __init__(self, creator, content, date, name):
        self.creator = creator
        self.content = content
        self.date = date
        self.name = name

    def __repr__(self):
        return self.name


class ItemClient(object):
    def __init__(self, db):
        self.db = db

    def search(self, search_string):
        items_query = Item.objects(name=search_string)

        result = []

        for item in items_query:
            result.append(item)

        return result

    def retrieve_item_by_id(self, item_id):
        item_url = self.base_url + f"i={imdb_id}&plot=full"

        resp = self.sess.get(movie_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        if data["Response"] == "False":
            raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        movie = Movie(data, detailed=True)

        return movie


## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client = MovieClient(os.environ.get("OMDB_API_KEY"))

    movies = client.search("guardians")

    for movie in movies:
        print(movie)

    print(len(movies))
