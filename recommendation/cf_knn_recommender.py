# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.sparse import csr_matrix
# from surprise import Dataset, Reader
# from surprise.model_selection import train_test_split
# from recommeders.knn_recommender import Recommender
# from collections import defaultdict
# from likes.models import Likes


# class RecommenderCFMatrix:

#     # def get_top_n(predictions, n=10):
#     #     top_n = defaultdict(list)
#     #     for uid, iid, true_r, est, _ in predictions:
#     #         top_n[uid].append((iid, est))

#     #     for uid, user_ratings in top_n.items():
#     #         user_ratings.sort(key=lambda x: x[1], reverse=True)
#     #         top_n[uid] = user_ratings[:n]

#     #     return top_n


#     # qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
#     # df = pd.DataFrame(list(qs))
    
#     # reader = Reader(rating_scale=(0, 1))
    
#     # data = Dataset.load_from_df(df, reader)
#     # trainset, testset = train_test_split(data, test_size=.25)
#     # algo = SVD()
#     # algo.fit(trainset)

#     # predictions = algo.test(testset)

#     # top_n = get_top_n(predictions, n=10)

#     # print(top_n)
#     # for uid, user_ratings in top_n.items():
#     #     print(uid, [iid for (iid, _) in user_ratings])
#     #     break
    

#     # qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
#     # df = pd.DataFrame(list(qs))

#     # mat_songs_features = csr_matrix(df_songs_features.values)