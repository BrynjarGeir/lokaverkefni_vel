import os
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.regularizers import l2
from keras import optimizers
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd, numpy as np
import warnings 
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)

import shap

df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

seed = 42
test_size = 0.2
validation_size = 0.2

X, y = df.drop(['_merge', 'stod', 'gust_factor'], axis = 1), df['gust_factor']
X = X.drop(['Landscape_' + str(i) for i in range(70)], axis = 1)

features = list(X.columns)

input_size = X.shape[1]

X, y = X.values, y.values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

nn = Sequential()

nn.add(Dense(128, kernel_initializer='normal', input_dim = input_size, activation='relu', kernel_regularizer=l2(0.01)))
nn.add(Dense(256, kernel_initializer='normal',activation='relu', kernel_regularizer=l2(0.01)))
nn.add(Dense(512, kernel_initializer='normal',activation='relu', kernel_regularizer=l2(0.01)))
nn.add(Dense(1, kernel_initializer='lecun_normal',activation='linear'))

lr_schedule = optimizers.schedules.ExponentialDecay(initial_learning_rate = 1e-2, decay_steps = 1e4, decay_rate = 0.9)
opt = optimizers.Adam(learning_rate = lr_schedule)
nn.compile(loss='mean_absolute_error', optimizer = opt, metrics = ['mean_absolute_error'])

nn.summary()
checkpoint_name = './weights/Weights-{epoch:03d}--{val_loss:.5f}.hdf5' 
checkpoint = ModelCheckpoint(checkpoint_name, monitor='val_loss', verbose = 1, save_best_only = True, mode ='auto')
earlyStopping = EarlyStopping(monitor = 'loss', patience = 5)
callbacks_list = [checkpoint, earlyStopping]

nn.fit(X_train, y_train, epochs = 500, batch_size = 64, validation_split = validation_size, callbacks = callbacks_list)

newest = [file for file in os.listdir('./weights') if file.endswith('.hdf5')]
wights_file = './weights/' + newest[-1] #'Weights-012--0.08281.hdf5' # choose the best checkpoint 
nn.load_weights(wights_file) # load it
nn.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])

y_pred = nn.predict(X_test)

mse = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"The mean absolute error for sequential model is {mse}")
print(f"The r2 score for the squential model is {r2}")

print("X_train shape is", X_train.shape)
print("X_test shape is", X_test.shape)

sample_size = 1000
random_rows = np.random.choice(X_train.shape[0], size = sample_size, replace = False)
sampled_data = X_train[random_rows]

explainer = shap.Explainer(nn, sampled_data, algorithm = 'auto')

sample_size = 100
random_rows = np.random.choice(X_test.shape[0], size = sample_size, replace = False)
sampled_data = X_train[random_rows]

shap_values = explainer.shap_values(sampled_data)

shap.summary_plot(shap_values, sampled_data, feature_names = features)




