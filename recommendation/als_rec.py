import implicit
from likes.models import Likes
import pandas as pd
import scipy
from pandas.api.types import CategoricalDtype
from scipy import sparse
from song.models import Song
from likes.models import Likes
import time

class Als:
    model = implicit.als.AlternatingLeastSquares(factors=50)
    qs = list(Likes.objects.all().values('user_id', 'song_id', 'liked'))
    df = pd.DataFrame(list(qs))
    
    users = df["user_id"].unique()
    movies = df["song_id"].unique()
    shape = (len(users), len(movies))

    # Create indices for users and movies
    user_cat = CategoricalDtype(categories=sorted(users), ordered=True)
    movie_cat = CategoricalDtype(categories=sorted(movies), ordered=True)
    user_index = df["user_id"].astype(user_cat).cat.codes
    movie_index = df["song_id"].astype(movie_cat).cat.codes

    # Conversion via COO matrix
    coo = sparse.coo_matrix((df["liked"], (user_index, movie_index)), shape=shape)
    user_item_data = coo.tocsr()
    
    print(user_item_data)
    # train the model on a sparse matrix of user/item/confidence weights
    model.fit(user_item_data)

    # recommend items for a user
    recommendations = model.recommend(12, user_item_data[12])
        
    print("Liked: ")
    lst = []
    for i in range(0, len(user_index)):
        if i == 12:
            print(df["user_id"][i])
            id = df["user_id"][i]
            for l in Likes.objects.all():
                if l.user_id == id:
                    s = Song.objects.filter(id=l.song_id).first()
                    lst.append(s.song_name)
    lst.sort()
    print(lst)
    
    print("\n\n")
    print("Recommendations: ")
    for r in recommendations[0]:
        s = Song.objects.filter(pk=r).first()
        print(s.song_name)
        
    # find related items
    related = model.similar_items(12)
    
    num_iterations = 10
    ranks = [8, 10, 12, 14, 16, 18, 20]
    reg_params = [0.001, 0.01, 0.05, 0.1, 0.2]
