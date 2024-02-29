function [objective, constraint] = multi_objective_function_ga(x, ...
    photopic_lux_fit, melanopic_lux_fit, cct_fit, mdr_fit, cri_fit, ...
    bri_grid, ct_grid, desired_metrics, cri_threshold, objective_flags)

    % Evaluate the lighting metrics using persistent fits and grid evaluations
    photopic_lux_value = photopic_lux_fit(x(1), x(2));
    melanopic_lux_value = melanopic_lux_fit(x(1), x(2));
    cct_value = cct_fit(x(1), x(2));
    mdr_value = mdr_fit(x(1), x(2));
    cri_value = cri_fit(x(1), x(2));
    arr = [photopic_lux_value, melanopic_lux_value, cct_value, mdr_value, cri_value];
    % Define the objectives and constraints
    % Objectives: Deviation from desired metrics (minimize)
    % objective = [abs(photopic_lux_value - desired_metrics(1)), ...
    %             abs(melanopic_lux_value - desired_metrics(2)), ...
    %             abs(cct_value - desired_metrics(3)), ...
    %             abs(mdr_value - desired_metrics(4)), ...
    %             abs(cri_value - desired_metrics(5))];
     % Define the objectives and constraints based on the specified flags
    num_objectives = length(objective_flags);
    objective = zeros(1, num_objectives);

    for i = 1:num_objectives
        if i == 4
            if objective_flags(i) == 1
                % Calculate the objective value based on the desired metrics
                objective(i) = log(10000*abs(arr(i) - desired_metrics(i)).^2 + 1);
            else
                % Set the objective value to 0 if the objective is turned off
                objective(i) = 0;
            end

        else 
            if objective_flags(i) == 1
                % Calculate the objective value based on the desired metrics
                objective(i) = abs(arr(i) - desired_metrics(i)).^2;
            else
                % Set the objective value to 0 if the objective is turned off
                objective(i) = 0;
            end
        end
        
    end

    % Constraints: CRI threshold (should be less than or equal to cri_threshold)
    constraint = cri_value - cri_threshold;
end
