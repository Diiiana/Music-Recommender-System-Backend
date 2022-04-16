import pandas as pd
import numpy as np

from lightfm.data import Dataset
from lightfm.evaluation import auc_score, precision_at_k, recall_at_k
from lightfm import LightFM, cross_validation

from likes.models import Likes
from song.models import Song

class LightfmRecommender:

    def create_features(dataframe, features_name, id_col_name):
        features = dataframe[features_name].apply(
            lambda x: ','.join(x.map(str)), axis=1)
        features = features.str.split(',')
        features = list(zip(dataframe[id_col_name], features))
        return features

    def generate_feature_list(dataframe, features_name):
        features = dataframe[features_name].apply(
            lambda x: ','.join(x.map(str)), axis=1)
        features = features.str.split(',')
        features = features.apply(pd.Series).stack().reset_index(drop=True)
        return features


    def calculate_auc_score(lightfm_model, interactions_matrix, 
                            question_features, professional_features): 
        score = auc_score( 
            lightfm_model, interactions_matrix, 
            item_features=question_features, 
            user_features=professional_features, 
            num_threads=4).mean()
        return score
    
    
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df_users = pd.DataFrame(list(qs))

    d = list(Likes.objects.values_list('song_id'))
    d = [i for sub in d for i in sub]
    
    qs_2 = list(Song.objects.all().filter(id__in=d).values('song_id', 'tag', 'instrumentalness', 'valence', 'energy', 'danceability', 'acousticness', 'speechiness'))
    df_songs = pd.DataFrame(qs_2)
    
    n_users = df_users['user_id'].unique().shape[0]
    n_items = df_songs['song_id'].unique().shape[0]
    print("users=", n_users, "| items= ", n_items, "\n")

    song_weights = (df_users['song_id'].value_counts()) / df_users['song_id'].value_counts().max()
    print(song_weights)
    z1 = song_weights.to_dict()

    df_users['weight'] = df_users['song_id'].map(z1) 

    count = 0
    user_ids = []
    final_users = []
    for el in df_users['user_id']:
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
    
    songs_features_list = generate_feature_list(df_songs, ['tag', 'instrumentalness', 'valence', 'energy', 'danceability', 'acousticness', 'speechiness'])
    users_features_list = generate_feature_list(df_users, ['user_id'])

    df_songs['song_features'] = create_features(df_songs, ['tag', 'instrumentalness', 'valence', 'energy', 'danceability', 'acousticness', 'speechiness'], 'song_id')
    df_users['user_features'] = create_features(df_users, ['user_id'], 'user_id')
    
    dataset = Dataset()
    dataset.fit(
        set(df_users['user_id']),
        set(df_songs['song_id']),
        item_features=songs_features_list, 
        user_features=users_features_list)
    
    df_merged['song_user_id_tuple'] = list(zip(df_merged['user_id'], df_merged['song_id'], df_merged['weight']))
    interactions, weights = dataset.build_interactions(df_merged['song_user_id_tuple'])
            
    song_features = dataset.build_item_features(df_songs['song_features'])
    user_features = dataset.build_user_features(df_users['user_features'])
    
    train_interactions, test_interactions = cross_validation.random_train_test_split(interactions, test_percentage=0.3, random_state=np.random.RandomState(3))
    train_weights, test_weights = cross_validation.random_train_test_split(weights, test_percentage=0.3, random_state=np.random.RandomState(3))
    
    model = LightFM(
    no_components=150,
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

    user_ids = [2]
    for user in user_ids:
        scores = model.predict(
            user,
            df_songs['song_id'].values.tolist(),
            item_features=song_features,
            user_features=user_features)
        
        v = (np.array(scores)).tolist()
        df_2 = pd.DataFrame({'scores': v})
        df_songs = df_songs.join(df_2)
        df_songs = df_songs.sort_values(by='scores', ascending=False)[:8]
        acc_train = calculate_auc_score(model, train_interactions, song_features, user_features)
        acc_test = calculate_auc_score(model, test_interactions, song_features, user_features)
         
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
        