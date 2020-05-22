import sys
from polyominos import Polyominos

# if len(sys.argv) != 2:
#     print(f"\n-E- Usage: ipy.py 'model.dill'")
#     sys.exit(1)
#
# name = sys.argv[1]
name = 'standard.dill'

m = Polyominos.load_result(name)
print(f"\n -M- model {name} available in variable: m")
