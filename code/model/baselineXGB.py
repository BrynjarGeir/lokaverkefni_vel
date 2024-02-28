from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import pandas as pd, tensorflow as tf, numpy as np

def mean_absolute_percentage_error(y_true, y_pred):
    return tf.reduce_mean(tf.abs((y_true-y_pred) / y_true)) * 100.0

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

model = XGBRegressor(eval_metric = mean_absolute_percentage_error)

param_grid = {
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [3, 4, 5],
    'n_estimators': [50, 100, 200],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0]
}

gridSearch = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring = 'neg_mean_squared_error',
    cv = 5,
    n_jobs = -1
)

#model.fit(X_train, y_train)

gridSearch.fit(X_train, y_train)

best_params = gridSearch.best_params_

final_model = XGBRegressor(**best_params)
final_model.fit(X_train, y_train)

#y_predict = model.predict(X_test)
y_predict = final_model.predict(X_test)


# Evaluate the model
mape = mean_absolute_percentage_error(y_test, y_predict)

print(y_predict[:5], y_test[:5])

print(f'Test MAPE: {mape}%')