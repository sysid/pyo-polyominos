import numpy as np
from twimage import dict2matrix, matrix2dict
import matplotlib.pyplot as plt

test = {
    'blocks': {
        1: {(0, 0): 1.0, (1, 0): 1.0, (2, 0): 1.0, (3, 0): 1.0},
        2: {(0, 0): 0.0, (0, 1): 1.0, (1, 0): 1.0, (1, 1): 1.0, (2, 0): 0.0, (2, 1): 1.0},
        3: {(0, 0): 1.0, (0, 1): 1.0, (1, 0): 1.0, (1, 1): 1.0},
        4: {(0, 0): 1.0, (0, 1): 1.0, (0, 2): 1.0, (1, 0): 1.0, (1, 1): 0.0, (1, 2): 0.0},
        5: {(0, 0): 0.0, (0, 1): 1.0, (1, 0): 1.0, (1, 1): 1.0, (2, 0): 1.0, (2, 1): 0.0},
    },
    'dimension': 7,
    'block_symmetry': {
        1: 2,
        2: 4,
        3: 1,
        4: 4,
        5: 4,
    },
    # 'block_shapes': {
    #     1: (4, 1),
    #     2: (3, 2),
    #     3: (2, 2),
    #     4: (2, 3),
    #     5: (3, 2),
    # },
}

if __name__ == '__main__':

    for k, block in test['blocks'].items():
        plt.imshow(dict2matrix(block))
        plt.show()
