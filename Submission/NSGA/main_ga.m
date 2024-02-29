clear all; close all; clc;

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

desired_photopic_lux = 300;
desired_melanopic_lux = 0;
desired_cct = 5000;
desired_mdr = 0;
desired_cri = 50;

objective_flags = [1 0 1 0 1];
% Define desired metrics and CRI threshold
desired_metrics = [desired_photopic_lux, desired_melanopic_lux, desired_cct, desired_mdr, desired_cri];
cri_threshold = desired_cri;

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
    bri_grid, ct_grid, desired_metrics, cri_threshold, objective_flags);

%%
bri = x(1);
ct = x(2);
photopic_lux_value = photopic_lux_fit(bri, ct);
melanopic_lux_value = melanopic_lux_fit(bri, ct);
cct_value = cct_fit(bri, ct);
mdr_value = mdr_fit(bri, ct);
cri_value = cri_fit(bri, ct);

% Display the values
fprintf('Photopic Lux Value: %f\n', photopic_lux_value);
fprintf('Melanopic Lux Value: %f\n', melanopic_lux_value);
fprintf('CCT Value: %f\n', cct_value);
fprintf('MDR Value: %f\n', mdr_value);
fprintf('CRI Value: %f\n', cri_value);