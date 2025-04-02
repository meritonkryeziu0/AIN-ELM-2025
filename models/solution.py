from .instance_data import InstanceData


class Solution:
    def __init__(self, problem: InstanceData):
        self.problem = problem
        self.allocation = [[0] * self.problem.num_warehouses for _ in range(self.problem.num_stores)]

    def allocate(self):
        """
        Simple greedy allocation strategy:
        - Assign each store's demand to the warehouse with the lowest supply cost
        - Ensure capacity constraints are met
        """
        warehouse_remaining_capacity = [w.capacity for w in self.problem.warehouses]

        for store in self.problem.stores:
            sorted_warehouses = sorted(
                enumerate(store.supply_costs), key=lambda x: x[1]
            )  # Sort by lowest cost
            remaining_demand = store.demand

            for w_id, _ in sorted_warehouses:
                if remaining_demand <= 0:
                    break

                if warehouse_remaining_capacity[w_id] > 0:
                    allocation = min(remaining_demand, warehouse_remaining_capacity[w_id])
                    self.allocation[store.id][w_id] = allocation
                    warehouse_remaining_capacity[w_id] -= allocation
                    remaining_demand -= allocation

    def export(self) -> str:
        """Export the solution in the required format."""
        result = []
        for store_id, warehouse_allocations in enumerate(self.allocation):
            result.append(f"({','.join(map(str, warehouse_allocations))})")
        return '\n'.join(result)

# Example usage:
# problem = WarehouseLocationProblem(json_data)
# solution = Solution(problem)
# solution.allocate()
# print(solution.export())
