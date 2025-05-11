import json
import math
import os

# Constants
S_TH = 70  # Desired security score threshold (example value)
EPSILON = 1e-6  # Small constant for division by zero
INFLUENCE_FACTOR = 0.5  # How much neighbors influence the score (0 to 1)

def calculate_sbase(sca_score, st_score):
    """Calculates Base Score (SBase) as the average of SCA and ST."""
    if sca_score is None or st_score is None:
        return None
    try:
        return (float(sca_score) + float(st_score)) / 2
    except ValueError:
        return None

def calculate_snis_for_employee(employee_id, all_employee_month_data, graph_month):
    """Calculates Network-Influenced Security Score (SNIS) for one employee."""
    if employee_id not in all_employee_month_data:
        return None
    
    employee_node = all_employee_month_data[employee_id]
    s_base_i = employee_node.get('s_base')

    if s_base_i is None:
        return None

    neighbors = graph_month.get(employee_id, set())
    num_neighbors = len(neighbors)

    if num_neighbors == 0:
        return s_base_i  # No neighbors, SNIS is just SBase

    sum_neighbor_deficit = 0
    for neighbor_id in neighbors:
        if neighbor_id in all_employee_month_data and \
           all_employee_month_data[neighbor_id].get('s_base') is not None:
            s_base_j = all_employee_month_data[neighbor_id]['s_base']
            deficit = max(0, S_TH - s_base_j)
            sum_neighbor_deficit += deficit

    average_neighbor_deficit = sum_neighbor_deficit / (num_neighbors + EPSILON)
    
    snis_i = s_base_i - (average_neighbor_deficit * INFLUENCE_FACTOR)
    return snis_i

def process_monthly_data(monthly_data_path):
    """
    Processes the monthly collaboration data to calculate SBase and SNIS for each user.
    Returns a tuple: (all_months_processed_data, all_months_graphs)
    """
    try:
        with open(monthly_data_path, 'r') as f:
            all_months_raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {monthly_data_path}")
        return {}, {} # Modified for new return type
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {monthly_data_path}")
        return {}, {} # Modified for new return type

    all_months_processed_data = {}
    all_months_graphs = {} # New: To store graphs for each month

    for month, interactions in all_months_raw_data.items():
        current_month_employee_data = {}
        current_month_graph = {}
        
        all_users_this_month = set()
        for interaction in interactions:
            user_from = interaction.get('from')
            user_to = interaction.get('to')

            if not user_from or not user_to: # Skip if 'from' or 'to' is missing
                continue

            all_users_this_month.add(user_from)
            all_users_this_month.add(user_to)

            current_month_graph.setdefault(user_from, set()).add(user_to)
            current_month_graph.setdefault(user_to, set()).add(user_from) # Assuming undirected graph for neighbors

            sca = interaction.get('cyber_awareness')
            st = interaction.get('trustability')

            if user_from not in current_month_employee_data or \
               current_month_employee_data[user_from].get('s_cyber_awareness') is None:
                current_month_employee_data[user_from] = {
                    's_cyber_awareness': sca,
                    's_trustability': st
                }
            if user_to not in current_month_employee_data:
                 current_month_employee_data[user_to] = {
                    's_cyber_awareness': None,
                    's_trustability': None
                }

        for user_id in all_users_this_month:
            if user_id not in current_month_employee_data:
                current_month_employee_data[user_id] = {
                    's_cyber_awareness': None,
                    's_trustability': None
                }
            current_month_employee_data[user_id].setdefault('s_base', None)
            current_month_employee_data[user_id].setdefault('snis', None)

        for user_id, data in current_month_employee_data.items():
            s_base = calculate_sbase(data.get('s_cyber_awareness'), data.get('s_trustability'))
            current_month_employee_data[user_id]['s_base'] = s_base

        for user_id in current_month_employee_data.keys():
            snis = calculate_snis_for_employee(user_id, current_month_employee_data, current_month_graph)
            current_month_employee_data[user_id]['snis'] = snis

        all_months_processed_data[month] = current_month_employee_data
        all_months_graphs[month] = current_month_graph # New: Store the graph for the current month
        
    return all_months_processed_data, all_months_graphs # Modified return

