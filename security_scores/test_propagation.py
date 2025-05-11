import unittest
import os
import sys
import copy

# Ensure propagate_score_update can be imported
# Assuming test_propagation.py is in the same directory as propagate_score_update.py
try:
    from propagate_score_update import (
        calculate_sbase,
        # calculate_snis_for_employee, # Not called directly by the test logic but implicitly tested
        update_single_employee_score_and_propagate,
        S_TH, EPSILON, INFLUENCE_FACTOR # Import constants used in SNIS calculation
    )
except ImportError as e:
    # Fallback if the script is run from a different CWD and security_scores is not in PYTHONPATH
    # This attempts to add the script's directory to sys.path
    # For simplicity, we'll assume direct import works. If not, path adjustments might be needed.
    print(f"Failed to import from propagate_score_update: {e}. Ensure it's in the same directory or PYTHONPATH.")
    # Attempt to add parent directory to sys.path if running from within security_scores
    # or if propagate_score_update is in a module structure.
    # This is a common pattern but might need adjustment based on your exact execution context.
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(script_dir) # Assuming security_scores is one level down from project root
    # if project_root not in sys.path:
    #     sys.path.insert(0, project_root)
    # # Then try importing again, perhaps with full path if it's a module
    # # from security_scores.propagate_score_update import ...
    sys.exit(1)


