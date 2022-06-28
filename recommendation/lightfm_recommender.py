import pandas as pd
import numpy as np

from lightfm.data import Dataset
from lightfm.evaluation import auc_score, precision_at_k, recall_at_k
from lightfm import LightFM, cross_validation

from likes.models import Likes
from song.models import Song

class LightfmRecommender:

    def get_data(dataset, info):
        values = dataset[info].apply(
            lambda x: ','.join(x.map(str)), axis=1)
        values = values.str.split(',')
        return values
    
    qs = list(Likes.objects.all().values('song_id', 'user_int_id', 'liked'))
    df_users = pd.DataFrame(list(qs))
    
    d = list(Likes.objects.values_list('song_id'))
    d = [i for sub in d for i in sub]
    
    qs_2 = list(Song.objects.all().filter(id__in=d).values('song_id', 'tag', 'instrumentalness', 'valence', 'energy', 'danceability', 'acousticness', 'speechiness'))
    df_songs = pd.DataFrame(qs_2)
    
    n_users = df_users['user_int_id'].unique().shape[0]
    n_items = df_songs['song_id'].unique().shape[0]

    song_weights = (df_users['song_id'].value_counts()) / df_users['song_id'].value_counts().max()
    song_data = song_weights.to_dict()

    df_users['weight'] = df_users['song_id'].map(song_data) 
    
    count = 0
    user_ids = []
    final_users = []
    for el in df_users['user_int_id']:
            if el in user_ids:
                df_users = df_users.replace(el, user_ids.index(el))
                final_users.append((el, user_ids.index(el)))
            else:
                df_users = df_users.replace(el, count)
                final_users.append((el, count))
                user_ids.append(el)
                count += 1
    count = 0
    song_ids = []
    for el in df_songs['song_id']:
            if el in user_ids:
                df_songs = df_songs.replace(el, song_ids.index(el))
                df_users = df_users.replace(el, song_ids.index(el))
            else:
                df_songs = df_songs.replace(el, count)
                df_users = df_users.replace(el, count)
                song_ids.append(el)
                count += 1
    df_merged = df_users.merge(df_songs, how='inner', left_on='song_id', right_on='song_id')
    
    song_info = get_data(df_songs, ['tag', 'instrumentalness', 'valence', 'energy', 'danceability', 'acousticness', 'speechiness'])
    songs_features_list = song_info.apply(pd.Series).stack().reset_index(drop=True)
    
    user_info = get_data(df_users, ['user_int_id'])
    users_features_list = user_info.apply(pd.Series).stack().reset_index(drop=True)

    df_songs['song_features'] = list(zip(df_songs['song_id'], song_info))
    df_users['user_features'] = list(zip(df_users['user_int_id'], user_info))
    
    df_merged['song_user_id_tuple'] = list(zip(df_merged['user_int_id'], df_merged['song_id'], df_merged['weight']))
    
    dataset = Dataset()
    dataset.fit(
        set(df_users['user_int_id']),
        set(df_songs['song_id']),
        item_features=songs_features_list, 
        user_features=users_features_list)
    
    interactions, weights = dataset.build_interactions(df_merged['song_user_id_tuple'])
            
    song_features = dataset.build_item_features(df_songs['song_features'])
    user_features = dataset.build_user_features(df_users['user_features'])
    
    train_interactions, test_interactions = cross_validation.random_train_test_split(interactions, test_percentage=0.3, random_state=np.random.RandomState(3))
    train_weights, test_weights = cross_validation.random_train_test_split(weights, test_percentage=0.3, random_state=np.random.RandomState(3))
    
    model = LightFM(
    no_components=10,
    learning_rate=0.05,
    loss='warp',
    random_state=3)
    
    model.fit(
        interactions=train_interactions,
        item_features=song_features.tocsr(),
        user_features=user_features.tocsr(), 
        sample_weight=train_weights,
        epochs=30, 
        num_threads=4, 
        verbose=True)
    
    scores = model.predict(
            2,
            df_songs['song_id'].values.tolist(),
            item_features=song_features,
            user_features=user_features)
        
    acc_train = auc_score( 
            model, train_interactions, 
            item_features=song_features, 
            user_features=user_features, 
            num_threads=4).mean()
    
    acc_test = auc_score( 
            model, test_interactions, 
            item_features=song_features, 
            user_features=user_features, 
            num_threads=4).mean()
         
    precision_train = precision_at_k(model, train_interactions,
                               user_features=user_features,
                               item_features=song_features,
                               num_threads=4).mean()
        
    precision_test = precision_at_k(model, test_interactions,
                               user_features=user_features,
                               item_features=song_features,
                               num_threads=4).mean()
        
    recall_train = recall_at_k(model, train_interactions,
                            user_features=user_features,
                            item_features=song_features).mean()
    recall_test = recall_at_k(model, test_interactions,
                            user_features=user_features,
                            item_features=song_features).mean()
    
    print("\n\nPrecision is: train", precision_train, ", test: ", precision_test)
    print("Recall is: train", recall_train, ", test: ", recall_test)
    print("Accuracy is: train", acc_train, ", test: ", acc_test)
        