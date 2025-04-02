from typing import List


class Store:
    def __init__(self, id: int, demand: int, supply_costs: List[int]):
        self.id = id  # 0-based index
        self.demand = demand
        # List of costs from each warehouse (length = num_warehouses)
        self.supply_costs = supply_costs

    def get_cost_from_warehouse(self, warehouse_id: int) -> int:
        """Get supply cost from a specific warehouse"""
        return self.supply_costs[warehouse_id]