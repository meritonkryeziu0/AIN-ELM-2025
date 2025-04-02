from models.solution import Solution


class Solver:
    def __init__(self, problem):
        self.problem = problem

    # def solve(self) -> Solution:
    #     """
    #     Simple greedy allocation strategy:
    #     - Assign each store's demand to the warehouse with the lowest supply cost
    #     - Ensure capacity constraints are met
    #     """
    #     solution = Solution(self.problem)
    #     warehouse_remaining_capacity = [w.capacity for w in self.problem.warehouses]
    #
    #     for store in self.problem.stores:
    #         sorted_warehouses = sorted(
    #             enumerate(store.supply_costs), key=lambda x: x[1]
    #         )  # Sort by lowest cost
    #         remaining_demand = store.demand
    #
    #         for w_id, _ in sorted_warehouses:
    #             if remaining_demand <= 0:
    #                 break
    #
    #             if warehouse_remaining_capacity[w_id] > 0:
    #                 allocation = min(remaining_demand, warehouse_remaining_capacity[w_id])
    #                 solution.allocation[store.id][w_id] = allocation
    #                 warehouse_remaining_capacity[w_id] -= allocation
    #                 remaining_demand -= allocation
    #
    #     return solution

    def solve(self) -> Solution:
        """
        Simple greedy allocation strategy:
        - Assign each store's demand to the warehouse with the lowest supply cost
        - Ensure capacity constraints are met
        - Enforce incompatible pairs constraint
        """
        solution = Solution(self.problem)
        warehouse_remaining_capacity = [w.capacity for w in self.problem.warehouses]
        warehouse_assignments = {w_id: set() for w_id in range(self.problem.num_warehouses)}

        for store in self.problem.stores:
            sorted_warehouses = sorted(
                enumerate(store.supply_costs), key=lambda x: x[1]
            )  # Sort by lowest cost
            remaining_demand = store.demand

            for w_id, _ in sorted_warehouses:
                if remaining_demand <= 0:
                    break

                # Check if assigning this store to this warehouse violates incompatibilities
                incompatible = any(
                    (store.id, other) in self.problem.incompatible_pairs or
                    (other, store.id) in self.problem.incompatible_pairs
                    for other in warehouse_assignments[w_id]
                )
                if incompatible:
                    continue

                if warehouse_remaining_capacity[w_id] > 0:
                    allocation = min(remaining_demand, warehouse_remaining_capacity[w_id])
                    solution.allocation[store.id][w_id] = allocation
                    warehouse_remaining_capacity[w_id] -= allocation
                    remaining_demand -= allocation
                    warehouse_assignments[w_id].add(store.id)

        return solution

    def export_solution(self) -> str:
        """Export the solution in the required format."""
        solution = self.solve()
        return solution.export()

# Example usage:
# problem = WarehouseLocationProblem(json_data)
# solver = Solver(problem)
# solution = solver.solve()
# print(solution.export())