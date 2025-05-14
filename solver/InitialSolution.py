from typing import List, Tuple, Dict, Set

from models.instance_data import InstanceData
from models.solution import Solution
from models.store import Store
from models.warehouse import Warehouse


class InitialSolution:
    def __init__(self, instance: InstanceData):
        self.instance = instance
        self.num_warehouses = instance.num_warehouses
        self.num_stores = instance.num_stores
        self.warehouses: List[Warehouse] = instance.warehouses
        self.stores: List[Store] = instance.stores
        self.incompatible_pairs: Set[Tuple[int, int]] = set(tuple(sorted(pair)) for pair in instance.incompatible_pairs )

        # Allocation: store_id -> warehouse_id -> allocated_amount
        self.allocation: List[Dict[int, int]] = [{} for _ in range(self.num_stores)]
        self.warehouse_remaining_capacity = {w.id: w.capacity for w in self.warehouses}
        self.open_warehouses = set()
        self.warehouse_assignments: Dict[int, Set[int]] = {w.id: set() for w in self.warehouses}

    def is_compatible(self, warehouse_id: int, store_id: int) -> bool:
        """Check if a store can be assigned to a warehouse without violating incompatibility constraints"""
        current_assigned_stores = self.warehouse_assignments[warehouse_id]
        for assigned_store in current_assigned_stores:
            pair = tuple(sorted((store_id, assigned_store)))
            if pair in self.incompatible_pairs:
                return False
        return True

    def generate_valid_solution(self) -> Solution:
        solution = Solution(self.instance)

        # Track current warehouse capacity used
        warehouse_capacity_used = [0] * self.instance.num_warehouses

        # Track which stores are assigned to which warehouses
        warehouse_store_map = {w.id: set() for w in self.instance.warehouses}

        for store in self.instance.stores:
            assigned = False
            # Try to assign to warehouses in order of increasing supply cost
            sorted_warehouses = sorted(self.instance.warehouses, key=lambda w: store.get_cost_from_warehouse(w.id))

            for warehouse in sorted_warehouses:
                w_id = warehouse.id
                # Check for incompatibility with already assigned stores in this warehouse
                if any((store.id, other) in self.instance.incompatible_pairs or (
                other, store.id) in self.instance.incompatible_pairs
                       for other in warehouse_store_map[w_id]):
                    continue

                if warehouse_capacity_used[w_id] + store.demand <= warehouse.capacity:
                    # Assign the entire store demand to this warehouse
                    solution.allocation[store.id][w_id] = store.demand
                    solution.open_warehouses[w_id] = True
                    warehouse_capacity_used[w_id] += store.demand
                    warehouse_store_map[w_id].add(store.id)
                    assigned = True
                    break

            if not assigned:
                raise ValueError(f"Could not assign store {store.id} to any warehouse without violating constraints")

        return solution

    def get_solution_summary(self):
        return {
            "open_warehouses": sorted(list(self.open_warehouses)),
            "allocations": self.allocation
        }
