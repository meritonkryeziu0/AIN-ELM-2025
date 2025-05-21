from typing import List

from models.store import Store
from models.warehouse import Warehouse


class InstanceData:

    def __init__(self, num_warehouses, num_stores, supply_costs_matrix, warehouses, stores: List[Store], incompatible_pairs):
        self.num_warehouses = num_warehouses
        self.num_stores = num_stores
        self.supply_costs_matrix = supply_costs_matrix
        self.warehouses = warehouses
        self.stores = stores
        self.incompatible_pairs = incompatible_pairs
        self.total_capacity = sum(w.capacity for w in warehouses)


    def summary(self) -> str:
        """Return a summary of the problem instance"""
        total_capacity = sum(w.capacity for w in self.warehouses)
        total_demand = sum(s.demand for s in self.stores)

        return (f"Warehouses: {self.num_warehouses}\n"
                f"Stores: {self.num_stores}\n"
                f"Total Capacity: {total_capacity}\n"
                f"Total Demand: {total_demand}\n"
                f"Incompatible Pairs (0-based): {self.incompatible_pairs}")
