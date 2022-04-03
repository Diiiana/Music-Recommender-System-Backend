import pandas as pd
from likes.models import Likes
from surprise import Dataset
import torch
import numpy as np
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.cluster import KMeans
from song.models import Song

class MatrixFactorization2(torch.nn.Module):
    def __init__(self, n_users, n_items, n_factors=20):
        super().__init__()
        self.user_factors = torch.nn.Embedding(n_users, n_factors)
        self.item_factors = torch.nn.Embedding(n_items, n_factors)
        self.user_factors.weight.data.uniform_(0, 0.05)
        self.item_factors.weight.data.uniform_(0, 0.05)
        
    def forward(self, data):
        users, items = data[:,0], data[:,1]
        return (self.user_factors(users)*self.item_factors(items)).sum(1)

    def predict(self, user, item):
        return self.forward(user, item)


class Loader(Dataset):
    def __init__(self):
        qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
        df = pd.DataFrame(list(qs))

        count = 0
        user_ids = []
        for el in df['user_id']:
            if el in user_ids:
                df = df.replace(el, user_ids.index(el))
            else:
                df = df.replace(el, count)
                user_ids.append(el)
                count += 1

        self.ratings = df.copy()
        users = df['user_id'].unique()
        songs = df['song_id'].unique()
        
        self.userid2idx = {o:i for i,o in enumerate(users)}
        self.songid2idx = {o:i for i,o in enumerate(songs)}
        
        self.idx2userid = {i:o for o,i in self.userid2idx.items()}
        self.idx2songid = {i:o for o,i in self.songid2idx.items()}
        
        self.ratings['liked'] = df['song_id'].apply(lambda x: self.songid2idx[x])
        self.ratings['song_id'] = df['user_id'].apply(lambda x: self.userid2idx[x])
        
        self.x = self.ratings.drop(['liked'], axis=1).values
        self.y = self.ratings['liked'].values

        self.x, self.y = torch.tensor(self.x), torch.tensor(self.y) # Transforms the data to tensors (ready for torch models.)

    def __getitem__(self, index):
        return (self.x[index], self.y[index])

    def __len__(self):
        return len(self.ratings)
    
class MatrixFactorization(torch.nn.Module):
    qs = list(Likes.objects.all().values('song_id', 'user_id', 'liked'))
    df = pd.DataFrame(list(qs))
    
    count = 0
    user_ids = []
    for el in df['user_id']:
            if el in user_ids:
                df = df.replace(el, user_ids.index(el))
            else:
                df = df.replace(el, count)
                user_ids.append(el)
                count += 1
    
    n_users = len(df['user_id'].unique())
    n_items = len(df['song_id'].unique())
    
    print(n_users, n_items)

    num_epochs = 128
    print(torch.version.cuda)
    cuda = torch.cuda.is_available()
    print("Is running on GPU:", cuda)

    model = MatrixFactorization2(n_users, n_items, n_factors=8)
    
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(name, param.data)
    if cuda:
        model = model.cuda()

    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    train_set = Loader()
    train_loader = DataLoader(train_set, 128, shuffle=True)

    for it in tqdm(range(num_epochs)):
        losses = []
        for x, y in train_loader:
            if cuda:
                x, y = x.cuda(), y.cuda()
                optimizer.zero_grad()
                outputs = model(x)
                loss = loss_fn(outputs.squeeze(), y.type(torch.float32))
                losses.append(loss.item())
                loss.backward()
                optimizer.step()
        print("iter #{}".format(it), "Loss:", sum(losses) / len(losses))
        
    c = 0
    uw = 0
    iw = 0 
    for name, param in model.named_parameters():
        if param.requires_grad:
            # print(name, param.data)
            if c == 0:
                uw = param.data
                c +=1
            else:
                iw = param.data
                # print('param_data', param.data)
    trained_song_embeddings = model.item_factors.weight.data.cpu().numpy()
    len(trained_song_embeddings)
    kmeans = KMeans(n_clusters=10, random_state=0).fit(trained_song_embeddings)
    
    for cluster in range(10):
        print("Cluster #{}".format(cluster))
        song_values = []
        for sid in np.where(kmeans.labels_ == cluster)[0]:
            id = train_set.idx2songid[sid]
            rat_count = df.loc[df['song_id']==id].count()[0]
            song_values.append((sid, rat_count))
        for s in sorted(song_values, key=lambda tup: tup[1], reverse=True)[:10]:
            print(",", s[0])