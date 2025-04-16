from models.instance_data import InstanceData
from models.solution import Solution


class Validator:
    def __init__(self, problem: InstanceData, solution: Solution):
        self.problem = problem
        self.solution = solution

    def validate(self) -> bool:
        """Check if the solution is valid."""
        # Validate capacity constraints
        warehouse_used_capacity = [0] * self.problem.num_warehouses

        for store_id, allocations in enumerate(self.solution.allocation):
            store_demand = self.problem.stores[store_id].demand
            allocated_sum = sum(allocations)

            if allocated_sum != store_demand:
                print(f"Invalid allocation for store {store_id}: allocated {allocated_sum}, required {store_demand}")
                return False

            for w_id, allocation in enumerate(allocations):
                warehouse_used_capacity[w_id] += allocation

        # Validate warehouse capacity constraints
        for w_id, used in enumerate(warehouse_used_capacity):
            if used > self.problem.warehouses[w_id].capacity:
                print(
                    f"Warehouse {w_id} exceeded capacity: used {used}, capacity {self.problem.warehouses[w_id].capacity}")
                return False

        # Validate incompatibilities
        for s1, s2 in self.problem.incompatible_pairs:
            for w_id in range(self.problem.num_warehouses):
                if self.solution.allocation[s1][w_id] > 0 and self.solution.allocation[s2][w_id] > 0:
                    print(f"Incompatible stores {s1} and {s2} assigned to warehouse {w_id}")
                    return False

        # Validate open warehouses condition
        for store_id, allocations in enumerate(self.solution.allocation):
            for w_id, allocation in enumerate(allocations):
                if allocation > 0 and not self.solution.open_warehouses[w_id]:
                    print(f"Store {store_id} is being supplied by a closed warehouse {w_id}")
                    return False

        return True

# Example usage:
# validator = Validator(problem, solution)
# print("Solution is valid:" if validator.validate() else "Solution is invalid")
