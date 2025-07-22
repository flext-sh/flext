#!/usr/bin/env python3
"""ARCHITECTURAL FIX: ServiceResult[Any] Standardization Across FLEXT Workspace.

This script fixes the ServiceResult duplicate/inconsistent usage across all projects:

1. Remove duplicated ServiceResult definitions
2. Standardize all imports to use flext_core.domain.shared_types.ServiceResult
3. Convert old syntax ServiceResult.ok(...) to ServiceResult.ok(...)
4. Convert old syntax ServiceResult.fail(...) to ServiceResult.fail(...)
5. Ensure consistent typing ServiceResult[T] usage

ZERO TOLERANCE: Every ServiceResult usage must be correct and consistent.
"""

import os
import re
import sys
from pathlib import Path
from typing import Any


# ServiceResult moved to flext_core.domain.shared_types
