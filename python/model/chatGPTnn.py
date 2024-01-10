from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import optuna
import pandas as pd
import numpy as np
from tqdm import trange

df = pd.read_feather('/mnt/d/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

test_size = 0.2
seed = 42
num_epochs = 10
batch_size = 64

X, y = df.drop(['_merge', 'f', 'fg', 'stod', 'gust_factor'], axis = 1), df['gust_factor']
X = X.to_numpy()
y = y.to_numpy()

# Assuming X_train, y_train are your training data
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=test_size, random_state=seed)

train_dataset = TensorDataset(torch.Tensor(X_train), torch.Tensor(y_train))
valid_dataset = TensorDataset(torch.Tensor(X_valid), torch.Tensor(y_valid))

train_loader = DataLoader(train_dataset, batch_size = batch_size, shuffle = True)
valid_loader = DataLoader(valid_dataset, batch_size = batch_size, shuffle = True)


class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, X):
        X = self.relu(self.fc1(X))
        X = self.fc2(X)
        return X
    
def objective(trial):
    input_size = X_train.shape[1]
    hidden_size = trial.suggest_int('hidden_size', 32, 256)
    output_size = 1
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-1)

    model = SimpleNN(input_size, hidden_size, output_size)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr = learning_rate)

    for epoch in trange(num_epochs):
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

    model.eval()

    with torch.no_grad():
        valid_loss = 0.0
        for inputs, targets in valid_loader:
            outputs = model(inputs)
            valid_loss += criterion(outputs, targets).item()
    
    return valid_loss

study = optuna.create_study(direction = 'minimize')
study.optimize(objective, n_trials = 10)
params = study.best_params

best_hidden_size = params['hidden_size']
best_learning_rate = params['learning_rate']

final_model = SimpleNN(input_size = X_train.shape[1], hidden_size=best_hidden_size, output_size=1)
criterion = nn.MSELoss()
optimizer = optim.Adam(final_model.parameters(), lr = best_learning_rate)

final_train_loader = DataLoader(train_dataset, batch_size = batch_size, shuffle = True)
final_valid_loader = DataLoader(valid_dataset, batch_size = batch_size, shuffle = True)

for epoch in trange(num_epochs):
    for inputs, targets in final_train_loader:
        optimizer.zero_grad()
        outputs = final_model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

final_model.eval()
with torch.no_grad():
    predictions = []
    true_labels = []
    for inputs, targets in final_valid_loader:
        outputs = final_model(inputs)
        predictions.extend(outputs.numpy())
        true_labels.extend(targets.numpy())

mse = mean_squared_error(true_labels, predictions)
r2 = r2_score(true_labels, predictions)

print(f"Mean Squared Error (MSE): {mse}")
print(f"R-squared (R2): {r2}")