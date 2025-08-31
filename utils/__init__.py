# Import from the root utils.py to avoid naming conflicts
import sys
import os

# Add project root to path and import from root utils.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import importlib.util
spec = importlib.util.spec_from_file_location("root_utils", os.path.join(project_root, "utils.py"))
root_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_utils)

# Re-export functions from root utils
fetch_data = root_utils.fetch_data
calculate_atr = root_utils.calculate_atr
plot_price_and_signals = root_utils.plot_price_and_signals
calculate_returns = root_utils.calculate_returns
calculate_volatility = root_utils.calculate_volatility
calculate_sharpe_ratio = root_utils.calculate_sharpe_ratio