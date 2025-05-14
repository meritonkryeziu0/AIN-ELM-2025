from models.parser import Parser
from solver.InitialSolution import InitialSolution
from solver.Tweaks import Tweaks
from solver.solver import Solver
from solver.validator import Validator


parser = Parser()

instance_files = [
        "parsed_instances/wlp01.dzn.json",
        "parsed_instances/wlp02.dzn.json",
        "parsed_instances/wlp03.dzn.json",
        "parsed_instances/wlp04.dzn.json",
    ]


if __name__ == "__main__":

    for file_path in instance_files:
        print(f"Solving instance: {file_path}")

        instance = parser.parse_instance(file_path)

        # solver = Solver(instance)
        # initial_solution = solver.solve()

        init = InitialSolution(instance)
        sol = init.generate_valid_solution()

        improved = Tweaks.move_store_allocation(sol, instance)

        # output_path = f"output/{file_path.split('/')[-1].replace('.dzn.json', '.txt')}"
        # initial_solution.export(output_path)

        is_valid = Validator(instance, sol).validate()
        # is_valid = Validator(instance, improved).validate()

        print(f"Initial score: {sol.fitness_score}")
        print(f"Solution score: {improved.fitness_score}")
        # print(f"Exported to: {output_path}")
        print(f"Valid: {'Yes' if is_valid else 'No'}")


# if __name__ == "__main__":
#
#     for file_path in instance_files:
#         instance = parser.parse_instance(file_path)
#         initial_solution = parser.parse_solution("output/" + file_path.split("/")[1].split(".")[0] + ".txt", instance)
#         initial_solution.fitness()
#
#         improved = Tweaks.move_store_allocation(initial_solution, instance)
#         print(improved.fitness_score)
#         print(Validator(instance, improved).validate())