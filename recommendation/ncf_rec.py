from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import pandas as pd
from likes.models import Likes


class NcfRecommender:
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))

    userids = df['user_id'].unique()
    count = 1
    dict_users = {}
    for u in userids:
        dict_users[u] = count
        count += 1

    df["user_id"] = df["user_id"].map(dict_users)
    train, test = train_test_split(df, test_size=0.3, stratify=df.liked)
    X_resampled, y_resampled = SMOTE(sampling_strategy='minority', k_neighbors=2).fit_resample(
        train[['user_id', 'song_id']], train['liked'])

    user_encoder = LabelEncoder()
    song_encoder = LabelEncoder()

    train_user_ids = user_encoder.fit_transform(X_resampled.user_id)
    train_song_ids = song_encoder.fit_transform(X_resampled.song_id)
    train_ratings = y_resampled

    user_encoder_test = LabelEncoder()
    song_encoder_test = LabelEncoder()

    val_user_ids = user_encoder_test.fit_transform(test.user_id)
    val_song_ids = song_encoder_test.fit_transform(test.song_id)
    val_ratings = test.liked

    n_users, n_songs = len(df.user_id.unique()), len(df.song_id.unique())

    song_input = tf.keras.layers.Input(shape=[1], name='Song')
    song_embedding = tf.keras.layers.Embedding(n_songs, 16,
                                               embeddings_initializer='uniform',
                                               embeddings_regularizer=tf.keras.regularizers.l2(
                                                   1e-6),
                                               embeddings_constraint='NonNeg',
                                               name='Song-Embedding')(song_input)
    song_vec = tf.keras.layers.Flatten(name='FlattenSongs')(song_embedding)

    user_input = tf.keras.layers.Input(shape=[1], name='User')
    user_embedding = tf.keras.layers.Embedding(n_users, 16,
                                               embeddings_initializer='uniform',
                                               embeddings_regularizer=tf.keras.regularizers.l2(
                                                   1e-6),
                                               embeddings_constraint='NonNeg',
                                               name='User-Embedding')(user_input)
    user_vec = tf.keras.layers.Flatten(name='FlattenUsers')(user_embedding)

    concat = tf.keras.layers.concatenate([song_vec, user_vec])
    mlp = concat
    for i in range(3, -1, -1):
        if i == 0:
            mlp = tf.keras.layers.Dense(8**i, activation='sigmoid', kernel_initializer='glorot_normal',
                                        name="output")(mlp)
        else:
            mlp = tf.keras.layers.Dense(8*2**i, activation='relu',
                                        kernel_initializer='he_uniform')(mlp)
        if i > 2:
            mlp = tf.keras.layers.BatchNormalization()(mlp)
            mlp = tf.keras.layers.Dropout(0.2)(mlp)
    model = tf.keras.Model(inputs=[user_input, song_input], outputs=[mlp])
    model.compile(optimizer='adadelta', loss='binary_crossentropy', metrics=[
                  'binary_accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall(), tf.keras.metrics.RootMeanSquaredError()])

    callbacks = [tf.keras.callbacks.EarlyStopping(patience=1)]

    num_users = val_user_ids.max() + 1
    num_songs = val_song_ids.max() + 1

    model.fit([train_user_ids, train_song_ids], train_ratings,
              validation_data=([val_user_ids, val_song_ids], val_ratings),
              epochs=10, batch_size=128, callbacks=callbacks)
    model.summary()

    e = model.evaluate([val_user_ids, val_song_ids],
                       val_ratings, batch_size=128)
    print("test loss, test acc, test precision, test recall:", e)

    prediction = model.predict([val_user_ids[:1], val_song_ids[:1]])
    print("Prediction:", prediction)

    # predictions = np.column_stack(
    #     (predictions, val_song_ids.astype(np.object)))
    # predictions = predictions[predictions[:, 0].argsort()[::-1]]
    # print(predictions)
