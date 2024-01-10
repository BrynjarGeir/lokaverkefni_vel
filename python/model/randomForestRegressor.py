from sklearn.ensemble import RandomForestRegressor
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


df = pd.read_feather('/mnt/d/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

seed = 42
test_size = 0.2
validation_size = 0.2

X, y = df.drop(['_merge', 'stod', 'gust_factor', 'fg'], axis = 1), df['gust_factor']
#X = X.drop(['Landscape_' + str(i) for i in range(70)], axis = 1)

features = list(X.columns)

input_size = X.shape[1]

X, y = X.values, y.values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)


ensemble_size = 10
models = [RandomForestRegressor() for _ in range(ensemble_size)]

for i in range(ensemble_size):
    indices = np.random.choice(len(X_train), size = len(X_train)//ensemble_size, replace = True)
    models[i].fit(X_train[indices], y_train[indices])


y_pred = np.mean([model.predict(X_test) for model in models], axis = 0)

mse = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"The mean absolute error for sequential model is {mse}")
print(f"The r2 score for the squential model is {r2}")
