from models.parser import Parser
from solver.solver import Solver
from solver.validator import Validator

def parse_instance():
    # parser = Parser("parsed_instances/toy.dzn.json")
    parser = Parser("parsed_instances/wlp01.dzn.json")
    return parser.parse()


if __name__ == "__main__":
    instance = parse_instance()
    solver = Solver(instance)
    solution = solver.solve()
    print(solution.export())
    print(Validator(instance, solution).validate())
