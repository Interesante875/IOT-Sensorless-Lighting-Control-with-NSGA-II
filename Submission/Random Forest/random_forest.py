#%% 
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.metrics import r2_score

# Create a function to augment the dataset with noise
def augment_data(X, y, num_samples):
    augmented_X = []
    augmented_y = []
    
    num_features = X.shape[1]
    
    for i in range(num_samples):
        p = len(X)
        random_idx = np.random.randint(0, len(X))
        data_point = X[random_idx,:]
        given_outputs = y[random_idx,:]
        augmented_data_point = data_point + 0.0 # to fix some memory bug

        # Add noise to the data point
        noise = np.random.normal(0, 0.3, size=num_features)  # Adjust the noise level as needed
        augmented_data_point = augmented_data_point + noise

        # Replace a random subset of features with 0
        num_to_replace = np.random.randint(0, num_features-2)
        features_to_replace = np.random.choice(num_features, num_to_replace, replace=False)
        augmented_data_point[features_to_replace] = 0

        augmented_X.append(augmented_data_point)
        augmented_y.append(given_outputs)
    
    return np.array(augmented_X), np.array(augmented_y)

def train():
    print("Start Training")
    df = pd.read_csv('lighting_data.csv')
    dataset = df.to_numpy()

    # Extract individual columns for clarity
    m = np.array([[0,2,3,4],[3,4,5,6]])
    bri = dataset[:, 0]
    cct = dataset[:, 1]
    ct = dataset[:, 2]
    photopic_lux = dataset[:, 4]
    melanopic_lux = dataset[:, 5]
    cct = dataset[:, 6]
    mdr = dataset[:, 7]
    cri = dataset[:, 8]
    control_input = dataset[:, [0, 1]].astype(np.float64)
    light_metrics = dataset[:,4:9].astype(np.float64)

    # # Augment the dataset
    num_augmented_samples = 20000  # Adjust the number of augmented samples as needed
    augmented_light_metrics, augmented_train_control_input = augment_data(light_metrics, control_input, num_augmented_samples)

    # # Combine the original and augmented datasets
    # original light metrics keeps getting altered for some reason, need to find reason
    X_combined = np.vstack((light_metrics, augmented_light_metrics))
    y_combined = np.vstack((control_input, augmented_train_control_input))

    # %%
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_combined, y_combined, test_size=0.2, random_state=42)

    # Train the whole model
    ctrl_model = RandomForestRegressor(n_estimators=100, random_state=42)
    ctrl_model.fit(X_train, y_train)  # Predicting only brightness and CCT
    ctrl_predictions = ctrl_model.predict(X_test)
    r2_ctrl = r2_score(y_test, ctrl_predictions)
    print(f'R-squared (CCT): {r2_ctrl:.4f}')

    return ctrl_model