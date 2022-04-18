# import numpy as np
# import pandas as pd
# from likes.models import Likes
# from sklearn.preprocessing import LabelEncoder
# from keras.models import Model
# from keras.layers import Input, Dense, Embedding, concatenate, Flatten, Activation, Add, Dropout, Multiply
# from tensorflow.keras.optimizers import Adam
# from keras.callbacks import EarlyStopping


# class BPDRecommender:
    
#     @staticmethod
#     def dcg_at_k(r, k):
#         '''
#         Compute DCG
#         args:
#             r: np.array, to be evaluated
#             k: int, number of entries to be considered
        
#         returns:
#             dcg: float, computed dcg
            
#         '''
#         r = r[:k]
#         dcg = np.sum(r / np.log2(np.arange(2, len(r) + 2)))
#         return dcg

#     @staticmethod
#     def ndcg_at_k(r, k, method=0):
#         '''
#         Compute NDCG
#         args:
#             r: np.array, to be evaluated
#             k: int, number of entries to be considered
        
#         returns:
#             dcg: float, computed ndcg
            
#         '''
#         dcg_max = BPDRecommender.dcg_at_k(sorted(r, reverse=True), k)

#         return BPDRecommender.dcg_at_k(r, k) / dcg_max
    
#     # compute average ndcg for all users
#     def evaluate_prediction(predictions, val_user_ids, val_song_ids, val_likes):
#         '''
#         Return the average ndcg for each users
#         args:
#             predictions: np.array user-item predictions
#         returns:
#             ndcg: float, computed NDCG
#         '''
#         ndcgs = []
#         # iterate
#         for target_user in np.unique(val_user_ids):
#             # get movie ids and ratings associated with the target user.
#             target_val_movie_ids = val_song_ids[val_user_ids == target_user] 
#             target_val_ratings = val_likes[val_user_ids == target_user] 
            
#             # compute ndcg for this user
#             ndcg = BPDRecommender.ndcg_at_k(target_val_ratings[np.argsort(-predictions[val_user_ids == target_user])], k=30)
#             ndcgs.append(ndcg)
#     #         print(np.argsort(-predictions[val_user_ids == target_user]))
#         ndcg = np.mean(ndcgs)
#         return ndcg



#     def get_mf_model():
#         # user input
#         user_inp = Input((1,))
#         user_hidden = Embedding(input_dim=69, output_dim=50)(user_inp)
#         user_hidden = Flatten()(user_hidden)
        
#         # item input
#         item_inp = Input((1,))
#         item_hidden = Embedding(input_dim=5018, output_dim=50)(item_inp)
#         item_hidden = Flatten()(item_hidden)
        
#         # element-wise multiplication
#         hidden = Multiply()([user_hidden, item_hidden])
        
#         output = Dense(1, activation='sigmoid')(hidden)
        
#         model = Model(inputs=[user_inp, item_inp], outputs=output)
#         model.compile(loss='mse', optimizer=Adam(lr=0.005))
#         return model
    
    
#     qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
#     df = pd.DataFrame(list(qs))

#     user_encoder = LabelEncoder()
#     movie_encoder = LabelEncoder()

#     user_ids = user_encoder.fit_transform(df.user_id)
#     song_ids = movie_encoder.fit_transform(df.song_id)
    
#     num_train = int(len(user_ids) * 0.8)
#     train_user_ids = user_ids[:num_train]
#     train_movie_ids = song_ids[:num_train]
#     train_ratings = df.liked.values[:num_train]
#     val_user_ids = user_ids[num_train:]
#     val_song_ids = song_ids[num_train:]
#     val_ratings = df.liked.values[num_train:]
    
#     num_users= user_ids.max()+1
#     num_songs = song_ids.max() + 1
    
#     print(num_users, num_songs)
    
#     model = get_mf_model()
#     model.summary()
    
#     # early stopping wait for 1 epoch
#     callbacks = [EarlyStopping(patience=1)]

#     # train for 50 epochs
#     model.fit([train_user_ids, train_movie_ids], train_ratings, 
#               validation_data=([val_user_ids, val_song_ids], val_ratings), epochs=50, batch_size=128, callbacks=callbacks)
#     # prediction & evalutation
#     predictions = model.predict([val_user_ids, val_song_ids])
#     print(predictions)
#     print(evaluate_prediction(predictions[:,0], val_user_ids, val_song_ids, val_ratings))