from collections import defaultdict
from likes.models import Likes
from surprise import SVD, NormalPredictor, Dataset, Reader
from surprise.model_selection import cross_validate, GridSearchCV, KFold
import pandas as pd
from surprise.accuracy import fcp
from scipy.sparse import csr_matrix
# importing product
from itertools import product


class FinalClass:
    def precision_recall_at_k(predictions, k=10, threshold=3.5):
        user_est_true = defaultdict(list)
        for uid, _, true_r, est, _ in predictions:
            user_est_true[uid].append((est, true_r))

        precisions = dict()
        recalls = dict()
        for uid, user_ratings in user_est_true.items():
            # Sort user ratings by estimated value
            user_ratings.sort(key=lambda x: x[0], reverse=True)
            # Number of relevant items
            n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
            # Number of recommended items in top k
            n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])
            # Number of relevant and recommended items in top k
            n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                                for (est, true_r) in user_ratings[:k])
            # Precision@K: Proportion of recommended items that are relevant
            # When n_rec_k is 0, Precision is undefined. We here set it to 0.
            # print(n_rec_k)
            precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
            # Recall@K: Proportion of relevant items that are recommended
            # When n_rel is 0, Recall is undefined. We here set it to 0.
            # print(n_rel)

            recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

        return precisions, recalls

    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))

    df_songs_features = df.pivot(index='song_id', columns='user_id', values='liked').fillna(0)
    print(df_songs_features)
    df_songs_features = df_songs_features.groupby('song_id')
        
    df_users = df['user_id'].unique()
    df_songs = df['song_id'].unique()
    
    print(len(df_users), len(df_songs))
    
    likes = df[['user_id', 'song_id']]
    df_likes = likes.reset_index()
    likes_values = []
    for index, row in df_likes.iterrows():
        likes_values.append((row['user_id'], row['song_id']))
    
    count = 0
    data = []
    for user in df_users:
        # count += 1
        for song in df_songs[:2000]:
            t = (user, song)
            if t in likes_values:
                data.append([user, song, 1])
            else:
                data.append([user, song, 0])
        if count > 200:
            break
    
    
    final_df = pd.DataFrame(df_likes, columns = ['user_id', 'song_id', 'liked'])
    print(final_df, len(final_df))
    
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(final_df[['user_id', 'song_id', 'liked']], reader)

    kf = KFold(n_splits=2)
    algo = SVD()
    
    param_grid = {'n_epochs': [5], 'lr_all': [0.002], 'reg_all': [0.6]}
    
    gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)
    gs.fit(data)
    print(gs.best_score['rmse'])

    cross_validate(NormalPredictor(), data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

    for trainset, testset in kf.split(data):
        algo.fit(trainset)
        predictions = algo.test(testset)
        # fcp(predictions)
        precisions, recalls = precision_recall_at_k(predictions, k=2, threshold=1)

        print(sum(prec for prec in precisions.values()) / len(precisions))
        print(sum(rec for rec in recalls.values()) / len(recalls))