from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
import tensorflow as tf, pandas as pd, numpy as np

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

# Create an SVM regression model
svm_model = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))

# Train the model
svm_model.fit(X_train, y_train)

# Evaluate the model
svm_mape = mean_absolute_percentage_error(y_test, svm_model.predict(X_test))
print(f'SVM Test MAPE: {svm_mape}%')
