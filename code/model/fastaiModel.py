from fastai.tabular.all import *

import tensorflow as tf, pandas as pd, numpy as np, torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def mean_absolute_percentage_error(y_true, y_pred):
    return torch.mean(torch.abs((y_true-y_pred) / y_true)) * 100.0

#df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/merged-test1month-26-2-24.feather')
df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')
df = df[df.f < df.fg]
df = df.dropna()

y = df['fg']/df['f']
X = df.drop(['_merge', 'gust_factor', 'f', 'fg', 'd', 'stod'] + [f'Landscape_{i}' for i in range(70)], axis = 1)

df = df.drop(['_merge', 'f', 'fg', 'd', 'stod'] + [f'Landscape_{i}' for i in range(70)], axis = 1)

# Changing the type of X,y so as to work with Tensorflow
#X, y = X.values.astype(np.float32), y.values.astype(np.float32)

#scaler = StandardScaler()

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


#X_train_scaled = scaler.fit_transform(X_train)
#X_test_scaled = scaler.fit_transform(X_test)

#X_train[X_train.columns] = X_train_scaled
#X_test[X_test.columns] = X_test_scaled

y_names = 'gust_factor'
cont_names = df.columns[df.columns != y_names].tolist()

splits = RandomSplitter(valid_pct=0.2)(range_of(df))

dls = TabularPandas(df, procs = [FillMissing, Normalize], cont_names = cont_names, y_names = y_names, splits = splits)

dls = dls.dataloaders()

learn = tabular_learner(dls, metrics = mean_absolute_percentage_error) #loss_func = mean_absolute_percentage_error,

lr = learn.lr.find()

print(lr)

learn.fit_one_cycle(5)

preds, targs = learn.get_preds()

mape = mean_absolute_percentage_error(targs, preds)

print(f'The MAPE is {mape} %')

print(learn.recorder.values)

train_losses = learn.recorder.losses
val_losses = learn.recorder.val_losses



df_history = pd.DataFrame([train_losses, val_losses], columns=['train_loss', 'valid_loss'])
df_history.to_csv('D:/Skóli/lokaverkefni_vel/code/model/saved_models/fastai_training_history.csv', index = False)

learn.save('D:/Skóli/lokaverkefni_vel/code/model/saved_models/fastai_model')
learn.export('D:/Skóli/lokaverkefni_vel/code/model/saved_models/export_fastai.pkl')

