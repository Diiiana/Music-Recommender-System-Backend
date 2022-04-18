from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.preprocessing import LabelEncoder
from likes.models import Likes
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


class NcfRecommender:
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))

    shuffled_df = df.sample(frac=1, random_state=4)
    fraud_df = shuffled_df.loc[shuffled_df['liked'] == 1]
    non_fraud_df = shuffled_df.loc[shuffled_df['liked'] == 0].sample(
        n=200, random_state=42)

    df = pd.concat([fraud_df, non_fraud_df])
    df = fraud_df

    n_users, n_songs = len(df.user_id.unique()), len(df.song_id.unique())

    song_input = keras.layers.Input(shape=[1], name='Song')
    song_embedding = keras.layers.Embedding(n_songs, 10,
                                            embeddings_initializer='uniform',
                                            embeddings_regularizer=l2(1e-6),
                                            embeddings_constraint='NonNeg',
                                            name='Song-Embedding')(song_input)
    song_vec = keras.layers.Flatten(name='FlattenSongs')(song_embedding)

    user_input = keras.layers.Input(shape=[1], name='User')
    user_embedding = keras.layers.Embedding(n_users, 10,
                                            embeddings_initializer='uniform',
                                            embeddings_regularizer=l2(1e-6),
                                            embeddings_constraint='NonNeg',
                                            name='User-Embedding')(user_input)
    user_vec = keras.layers.Flatten(name='FlattenUsers')(user_embedding)

    concat = keras.layers.concatenate([song_vec, user_vec])
    mlp = concat
    for i in range(3, -1, -1):
        if i == 0:
            mlp = Dense(8**i, activation='sigmoid', kernel_initializer='glorot_normal',
                        name="output")(mlp)
        else:
            mlp = Dense(8*2**i, activation='relu',
                        kernel_initializer='he_uniform')(mlp)
        if i > 2:
            mlp = BatchNormalization()(mlp)
            mlp = Dropout(0.2)(mlp)
    model = Model(inputs=[user_input, song_input], outputs=[mlp])
    model.compile(optimizer='adadelta', loss='binary_crossentropy', metrics=[
                  'binary_accuracy', keras.metrics.Precision(), keras.metrics.Recall()])

    callbacks = [EarlyStopping(patience=1)]

    user_encoder = LabelEncoder()
    song_encoder = LabelEncoder()

    user_ids = user_encoder.fit_transform(df.user_id)
    song_ids = song_encoder.fit_transform(df.song_id)

    num_train = int(len(user_ids) * 0.8)
    train_user_ids = user_ids[:num_train]
    train_song_ids = song_ids[:num_train]
    train_ratings = df.liked.values[:num_train]
    val_user_ids = user_ids[num_train:]
    val_song_ids = song_ids[num_train:]
    val_ratings = df.liked.values[num_train:]

    num_users = user_ids.max() + 1
    num_songs = song_ids.max() + 1

    # train, test = train_test_split(df, test_size = 0.2, stratify=df.liked)
    # X_resampled, y_resampled = SMOTE().fit_resample(train[['liked']], train['liked'])
    # print(X_resampled)

    model.fit([train_user_ids, train_song_ids], train_ratings,
              validation_data=([val_user_ids, val_song_ids], val_ratings),
              epochs=20, batch_size=128, callbacks=callbacks)
    model.summary()
    # pentru testare
    # predictions = model.predict([val_user_ids, val_song_ids])
    print(len(val_user_ids), len(val_song_ids))
    results = model.evaluate([val_user_ids, val_song_ids])
    print("test loss, test acc, test precision, test recall:", results)
    # predictions = np.column_stack(
    #     (predictions, val_song_ids.astype(np.object)))
    # predictions = predictions[predictions[:, 0].argsort()[::-1]]
    # print(predictions)
