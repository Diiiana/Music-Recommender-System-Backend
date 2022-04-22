from typing import Dict, Text

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_recommenders as tfrs
from likes.models import Likes
from song.models import Song
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class TensorRecommender:
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    data = pd.DataFrame(list(qs))

    data_items = data.drop('user_id', 1)
    magnitude = np.sqrt(np.square(data_items).sum(axis=1))
    data_items = data_items.divide(magnitude, axis='index')

    def calculate_similarity(data_items):
        data_sparse = sparse.csr_matrix(data_items)
        similarities = cosine_similarity(data_sparse.transpose())
        sim = pd.DataFrame(data=similarities, index= data_items.columns, columns= data_items.columns)
        return sim

    data_matrix = calculate_similarity(data_items)
    # print(data_matrix)
    # print(data_matrix.loc['12'].nlargest(11))

    data_neighbours = pd.DataFrame(index=data_matrix.columns, columns=range(1,11))
    for i in range(0, len(data_matrix.columns)):
        data_neighbours.ix[i,:10] = data_matrix.ix[0:,i].sort_values(ascending=False)[:10].index

    # user = 5985
    # user_index = data[data.user == user].index.tolist()[0]

    # known_user_likes = data_items.ix[user_index]
    # known_user_likes = known_user_likes[known_user_likes >0].index.values

    # most_similar_to_likes = data_neighbours.ix[known_user_likes]
    # similar_list = most_similar_to_likes.values.tolist()
    # similar_list = list(set([item for sublist in similar_list for item in sublist]))
    # neighbourhood = data_matrix[similar_list].ix[similar_list]

    # user_vector = data_items.ix[user_index].ix[similar_list]
    # score = neighbourhood.dot(user_vector).div(neighbourhood.sum(axis=1))
    # score = score.drop(known_user_likes)

    # print(known_user_likes)
    # print(score.nlargest(20))