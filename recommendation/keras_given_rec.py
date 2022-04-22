from likes.models import Likes
import pandas as pd
import numpy as np
from tensorflow import keras
import tensorflow as tf
import random
import scipy

class RecommenderNet(keras.Model):
    def __init__(self, num_users, num_songs, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_songs = num_songs
        self.embedding_size = embedding_size
        self.user_embedding = keras.layers.Embedding(
            num_users,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.user_bias = keras.layers.Embedding(num_users, 1)
        self.song_embedding = keras.layers.Embedding(
            num_songs,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.song_bias = keras.layers.Embedding(num_songs, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        song_vector = self.song_embedding(inputs[:, 1])
        song_bias = self.song_bias(inputs[:, 1])
        dot_user_song = tf.tensordot(user_vector, song_vector, 2)
        x = dot_user_song + user_bias + song_bias
        # The sigmoid activation forces the rating to between 0 and 1
        return tf.nn.sigmoid(x)


class KerasRecommender:
    
    def neg_sampling(ratings_df, n_neg=5, neg_val=0, percent_print=5):
        ratings_df.user_id = ratings_df.user_id.astype(
            'category').cat.codes.values
        ratings_df.song_id = ratings_df.song_id.astype(
            'category').cat.codes.values
        sparse_mat = scipy.sparse.coo_matrix(
            (ratings_df.liked, (ratings_df.user_id, ratings_df.song_id)))
        dense_mat = np.asarray(sparse_mat.todense())

        nsamples = ratings_df[['user_id', 'song_id']]
        nsamples['liked'] = nsamples.apply(lambda row: 1, axis=1)
        length = dense_mat.shape[0]
        printpc = int(length * percent_print/100)
        nTempData = []
        i = 0

        extra_samples = 0
        for row in dense_mat:
            if(i % printpc == 0):
                n_non_0 = len(np.nonzero(row)[0])
                zero_indices = np.where(row == 0)[0]
            if(n_non_0 * n_neg + extra_samples > len(zero_indices)):
                neg_indices = zero_indices.tolist()
                extra_samples = n_non_0 * n_neg + \
                    extra_samples - len(zero_indices)
            else:
                neg_indices = random.sample(
                    zero_indices.tolist(), n_non_0 * n_neg + extra_samples)
                extra_samples = 0
                nTempData.extend([(uu, ii, rr) for (uu, ii, rr) in zip(np.repeat(
                    i, len(neg_indices)), neg_indices, np.repeat(neg_val, len(neg_indices)))])
            i += 1
        nsamples = nsamples.append(pd.DataFrame(
            nTempData, columns=["user_id", "song_id", "liked"]), ignore_index=True)
        return nsamples
    
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))
    df = neg_sampling(df)
    
    user_ids = df["user_id"].unique().tolist()

    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    userencoded2user = {i: x for i, x in enumerate(user_ids)}

    movie_ids = df["song_id"].unique().tolist()

    movie2movie_encoded = {x: i for i, x in enumerate(movie_ids)}
    movie_encoded2movie = {i: x for i, x in enumerate(movie_ids)}

    df["user_id"] = df["user_id"].map(user2user_encoded)
    df["song_id"] = df["song_id"].map(movie2movie_encoded)

    num_users = len(user2user_encoded)
    num_movies = len(movie_encoded2movie)

    df["liked"] = df["liked"].values.astype(np.float32)

    df = df.sample(frac=1, random_state=42)
    x = df[["user_id", "song_id"]].values
    y = df["liked"]
    train_indices = int(0.7 * df.shape[0])
    x_train, x_val, y_train, y_val = (
        x[:train_indices],
        x[train_indices:],
        y[:train_indices],
        y[train_indices:],
    )

    model = RecommenderNet(num_users, num_movies, 10)
    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(), optimizer=keras.optimizers.Adam(lr=0.001),
        metrics=['binary_accuracy', keras.metrics.Precision(), keras.metrics.Recall(), keras.metrics.RootMeanSquaredError(), 
                  keras.metrics.TruePositives()])

    history = model.fit(
        x=x_train,
        y=y_train,
        batch_size=64,
        epochs=5,
        verbose=1,
        validation_data=(x_val, y_val),
    )
