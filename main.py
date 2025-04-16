from models.parser import Parser
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

        solver = Solver(instance)
        solution = solver.solve()

        output_path = f"output/{file_path.split('/')[-1].replace('.dzn.json', '.txt')}"
        solution.export(output_path)

        is_valid = Validator(instance, solution).validate()

        print(f"Solution score: {solution.fitness()}")
        print(f"Exported to: {output_path}")
        print(f"Valid: {'Yes' if is_valid else 'No'}")


if __name__ == "__main__":

    for file_path in instance_files:
        instance = parser.parse_instance(file_path)
        solution = parser.parse_solution("output/" + file_path.split("/")[1].split(".")[0] + ".txt", instance)
        print(Validator(instance, solution).validate())