import sys
from template import Template

if len(sys.argv) != 2:
    print(f"\n-E- Usage: ipy.py 'model.dill'")
    sys.exit(1)

name = sys.argv[1]
# name = 'test_objective3.dill'

m = Template.load_result(name)
print(f"\n -M- model {name} available in variable: m")
