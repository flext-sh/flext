#!/usr/bin/env python3
"""
Test FLEXT Meltano gopy integration
"""

import os
import sys

sys.path.append("/home/marlonsc/flext/python-meltano-gopy")

# Test the manual flext_meltano library
try:
    import flext_meltano

    available = flext_meltano.check_meltano()

    if available:
        adapter = flext_meltano.init_meltano()

        result = adapter.run_pipeline("tap-sample", "target-sample")
    else:
        pass

except ImportError:
    pass
except Exception:
    pass

# Test the gopy-generated library

try:
    # Change to the directory to avoid relative import issues
    old_cwd = os.getcwd()
    os.chdir("/home/marlonsc/flext/python-meltano-gopy")

    import meltano

    available = meltano.QuickCheck()

    if available:
        adapter = meltano.NewMeltanoAdapter()
    else:
        pass

except ImportError:
    pass
except Exception:
    pass
finally:
    os.chdir(old_cwd)
