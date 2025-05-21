import os

import numpy as np

from .instance_data import InstanceData

class Solution:
    def __init__(self, problem=None):
        self.problem = problem
        self.fitness_score = None

        # Your original allocation style (optional if you keep your current design)
        self.allocation = []
        self.open_warehouses = []

        # New properties for tweak_store compatibility
        self.stores = []             # list of Store objects
        self.warehouses = []         # list of Warehouse objects
        self.incompatible_pairs = set()
        self.count_req = 0           # used in tweak_store

        if problem is not None:
            # Initialize allocation and open_warehouses if needed
            self.allocation = [[0] * problem.num_warehouses for _ in range(problem.num_stores)]
            self.open_warehouses = [False] * problem.num_warehouses
            # You may want to initialize stores and warehouses here or separately

        # Compute initial fitness
        # self.fitness_score = self.fitness()

    @classmethod
    def from_solution_data(cls, solution_data: str, problem: InstanceData) -> 'Solution':
        """Create a Solution object from the parsed solution data."""
        solution = cls(problem)  # Create an instance with the problem
        # Now we can populate the allocation from solution_data (as string or parsed list)
        rows = solution_data.strip().split("\n")
        for store_id, row in enumerate(rows):
            allocations = row.strip()[1:-1].split(',')
            for warehouse_id, allocation in enumerate(allocations):
                solution.allocation[store_id][warehouse_id] = int(allocation)
        return solution

    # def fitness(self) -> int:
    #     total_fixed_cost = 0
    #     total_supply_cost = 0
    #     used_warehouses = set()
    #
    #     for store_id, allocations in enumerate(self.allocation):
    #         for warehouse_id, amount in enumerate(allocations):
    #             if amount > 0:
    #                 used_warehouses.add(warehouse_id)
    #                 supply_cost = self.problem.supply_costs_matrix[store_id][warehouse_id]
    #                 total_supply_cost += amount * supply_cost
    #
    #     total_fixed_cost = sum(
    #         self.problem.warehouses[w_id].fixed_cost for w_id in used_warehouses
    #     )
    #
    #     self.fitness_score = total_fixed_cost + total_supply_cost
    #     return self.fitness_score

    def fitness(self) -> int:
        # Convert allocation and supply_costs_matrix to numpy arrays
        allocation_np = np.array(self.allocation)
        supply_costs_np = np.array(self.problem.supply_costs_matrix)

        # Calculate total supply cost with element-wise multiplication and sum
        total_supply_cost = np.sum(allocation_np * supply_costs_np)

        # Warehouses used: any warehouse with sum of allocated supply > 0
        used_warehouses = np.where(np.sum(allocation_np, axis=0) > 0)[0]

        # Sum fixed costs of used warehouses
        total_fixed_cost = sum(self.problem.warehouses[w].fixed_cost for w in used_warehouses)

        self.fitness_score = total_fixed_cost + total_supply_cost
        return self.fitness_score

    def export(self, file_path: str) -> None:
        """Export the solution to a file in the required matrix format, creating the directory if it doesn't exist."""
        # Get the directory from the file path
        directory = os.path.dirname(file_path)

        # If the directory doesn't exist, create it
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Open the file for writing
        with open(file_path, 'w') as file:
            file.write('[')  # Add opening bracket

            # Write the solution rows in the required format
            for store_id, warehouse_allocations in enumerate(self.allocation):
                file.write(f"({','.join(map(str, warehouse_allocations))})")

                # Add a newline after each line except the last one
                if store_id < len(self.allocation) - 1:
                    file.write('\n')

            file.write(']')  # Add closing bracket

    def shallow_copy(self):
        """Returns a shallow copy of the current instance."""

        # self.problem = problem
        # self.fitness_score = None
        #
        # # Your original allocation style (optional if you keep your current design)
        # self.allocation = []
        # self.open_warehouses = []
        #
        # # New properties for tweak_store compatibility
        # self.stores = []             # list of Store objects
        # self.warehouses = []         # list of Warehouse objects
        # self.incompatible_pairs = set()
        # self.count_req = 0           # used in tweak_store
        copy = self.__class__(self.problem)  # Create a new instance of the same class
        copy.problem = self.problem
        copy.allocation = self.allocation.copy()
        copy.open_warehouses = self.open_warehouses.copy()
        copy.fitness_score = self.fitness_score
        copy.stores = self.stores.copy()
        copy.warehouses = self.warehouses.copy()
        copy.incompatible_pairs = self.incompatible_pairs.copy()
        copy.count_req = self.count_req
        return copy

# Example usage:
# problem = WarehouseLocationProblem(json_data)
# solution = Solution(problem)
# solution.allocate()
# print(solution.export())