def update_single_employee_score_and_propagate(
    month_key, 
    employee_id, 
    score_type_to_update, # Expects "cyber_awareness" or "trustability"
    new_score_value, 
    all_employee_data,    # The entire multi-month data structure
    monthly_graphs        # The entire multi-month graph structure
):
    """
    Updates a single employee's SCA or ST score for a given month,
    recalculates their SBase, and then recalculates SNIS for them and their direct neighbors.
    Modifies the all_employee_data structure in place.
    Returns True if successful, False otherwise.
    """
    if month_key not in all_employee_data:
        print(f"Error: Month '{month_key}' not found in all_employee_data.")
        return False
    
    if month_key not in monthly_graphs:
        print(f"Error: Month '{month_key}' not found in monthly_graphs.")
        return False

    month_specific_data = all_employee_data[month_key]
    month_specific_graph = monthly_graphs[month_key]

    if employee_id not in month_specific_data:
        print(f"Error: Employee '{employee_id}' not found in data for month '{month_key}'.")
        return False

    employee_scores = month_specific_data[employee_id]
    
    internal_score_key = None
    if score_type_to_update == "cyber_awareness":
        internal_score_key = 's_cyber_awareness'
    elif score_type_to_update == "trustability":
        internal_score_key = 's_trustability'
    else:
        print(f"Error: Invalid score_type_to_update '{score_type_to_update}'. Must be 'cyber_awareness' or 'trustability'.")
        return False

    original_value = employee_scores.get(internal_score_key)
    employee_scores[internal_score_key] = new_score_value
    print(f"Updated {internal_score_key} for {employee_id} in {month_key} from {original_value} to {new_score_value}")

    new_sbase = calculate_sbase(employee_scores.get('s_cyber_awareness'), employee_scores.get('s_trustability'))
    employee_scores['s_base'] = new_sbase

    employees_to_recalculate_snis = {employee_id}
    if employee_id in month_specific_graph:
        employees_to_recalculate_snis.update(month_specific_graph.get(employee_id, set()))

    for emp_to_update_snis in employees_to_recalculate_snis:
        if emp_to_update_snis in month_specific_data: 
            new_snis = calculate_snis_for_employee(emp_to_update_snis, month_specific_data, month_specific_graph)
            month_specific_data[emp_to_update_snis]['snis'] = new_snis
        else:
            print(f"  - Warning: Neighbor {emp_to_update_snis} (of {employee_id}) not found in month_data for SNIS recalculation in {month_key}.")
            
    return True

def main_propagator():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    json_file_name = 'numpy_numpy_monthly_collaboration.json'
    json_file_path = os.path.join(base_dir, json_file_name)
    
    output_file_name = 'propagated_scores.json'
    output_json_path = os.path.join(script_dir, output_file_name)

    if not os.path.exists(json_file_path):
        current_working_dir_path = os.path.join(os.getcwd(), json_file_name)
        if os.path.exists(current_working_dir_path):
            json_file_path = current_working_dir_path
            potential_output_dir = os.path.join(os.getcwd(), 'security_scores')
            if os.path.isdir(potential_output_dir):
                 output_json_path = os.path.join(potential_output_dir, output_file_name)
        else:
            print(f"Error: Could not find data file '{json_file_name}' at expected path {json_file_path} or in CWD {current_working_dir_path}")
            return

    print(f"Processing data from: {json_file_path}")
    all_processed_data, all_graphs = process_monthly_data(json_file_path)

    if all_processed_data:
        test_month_to_update = "2021-09" 
        test_employee_to_update = "charris"
        test_score_type_to_update = "cyber_awareness" 
        test_new_score_value = 80

        if test_month_to_update in all_processed_data and \
           all_graphs.get(test_month_to_update) is not None and \
           test_employee_to_update in all_processed_data[test_month_to_update]:
            
            print(f"\nAttempting single update for employee '{test_employee_to_update}' in month '{test_month_to_update}'...")
            print(f"Changing '{test_score_type_to_update}' to {test_new_score_value}.")
            
            original_employee_scores = dict(all_processed_data[test_month_to_update][test_employee_to_update])
            print(f"Scores for {test_employee_to_update} BEFORE update: {original_employee_scores}")

            original_neighbor_snis_map = {}
            if test_employee_to_update in all_graphs[test_month_to_update]:
                for neighbor_id in all_graphs[test_month_to_update][test_employee_to_update]:
                    if neighbor_id in all_processed_data[test_month_to_update]:
                        original_neighbor_snis_map[neighbor_id] = all_processed_data[test_month_to_update][neighbor_id].get('snis')

            update_successful = update_single_employee_score_and_propagate(
                month_key=test_month_to_update,
                employee_id=test_employee_to_update,
                score_type_to_update=test_score_type_to_update,
                new_score_value=test_new_score_value,
                all_employee_data=all_processed_data, 
                monthly_graphs=all_graphs          
            )

            if update_successful:
                print(f"Single update for '{test_employee_to_update}' in '{test_month_to_update}' processed successfully.")
                updated_employee_scores = all_processed_data[test_month_to_update][test_employee_to_update]
                print(f"Scores for {test_employee_to_update} AFTER update: {updated_employee_scores}")

                if test_employee_to_update in all_graphs[test_month_to_update]:
                    print("Neighbor SNIS comparison (Original -> New):")
                    for neighbor_id in all_graphs[test_month_to_update][test_employee_to_update]:
                        if neighbor_id in all_processed_data[test_month_to_update]:
                            original_snis = original_neighbor_snis_map.get(neighbor_id, 'N/A')
                            current_snis = all_processed_data[test_month_to_update][neighbor_id].get('snis', 'N/A')
                            print(f"  - Neighbor '{neighbor_id}': SNIS {original_snis} -> {current_snis}")
            else:
                print(f"Single update for '{test_employee_to_update}' in '{test_month_to_update}' failed or did not apply.")
        else:
            print(f"\nSkipping single update example: Employee '{test_employee_to_update}' or month '{test_month_to_update}' not found in initial data, or graph missing for month.")

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        try:
            with open(output_json_path, 'w') as outfile:
                sorted_propagated_data = {month: all_processed_data[month] for month in sorted(all_processed_data.keys())}
                json.dump(sorted_propagated_data, outfile, indent=4)
            print(f"Successfully processed data and saved to {output_json_path}")
        except IOError as e:
            print(f"Error writing output file {output_json_path}: {e}")

if __name__ == '__main__':
    main_propagator()
