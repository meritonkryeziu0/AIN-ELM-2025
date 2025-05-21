from models.instance_data import InstanceData
from models.solution import Solution
from models.supply_req import SupplyReq


class Solver:
    def __init__(self, problem):
        self.problem = problem

    # @staticmethod
    # def initial_solution(instance: InstanceData) -> Solution:
    #     # Create a set to store incompatible pairs
    #     incompatible_pairs = set()
    #
    #     # Assign goods to stores
    #     for store in instance.stores:
    #         # Set supplyForStore for each warehouse based on this store's supply cost
    #         for i, cost in enumerate(store.supply_costs):
    #             sol_warehouse = instance.warehouses[i]
    #             sol_warehouse.supply_for_store = int(cost)
    #             sol_warehouse = next((w for w in instance.warehouses if w.id == i), None)
    #             if sol_warehouse:
    #                 sol_warehouse.supply_for_store = int(cost)
    #
    #         # Sort warehouses by supply cost
    #         instance.warehouses.sort(key=lambda w: w.supply_for_store)
    #
    #         for warehouse in instance.warehouses:
    #             # Skip incompatible warehouse-store pair
    #             if f"{warehouse.id},{store.id}" in incompatible_pairs:
    #                 continue
    #
    #             if warehouse.capacity >= store.demand:
    #                 warehouse.open = True
    #                 instance.total_capacity -= store.demand
    #                 warehouse.capacity -= store.demand
    #                 store.supply = store.supply_costs[warehouse.id]
    #                 store.suppliers.append(warehouse)
    #                 store.warehouses_supply.append(SupplyReq(warehouse, store.demand))
    #
    #                 # Mark all incompatible pairs for this store
    #                 for inc_store in store.incompatible_stores:
    #                     incompatible_pairs.add(f"{warehouse.id},{inc_store}")
    #                 break
    #
    #     instance.incompatible_pairs = incompatible_pairs
    #     return instance

    @staticmethod
    def initial_solution1(instance: InstanceData) -> Solution:
        solution = Solution(instance)
        incompatible_pairs = set()

        # Track how much capacity each warehouse has used (instead of mutating warehouse objects)
        used_capacity = [0] * instance.num_warehouses

        for store in instance.stores:
            # Sort warehouses by cost to this store
            sorted_warehouses = sorted(
                instance.warehouses,
                key=lambda w: store.supply_costs[w.id]
            )

            for warehouse in sorted_warehouses:
                pair_key = f"{warehouse.id},{store.id}"
                if pair_key in incompatible_pairs:
                    continue

                if used_capacity[warehouse.id] + store.demand <= warehouse.capacity:
                    # Assign the store to this warehouse
                    used_capacity[warehouse.id] += store.demand
                    solution.allocation[store.id][warehouse.id] = store.demand
                    solution.open_warehouses[warehouse.id] = True

                    # Optional: track per-store metadata
                    store.suppliers.append(warehouse)
                    store.warehouses_supply.append(SupplyReq(warehouse, store.demand))

                    # Mark warehouse as incompatible with incompatible stores
                    for inc_store_id in store.incompatible_stores:
                        incompatible_pairs.add(f"{warehouse.id},{inc_store_id}")
                    break  # assignment done

        solution.fitness()

        return solution

    @staticmethod
    def initial_solution2(instance: InstanceData) -> Solution:
        solution = Solution(instance)
        incompatible_pairs = set()

        used_capacity = [0] * instance.num_warehouses

        for store in instance.stores:
            demand_left = store.demand

            # Sort warehouses by cost to this store
            sorted_warehouses = sorted(
                instance.warehouses,
                key=lambda w: store.supply_costs[w.id]
            )

            for warehouse in sorted_warehouses:
                pair_key = f"{warehouse.id},{store.id}"
                if pair_key in incompatible_pairs:
                    continue

                # Calculate how much capacity is left in this warehouse
                capacity_left = warehouse.capacity - used_capacity[warehouse.id]

                if capacity_left <= 0:
                    continue  # no capacity left here

                # Assign the minimum of demand left or capacity left
                supply_amount = min(demand_left, capacity_left)

                # Assign to solution
                used_capacity[warehouse.id] += supply_amount
                solution.allocation[store.id][warehouse.id] = supply_amount
                solution.open_warehouses[warehouse.id] = True

                # Update metadata
                store.suppliers.append(warehouse)
                store.warehouses_supply.append(SupplyReq(warehouse, supply_amount))

                # Mark incompatible pairs
                for inc_store_id in store.incompatible_stores:
                    incompatible_pairs.add(f"{warehouse.id},{inc_store_id}")

                demand_left -= supply_amount

                if demand_left <= 0:
                    break  # done with this store

            if demand_left > 0:
                # Could not fully assign demand, solution invalid or partial
                # Optionally handle or log this
                print(f"Warning: Could not fully allocate store {store.id} demand: {demand_left} units left unassigned")

        solution.fitness()

        return solution

    @staticmethod
    def initial_solution(instance: InstanceData) -> Solution:
        solution = Solution(instance)
        incompatible_pairs = set()

        for store in instance.stores:
            store.suppliers.clear()
            store.warehouses_supply.clear()

            # Sort warehouses by cost to this store
            sorted_warehouses = sorted(
                instance.warehouses,
                key=lambda w: store.supply_costs[w.id]
            )

            for warehouse in sorted_warehouses:
                pair_key = f"{warehouse.id},{store.id}"
                if pair_key in incompatible_pairs:
                    continue

                if warehouse.capacity >= store.demand:
                    # Mutate actual warehouse capacity (just like in C#)
                    warehouse.capacity -= store.demand

                    # Assign the store to this warehouse
                    solution.allocation[store.id][warehouse.id] = store.demand
                    solution.open_warehouses[warehouse.id] = True

                    # Track store-warehouse relationship
                    store.suppliers.append(warehouse)
                    store.warehouses_supply.append(SupplyReq(warehouse, store.demand))

                    # Add incompatible pairs
                    for inc_store_id in store.incompatible_stores:
                        incompatible_pairs.add(f"{warehouse.id},{inc_store_id}")
                    break  # stop after first valid assignment

        solution.fitness()

        return solution

    @staticmethod
    def evaluate_solution(stores, warehouses):
        total_cost = 0
        warehouses_added = set()

        for store in stores:
            for supplier in store.suppliers:
                if supplier.id not in warehouses_added:
                    total_cost += next(w.fixed_cost for w in warehouses if w.id == supplier.id)
                    warehouses_added.add(supplier.id)

                supply_req = next(ws.supplyreq for ws in store.warehouses_supply if ws.warehouse.id == supplier.id)
                total_cost += store.supply_costs[supplier.id] * supply_req

        return total_cost

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