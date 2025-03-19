from typing import List, Tuple
import json


class Warehouse:
    def __init__(self, id: int, capacity: int, fixed_cost: int, supply_costs: List[int]):
        self.id = id  # 0-based index
        self.capacity = capacity
        self.fixed_cost = fixed_cost
        self.supply_costs = supply_costs

    def get_cost_to_store(self, store_id: int) -> int:
        """Get supply cost to a specific store"""
        return self.supply_costs[store_id]


class Store:
    def __init__(self, id: int, demand: int, supply_costs: List[int]):
        self.id = id  # 0-based index
        self.demand = demand
        # List of costs from each warehouse (length = num_warehouses)
        self.supply_costs = supply_costs

    def get_cost_from_warehouse(self, warehouse_id: int) -> int:
        """Get supply cost from a specific warehouse"""
        return self.supply_costs[warehouse_id]


class WarehouseLocationProblem:
    def __init__(self, json_data: str):
        # Parse JSON data
        data = json.loads(json_data)

        # Initialize basic properties
        self.num_warehouses = data["Warehouses"]
        self.num_stores = data["Stores"]

        # Supply costs matrix [stores][warehouses]
        self.supply_costs_matrix: List[List[int]] = data["SupplyCost"]

        # Create warehouses
        self.warehouses: List[Warehouse] = []
        for i in range(self.num_warehouses):
            supply_costs = [self.supply_costs_matrix[s][i] for s in range(self.num_stores)]
            warehouse = Warehouse(
                id=i,
                capacity=data["Capacity"][i],
                fixed_cost=data["FixedCost"][i],
                supply_costs=supply_costs
            )
            self.warehouses.append(warehouse)

        # Create stores
        self.stores: List[Store] = []
        for i in range(self.num_stores):
            store = Store(
                id=i,
                demand=data["Goods"][i],
                supply_costs=self.supply_costs_matrix[i]
            )
            self.stores.append(store)

        # Incompatibilities (converted to 0-based indexing)
        self.incompatible_pairs: List[Tuple[int, int]] = [
            (pair[0] - 1, pair[1] - 1)  # Convert to 0-based
            for pair in data["IncompatiblePairs"]
        ]

    def summary(self) -> str:
        """Return a summary of the problem instance"""
        total_capacity = sum(w.capacity for w in self.warehouses)
        total_demand = sum(s.demand for s in self.stores)

        return (f"Warehouses: {self.num_warehouses}\n"
                f"Stores: {self.num_stores}\n"
                f"Total Capacity: {total_capacity}\n"
                f"Total Demand: {total_demand}\n"
                f"Incompatible Pairs (0-based): {self.incompatible_pairs}")


# Usage with your JSON instance
problem_instance = """{
  "Warehouses": 4,
  "Stores": 10,
  "Capacity": [100, 40, 60, 60],
  "FixedCost": [860, 350, 440, 580],
  "Goods": [12, 17, 5, 13, 20, 20, 17, 19, 11, 20],
  "SupplyCost": [
    [27, 66, 44, 55], [53, 89, 68, 46], [17, 40, 18, 61], [20, 68, 44, 78],
    [42, 89, 65, 78], [57, 55, 49, 31], [89, 101, 90, 16], [37, 31, 23, 55],
    [76, 60, 63, 44], [82, 107, 91, 31]
  ],
  "Incompatibilities": 3,
  "IncompatiblePairs": [[1, 10], [2, 7], [8, 9]]
}"""

# Create and demonstrate
problem = WarehouseLocationProblem(problem_instance)
print(problem.summary())

print("\nWarehouse 0 supply costs to all stores:")
print(problem.warehouses[0].supply_costs)

print("\nStore 0 supply costs from all warehouses:")
print(problem.stores[0].supply_costs)

# Demonstrate accessing specific costs
print(f"\nCost from Warehouse 1 to Store 2: {problem.warehouses[1].get_cost_to_store(2)}")
print(f"Cost to Store 3 from Warehouse 2: {problem.stores[3].get_cost_from_warehouse(2)}")