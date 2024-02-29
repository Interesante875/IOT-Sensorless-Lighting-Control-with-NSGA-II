#%%
import matlab.engine
import numpy as np
from user_interface import *
from speccy_collection import *
import matplotlib.pyplot as plt
from data_collection import *
from tqdm import tqdm
eng = matlab.engine.start_matlab()
############################################################################################
# start data collection
start_data_collection()
############################################################################################

############################################################################################
#%%
print("Structuring Time Series")
# select the combination
user_input,metric_1_name,metric_2_name = select_pairwise()

# structure the time series for metric 1
timestep = 15
calib_num_ps = int(120/timestep) # number of calibration per second
segment_num = 4
metric_1_values = [5000,5000,4000,3000] #input_metric_1_val(user_input)
# metric_1_values = [200,150,100,75] #input_metric_1_val(user_input)
metric_1_order = [2,1,0,3,0]
metric_1 = [] #input_metric_1_val(user_input)
for i in range(segment_num):
    if i != 3:
        test = metric_1_values[metric_1_order[i]]*np.ones(calib_num_ps)
        metric_1.append(test)
    else:
        # hard coded way to split the 2 seconds paiseh
        test = np.linspace(metric_1_values[metric_1_order[i]],metric_1_values[metric_1_order[i+1]],2*calib_num_ps)
        test_1 = test[0:calib_num_ps]
        test_2 = test[calib_num_ps:2*calib_num_ps]
        metric_1.append(test_1)
        metric_1.append(test_2)
        p = 0
metric_1 = np.hstack(metric_1).tolist() #input_metric_1_val(user_input)

# structure the time series for metric 2
metric_2_values = [150,120,100,75] #input_metric_2_val(user_input)
# metric_2_values = [180,140,75,75] #input_metric_1_val(user_input)
metric_2_order = [3,2,1,0,0]
metric_2 = [] #input_metric_1_val(user_input)
for i in range(segment_num):
    if i != 3:
        test = metric_2_values[metric_2_order[i]]*np.ones(calib_num_ps)
        metric_2.append(test)
    else:
        # hard coded way to split the 2 seconds paiseh
        test = metric_2_values[metric_2_order[i]]*np.ones(2*calib_num_ps)
        test_1 = test[0:calib_num_ps]
        test_2 = test[calib_num_ps:2*calib_num_ps]
        metric_2.append(test_1)
        metric_2.append(test_2)
        p = 0
metric_2 = np.hstack(metric_2).tolist() #input_metric_1_val(user_input)

cri_constraint = 75 #input_cri_constraint()

# reverse if metric order different
flag = check_order(metric_1_name,metric_2_name,metric_1,metric_2)
# reverse the order
if flag == 1:
    temp = metric_1
    metric_1 = metric_2
    metric_2 = temp

plt.plot(metric_1)
plt.ylabel(f'{metric_1_name}')
plt.show()

plt.plot(metric_2)
plt.ylabel(f'{metric_2_name}')
plt.show()

measured_metric_1 = []
measured_metric_2 = []
exceed_constraint = []
total_cri = 0
############################################################################################

############################################################################################
print("Deploying NSGA-II Calibration\n")
# Deploy the calibrated model
for i in tqdm(range(len(metric_1))):
    X_input,objective_flags = compile_user_input(user_input,metric_1[i],metric_2[i],cri_constraint)
    print(f"Target Metric - {metric_1_name}:{metric_1[i]:.4f},{metric_2_name}:{metric_2[i]:.4f},CRI:{cri_constraint:.4f}")
 
    print(X_input)
    print(objective_flags)
    optimal_x,fitted_metrics = eng.main_ga_func(matlab.double(objective_flags),matlab.double(X_input),matlab.double(timestep-5),nargout=2)
    optimal_x,fitted_metrics = np.array(optimal_x),np.array(fitted_metrics)
    print(f"Finished Calibrating - Surface Fit: Plux:{fitted_metrics[0,0]:.4f},Mlux:{fitted_metrics[0,1]:.4f},CCT:{fitted_metrics[0,2]:.4f},MDER:{fitted_metrics[0,3]:.4f},CRI:{fitted_metrics[0,4]:.4f}")

    bri = int(np.rint(optimal_x[0,0]))
    ct = int(np.rint(optimal_x[0,1]))
    cct = int(np.rint(1000000.0/optimal_x[0,1]))
    print(f"Predicted Control Input - BRI:{np.rint(optimal_x[0,0])}, CCT:{cct}, CT:{ct}\n")

    ctrl_input = tune_lights(bri=bri, cct=cct, max_retries=5, wait_time=20)
    time.sleep(5)
    speccy_data = collect_lights(5, 20)
    measured_output = processSPD(speccy_data)
    cur_metric_1,cur_metric_2,measured_CRI= processMetrics(speccy_data,user_input)
    measured_metric_1.append(cur_metric_1)
    measured_metric_2.append(cur_metric_2)
    total_cri += measured_CRI

    # calculate percentage difference for the current measurement
    difference_metric_1 = abs(metric_1[i]-cur_metric_1)*100/metric_1[i]
    difference_metric_2 = abs(metric_2[i]-cur_metric_2)*100/metric_2[i]
    print(f"Percentage Difference - {metric_1_name}:{difference_metric_1:.4f},{metric_2_name}:{difference_metric_2:.4f},CRI:{measured_CRI:.4f} {measured_CRI>cri_constraint}\n")
    exceed_constraint.append(measured_CRI>cri_constraint)
    
    # data visualization
    plt.plot(metric_1)
    plt.plot(measured_metric_1,marker=".", markersize=20)
    plt.ylabel(f'{metric_1_name}')
    plt.show()

    plt.plot(metric_2)
    plt.plot(measured_metric_2,marker=".", markersize=20)
    plt.ylabel(f'{metric_2_name}')
    plt.show()
############################################################################################
MSE_metric_1 = np.square(np.subtract(metric_1,measured_metric_1)).mean() 
RMSE_metric_1= math.sqrt(MSE_metric_1)
print(f"{metric_1_name} Root Mean Square Error:{RMSE_metric_1}\n")

MSE_metric_2 = np.square(np.subtract(metric_2,measured_metric_2)).mean() 
RMSE_metric_2= math.sqrt(MSE_metric_2)
print(f"{metric_2_name} Root Mean Square Error:{RMSE_metric_2}\n")

exceed_constraint_num = np.sum(exceed_constraint)
print(f"Number of times exceeded constraint:{exceed_constraint_num}/{len(metric_1)}\n")
print(f"Mean CRI:{total_cri/len(metric_1)}\n")
# %%
