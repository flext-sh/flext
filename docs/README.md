# FLEXT Documentation

**SOURCE OF TRUTH** - All documentation has been consolidated into a single, authoritative source.

## 📖 Primary Documentation

- **[FLEXT Service Architecture](FLEXT_SERVICE_ARCHITECTURE.md)** - Complete architectural overview of the FLEXT service with Plugin orchestration + DI

## 🗂️ Archive

All previous documentation has been moved to `.bak/` to prevent conflicts while maintaining historical reference.

## 🎯 Key Concepts

**FLEXT is a SINGLE SERVICE** that orchestrates enterprise data integration through:

1. **Plugin System** - Dynamic extensibility 
2. **Library Architecture** - `flext-core`, `flext-api`, `flext-auth`, `flext-cli`, `flext-grpc`, `flext-plugin`, `flext-web` are LIBRARIES, not services
3. **Dependency Injection** - Clean boundaries with maximum flexibility
4. **Clean Architecture** - Domain-driven design with clear separation of concerns

## 🔗 Quick Links

- Service runs in namespace: `flext`
- Main documentation: [FLEXT_SERVICE_ARCHITECTURE.md](FLEXT_SERVICE_ARCHITECTURE.md)
- Archived docs: `.bak/` directory

---

**Version**: 2.0.0  
**Last Updated**: 2025-01-22  
**Status**: SOURCE OF TRUTH