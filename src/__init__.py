"""FLEXT Source Package.

This package contains the core FLEXT framework modules and tools for enterprise data integration.
It includes the main FLEXT application framework and development tools.

Modules:
    flext: Main FLEXT application framework with CLI, workspace management, and services
    flext_quality.tools: Development and operational tools for quality assurance, monitoring, and deployment

The package provides a comprehensive platform for:
- Data integration pipeline management
- Development workflow automation
- Quality assurance and testing
- Enterprise deployment and monitoring
- Cross-project coordination and orchestration

Usage:
    import flext
    from flext_quality.tools import FlextQualityOperations

    # Use FLEXT framework
    app = flext.FlextCli()
    app.run()

    # Use development tools
    FlextQualityOperations().gateway.run_all_checks(".")
"""
