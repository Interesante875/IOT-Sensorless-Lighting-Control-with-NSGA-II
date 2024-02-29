function [x,fitted_metrics] = main_ga_func(flag,metric_arr,timestep)
% Load control input data (brightness and CCT) from HDF5 file
bri = h5read('data.h5', '/bri');
ct = h5read('data.h5', '/ct');

% Load output data (Photopic_lux, Melanopic_lux, CCT, MDER, CRI) from HDF5 file
photopic_lux = h5read('data.h5', '/photopic_lux');
melanopic_lux = h5read('data.h5', '/melanopic_lux');
cct = h5read('data.h5', '/cct');
mdr = h5read('data.h5', '/mdr');
cri = h5read('data.h5', '/cri');

% Create a grid of bri and ct values
bri_values = linspace(min(bri), max(bri), 100);  % Adjust the number of points as needed
ct_values = linspace(min(ct), max(ct), 100);    % Adjust the number of points as needed
[bri_grid, ct_grid] = meshgrid(bri_values, ct_values);

% Create scattered interpolants for each variable using 'natural' interpolation method
photopic_lux_fit = scatteredInterpolant(bri, ct, photopic_lux, 'natural');
melanopic_lux_fit = scatteredInterpolant(bri, ct, melanopic_lux, 'natural');
cct_fit = scatteredInterpolant(bri, ct, cct, 'natural');
mdr_fit = scatteredInterpolant(bri, ct, mdr, 'natural');
cri_fit = scatteredInterpolant(bri, ct, cri, 'natural');

objective_flags = flag;
% Define desired metrics and CRI threshold
desired_metrics = metric_arr;
cri_threshold = metric_arr(end);

% Define optimization variables
nvars = 2;  % Number of optimization variables
lb = [40, 154];  % Lower bounds for (bri, ct)
ub = [254, 500];  % Upper bounds for (bri, ct)
A = [];
b = [];
Aeq = [];
beq = [];
PopulationSize_Data = 3000; % Population size
MaxGenerations_Data = 500; % Maximum generations
FunctionTolerance_Data = 1e-3; % Function tolerance
ConstraintTolerance_Data = 1e-3; % Constraint tolerance

% Call gamultiobj with persistent fits and grid evaluations
[x, fval, exitflag, output, population, score] = multi_objective_genetic_algorithm_solver(nvars, lb, ub, ...
    PopulationSize_Data, MaxGenerations_Data, FunctionTolerance_Data, ConstraintTolerance_Data, ...
    A, b, Aeq, beq, ...
    photopic_lux_fit, melanopic_lux_fit, cct_fit, mdr_fit, cri_fit, ...
    bri_grid, ct_grid, desired_metrics, cri_threshold, objective_flags,timestep);

bri = x(1);
ct = x(2);
photopic_lux_value = photopic_lux_fit(bri, ct);
melanopic_lux_value = melanopic_lux_fit(bri, ct);
cct_value = cct_fit(bri, ct);
mdr_value = mdr_fit(bri, ct);
cri_value = cri_fit(bri, ct);

fitted_metrics = [photopic_lux_value,melanopic_lux_value,cct_value,mdr_value,cri_value];
end