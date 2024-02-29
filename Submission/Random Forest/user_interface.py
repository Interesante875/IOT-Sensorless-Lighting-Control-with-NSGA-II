import numpy as np

def select_pairwise ():
    pair_index = int(input(f"photo_melano 0\nphoto_cct 1\nphoto_mdr  2\nmelano_cct 3\nmelano_mdr  4\ncct_mdr 5\nSelect a pair number:"))

    match pair_index:
        case 0:
            metric_1_name = "Photopic Lux"
            metric_2_name = "Melanopic Lux"
        case 1:
            metric_1_name = "Photopic_Lux"
            metric_2_name = "CCT"
        case 2:
            metric_1_name = "Photopic Lux"
            metric_2_name = "MDER"
        case 3:
            metric_1_name = "Melanopic Lux"
            metric_2_name = "CCT"
        case 4:
            metric_1_name = "Melanopic Lux"
            metric_2_name = "MDER"
        case 5:
            metric_1_name = "CCT"
            metric_2_name = "MDER"


    return pair_index,metric_1_name,metric_2_name

def input_metric_1_val(user_input):
    match user_input:
        case 0:
            return float(input("Enter Desired Photopic Lux"))
        case 1:
            return float(input("Enter Desired Photopic Lux"))
        case 2:
            return float(input("Enter Desired Photopic Lux"))
        case 3:
            return float(input("Enter Desired Melanopic Lux"))
        case 4:
            return float(input("Enter Desired Melanopic Lux"))
        case 5:
            return float(input("Enter Desired CCT")),"CCT"
        
def input_metric_2_val(user_input):
    match user_input:
        case 0:
            return float(input("Enter Desired Melanopic Lux"))
        case 1:
            return float(input("Enter Desired CCT"))
        case 2:
            return float(input("Enter Desired MDER"))
        case 3:
            return float(input("Enter Desired CCT"))
        case 4:
            return float(input("Enter Desired MDER"))
        case 5:
            return float(input("Enter Desired MDER"))

def input_cri_constraint():
    return float(input("Enter Desired CRI"))

def compile_user_input(user_input,metric_1,metric_2,cri_constraint):
    match user_input:
        case 0:
            return [metric_1,metric_2,0,0,cri_constraint],[1,1,0,0,1]
        case 1:
            return [metric_1,0,metric_2,0,cri_constraint],[1,0,1,0,1]
        case 2:
            return [metric_1,0,0,metric_2,cri_constraint],[1,0,0,1,1]
        case 3:
            return [0,metric_1,metric_2,0,cri_constraint],[0,1,1,0,1]
        case 4:
            return [0,metric_1,0,metric_2,cri_constraint],[0,1,0,1,1]
        case 5:
            return [0,0,metric_1,metric_2,cri_constraint],[0,0,1,1,1]
        
def check_order(metric_1_name,metric_2_name,metric_1,metric_2):
    check = input(f"Metric 1: {metric_1_name}, Metric 2: {metric_2_name}\nIs the order correct? (Y/N):")
    flag = 0
    if (check == "N"):
        print("Change in order")
        flag = 1
    
    return flag