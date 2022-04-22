import numpy as np
import pandas as pd
import tensorflow as tf
from likes.models import Likes


# used to obtain list of songs user did not listen
class Mapper():

    def __init__(self, possible_products, num_negative_products):
        self.num_possible_products = len(possible_products)
        self.possible_products_tensor = tf.constant(
            possible_products, dtype=tf.int32)

        self.num_negative_products = num_negative_products
        self.y = tf.one_hot(0, num_negative_products+1) # folosit pt predictie - pt primul se prezice, pt restul nu

    def __call__(self, user, product):
        random_negatives = tf.random.uniform(
             (self.num_negative_products, ), minval=0, maxval=self.num_possible_products, 
             dtype=tf.int32)
        negatives = tf.gather(self.possible_products_tensor, random_negatives)
        candidates = tf.concat([product, negatives], axis = 0)
        return (user, candidates), self.y

class Datascience:
    class SimpleRecommender(tf.keras.Model):
        def __init__(self, dummy_users, songs, embedding_size):
            super().__init__()
            self.songs = tf.constant(songs, dtype=tf.int32)
            self.dummy_users = tf.constant(dummy_users, dtype=tf.string)
            self.dummy_user_table = tf.lookup.StaticHashTable(
                tf.lookup.KeyValueTensorInitializer(self.dummy_users, range(len(dummy_users))), -1)
            self.song_table = tf.lookup.StaticHashTable(
                tf.lookup.KeyValueTensorInitializer(self.songs, range(len(songs))), -1)

            self.user_embedding = tf.keras.layers.Embedding(
                len(dummy_users), embedding_size)
            self.song_embedding = tf.keras.layers.Embedding(
                len(songs), embedding_size)

            self.dot = tf.keras.layers.Dot(axes=-1)

        def call(self, inputs):
            user = inputs[0]
            songs = inputs[1]
            user_embedding_index = self.dummy_user_table.lookup(user)
            song_embedding_index = self.song_table.lookup(songs)

            user_embedding_values = self.user_embedding(user_embedding_index)
            song_embedding_values = self.song_embedding(song_embedding_index)

            return tf.squeeze(self.dot([user_embedding_values, song_embedding_values]), 1)

        @tf.function
        def call_item_item(self, product):
            product_x = self.product_table.lookup(product)
            pe = tf.expand_dims(self.product_embedding(product_x), 0)

            # note this only works if the layer has been built!
            all_pe = tf.expand_dims(self.product_embedding.embeddings, 0)
            scores = tf.reshape(self.dot([pe, all_pe]), [-1])

            top_scores, top_indices = tf.math.top_k(scores, k=100)
            top_ids = tf.gather(self.songs, top_indices)
            return top_ids, top_scores

    def get_dataset(df, songs, num_negative_songs):
            dummy_user_tensor = tf.constant(df[["user_id"]].values, dtype=tf.string)
            song_tensor = tf.constant(df[["song_id"]].values, dtype=tf.int32)

            dataset = tf.data.Dataset.from_tensor_slices((dummy_user_tensor, song_tensor))
            dataset = dataset.map(Mapper(songs, num_negative_songs))
            dataset = dataset.batch(1024)
            return dataset
    
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))

    dummy_users = np.array(df["user_id"].unique())
    products = np.array(df["song_id"].unique())
    print(dummy_users, products)

    num_train = int(len(df) * 0.7)
    train = df[:num_train]
    valid = df[num_train:]

    songs = np.array(df['song_id'].unique())
    # print("prev songs: ", songs)
    song_table = tf.lookup.StaticHashTable(
        tf.lookup.KeyValueTensorInitializer(tf.constant(songs, dtype=tf.int32),
                                            range(len(songs))), -1)
    # print("song: ", song_table.lookup(tf.constant(2548)))
    dummy_user_tensor = tf.constant(df[["user_id"]].values, dtype=tf.string)
    song_tensor = tf.constant(df[["song_id"]].values, dtype=tf.int32)

    dataset = tf.data.Dataset.from_tensor_slices(
        (dummy_user_tensor, song_tensor))
    print("\n\nDataset")
    for x, y in dataset:
        print(x)
        print(y)
        break
    # prima piesa e ceva ce a ascultat si restul e ceva ce nu
    dataset = get_dataset(train, songs, 5)
    print("\n\nNew Dataset")
    for (x, y), y in dataset:
        print(x)
        print(y)
        break
    # print("Recs for item {}: {}".format(12, model.call_item_item(tf.constant(12, dtype=tf.int32))))
    model = SimpleRecommender(dummy_users, products, 15)
    result = model([tf.constant([['fd4f7fbb-322f-40ae-812b-1ba2c9020196']]),
                    tf.constant([[2548, 2550, 2559]])])
    # print(result)
    model.compile(loss=tf.keras.losses.CategoricalCrossentropy(),
                  optimizer=tf.keras.optimizers.SGD(learning_rate=100.),
                  metrics=[tf.keras.metrics.CategoricalAccuracy()])
    print("valid = ", valid)
    model.fit(get_dataset(train, songs, 10), validation_data=get_dataset(valid, songs, 10), epochs=100)