import logging
import time
from datetime import datetime

import pandas as pd
from pprint import pprint
from typing import Iterable, Any, Dict

import dill
from pyomo.core import value, Var, ConcreteModel
from pyomo.opt import SolverStatus, TerminationCondition, SolverFactory

from common.database import SessionLocal, Logdata

_log = logging.getLogger(__name__)


def save_to_db(logdata: Dict):
    session = SessionLocal()
    session.add(Logdata(**logdata))
    session.commit()


class BaseModel(object):

    SOLVER_NAME = 'cplex'
    TIME_LIMIT = 600

    if SOLVER_NAME == 'cplex':
        solver = SolverFactory("cplex", executable='~/dev/cplex/opt/cplex/bin/x86-64_linux/cplex')
        solver.options['timelimit'] = TIME_LIMIT
        # solver.options['threads'] = 1

    elif SOLVER_NAME == 'glpk':
        solver = SolverFactory(SOLVER_NAME)
        solver.options['tmlim'] = TIME_LIMIT

    elif SOLVER_NAME == 'gurobi':
        solver = SolverFactory(SOLVER_NAME)
        solver.options['TimeLimit'] = TIME_LIMIT

    elif SOLVER_NAME == 'cbc':
        # solver = SolverFactory("cbc", io_format='nl')  # python, nl, not setting
        solver = SolverFactory(SOLVER_NAME)
        solver.options["threads"] = 6
        # https://stackoverflow.com/questions/60595491/how-you-enable-cbc-to-return-best-solution-when-timelimit-pyomo
        solver.options['seconds'] = TIME_LIMIT
        solver.options['slogLevel'] = 3  # -1 - 63
        solver.options['logLevel'] = 3  # -1 - 63
        solver.options['maxSolutions'] = 3  # -1 - 2147483647

    elif SOLVER_NAME == 'ipopt':
        executable = os.getcwd()+'/Ipopt/Ipopt/build/bin/ipopt.exe'
        solver = SolverFactory("ipopt", executable=executable,solver_io='nl')
        solver.options['nlp_scaling_method'] = 'user-scaling'
        solver.options['max_iter'] = 10  # ipopt --print-options


    def __init__(self, name: str) -> None:

        model = ConcreteModel()

        self.name = name
        self.is_solved = False
        self.objective = None
        self.instance = model
        self.result = dict()

        self.logdata = dict(
            timestamp=datetime.utcnow(),
            name=name,
        )

    def save_model(self):
        self.instance.display(filename=f"{self.name}.display.dump")
        path = f"{self.name}.model.dump"
        with open(path, 'w') as output_file:
            self.instance.pprint(output_file)

    def get_NL_file(self):
        path = f"{self.name}.model.nl"
        self.instance.write(path)

    def solve(self, tee: bool = False, *args, **kwargs):
        _log.info(f"Solving with tee: {tee}, kwargs: {kwargs}")
        start_time = time.time()

        result = self.solver.solve(self.instance, tee=tee, **kwargs)
        self.objective = value(self.instance.objective)

        # self.instance.display()
        self.show_result(result)

        # load the results
        for var in self.instance.component_objects(Var, active=True):
            _log.info(f"{var.name}: index dim: {var.dim()}, len: {len(var)}")
            self.result[var.name] = {k: v for (k, v) in var.get_values().items()}

        self.instance.compute_statistics()
        _log.info(f"Number of constraints : {self.instance.statistics.number_of_constraints}")
        _log.info(f"Number of variables : {self.instance.statistics.number_of_variables}")

        elapsed_time = time.time() - start_time
        _log.info(f'Duration: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')

        self.logdata['objective'] = self.objective
        self.logdata['constraints'] = self.instance.statistics.number_of_constraints
        self.logdata['variables'] = self.instance.statistics.number_of_variables
        self.logdata['duration'] = elapsed_time
        self.logdata['solved'] = self.is_solved
        # print(self.logdata)
        save_to_db(self.logdata)

    def populate_df(self, variables: Iterable[str]) -> pd.DataFrame:
        """ Input variables must have the same dimension
        """
        return pd.DataFrame({k: pd.Series(self.result[k]) for k in variables})

    def save_dill(self):
        p = f"{self.name}.dill"
        _log.info(f"Saving result to: {p}.")
        with open(p, 'wb') as handle:
            dill.dump(self, handle)

    @staticmethod
    def load_dill(p: str = 'result.dill') -> Any:
        """Loads full class via dill
        """
        _log.info(f"Loading result from: {p}.")
        with open(p, 'rb') as handle:
            return dill.load(handle)

    def show_result(self, result):
        if (result.solver.status == SolverStatus.ok) and (
                result.solver.termination_condition == TerminationCondition.optimal
        ):
            _log.info("# feasible and optimal solution found")
            self.is_solved = True
            _log.info("# Solution {}".format(
                [result.Problem.get("Lower bound").value, result.Problem.get("Upper bound").value, ]
            ))
        elif result.solver.termination_condition == TerminationCondition.infeasible:
            _log.info("# no feasible solution found")
        else:
            _log.warning(str(result.solver))

    def show(self):
        raise NotImplementedError()
