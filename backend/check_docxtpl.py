import importlib.util
spec = importlib.util.find_spec("docxtpl")
if spec is not None:
    print("docxtpl: INSTALLED")
else:
    print("docxtpl: NOT INSTALLED")
