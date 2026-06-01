import pandas as pd
print(type(pd))  # Should print: <class 'module'>
print(pd.__file__)  # Should point to site-packages/pandas/__init__.py
print(hasattr(pd, 'DataFrame'))  # Should print: True
df = pd.DataFrame([{'a': 1, 'b': 2}])
print(df)