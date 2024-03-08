from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import pandas as pd, numpy as np, tensorflow as tf

from tensorflow.keras.layers import Input, Dense, concatenate
from tensorflow.keras.models import Model


def mean_absolute_percentage_error(y_true, y_pred):
    return tf.reduce_mean(tf.abs((y_true-y_pred) / y_true)) * 100.0

df = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/merged-full-25ms-24hr-28-2-24.feather')
df = df[df.f < df.fg]
df['gust_factor'] = df.fg / df.f
df = df.dropna()
df = df.drop(['f', 'fg', 'fsdev', 'd', 'dsdev', 'longitude', 'latitude', 'X', 'Y', 'time', 'stod'], axis = 1)# + [f'Landscape_{i}' for i in range(70)], axis = 1)

y = df.gust_factor
X = df.drop(['gust_factor'], axis = 1)

# Changing the type of X,y so as to work with Tensorflow
X, y = X.values.astype(np.float32), y.values.astype(np.float32)

scaler = StandardScaler()

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)

batch_size = 64
num_epochs = 20
input_size = X_train.shape[1]
output_size = 1

def build_autoencoder(input_size):
    # Encoder
    inputs = Input(shape=(input_size,))
    encoded = Dense(64, activation='relu')(inputs)
    encoded = Dense(32, activation='relu')(encoded)

    # Decoder
    decoded = Dense(64, activation='relu')(encoded)
    decoded = Dense(input_size, activation='linear')(decoded)

    # Autoencoder model
    autoencoder = Model(inputs, decoded)
    autoencoder.compile(optimizer='adam', loss=mean_absolute_percentage_error)

    return autoencoder

autoencoder = build_autoencoder(input_size)
autoencoder.fit(X_train, X_train, epochs = 20, batch_size = 32, validation_data = (X_test, X_test))

encoder = Model(autoencoder.input, autoencoder.layers[2].output)

X_train = encoder.predict(X_train)
X_test = encoder.predict(X_test)

input_size = X_train.shape[1]

# Define input layers
input1 = Input(shape=(input_size,))
input2 = Input(shape=(input_size,))
# Define input layer
input_layer = Input(shape=(input_size,))

# Shared hidden layers
shared_layer = Dense(64, activation='relu')

# Hidden layers for input
hidden1 = shared_layer(input_layer)
hidden2 = Dense(32, activation='relu')(hidden1)

# Additional hidden layers
hidden3 = Dense(128, activation='relu')(hidden2)

# Output layer
outputs = Dense(output_size, activation='linear')(hidden3)

# Create model
model = tf.keras.Model(inputs=input_layer, outputs=outputs)

# Compile the model
model.compile(optimizer='adam', loss=mean_absolute_percentage_error)

# Display model summary
model.summary()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

    
mape = mean_absolute_percentage_error(y_test, y_pred)

print(f"MAPE: {mape}")

model.save('C:/Users/Brynjar Geir/Documents/lokaverkefni_vel/lokaverkefni_vel/code/model/saved_models/mergedNN.keras')