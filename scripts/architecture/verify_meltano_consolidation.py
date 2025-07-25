#!/usr/bin/env python3
"""Meltano Consolidation Verifier - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.architecture directly.

Validates that Singer/Meltano/DBT consolidation has been successfully implemented
according to the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, acabae com essa confusão arrumando isso"
"""

from __future__ import annotations

from pathlib import Path

# Import consolidated components from flext-meltano
from flext_meltano.architecture import FlextMeltanoConsolidationVerifier


def main() -> None:
    """Main execution function."""
    flext_root = Path('/home/marlonsc/flext')
    
    verifier = FlextMeltanoConsolidationVerifier(flext_root)
    results = verifier.verify_consolidation()
    verifier.report_verification(results)
    
    # Exit with appropriate code
    if results['consolidation_successful']:
        print("🎉 CONSOLIDATION VERIFICATION PASSED!")
    else:
        print("⚠️ Consolidation needs additional work")


if __name__ == '__main__':
    main()