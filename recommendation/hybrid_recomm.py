from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import pandas as pd
from likes.models import Likes
import numpy as np
from song.models import Song


class HybridRecomm:
    qs = list(Likes.objects.all().values('song_id', 'user_int_id', 'liked'))
    df = pd.DataFrame(list(qs))

    features = pd.DataFrame(list(
        list(Song.objects.filter(id__in=list(df.song_id.unique())).values('id', 'energy', 'valence'))))
    print(len(features))
    feat = 2

    df_merged = features.merge(df, left_on='id', right_on='song_id')
    n_users, n_songs = len(df.user_int_id.unique()), len(df.song_id.unique())

    embeddings_size = 50
    usr, prd = len(df.user_int_id.unique()), len(df.song_id.unique())

    xusers_in = tf.keras.layers.Input(name="xusers_in", shape=(1,))
    xproducts_in = tf.keras.layers.Input(name="xproducts_in", shape=(1,))

    cf_xusers_emb = tf.keras.layers.Embedding(
        name="cf_xusers_emb", input_dim=usr, output_dim=embeddings_size)(xusers_in)
    cf_xusers = tf.keras.layers.Reshape(
        name='cf_xusers', target_shape=(embeddings_size,))(cf_xusers_emb)

    cf_xproducts_emb = tf.keras.layers.Embedding(
        name="cf_xproducts_emb", input_dim=prd, output_dim=embeddings_size)(xproducts_in)
    cf_xproducts = tf.keras.layers.Reshape(
        name='cf_xproducts', target_shape=(embeddings_size,))(cf_xproducts_emb)

    cf_xx = tf.keras.layers.Dot(name='cf_xx', normalize=True, axes=1)([
        cf_xusers, cf_xproducts])

    nn_xusers_emb = tf.keras.layers.Embedding(
        name="nn_xusers_emb", input_dim=usr, output_dim=embeddings_size)(xusers_in)
    nn_xusers = tf.keras.layers.Reshape(
        name='nn_xusers', target_shape=(embeddings_size,))(nn_xusers_emb)

    nn_xproducts_emb = tf.keras.layers.Embedding(
        name="nn_xproducts_emb", input_dim=prd, output_dim=embeddings_size)(xproducts_in)
    nn_xproducts = tf.keras.layers.Reshape(
        name='nn_xproducts', target_shape=(embeddings_size,))(nn_xproducts_emb)

    nn_xx = tf.keras.layers.Concatenate()([nn_xusers, nn_xproducts])
    nn_xx = tf.keras.layers.Dense(name="nn_xx", units=int(
        embeddings_size/2), activation='relu')(nn_xx)

    ######################### CONTENT BASED ############################
    features_in = tf.keras.layers.Input(name="features_in", shape=(feat,))
    features_x = tf.keras.layers.Dense(
        name="features_x", units=feat, activation='relu')(features_in)

    y_out = tf.keras.layers.Concatenate()([cf_xx, nn_xx, features_x])
    y_out = tf.keras.layers.Dense(
        name="y_out", units=1, activation='linear')(y_out)

    model = tf.keras.models.Model(
        inputs=[xusers_in, xproducts_in, features_in], outputs=y_out, name="Hybrid_Model")
    model.compile(optimizer='adam', loss='mean_absolute_error',
                  metrics=['mean_absolute_percentage_error', 'binary_accuracy'])

    model.summary()
    tf.keras.utils.plot_model(
        model, to_file='hybrid_model.png', show_shapes=True)

    train, test = train_test_split(df_merged, test_size=0.3)
    features = df_merged.drop(
        ["id", "user_int_id", "liked", "song_id"], axis=1).columns
    training = model.fit(x=[train["user_int_id"], train["song_id"], train[features]], y=train["liked"],
                         epochs=10, batch_size=128, shuffle=True, verbose=1, validation_split=0.3)

    e = model.evaluate(x=[test["user_int_id"], test["song_id"],
                       test[features]], y=test["liked"], batch_size=128)
    print("test loss, test acc, test precision, test recall:", e)

    print(model.predict([test["user_int_id"],
          test["song_id"], test[features]]))