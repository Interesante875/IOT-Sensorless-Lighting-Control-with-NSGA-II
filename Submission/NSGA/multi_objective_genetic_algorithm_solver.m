function [optimal_x,optimal_fval,exitflag,output,population,score] = ...
    multi_objective_genetic_algorithm_solver(nvars,lb,ub, ...
    PopulationSize_Data, ...
    MaxGenerations_Data, ...
    FunctionTolerance_Data, ...
    ConstraintTolerance_Data, ...
    A, b, Aeq, beq, ...
    photopic_lux_fit, melanopic_lux_fit, cct_fit, mdr_fit, cri_fit, ...
    bri_grid, ct_grid, desired_metrics, cri_threshold, objective_flags,timestep)

    options = optimoptions('gamultiobj');
    options = optimoptions(options,'PopulationSize', PopulationSize_Data);
    options = optimoptions(options,'MaxGenerations', MaxGenerations_Data);
    options = optimoptions(options,'FunctionTolerance', FunctionTolerance_Data);
    options = optimoptions(options,'ConstraintTolerance', ConstraintTolerance_Data);
    options = optimoptions(options,'CrossoverFcn', {  @crossoverintermediate [] });
    options = optimoptions(options,'Display', 'off');
    options = optimoptions(options,'MaxTime', timestep);
    options = optimoptions(options,'PlotFcn', { @gaplotpareto });

    % Create an anonymous function that passes the additional parameters to the objective function
    objective_function = @(x) multi_objective_function_ga(x, ...
        photopic_lux_fit, melanopic_lux_fit, cct_fit, mdr_fit, cri_fit, ...
        bri_grid, ct_grid, desired_metrics, cri_threshold, objective_flags);

    [x,fval,exitflag,output,population,score] = ...
    gamultiobj(objective_function,nvars,A,b,Aeq,beq,lb,ub,[],options);

    % Display results
    % disp('Optimal values of bri and ct:');
    % disp(x);
    % disp('Optimal objectives (Photopic Lux, Melanopic Lux, CCT, MDER, CRI):');
    % disp(fval);
    % Compute the magnitude of objectives in fval
    magnitude = sqrt(sum(fval.^2, 2));
    
    % Find the index of the smallest magnitude (the optimal solution)
    [~, optimal_index] = min(magnitude);
    
    % Extract the optimal x and fval
    optimal_x = x(optimal_index, :);
    optimal_fval = fval(optimal_index, :);

    % Display the optimal x and fval
    fprintf('Optimal x: [%f, %f]\n', optimal_x(1), optimal_x(2));
    fprintf('Optimal fval: [');
    fprintf('%f, ', optimal_fval);
    fprintf('\b\b]\n');
end

function plot_selected_objectives(options, state, varargin)
    % Extract data from the optimization run
    population = state.Population;
    scores = state.Score;

    % Extract objective flags from options
    objective_flags = options.UserData.objective_flags;

    % Initialize a matrix to store selected objectives
    selected_objectives = [];

    % Identify selected objectives based on objective flags
    for i = 1:numel(objective_flags)
        if objective_flags(i) == 1
            selected_objectives = [selected_objectives, scores(:, i)];
        else
            selected_objectives = [selected_objectives, NaN(size(scores, 1), 1)];
        end
    end

    % Plot the selected objectives
    plot(selected_objectives(:, 1), selected_objectives(:, 2), 'bo');  % Adjust for the number of selected objectives

    % Add labels to the axes
    xlabel('Objective 1 Label');  % Replace with your label
    ylabel('Objective 2 Label');  % Replace with your label

    % Adjust axis limits as needed
    axis([min(selected_objectives(:, 1)), max(selected_objectives(:, 1)), ...
        min(selected_objectives(:, 2)), max(selected_objectives(:, 2))]);
end