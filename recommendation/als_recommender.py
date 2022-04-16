import pandas as pd
import numpy as np
import scipy.sparse as sparse
from sklearn import metrics
import implicit
from likes.models import Likes
from sklearn.model_selection import train_test_split

class AlsRecommender:
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    data = pd.DataFrame(list(qs))
    
    data['user_id'] = data['user_id'].astype("category")
    data['song_id'] = data['song_id'].astype("category")

    data['user_id'] = data['user_id'].cat.codes
    data['song_id'] = data['song_id'].cat.codes

    sparse_item_user = sparse.csr_matrix((data['liked'].astype(float), (data['song_id'], data['user_id'])))
    sparse_user_item = sparse.csr_matrix((data['liked'].astype(float), (data['user_id'], data['song_id'])))
    
    matrix_size = sparse_user_item.shape[0]*sparse_user_item.shape[1]
    num_purchases = len(sparse_user_item.nonzero()[0])
    sparsity = 100*(1 - (num_purchases/matrix_size))
    print('sparsity: ', sparsity)
    
    product_train, product_test = train_test_split(sparse_item_user, test_size=0.20, random_state=42)
    
    model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=40)
    alpha_val = 15
    data_conf = (product_train * alpha_val).astype('double')
    model.fit(data_conf)
    
    item_vecs = model.item_factors
    user_vecs = model.user_factors
    
    print('Shape of Song vector matrix : ', item_vecs.shape)
    print('Shape of User vector matrix : ', user_vecs.shape)

    similar = model.similar_items(19, 5)
    print(similar)
    d = data[data['user_id'] == 19].head(5)
