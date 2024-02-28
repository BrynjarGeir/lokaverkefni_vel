import tensorflow as tf, pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from evolutionary_algorithm import EvolutionaryAlgorithm

def mean_absolute_percentage_error(y_true, y_pred):
    return tf.reduce_mean(tf.abs((y_true-y_pred) / y_true)) * 100.0

#df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/merged-test1month-26-2-24.feather')
df = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')
df = df.dropna()
df = df[df.f < df.fg]
df = df.reset_index()

y = df['fg']/df['f']
X = df.drop(['_merge', 'gust_factor', 'f', 'fg', 'd', 'stod', 'DateTime', 'lat', 'lon'] + [f'Landscape_{i}' for i in range(70)], axis = 1)


# Changing the type of X,y so as to work with Tensorflow
X, y = X.values.astype(np.float32), y.values.astype(np.float32)

scaler = StandardScaler()

# Assuming 'X' is your feature matrix and 'y' is your target variable
# Replace 'X' and 'y' with your actual data

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)

# Assuming X_train and X_test are tabular numerical data with shape (num_samples, num_features)
num_features = X_train.shape[1]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the search space for NAS
#search_space = {
#    'layer_1_units': np.arange(8, 128),
#    'layer_2_units': np.arange(8, 128),
#    'activation': ['relu', 'tanh', 'sigmoid'],
#    'optimizer': ['adam', 'rmsprop', 'sgd'],
#    'learning_rate': [0.001, 0.01, 0.1],
#}
search_space = [
    {'name': 'layer_1_units',
     'bounds': [8, 128],
     'type': 'int'},
    {'name': 'layer_2_units',
     'bounds': [8, 128],
     'type': 'int'},
    {'name': 'activation',
     'bounds': ['relu', 'tanh'],#, 'sigmoid'],
     'type': 'cat'},
    {'name': 'optimizer',
     'bounds': ['adam', 'rmsprop'],#, 'sgd'],
     'type': 'cat'},
    {'name': 'learning_rate',
     'bounds': [0.001, 0.1],
     'type': 'float'},
]

# Define the fitness function (objective to maximize or minimize)
def fitness_function(params):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(units=params['layer_1_units'], activation=params['activation'], input_dim=X_train.shape[1]))
    model.add(tf.keras.layers.Dense(units=params['layer_2_units'], activation=params['activation']))
    model.add(tf.keras.layers.Dense(1, activation='linear'))

    model.compile(optimizer=params['optimizer'], loss=mean_absolute_percentage_error)

    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2, verbose=0)

    y_pred = model.predict(X_test)

    # The fitness function should return a value to maximize or minimize
    mape = mean_absolute_percentage_error(y_pred, y_test)
    return mape

# Use EvolutionaryAlgorithmSearchCV for NAS
#evolution = EvolutionaryAlgorithmSearchCV(
#    estimator=None,  # Not needed as we are using a custom fitness function
#    params=search_space,
#    scoring="neg_mean_squared_error",  # This is a placeholder, as the actual score is returned by the fitness function
#    cv=3,
#    n_jobs=-1,
#    verbose=1,
#    population_size=10,
#    gene_mutation_prob=0.10,
#    gene_crossover_prob=0.5,
#    tournament_size=3,
#)

evo_algo = EvolutionaryAlgorithm(function=fitness_function, parameters=search_space)
evo_algo.run()

# Best Params
best_params = evo_algo.best_parameters

print("Best architecture found:")
print(best_params)

mape = fitness_function(best_params)
print(f"The mape of the best parameters is {mape}%")