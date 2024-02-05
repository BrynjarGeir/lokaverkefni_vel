# Asked ChatGPT for a baseline and this is it
# The parameters are the below along with 70 landscape parameters with 
    #Index(['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150',
    #       't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250',
    #       'wdir500', 't500', 'ws500', 'pres500', 'f', 'fg', 'gust_factor'],
    #      dtype='object')

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combinedWTargetAndDesc-4-1-24.feather')
y = df['gust_factor']
X = df.drop(['_merge', 'f', 'fg', 'stod', 'gust_factor'], axis = 1)

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a linear regression model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'Mean Squared Error: {mse}')
print(f'R2 score is: {r2}')
