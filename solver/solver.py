from models.solution import Solution


class Solver:
    def __init__(self, problem):
        self.problem = problem

    def solve1(self) -> Solution:
        """
        Simple greedy allocation strategy:
        - Assign each store's demand to the warehouse with the lowest supply cost
        - Ensure capacity constraints are met
        """
        solution = Solution(self.problem)
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
                    solution.allocation[store.id][w_id] = allocation
                    warehouse_remaining_capacity[w_id] -= allocation
                    remaining_demand -= allocation

        solution.fitness()
        return solution

    def solve1(self) -> Solution:
        """
        Greedy allocation strategy with constraints:
        1. Don't exceed warehouse capacity
        2. Fully satisfy store demand
        3. Only use open warehouses for supply
        4. No incompatible stores in the same warehouse
        """
        solution = Solution(self.problem)
        warehouse_remaining_capacity = [w.capacity for w in self.problem.warehouses]
        warehouse_assignments = {w_id: set() for w_id in range(self.problem.num_warehouses)}

        for store in self.problem.stores:
            sorted_warehouses = sorted(
                enumerate(store.supply_costs), key=lambda x: x[1]
            )
            remaining_demand = store.demand

            for w_id, _ in sorted_warehouses:
                if remaining_demand <= 0:
                    break

                # Skip warehouse if assigning would create an incompatible pairing
                if any(
                        (store.id, other) in self.problem.incompatible_pairs or
                        (other, store.id) in self.problem.incompatible_pairs
                        for other in warehouse_assignments[w_id]
                ):
                    continue

                # Skip if no capacity left
                if warehouse_remaining_capacity[w_id] <= 0:
                    continue

                allocation = min(remaining_demand, warehouse_remaining_capacity[w_id])
                solution.allocation[store.id][w_id] = allocation
                warehouse_remaining_capacity[w_id] -= allocation
                remaining_demand -= allocation
                warehouse_assignments[w_id].add(store.id)

                # Mark warehouse as open
                solution.open_warehouses[w_id] = True

            # Constraint 2: Store demand must be fully satisfied
            if remaining_demand > 0:
                raise ValueError(f"Could not fully satisfy store {store.id}'s demand.")

        return solution

    def solve(self) -> Solution:
        """
        Greedy allocation strategy with constraints:
        1. Don't exceed warehouse capacity
        2. Fully satisfy store demand
        3. Only use open warehouses for supply
        4. No incompatible stores in the same warehouse
        """
        solution = Solution(self.problem)
        warehouse_remaining_capacity = [w.capacity for w in self.problem.warehouses]

        # Track stores already assigned to a warehouse
        warehouse_assignments = {w_id: set() for w_id in range(self.problem.num_warehouses)}

        # Precompute incompatibility map for fast lookup
        incompatible_map = {s.id: set() for s in self.problem.stores}
        for s1, s2 in self.problem.incompatible_pairs:
            incompatible_map[s1].add(s2)
            incompatible_map[s2].add(s1)

        for store in self.problem.stores:
            sorted_warehouses = sorted(
                enumerate(store.supply_costs), key=lambda x: x[1]
            )
            remaining_demand = store.demand

            for w_id, _ in sorted_warehouses:
                if remaining_demand <= 0:
                    break

                # Check for any incompatible store already assigned to this warehouse
                if warehouse_assignments[w_id] & incompatible_map[store.id]:
                    continue

                # Skip if no capacity left
                if warehouse_remaining_capacity[w_id] <= 0:
                    continue

                allocation = min(remaining_demand, warehouse_remaining_capacity[w_id])
                if allocation > 0:
                    solution.allocation[store.id][w_id] = allocation
                    warehouse_remaining_capacity[w_id] -= allocation
                    remaining_demand -= allocation

                    warehouse_assignments[w_id].add(store.id)
                    solution.open_warehouses[w_id] = True

            # Store demand must be fully satisfied
            if remaining_demand > 0:
                raise ValueError(
                    f"Could not fully satisfy store {store.id}'s demand due to capacity or incompatibility.")

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