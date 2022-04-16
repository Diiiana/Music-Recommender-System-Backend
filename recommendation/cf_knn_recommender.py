import pandas as pd
from scipy.sparse import csr_matrix
from likes.models import Likes
from song.models import Song
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz
import numpy as np
from sklearn import metrics


class Recommender:
    def __init__(self, metric, algorithm, k, data, decode_id_song):
        self.metric = metric
        self.algorithm = algorithm
        self.k = k
        self.data = data
        self.decode_id_song = decode_id_song
        self.data = data
        self.model = self._recommender().fit(data)
    
    def make_recommendation(self, new_song, n_recommendations):
        recommended = self._recommend(new_song=new_song, n_recommendations=n_recommendations)
        return recommended 
    
    def _recommender(self):
        return NearestNeighbors(metric=self.metric, algorithm=self.algorithm, n_neighbors=self.k, n_jobs=-1)
    
    def _recommend(self, new_song, n_recommendations):
        recommendations = []
        recommendation_ids = self._get_recommendations(new_song=new_song, n_recommendations=n_recommendations)
        recommendations_map = self._map_indeces_to_song_title(recommendation_ids)
        print(recommendation_ids)
        for i, (idx, dist) in enumerate(recommendation_ids):
            try:
                recommendations.append(recommendations_map[idx])
            except:
                pass
        return recommendations

    def _get_recommendations(self, new_song, n_recommendations):
        recom_song_id = self._fuzzy_matching(song=new_song)
        print(f"Starting the recommendation process for {new_song} ...")
        distances, indices = self.model.kneighbors(self.data[2000], n_neighbors=n_recommendations+1)
        return sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
    
    def _map_indeces_to_song_title(self, recommendation_ids):
        return {song_id: song_title for song_title, song_id in self.decode_id_song.items()}
    
    def _fuzzy_matching(self, song):
        match_tuple = []
        for title, idx in self.decode_id_song.items():
            ratio = fuzz.ratio(title.lower(), song.lower())
            if ratio >= 60:
                match_tuple.append((title, idx, ratio))
        match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
        if not match_tuple:
            print(f"The recommendation system could not find a match for {song}")
            return
        return match_tuple[0][1]

class RecommenderCFMatrix:
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))

    qs_song = list(Song.objects.all().values('id', 'song_name'))
    df_song = pd.DataFrame(list(qs_song))
    
    df_final = df.merge(df_song, how='inner', left_on='song_id', right_on='id')
    df_songs_features = df_final.pivot(index='song_id', columns='user_id', values='liked').fillna(0)
    
    df_unique_songs = df_final.drop_duplicates(subset=['song_id']).reset_index(drop=True)[['song_id', 'song_name']]
    mat_songs_features = csr_matrix(df_songs_features.values)

    decode_id_song = { song: i for i, song in enumerate(list(df_final.set_index('song_id').loc[df_songs_features.index].song_name))}

    model = Recommender(metric='cosine', algorithm='brute', k=20, data=mat_songs_features, decode_id_song=decode_id_song)
    song = 'Rise'
    # 'Rise': 53033
    new_recommendations = model.make_recommendation(new_song=song, n_recommendations=10)