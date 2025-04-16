import os
from .instance_data import InstanceData


# class Solution:
#     def __init__(self, problem: InstanceData):
#         self.problem = problem
#         self.allocation = [[0] * self.problem.num_warehouses for _ in range(self.problem.num_stores)]
#
#     def fitness(self) -> int:
#         total_fixed_cost = 0
#         total_supply_cost = 0
#         used_warehouses = set()
#
#         for store_id, allocations in enumerate(self.allocation):
#             for warehouse_id, amount in enumerate(allocations):
#                 if amount > 0:
#                     used_warehouses.add(warehouse_id)
#                     supply_cost = self.problem.supply_costs_matrix[store_id][warehouse_id]
#                     total_supply_cost += amount * supply_cost
#
#         total_fixed_cost = sum(
#             self.problem.warehouses[w_id].fixed_cost for w_id in used_warehouses
#         )
#
#         return total_fixed_cost + total_supply_cost
#
#     def export(self) -> str:
#         """Export the solution in the required format."""
#         result = []
#         for store_id, warehouse_allocations in enumerate(self.allocation):
#             result.append(f"({','.join(map(str, warehouse_allocations))})")
#         return '\n'.join(result)

class Solution:

    # def __init__(self, problem: InstanceData):
    #     self.problem = problem
    #     self.allocation = [[0] * self.problem.num_warehouses for _ in range(self.problem.num_stores)]
    #     self.open_warehouses = [False] * self.problem.num_warehouses

    def __init__(self, problem: InstanceData = None):
        """ Initialize with an optional InstanceData problem. """
        if problem is not None:
            self.problem = problem
            self.allocation = [[0] * self.problem.num_warehouses for _ in range(self.problem.num_stores)]
            self.open_warehouses = [False] * self.problem.num_warehouses
        else:
            self.problem = None  # If no problem, set it to None
            self.allocation = []  # Empty allocation
            self.open_warehouses = []  # Empty warehouse list

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

    def fitness(self) -> int:
        total_fixed_cost = 0
        total_supply_cost = 0
        used_warehouses = set()

        for store_id, allocations in enumerate(self.allocation):
            for warehouse_id, amount in enumerate(allocations):
                if amount > 0:
                    used_warehouses.add(warehouse_id)
                    supply_cost = self.problem.supply_costs_matrix[store_id][warehouse_id]
                    total_supply_cost += amount * supply_cost

        total_fixed_cost = sum(
            self.problem.warehouses[w_id].fixed_cost for w_id in used_warehouses
        )

        return total_fixed_cost + total_supply_cost

    # def export(self) -> str:
    #     """Export the solution in the required format."""
    #     result = []
    #     for store_id, warehouse_allocations in enumerate(self.allocation):
    #         result.append(f"({','.join(map(str, warehouse_allocations))})")
    #     return '\n'.join(result)

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

# Example usage:
# problem = WarehouseLocationProblem(json_data)
# solution = Solution(problem)
# solution.allocate()
# print(solution.export())
