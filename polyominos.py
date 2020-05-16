#!/usr/bin/env python
import logging
import numpy as np
from pprint import pprint

from pyomo.environ import *
from twimage import dict2matrix, add2canvas, Point, heatmap, rotate_dict

import settings
from BaseModel import BaseModel
from helper import Cover

_log = logging.getLogger(__name__)


class Polyominos(BaseModel):

    def __init__(self, name: str, config: dict) -> None:
        super().__init__(name)

        self.config = config
        model = self.instance  # from BaseModel

        cover = Cover(config=config)
        self.ok = cover.ok
        self.cover = cover.cover

        self.dimension = config['dimension']
        self.blocks = config['blocks']
        # self.block_shapes = config['block_shapes']

        ################################################################################
        # Sets
        ################################################################################

        model.K = Set(initialize=self.blocks.keys())
        model.I = RangeSet(self.dimension)
        model.J = RangeSet(self.dimension)
        model.R = Set(initialize=[0, 1, 2, 3])
        model.ok = Set(initialize=self.ok.keys())
        model.cover = Set(initialize=self.cover.keys())

        ################################################################################
        # Params put at model
        ################################################################################

        ################################################################################
        # Var
        ################################################################################

        model.x = Var(model.K, model.R, model.I, model.J, domain=Boolean, initialize=0,
                      doc='if we place polyomino k at location (i,j')

        # slack variable
        model.y = Var(model.I, model.J, domain=Boolean, initialize=0,
                      doc='(i,j) is covered exactly once (allow infeasable solutions)')

        ################################################################################
        # Constraints
        ################################################################################

        def overlap_c(model, iii, jjj):
            return sum(
                model.x[k, r, i, j] for (k, r, i, j, ii, jj) in model.cover if ii == iii and jj == jjj
            ) == model.y[iii, jjj]

        model.overlap_c = Constraint(model.I, model.J, rule=overlap_c)

        ################################################################################
        # Objective
        ################################################################################
        def obj_profit(model):
            return sum(model.y[i, j] for i in model.I for j in model.J)

        model.objective = Objective(rule=obj_profit, sense=maximize)

    def show(self):
        if self.is_solved:
            pprint([x for x in self.result['x'] if self.result['x'][x] > 0.7])
            # df = self.populate_df(('x',))  # must have same dimension
        else:
            _log.warning(f"Model not solved optimally.")

    def plot(self, debug: bool = False):
        if not self.is_solved:
            _log.warning(f"Cannot plot, model solved properly.")
            return
        blocks = [x for x in self.result['x'] if self.result['x'][x] > 0.7]
        canvas = np.zeros((self.dimension, self.dimension))
        for (k, r, i, j) in blocks:
            block = self.blocks[k]
            rblock = rotate_dict(block, k=r)
            m = dict2matrix(rblock) * k
            _log.debug(f"Adding block {k} rotation: {r} at {Point(i - 1, j - 1)}")
            canvas = add2canvas(canvas, m, Point(i - 1, j - 1), debug=debug)

        _log.info(f"Creating heatmap plot.")
        heatmap(canvas, show_data=True)


if __name__ == "__main__":
    log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)
    print(f"{'Polyominos':.^80}")

    name = 'test'
    config = getattr(settings, name)

    m = Polyominos(name=name, config=config)
    m.save_model()
    m.solve(tee=False)
    m.save_model()
    m.save_result()
    m.show()
    m.plot(debug=True)
