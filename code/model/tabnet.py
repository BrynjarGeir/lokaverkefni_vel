from pytorch_tabnet.tab_model import TabNetRegressor
from tensorflow.keras.callbacks import Callback

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer

import pandas as pd, numpy as np, tensorflow as tf, torch

class CustomEarlyStopping:
    def __init__(self, patience, threshold):
        self.patience = patience
        self.threshold = threshold
        self.counter = 0
        self.best_metric = float('inf')

    def __call__(self, epoch, logs):
        current_metric = logs['val_mean_absolute_percentage_error']
        
        if current_metric > self.threshold:
            self.counter += 1
        else:
            self.counter = 0
            self.best_metric = current_metric

        if self.counter >= self.patience:
            print(f"Early stopping due to threshold {self.threshold} reached.")
            self.model.stop_training = True

class MeanAbsolutePercentageError(torch.nn.Module):
    def __init__(self):
        super(MeanAbsolutePercentageError, self).__init__()
    def forward(self, y_true, y_pred):
        absolute_percentage_error = torch.abs((y_true - y_pred) / y_true)
        return torch.mean(absolute_percentage_error) * 100.0

def mean_absolute_percentage_error(y_true, y_pred):
    y_true = torch.tensor(y_true)
    y_pred = torch.tensor(y_pred)
    return torch.mean(torch.abs((y_true-y_pred) / y_true)) * 100.0

mape_scorer = make_scorer(mean_absolute_percentage_error, greater_is_better=False)
mape_metric = MeanAbsolutePercentageError()

#df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/merged-test1month-26-2-24.feather')
df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')
df = df[df.f < df.fg]

y = df['fg']/df['f']
X = df.drop(['_merge', 'gust_factor', 'f', 'fg', 'd', 'stod'] + [f'Landscape_{i}' for i in range(70)], axis = 1)

# Changing the type of X,y so as to work with Tensorflow
X, y = X.values.astype(np.float32), y.values.astype(np.float32)

scaler = StandardScaler()

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)

y_train, y_test = y_train.reshape(-1, 1), y_test.reshape(-1, 1)

param_dist = {
    'n_d': [8, 64],
    'n_a': [8, 64],
    'n_steps': [3, 5],
    'gamma': [1.0, 1.8],
    'lambda_sparse': [1e-3],
}

custom_early_stopping = CustomEarlyStopping(patience = 5, threshold = 100)
model = TabNetRegressor()

random_search = RandomizedSearchCV(model, param_distributions=param_dist, scoring = mape_scorer, cv = 3, n_iter = 5)
history = random_search.fit(X_train, y_train, loss_fn = mape_metric)

best_model = random_search.best_estimator_
best_param = random_search.best_params_

mape = best_model.evaluate(X_test, y_test)
print(f'Test mape: {mape}')