from typing import List


class Store:
    def __init__(self, id: int, demand: int, supply_costs: List[int]):
        self.id = id
        self.demand = demand
        self.supply_costs = supply_costs
        self.suppliers = []
        self.warehouses_supply = []
        self.supply = 0
        self.incompatible_stores: List[int] = []

    def get_cost_from_warehouse(self, warehouse_id: int) -> int:
        """Get supply cost from a specific warehouse"""
        return self.supply_costs[warehouse_id]