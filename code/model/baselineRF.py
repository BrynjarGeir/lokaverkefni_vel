from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

y = df['gust_factor']
X = df.drop(['_merge', 'f', 'fg', 'stod', 'gust_factor'], axis = 1)

seed = 42
test_size = 0.2

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

model = RandomForestRegressor()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R2 score is: {r2}')