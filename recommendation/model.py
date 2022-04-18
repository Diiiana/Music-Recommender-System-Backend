import torch

class NeuMF(torch.nn.Module):
    def __init__(self, config):
        super(NeuMF, self).__init__()

        #mf part
        self.embedding_user_mf = torch.nn.Embedding(num_embeddings=self.num_users, embedding_dim=self.latent_dim_mf)
        self.embedding_item_mf = torch.nn.Embedding(num_embeddings=self.num_items, embedding_dim=self.latent_dim_mf)
        
        #mlp part
        self.embedding_user_mlp = torch.nn.Embedding(num_embeddings=self.num_users, embedding_dim=self.latent_dim_mlp)
        self.embedding_item_mlp = torch.nn.Embedding(num_embeddings=self.num_items, embedding_dim=self.latent_dim_mlp)
        
        self.fc_layers = torch.nn.ModuleList()
        for idx, (in_size, out_size) in enumerate(zip(config['layers'][:-1], config['layers'][1:])):
            self.fc_layers.append(torch.nn.Linear(in_size, out_size))

        self.logits = torch.nn.Linear(in_features=config['layers'][-1] + config['latent_dim_mf']  , out_features=1)
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, user_indices, item_indices, titles):
        user_embedding_mlp = self.embedding_user_mlp(user_indices)
        item_embedding_mlp = self.embedding_item_mlp(item_indices)
        user_embedding_mf = self.embedding_user_mf(user_indices)
        item_embedding_mf = self.embedding_item_mf(item_indices)

        #### mf part
        mf_vector =torch.mul(user_embedding_mf, item_embedding_mf)
        mf_vector = torch.nn.Dropout(self.config.dropout_rate_mf)(mf_vector)

        #### mlp part        
        mlp_vector = torch.cat([user_embedding_mlp, item_embedding_mlp], dim=-1)  # the concat latent vector
        
        for idx, _ in enumerate(range(len(self.fc_layers))):
            mlp_vector = self.fc_layers[idx](mlp_vector)
            mlp_vector = torch.nn.ReLU()(mlp_vector)
        mlp_vector = torch.nn.Dropout(self.config.dropout_rate_mlp)(mlp_vector)

        vector = torch.cat([mlp_vector, mf_vector], dim=-1)
        logits = self.logits(vector)
        output = self.sigmoid(logits)
        return output