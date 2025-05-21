from typing import List


class Warehouse:
    def __init__(self, id: int, capacity: int, fixed_cost: int, supply_costs: List[int]):
        self.id = id  # 0-based index
        self.capacity = capacity
        self.fixed_cost = fixed_cost
        self.supply_costs = supply_costs
        self.open = True
        self.start_capacity = capacity

    def get_cost_to_store(self, store_id: int) -> int:
        """Get supply cost to a specific store"""
        return self.supply_costs[store_id]