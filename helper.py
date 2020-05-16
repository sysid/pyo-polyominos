import logging
from pprint import pprint

import numpy as np
from collections import defaultdict
from typing import Dict, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt

from twimage import Point, heatmap, matrix2dict

import settings

_log = logging.getLogger(__name__)


def create_blocks():
    # create dicts for blocks
    block = np.ones((3, 2))
    block[0, 0] = 0
    block[2, 1] = 0
    print(matrix2dict(block))
    plt.imshow(block)


class Ok(object):
    """Location where a block can be put within grid
    (k,i,j)
    """

    def __init__(self, config: Dict) -> None:
        super().__init__()
        self.config = config

        self.dimension = config['dimension']
        self.blocks = config['blocks']
        self.block_shapes = config['block_shapes']

        self.ok = defaultdict(lambda: 0)
        self.create_ok()

    def create_ok(self) -> None:
        for k, block in self.blocks.items():
            for i in range(1, self.dimension + 1):
                if self.block_shapes[k][0] > self.dimension + 1 - i:
                    continue
                for j in range(1, self.dimension + 1):
                    if self.block_shapes[k][1] > self.dimension + 1 - j:
                        continue
                    self.ok[k, i, j] = 1
        _ = None
        _log.info(f"Oks created: {len(self.ok)}")


class Cover(object):
    """Location where a block can be put within grid
    (k,i,j, ii, jj)
    """

    def __init__(self, config: Dict) -> None:
        super().__init__()
        self.config = config

        self.ok = Ok(config=config).ok

        self.dimension = config['dimension']
        self.blocks = config['blocks']
        self.block_shapes = config['block_shapes']

        self.cover = defaultdict(lambda: 0)
        self.create_cover()

    def create_cover(self) -> None:
        for (k, i, j) in self.ok:
            block = self.blocks[k]
            for (ii, jj), v in block.items():
                if v == 0:
                    continue
                self.cover[k, i, j, i + ii, j + jj] = 1
        _log.info(f"Covers created: {len(self.cover)}")


if __name__ == '__main__':
    log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    # create_blocks()

    name = 'test'
    # ok = Ok(config=getattr(settings, name))
    cover = Cover(config=getattr(settings, name))
