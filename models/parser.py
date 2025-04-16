import ast
import json
from typing import List, Tuple

from models.instance_data import InstanceData
from models.solution import Solution
from models.store import Store
from models.warehouse import Warehouse


class Parser:

    def parse_instance(self, instance_file_path) -> InstanceData:
        with open(instance_file_path, 'r') as file:
            data = json.loads(file.read())

        # Initialize basic properties
        num_warehouses = data["Warehouses"]
        num_stores = data["Stores"]

        # Supply costs matrix [stores][warehouses]
        supply_costs_matrix: List[List[int]] = data["SupplyCost"]

        # Create warehouses
        warehouses: List[Warehouse] = []
        for i in range(num_warehouses):
            supply_costs = [supply_costs_matrix[s][i] for s in range(num_stores)]
            warehouse = Warehouse(
                id=i,
                capacity=data["Capacity"][i],
                fixed_cost=data["FixedCost"][i],
                supply_costs=supply_costs
            )
            warehouses.append(warehouse)

        # Create stores
        stores: List[Store] = []
        for i in range(num_stores):
            store = Store(
                id=i,
                demand=data["Goods"][i],
                supply_costs=supply_costs_matrix[i]
            )
            stores.append(store)

        # Incompatibilities (converted to 0-based indexing)
        incompatible_pairs: List[Tuple[int, int]] = [
            (pair[0] - 1, pair[1] - 1)  # Convert to 0-based
            for pair in data["IncompatiblePairs"]
        ]

        return InstanceData(num_warehouses, num_stores, supply_costs_matrix, warehouses, stores, incompatible_pairs)

    def parse_solution(self, solution_file_path: str, problem: InstanceData) -> Solution:
        """Parse the solution from the exported file format and return a Solution object."""
        with open(solution_file_path, 'r') as file:
            # Read the entire file and remove the surrounding square brackets
            file_content = file.read().strip()
            if file_content.startswith('[') and file_content.endswith(']'):
                file_content = file_content[1:-1]  # Remove leading and trailing brackets

            # Split the content into rows, each corresponding to a store's allocations
            rows = file_content.split('\n')

            # Create a Solution object, passing the problem to initialize allocations
            solution = Solution(problem)

            for store_id, row in enumerate(rows):
                # Remove parentheses and split by commas to get the allocations
                allocations = row.strip()[1:-1].split(',')
                for warehouse_id, allocation in enumerate(allocations):
                    solution.allocation[store_id][warehouse_id] = int(allocation)

            for store_alloc in solution.allocation:
                for warehouse_id, amount in enumerate(store_alloc):
                    if amount > 0:
                        solution.open_warehouses[warehouse_id] = True

        return solution