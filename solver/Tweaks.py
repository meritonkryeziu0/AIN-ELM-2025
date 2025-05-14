from typing import Optional

from models.instance_data import InstanceData
from models.solution import Solution


class Tweaks:
    @staticmethod
    def try_shift_store(solution: Solution, store_id: int, from_w: int, to_w: int) -> bool:
        # Try moving allocation for a store from warehouse A to B
        allocation = solution.allocation[store_id]
        demand_shift = allocation[from_w]
        if demand_shift == 0:
            return False

        # Check capacity and incompatibility
        if solution.problem.warehouses[to_w].capacity < demand_shift:
            return False

        # Apply move if valid
        allocation[to_w] += demand_shift
        allocation[from_w] = 0
        # update open_warehouses, capacities, etc.
        return True

    def move_store_allocation(solution: Solution, instance: InstanceData) -> Optional[Solution]:
        for store in instance.stores:
            current_alloc = solution.allocation[store.id]

            for src_warehouse_id, amount in enumerate(current_alloc):
                if amount == 0:
                    continue

                for dst_warehouse_id in range(instance.num_warehouses):
                    if dst_warehouse_id == src_warehouse_id:
                        continue

                    # Check capacity
                    dst_capacity_used = sum(solution.allocation[s.id][dst_warehouse_id] for s in instance.stores)
                    if dst_capacity_used + amount > instance.warehouses[dst_warehouse_id].capacity:
                        continue

                    # Check incompatibility
                    if (store.id, dst_warehouse_id) in instance.incompatible_pairs or (
                            dst_warehouse_id, store.id) in instance.incompatible_pairs:
                        continue

                    # Apply move to a new solution
                    new_solution = solution.shallow_copy()
                    new_solution.allocation[store.id][src_warehouse_id] -= amount
                    new_solution.allocation[store.id][dst_warehouse_id] += amount
                    new_solution.open_warehouses[src_warehouse_id] = any(
                        new_solution.allocation[s.id][src_warehouse_id] > 0 for s in instance.stores
                    )
                    new_solution.open_warehouses[dst_warehouse_id] = True
                    new_solution.fitness()
                    if new_solution.fitness() < solution.fitness():
                        return new_solution

        return solution  # No better neighbor found

    @staticmethod
    def tweak_with_iterations(solution: Solution, data: InstanceData, iterations=1000) -> Solution:
        for i in range(iterations - 1):
            solution_copy = solution.shallow_copy()
            tweaked = Tweaks.move_store_allocation(solution_copy, data)

            if tweaked.fitness_score >= solution.fitness_score:
                solution = tweaked

        return solution