class TestScorePropagation(unittest.TestCase):

    def setUp(self):
        """Set up a small, controlled dataset for testing."""
        self.month_key = "2025-01"
        
        # Initial raw scores
        self.alice_sca_initial = 60.0
        self.alice_st_initial = 60.0
        self.bob_sca_initial = 80.0
        self.bob_st_initial = 80.0
        self.charlie_sca_initial = 50.0 # Another neighbor for Alice
        self.charlie_st_initial = 50.0

        # Calculate initial SBase values
        sbase_alice_initial = calculate_sbase(self.alice_sca_initial, self.alice_st_initial)
        sbase_bob_initial = calculate_sbase(self.bob_sca_initial, self.bob_st_initial)
        sbase_charlie_initial = calculate_sbase(self.charlie_sca_initial, self.charlie_st_initial)

        self.initial_employee_data_month = {
            "Alice": {
                's_cyber_awareness': self.alice_sca_initial,
                's_trustability': self.alice_st_initial,
                's_base': sbase_alice_initial,
                'snis': None # Will be calculated based on initial state
            },
            "Bob": {
                's_cyber_awareness': self.bob_sca_initial,
                's_trustability': self.bob_st_initial,
                's_base': sbase_bob_initial,
                'snis': None # Will be calculated
            },
            "Charlie": {
                's_cyber_awareness': self.charlie_sca_initial,
                's_trustability': self.charlie_st_initial,
                's_base': sbase_charlie_initial,
                'snis': None # Will be calculated
            }
        }

        self.initial_monthly_graph = {
            "Alice": {"Bob", "Charlie"},
            "Bob": {"Alice"},
            "Charlie": {"Alice"}
        }

        # Manually calculate initial SNIS values for the setUp state
        # This uses the logic from calculate_snis_for_employee for verification

        # SNIS for Alice
        deficit_bob_to_alice = max(0, S_TH - sbase_bob_initial)                 # max(0, 70 - 80) = 0
        deficit_charlie_to_alice = max(0, S_TH - sbase_charlie_initial)         # max(0, 70 - 50) = 20
        avg_deficit_for_alice = (deficit_bob_to_alice + deficit_charlie_to_alice) / (len(self.initial_monthly_graph["Alice"]) + EPSILON) # (0+20)/2 = 10
        self.initial_employee_data_month["Alice"]['snis'] = sbase_alice_initial - (avg_deficit_for_alice * INFLUENCE_FACTOR) # 60 - (10*0.5) = 55

        # SNIS for Bob
        deficit_alice_to_bob = max(0, S_TH - sbase_alice_initial)               # max(0, 70 - 60) = 10
        avg_deficit_for_bob = deficit_alice_to_bob / (len(self.initial_monthly_graph["Bob"]) + EPSILON) # 10/1 = 10
        self.initial_employee_data_month["Bob"]['snis'] = sbase_bob_initial - (avg_deficit_for_bob * INFLUENCE_FACTOR) # 80 - (10*0.5) = 75
        
        # SNIS for Charlie
        deficit_alice_to_charlie = max(0, S_TH - sbase_alice_initial)           # max(0, 70 - 60) = 10
        avg_deficit_for_charlie = deficit_alice_to_charlie / (len(self.initial_monthly_graph["Charlie"]) + EPSILON) # 10/1 = 10
        self.initial_employee_data_month["Charlie"]['snis'] = sbase_charlie_initial - (avg_deficit_for_charlie * INFLUENCE_FACTOR) # 50 - (10*0.5) = 45

        # These are the data structures that update_single_employee_score_and_propagate expects
        self.all_employee_data = {
            self.month_key: copy.deepcopy(self.initial_employee_data_month)
        }
        self.monthly_graphs = {
            self.month_key: copy.deepcopy(self.initial_monthly_graph)
        }

    def test_propagation_on_cyber_awareness_change(self):
        """Test propagation when an employee's cyber_awareness score changes."""
        employee_to_update = "Alice"
        score_type_to_update = "cyber_awareness"
        new_sca_score_alice = 40.0 # Alice's SCA changes from 60 to 40
        print(f"\n--- Test: Propagation on '{score_type_to_update}' change for {employee_to_update} ---")
        print(f"Changing {employee_to_update}'s '{score_type_to_update}' from {self.alice_sca_initial} to {new_sca_score_alice}")

        # Get initial SNIS values from the setUp data for comparison
        initial_snis_alice = self.all_employee_data[self.month_key][employee_to_update]['snis']
        initial_snis_bob = self.all_employee_data[self.month_key]["Bob"]['snis']
        initial_snis_charlie = self.all_employee_data[self.month_key]["Charlie"]['snis']
        
        # Verify setUp calculations are as expected by the test logic
        self.assertAlmostEqual(initial_snis_alice, 55.0, places=5, msg="Initial SNIS for Alice in setUp is incorrect.")
        print(f"SUCCESS: Initial SNIS for Alice ({initial_snis_alice}) matches expected (55.0).")
        self.assertAlmostEqual(initial_snis_bob, 75.0, places=5, msg="Initial SNIS for Bob in setUp is incorrect.")
        print(f"SUCCESS: Initial SNIS for Bob ({initial_snis_bob}) matches expected (75.0).")
        self.assertAlmostEqual(initial_snis_charlie, 45.0, places=5, msg="Initial SNIS for Charlie in setUp is incorrect.")
        print(f"SUCCESS: Initial SNIS for Charlie ({initial_snis_charlie}) matches expected (45.0).")

        # Perform the update
        print(f"Calling update_single_employee_score_and_propagate for {employee_to_update}...")
        success = update_single_employee_score_and_propagate(
            month_key=self.month_key,
            employee_id=employee_to_update,
            score_type_to_update=score_type_to_update,
            new_score_value=new_sca_score_alice,
            all_employee_data=self.all_employee_data, # This will be modified in place
            monthly_graphs=self.monthly_graphs
        )
        self.assertTrue(success, "Update function should return True on success.")
        print(f"SUCCESS: update_single_employee_score_and_propagate returned True.")

        updated_data_month = self.all_employee_data[self.month_key]

        # 1. Check Alice's direct score update
        self.assertEqual(updated_data_month[employee_to_update]['s_cyber_awareness'], new_sca_score_alice)
        print(f"SUCCESS: {employee_to_update}'s s_cyber_awareness updated to {new_sca_score_alice}.")

        # 2. Check Alice's SBase update
        expected_sbase_alice_new = calculate_sbase(new_sca_score_alice, self.alice_st_initial) # (40+60)/2 = 50
        self.assertAlmostEqual(updated_data_month[employee_to_update]['s_base'], expected_sbase_alice_new, places=5)
        print(f"SUCCESS: {employee_to_update}'s s_base updated to {expected_sbase_alice_new}.")

        # 3. Check Alice's SNIS update
        # Alice's neighbors are Bob (SBase=80) and Charlie (SBase=50)
        # Their SBase values haven't changed directly from Alice's SCA update
        sbase_bob_current = updated_data_month["Bob"]['s_base'] # Should still be 80
        sbase_charlie_current = updated_data_month["Charlie"]['s_base'] # Should still be 50

        deficit_bob_to_alice_new = max(0, S_TH - sbase_bob_current)                 # max(0, 70 - 80) = 0
        deficit_charlie_to_alice_new = max(0, S_TH - sbase_charlie_current)         # max(0, 70 - 50) = 20
        avg_deficit_for_alice_new = (deficit_bob_to_alice_new + deficit_charlie_to_alice_new) / (len(self.monthly_graphs[self.month_key]["Alice"]) + EPSILON) # (0+20)/2 = 10
        expected_snis_alice_new = expected_sbase_alice_new - (avg_deficit_for_alice_new * INFLUENCE_FACTOR) # 50 - (10*0.5) = 45
        
        self.assertAlmostEqual(updated_data_month[employee_to_update]['snis'], expected_snis_alice_new, places=5)
        print(f"SUCCESS: {employee_to_update}'s SNIS updated to {expected_snis_alice_new}.")
        self.assertNotAlmostEqual(updated_data_month[employee_to_update]['snis'], initial_snis_alice, places=5, msg="Alice's SNIS should have changed.")
        print(f"SUCCESS: {employee_to_update}'s SNIS ({expected_snis_alice_new}) correctly differs from initial ({initial_snis_alice}).")


        # 4. Check Bob's SNIS update (propagation)
        # Bob's neighbor is Alice (new SBase = 50)
        deficit_alice_to_bob_new = max(0, S_TH - expected_sbase_alice_new) # max(0, 70 - 50) = 20
        avg_deficit_for_bob_new = deficit_alice_to_bob_new / (len(self.monthly_graphs[self.month_key]["Bob"]) + EPSILON) # 20/1 = 20
        expected_snis_bob_new = sbase_bob_current - (avg_deficit_for_bob_new * INFLUENCE_FACTOR) # 80 - (20*0.5) = 70
        
        self.assertAlmostEqual(updated_data_month["Bob"]['snis'], expected_snis_bob_new, places=5)
        print(f"SUCCESS: Bob's SNIS (neighbor of {employee_to_update}) propagated to {expected_snis_bob_new}.")
        self.assertNotAlmostEqual(updated_data_month["Bob"]['snis'], initial_snis_bob, places=5, msg="Bob's SNIS should have changed due to Alice.")
        print(f"SUCCESS: Bob's SNIS ({expected_snis_bob_new}) correctly differs from initial ({initial_snis_bob}).")

        # 5. Check Charlie's SNIS update (propagation)
        # Charlie's neighbor is Alice (new SBase = 50)
        deficit_alice_to_charlie_new = max(0, S_TH - expected_sbase_alice_new) # max(0, 70 - 50) = 20
        avg_deficit_for_charlie_new = deficit_alice_to_charlie_new / (len(self.monthly_graphs[self.month_key]["Charlie"]) + EPSILON) # 20/1 = 20
        expected_snis_charlie_new = sbase_charlie_current - (avg_deficit_for_charlie_new * INFLUENCE_FACTOR) # 50 - (20*0.5) = 40

        self.assertAlmostEqual(updated_data_month["Charlie"]['snis'], expected_snis_charlie_new, places=5)
        print(f"SUCCESS: Charlie's SNIS (neighbor of {employee_to_update}) propagated to {expected_snis_charlie_new}.")
        self.assertNotAlmostEqual(updated_data_month["Charlie"]['snis'], initial_snis_charlie, places=5, msg="Charlie's SNIS should have changed due to Alice.")
        print(f"SUCCESS: Charlie's SNIS ({expected_snis_charlie_new}) correctly differs from initial ({initial_snis_charlie}).")
        print(f"--- Test: Propagation on '{score_type_to_update}' change for {employee_to_update} PASSED ---")

if __name__ == '__main__':
    unittest.main()
