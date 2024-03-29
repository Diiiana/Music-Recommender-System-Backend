from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import pandas as pd
from likes.models import Likes
from matplotlib import pyplot as plt


class NcfRecommender:
    qs = list(Likes.objects.all().values('song_id', 'user_int_id', 'liked'))
    df = pd.DataFrame(list(qs))

    train, test = train_test_split(df, test_size=0.3, stratify=df.liked)
    X_resampled, y_resampled = SMOTE(sampling_strategy='minority', k_neighbors=2).fit_resample(
        train[['user_int_id', 'song_id']], train['liked'])

    user_encoder = LabelEncoder()
    song_encoder = LabelEncoder()

    train_user_ids = user_encoder.fit_transform(X_resampled.user_int_id)
    train_song_ids = song_encoder.fit_transform(X_resampled.song_id)
    train_ratings = y_resampled

    user_encoder_test = LabelEncoder()
    song_encoder_test = LabelEncoder()

    val_user_ids = user_encoder_test.fit_transform(test.user_int_id)
    val_song_ids = song_encoder_test.fit_transform(test.song_id)
    val_ratings = test.liked

    n_users, n_songs = len(df.user_int_id.unique()), len(df.song_id.unique())

    song_input = tf.keras.layers.Input(shape=[1], name='Song')
    song_vec = tf.keras.layers.Flatten(name='FlattenSongs')(song_input)

    user_input = tf.keras.layers.Input(shape=[1], name='User')
    user_vec = tf.keras.layers.Flatten(name='FlattenUsers')(user_input)

    concat = tf.keras.layers.concatenate([song_vec, user_vec])
    mlp = tf.keras.layers.BatchNormalization()(concat)
    mlp = tf.keras.layers.Dropout(0.2)(mlp)
    mlp = tf.keras.layers.Dense(32, activation='relu',
                                kernel_initializer='he_uniform')(mlp)
    mlp = tf.keras.layers.Dense(16, activation='relu',
                                kernel_initializer='he_uniform')(mlp)
    mlp = tf.keras.layers.Dense(1, activation='sigmoid', kernel_initializer='glorot_normal',
                                name="output")(mlp)

    model = tf.keras.Model(inputs=[user_input, song_input], outputs=[mlp])
    model.compile(optimizer='adadelta', loss='binary_crossentropy', metrics=[
                  'binary_accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall(), tf.keras.metrics.RootMeanSquaredError()])

    callbacks = [tf.keras.callbacks.EarlyStopping(patience=1)]

    num_users = val_user_ids.max() + 1
    num_songs = val_song_ids.max() + 1

    history = model.fit([train_user_ids, train_song_ids], train_ratings,
              validation_data=([val_user_ids, val_song_ids], val_ratings),
              epochs=30, batch_size=128, callbacks=callbacks)
    model.summary()
    
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Evaluare Loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()

    e = model.evaluate([val_user_ids, val_song_ids],
                       val_ratings, batch_size=128)

    model.save('neural_model')
