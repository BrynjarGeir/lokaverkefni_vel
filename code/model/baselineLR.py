# Asked ChatGPT for a baseline and this is it
# The parameters are the below along with 70 landscape parameters with 
    #Index(['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150',
    #       't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250',
    #       'wdir500', 't500', 'ws500', 'pres500', 'f', 'fg', 'gust_factor'],
    #      dtype='object')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd, numpy as np, tensorflow as tf

def mean_absolute_percentage_error(y_true, y_pred):
    return tf.reduce_mean(tf.abs((y_true-y_pred) / y_true)) * 100.0

df = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/merged-full-25ms-24hr-28-2-24.feather')
df = df[df.f < df.fg]
df['gust_factor'] = df.fg / df.f
df = df.dropna()
df = df.drop(['f', 'fg', 'fsdev', 'd', 'dsdev', 'longitude', 'latitude', 'X', 'Y', 'time', 'stod'], axis = 1)# + [f'Landscape_{i}' for i in range(70)], axis = 1)


y = df.gust_factor
X = df.drop(['gust_factor'], axis = 1)
X = X.drop(['ws_15', 'ws_250', 'ws_500', 'wd_15', 'wd_250', 'wd_500', 'p_15', 'p_250', 'p_500', 't_15', 't_250', 't_500', 'N_01', 'N_12'], axis = 1)


# Changing the type of X,y so as to work with Tensorflow
X, y = X.values.astype(np.float32), y.values.astype(np.float32)

scaler = StandardScaler()

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)

# Create a linear regression model
model = tf.keras.Sequential(
    [
        tf.keras.layers.Dense(units = 128, activation = 'relu', input_shape = (X_train.shape[1],)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(units = 64, activation = 'relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(units = 32, activation = 'relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(units = 1, activation = 'linear')

    ]
) #LinearRegression()

model.compile(optimizer='adam', loss=mean_absolute_percentage_error)


# Train the model
model.fit(X_train, y_train, epochs = 50, batch_size = 128, validation_data = (X_test, y_test))

# Evaluate the model
mape = model.evaluate(X_test, y_test)

y_predict = model.predict(X_test)

print(f'Test MAPE: {mape}%')

model.save('./model/saved_models/baselineLR.keras')

