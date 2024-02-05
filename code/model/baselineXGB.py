from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
import pandas as pd

df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

y = df['gust_factor']
X = df.drop(['_merge', 'f', 'fg', 'stod', 'gust_factor'], axis = 1)

test_size = 0.2
seed = 42

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

model = XGBRegressor()

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

#y_pred = model.predict(X_test)
y_pred = final_model.predict(X_test)


mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R2 score is: {r2}')