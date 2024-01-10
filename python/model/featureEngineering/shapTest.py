import shap
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline

import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
import pandas as pd, numpy as np

shap.initjs()

pd.set_option('display.max_columns', None)

df = pd.read_feather('/mnt/d/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')

seed = 42
test_size = 0.2
validation_size = 0.2

X, y = df.drop(['_merge', 'stod', 'gust_factor', 'fg'], axis = 1), df['gust_factor']
X = X.drop(['Landscape_' + str(i) for i in range(70)], axis = 1)

ws15 = X['ws15']
f = X['f']

print("Mean for 15 meter ws: ", np.mean(ws15/f))

plt.hist(ws15/f)
plt.show()

features = list(X.columns)

X = X.values
y = y.values

input_size = X.shape[1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

model = make_pipeline(
    StandardScaler(),
    MLPRegressor(hidden_layer_sizes=(input_size,),activation='logistic', max_iter=10000,learning_rate='invscaling',random_state=seed)
)

model.fit(X_train,y_train)

sample_size = 100
random_rows = np.random.choice(X_train.shape[0], size = sample_size, replace = False)
sampled_data = X_train[random_rows]

explainer = shap.KernelExplainer(model.predict,sampled_data)

sample_size = 100
random_rows = np.random.choice(X_test.shape[0], size = sample_size, replace = False)
sampled_data = X_test[random_rows]

shap_values = explainer.shap_values(sampled_data,nsamples=100)

shap.summary_plot(shap_values,X_test,feature_names=features)
