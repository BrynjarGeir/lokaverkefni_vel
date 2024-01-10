import torch.nn as nn, torch.optim as optim
import torch
from torch import tensor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
import copy
import tqdm
from sklearn.metrics import r2_score

df = pd.read_feather('/mnt/d/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

X, y = df.drop(['_merge', 'f', 'fg', 'stod', 'gust_factor'], axis = 1), df['gust_factor']

X, y = X.to_numpy(), y.to_numpy()

test_size = 0.2
seed = 42

input_size = X.shape[1]

model = nn.Sequential(
    nn.Linear(input_size, 24),
    nn.ReLU(),
    nn.Linear(24, 12),
    nn.ReLU(),
    nn.Linear(12, 6),
    nn.ReLU(),
    nn.Linear(6, 1)
)

loss_fn = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr = 1e-4)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).reshape(-1, 1)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32).reshape(-1, 1)

n_epochs = 100   # number of epochs to run
batch_size = 10  # size of each batch
batch_start = torch.arange(0, len(X_train), batch_size)
 
# Hold the best model
best_mse = np.inf   # init to infinity
best_weights = None
history = []
 
# training loop
for epoch in range(n_epochs):
    model.train()
    with tqdm.tqdm(batch_start, unit="batch", mininterval=0, disable=True) as bar:
        bar.set_description(f"Epoch {epoch}")
        for start in bar:
            # take a batch
            X_batch = X_train[start:start+batch_size]
            y_batch = y_train[start:start+batch_size]
            # forward pass
            y_pred = model(X_batch)
            loss = loss_fn(y_pred, y_batch)
            # backward pass
            optimizer.zero_grad()
            loss.backward()
            # update weights
            optimizer.step()
            # print progress
            bar.set_postfix(mse=float(loss))
    # evaluate accuracy at end of each epoch
    model.eval()
    y_pred = model(X_test)
    mse = loss_fn(y_pred, y_test)
    mse = float(mse)
    history.append(mse)
    if mse < best_mse:
        best_mse = mse
        best_weights = copy.deepcopy(model.state_dict())
 
# restore model and return best accuracy
model.load_state_dict(best_weights)

y_pred = model(X_test)

y_test, y_pred = y_test.detach().numpy(), y_pred.detach().numpy()
r2 = r2_score(y_test, y_pred)

print("MSE: %.2f" % best_mse)
print("RMSE: %.2f" % np.sqrt(best_mse))
print(f"The r2 score is {r2}")
plt.plot(history)
plt.show()