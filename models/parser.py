import json
from typing import List, Tuple

from models.instance_data import InstanceData
from models.store import Store
from models.warehouse import Warehouse


class Parser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        with open(self.file_path, 'r') as file:
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
