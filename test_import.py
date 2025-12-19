import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'bool'):
    np.bool = bool

try:
    from paddleocr import PPStructure
    print("PaddleOCR imported successfully.")
    import pandas as pd
    print("Pandas imported successfully.")
except Exception as e:
    print(f"Import failed: {e}")
