import math
import random
from typing import Optional

from models.instance_data import InstanceData
from models.solution import Solution
from models.store import Store
from models.supply_req import SupplyReq
from models.warehouse import Warehouse


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

    def tweak_warehouse(instance: InstanceData) -> Solution:
        # Copy of the original state (as the old solution)
        old_instance = InstanceData(
            num_warehouses=instance.num_warehouses,
            num_stores=instance.num_stores,
            supply_costs_matrix=instance.supply_costs_matrix,
            warehouses=[Warehouse(w.id, w.capacity, w.fixed_cost, w.supply_costs) for w in instance.warehouses],
            stores=[Store(s.id, s.demand, s.supply_costs) for s in instance.stores],
            incompatible_pairs=set(instance.incompatible_pairs)
        )

        # Sort open warehouses by fixed cost (descending) and then by start capacity (ascending)
        open_warehouses = sorted(
            [w for w in instance.warehouses if w.open],
            key=lambda w: (-w.fixed_cost, w.start_capacity)
        )

        # Randomly select one warehouse
        rnd_warehouse = random.choice(open_warehouses)
        old_warehouse = next((w for w in instance.warehouses if w.id == rnd_warehouse.id), None)

        stores_with_suppliers = [s for s in instance.stores if any(sup.id == old_warehouse.id for sup in s.suppliers)]

        all_supply_request = 0

        # Loop through stores with the old warehouse as a supplier
        for store in stores_with_suppliers:
            remaining_demand = store.demand
            all_supply_request += store.demand

            if remaining_demand <= instance.num_warehouses:  # Compare demand with warehouse capacity
                # Order and remove the previous supply costs
                for idx, cost in enumerate(store.supply_costs):
                    warehouse = next((w for w in instance.warehouses if w.id == idx), None)
                    if warehouse:
                        warehouse.supply_costs[idx] = cost  # Update supply cost to warehouse

                # Filter warehouses that can potentially supply this store
                eligible_warehouses = sorted(
                    [w for w in instance.warehouses if not any(sup.id == w.id for sup in store.suppliers) and w.open],
                    key=lambda w: (w.capacity, w.fixed_cost)
                )

                store.suppliers = []
                store.warehouses_supply = []

                for warehouse in eligible_warehouses:
                    if remaining_demand == 0:
                        break

                    supply_amount = 0
                    if warehouse.capacity > 0 and f"{warehouse.id},{store.id}" not in instance.incompatible_pairs:
                        if warehouse.capacity >= remaining_demand:
                            supply_amount = remaining_demand
                        else:
                            supply_amount = warehouse.capacity

                        remaining_demand -= supply_amount
                        all_supply_request -= supply_amount
                        warehouse.capacity -= supply_amount

                        store.suppliers.append(warehouse)
                        store.warehouses_supply.append((warehouse, supply_amount))

                        # Add incompatible pairs
                        for incompatible_store in store.suppliers:
                            instance.incompatible_pairs.add(f"{warehouse.id},{incompatible_store.id}")

        if all_supply_request == 0:
            # If all supply requests have been fulfilled, update incompatible pairs
            for store in instance.stores:
                for supplier in store.suppliers:
                    for incompatible_store in store.suppliers:
                        instance.incompatible_pairs.add(f"{supplier.id},{incompatible_store.id}")

            old_warehouse.open = False

            # Return a new Solution object with the updated problem state
            sol = Solution(problem=instance)
            sol.fitness()
            return sol
        else:
            # Return a Solution object with the original problem state if supply wasn't fulfilled
            sol = Solution(problem=old_instance)
            sol.fitness()
            return sol

    def tweak_store(sol: Solution) -> Solution:
        # Deep copy the solution (like new ProSolution with copied fields)
        oldsol = sol.shallow_copy()

        rnd = random.Random()
        random_index = rnd.randint(0, len(sol.problem.stores) - 1)
        store = sol.problem.stores[random_index]

        ncost = sol.fitness()

        # Return capacity from current suppliers of store
        for w in store.suppliers:
            # Find the supplyreq for this warehouse in store.warehouses_supply
            supplyreq_obj = next((x for x in store.warehouses_supply if x.warehouse.id == w.id), None)
            if supplyreq_obj is None:
                continue
            supplyreq = supplyreq_obj.supplyreq

            # Find corresponding warehouse in solution
            wr = next((x for x in sol.problem.warehouses if x.id == w.id), None)
            if wr:
                wr.capacity += supplyreq
                ncost -= store.supply_costs[w.id] * supplyreq

                if wr.capacity == wr.start_capacity:
                    wr.open = False
                    # Subtract fixed cost if warehouse closed
                    orig_wr = next((x for x in oldsol.warehouses if x.id == wr.id), None)
                    if orig_wr:
                        ncost -= orig_wr.fixed_cost

        # Extract incompatible pairs for this store only
        storeinc = {p for p in sol.problem.incompatible_pairs if str(store.id) in p}

        # Clear incompatible pairs in solution to rebuild
        sol.incompatible_pairs = set()

        # Update supply_for_store for warehouses based on this store's supply costs
        for wid, cost_val in enumerate(store.supply_costs):
            wr = next((w for w in sol.problem.warehouses if w.id == wid), None)
            if wr:
                wr.supply_for_store = int(cost_val)

        # Get warehouses sorted by supply_for_store and exclude those already supplying store and those closed
        warehouses = sorted(
            [w for w in sol.problem.warehouses if w.open and w.id not in {s.id for s in store.suppliers}],
            key=lambda w: w.supply_for_store
        )

        req = int(store.demand)

        # Reset suppliers and warehouses_supply for this store
        store.suppliers = []
        store.warehouses_supply = []

        # Prepare requests list (only one request as per your original code)
        request_list = [int(store.demand)]  # could be randomized if needed

        sol.count_req = int(store.demand)

        for request in request_list:
            for wr in warehouses[:]:  # copy of list so we can remove
                # Skip incompatible warehouse-store pair
                if f"{wr.id},{store.id}" in storeinc:
                    continue

                if wr.capacity >= request:
                    wr.capacity -= request
                    store.supply = store.supply_costs[wr.id]
                    store.suppliers.append(wr)
                    store.warehouses_supply.append(SupplyReq(wr, request))

                    sol.count_req -= request
                    req -= request

                    # Add all incompatible pairs for this store
                    for incompatible_store in store.incompatible_stores:
                        sol.incompatible_pairs.add(f"{wr.id},{incompatible_store}")

                    warehouses.remove(wr)
                    break

        # Rebuild incompatible pairs for all stores and their suppliers
        for s in sol.stores:
            for wrs in s.suppliers:
                for incompatible_store in s.incompatible_stores:
                    sol.incompatible_pairs.add(f"{wrs.id},{incompatible_store}")

        # If request not fulfilled, return old solution and cost
        if req != 0:
            return oldsol
        else:
            # Calculate new cost by adding supply costs for this store's suppliers
            for i in range(len(store.suppliers)):
                w = store.suppliers[i]
                supplyreq_obj = next((x for x in store.warehouses_supply if x.warehouse.id == w.id), None)
                if supplyreq_obj:
                    ncost += store.supply_costs[w.id] * supplyreq_obj.supplyreq

            sol.fitness()
            return sol

    @staticmethod
    def tweak_with_iterations(solution: Solution, data: InstanceData, iterations=1000) -> Solution:
        for i in range(iterations - 1):
            solution_copy = solution.shallow_copy()
            tweaked = Tweaks.tweak_store(solution_copy)

            if tweaked.fitness_score >= solution.fitness_score:
                solution = tweaked

        return solution

    def tweak_store1(sol: Solution, max_store_tweaks: int = 3) -> Solution:
        # Deep copy the original solution for rollback
        oldsol = sol.shallow_copy()
        rnd = random.Random()

        store_indices = rnd.sample(range(len(sol.problem.stores)), k=min(max_store_tweaks, len(sol.problem.stores)))
        ncost = sol.fitness_score

        for idx in store_indices:
            store = sol.problem.stores[idx]

            # Release supply from current suppliers
            for w in store.suppliers:
                supplyreq_obj = next((x for x in store.warehouses_supply if x.warehouse.id == w.id), None)
                if supplyreq_obj:
                    wr = next((x for x in sol.problem.warehouses if x.id == w.id), None)
                    if wr:
                        wr.capacity += supplyreq_obj.supplyreq
                        ncost -= store.supply_costs[w.id] * supplyreq_obj.supplyreq

                        if wr.capacity == wr.start_capacity:
                            wr.open = False
                            ncost -= wr.fixed_cost

            # Clear store assignments
            store.suppliers = []
            store.warehouses_supply = []

            # Extract incompatible pairs for this store
            storeinc = {p for p in sol.problem.incompatible_pairs if str(store.id) in p}

            # Rebuild supply cost ranking
            for wid, cost_val in enumerate(store.supply_costs):
                wr = next((w for w in sol.problem.warehouses if w.id == wid), None)
                if wr:
                    wr.supply_for_store = int(cost_val)

            # Allow both open and closed warehouses for reallocation
            warehouses = sorted(
                [w for w in sol.problem.warehouses if w.id not in {s.id for s in store.suppliers}],
                key=lambda w: w.supply_for_store
            )

            req = int(store.demand)
            sol.count_req = req

            # Reallocate demand
            for wr in warehouses[:]:
                if f"{wr.id},{store.id}" in storeinc:
                    continue

                if wr.capacity >= req:
                    wr.capacity -= req
                    wr.open = True
                    store.supply = store.supply_costs[wr.id]
                    store.suppliers.append(wr)
                    store.warehouses_supply.append(SupplyReq(wr, req))
                    ncost += store.supply_costs[wr.id] * req
                    if wr.capacity + req == wr.start_capacity:
                        ncost += wr.fixed_cost

                    # Add incompatibilities
                    for incompatible_store in store.incompatible_stores:
                        sol.incompatible_pairs.add(f"{wr.id},{incompatible_store}")

                    break

            # If demand wasn't satisfied, rollback immediately
            if not store.suppliers:
                return oldsol

        sol.fitness_score = ncost
        return sol

    @staticmethod
    def tweak_with_iterations1(solution: Solution, data: InstanceData, iterations=1000) -> Solution:
        current = solution
        best = solution
        temp = 100.0

        for i in range(iterations):
            candidate = Tweaks.tweak_store(current.shallow_copy())

            delta = candidate.fitness_score - current.fitness_score

            # Accept candidate if better or probabilistically
            if delta > 0 or math.exp(delta / temp) > random.random():
                current = candidate

            # Update best if improved
            if current.fitness_score > best.fitness_score:
                best = current

            # Cool down temperature
            temp *= 0.995

        return best
