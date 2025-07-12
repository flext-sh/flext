# 🚀 PLANO DE IMPLEMENTAÇÃO: Regras de Refatoração

## 📋 ROADMAP DETALHADO

### ETAPA 1: SCHEMA ENHANCEMENT IMPLEMENTATION

```python
# 1.1 Enhanced Schema Service
class EnhancedSchemaConversionService:
    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    def extract_custom_schema(self, input_schema_path: Path) -> dict:
        """
        REGRA #1 APLICADA: Schema_Customization_Enhancement

        Transformações:
        - Parse attributeTypes com OID patterns 99.*
        - Extract objectClasses customizadas
        - Generate changetype: modify format
        """
        custom_schema = {"attributeTypes": [], "objectClasses": []}

        # Parse schema file with enhanced extraction
        with open(input_schema_path) as f:
            content = f.read()

        # Extract attributeTypes with OID filtering
        attr_pattern = r"attributeTypes:\s*\(\s*([^)]+)\s*\)"
        for match in re.finditer(attr_pattern, content, re.DOTALL):
            attr_def = match.group(1)
            oid = self._extract_oid(attr_def)

            if self._matches_custom_patterns(oid):
                custom_schema["attributeTypes"].append(attr_def)

        # Extract objectClasses with custom OIDs
        class_pattern = r"objectClasses:\s*\(\s*([^)]+)\s*\)"
        for match in re.finditer(class_pattern, content, re.DOTALL):
            class_def = match.group(1)
            oid = self._extract_oid(class_def)

            if self._matches_custom_patterns(oid):
                custom_schema["objectClasses"].append(class_def)

        return custom_schema

    def _matches_custom_patterns(self, oid: str) -> bool:
        """Check if OID matches 99.* pattern or exact matches"""
        patterns = self.rules["schema_rules"]["schema_whitelist"]["oid_patterns"]
        exact_matches = self.rules["schema_rules"]["schema_whitelist"]["exact_oid_matches"]

        # Check exact matches first
        if oid in exact_matches:
            return True

        # Check patterns
        for pattern in patterns:
            if re.match(pattern.replace("*", ".*"), oid):
                return True

        return False

    def generate_schema_modify_ldif(self, schema: dict) -> str:
        """
        Generate LDIF in changetype: modify format like test_output
        """
        ldif_lines = [
            "# LDIF Export",
            "# Generator: enhanced-schema-service",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Entries: {len(schema['attributeTypes']) + len(schema['objectClasses'])}",
            "#",
            "version: 1",
            "",
            "dn: cn=schema",
            "changetype: modify"
        ]

        # Add attributeTypes
        for attr_def in schema["attributeTypes"]:
            ldif_lines.extend([
                "add: attributetypes",
                f"attributetypes: ( {attr_def} )",
                "-"
            ])

        # Add objectClasses
        for class_def in schema["objectClasses"]:
            ldif_lines.extend([
                "add: objectclasses",
                f"objectclasses: ( {class_def} )",
                "-"
            ])

        return "\n".join(ldif_lines)
```

### ETAPA 2: ACL FORMAT TRANSFORMATION

```python
# 2.1 Enhanced ACL Service
class EnhancedACLProcessorService:
    def convert_to_modify_format(self, acl_entries: list) -> list:
        """
        REGRA #2 APLICADA: ACL_Format_Modernization

        Transformações:
        - Converter entradas separadas → changetype: modify
        - Consolidar ACIs por DN de destino
        - Aplicar permissões específicas por contexto
        """
        # Group ACIs by target DN
        acis_by_dn = {}

        for entry in acl_entries:
            target_dn = self._extract_target_dn(entry)
            if target_dn not in acis_by_dn:
                acis_by_dn[target_dn] = []
            acis_by_dn[target_dn].append(entry["aci"])

        # Generate modify format entries
        modify_entries = []
        for dn, acis in acis_by_dn.items():
            modify_entry = {
                "dn": dn,
                "changetype": "modify"
            }

            # Add multiple ACIs as separate add operations
            for i, aci in enumerate(acis):
                if i == 0:
                    modify_entry["add"] = "aci"
                    modify_entry["aci"] = aci
                else:
                    # Additional ACIs as separate operations
                    modify_entry[f"add_{i}"] = "aci"
                    modify_entry[f"aci_{i}"] = aci

            modify_entries.append(modify_entry)

        return modify_entries

    def enhance_permissions(self, aci: str, context: str) -> str:
        """
        Enhance permissions based on context (users, groups, etc.)
        """
        permission_mappings = {
            "admin_context": "read,search,compare,write,add,delete",
            "user_context": "read,search,compare",
            "group_context": "read,search,compare,write",
            "default": "read,search"
        }

        context_key = self._determine_context(aci)
        permissions = permission_mappings.get(context_key, permission_mappings["default"])

        # Replace generic permissions with context-specific ones
        enhanced_aci = re.sub(
            r"allow \([^)]+\)",
            f"allow ({permissions})",
            aci
        )

        return enhanced_aci
```

### ETAPA 3: CONFIGURATION-DRIVEN PROCESSING

```python
# 3.1 Enhanced Rules Engine
class EnhancedRulesEngine:
    def __init__(self, rules_path: Path):
        self.rules = self._load_enhanced_rules(rules_path)

    def _load_enhanced_rules(self, rules_path: Path) -> dict:
        """
        REGRA #4 APLICADA: Configuration_Driven_Processing

        Load enhanced rules with templates and patterns
        """
        with open(rules_path) as f:
            rules = json.load(f)

        # Validate and enhance rules
        self._validate_rules_completeness(rules)
        self._add_template_engine(rules)

        return rules

    def _validate_rules_completeness(self, rules: dict):
        """Ensure all required sections exist"""
        required_sections = [
            "schema_rules.schema_whitelist",
            "transformation_definitions.convert_orclaci_to_oud",
            "transformation_definitions.convert_orclentrylevelaci_to_oud",
            "transformation_definitions.boolean_value_conversion",
            "transformation_definitions.telephone_number_filtering"
        ]

        for section in required_sections:
            if not self._get_nested_value(rules, section):
                raise ValueError(f"Missing required rules section: {section}")

    def process_with_templates(self, template_name: str, **kwargs) -> str:
        """
        Process templates with variable substitution
        """
        template = self.rules["transformation_definitions"][template_name]["template"]

        # Safe template substitution
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
```

### ETAPA 4: ENTRY CONSOLIDATION

```python
# 4.1 Enhanced Consolidator
class EnhancedEntryConsolidator:
    def consolidate_entries(self, entries: list) -> list:
        """
        REGRA #3 APLICADA: Entry_Consolidation_Optimization

        Transformações:
        - Eliminate duplicates by DN
        - Sort by hierarchical dependencies
        - Optimize for size and efficiency
        """
        # Step 1: Deduplication
        unique_entries = self._deduplicate_by_dn(entries)

        # Step 2: Hierarchical sorting
        sorted_entries = self._sort_by_hierarchy(unique_entries)

        # Step 3: Size optimization
        optimized_entries = self._optimize_for_size(sorted_entries)

        return optimized_entries

    def _deduplicate_by_dn(self, entries: list) -> list:
        """Remove duplicates, keeping most complete entry"""
        dn_map = {}

        for entry in entries:
            dn = entry.get("dn", "")
            if dn not in dn_map:
                dn_map[dn] = entry
            else:
                # Keep entry with more attributes
                if len(entry) > len(dn_map[dn]):
                    dn_map[dn] = entry

        return list(dn_map.values())

    def _sort_by_hierarchy(self, entries: list) -> list:
        """Sort entries by DN depth and dependencies"""
        def dn_depth(entry):
            dn = entry.get("dn", "")
            return len(dn.split(","))

        return sorted(entries, key=dn_depth)

    def _optimize_for_size(self, entries: list) -> list:
        """Remove unnecessary attributes and optimize structure"""
        optimized = []

        for entry in entries:
            # Remove internal processing attributes
            cleaned_entry = {
                k: v for k, v in entry.items()
                if not k.startswith("_") and k not in ["changetype"]
            }
            optimized.append(cleaned_entry)

        return optimized
```

### ETAPA 5: QUALITY ASSURANCE IMPLEMENTATION

```python
# 5.1 Enhanced Validator
class EnhancedQualityValidator:
    def validate_output_equivalence(self, output_path: Path, test_output_path: Path) -> dict:
        """
        REGRA #5 APLICADA: Quality_Parity_Achievement

        Validate that output meets test_output quality standards
        """
        results = {
            "schema_quality": self._validate_schema_quality(output_path, test_output_path),
            "acl_quality": self._validate_acl_quality(output_path, test_output_path),
            "structure_quality": self._validate_structure_quality(output_path, test_output_path),
            "size_efficiency": self._validate_size_efficiency(output_path, test_output_path)
        }

        results["overall_score"] = self._calculate_overall_score(results)
        return results

    def _validate_schema_quality(self, output_path: Path, test_output_path: Path) -> dict:
        """Validate schema output quality"""
        output_schema = self._parse_schema_file(output_path / "00_custom_schema_oud.ldif")
        test_schema = self._parse_schema_file(test_output_path / "00_custom_schema_oud.ldif")

        return {
            "attribute_count_ratio": len(output_schema["attributes"]) / len(test_schema["attributes"]),
            "objectclass_count_ratio": len(output_schema["objectClasses"]) / len(test_schema["objectClasses"]),
            "format_compliance": output_schema["format"] == test_schema["format"],
            "oid_pattern_compliance": self._check_oid_patterns(output_schema, test_schema)
        }

    def _validate_acl_quality(self, output_path: Path, test_output_path: Path) -> dict:
        """Validate ACL output quality"""
        output_acls = self._parse_acl_file(output_path / "04_acls_permissions.ldif")
        test_acls = self._parse_acl_file(test_output_path / "04_acls_permissions.ldif")

        return {
            "format_modernization": self._check_modify_format(output_acls),
            "consolidation_ratio": self._calculate_consolidation_ratio(output_acls, test_acls),
            "permission_specificity": self._check_permission_specificity(output_acls, test_acls),
            "syntax_compliance": self._validate_oud_syntax(output_acls)
        }
```

## 📊 MÉTRICAS DE IMPLEMENTAÇÃO

### PROGRESS TRACKING

```yaml
Phase 1 - Schema Enhancement:
  - Custom attributeTypes extraction: 0% → 100%
  - ObjectClass enhancement: 0% → 100%
  - Modify format generation: 0% → 100%

Phase 2 - ACL Transformation:
  - Format modernization: 0% → 100%
  - Entry consolidation: 0% → 100%
  - Permission enhancement: 0% → 100%

Phase 3 - Configuration Enhancement:
  - Hardcoding elimination: 0% → 100%
  - Template implementation: 0% → 100%
  - Pattern matching: 0% → 100%

Phase 4 - Quality Assurance:
  - Validation coverage: 0% → 100%
  - Performance optimization: 0% → 100%
  - Equivalence achievement: 0% → 100%
```

### SUCCESS CRITERIA

```yaml
Schema Equivalence:
  ✅ Size: 1.3KB → 2.6KB (≥2x expansion)
  ✅ AttributeTypes: 0 → 11+ custom attributes
  ✅ ObjectClasses: 0 → 3+ custom classes
  ✅ Format: Basic → changetype: modify

ACL Equivalence:
  ✅ Size: 325KB → 83KB (≤0.25x reduction)
  ✅ Lines: 4568 → 1256 (≤0.27x reduction)
  ✅ Format: Separate entries → modify operations
  ✅ Consolidation: Individual → grouped by DN

Quality Equivalence:
  ✅ Structure: Fragmented → consolidated
  ✅ Configuration: Hardcoded → rules-driven
  ✅ Validation: Basic → comprehensive
  ✅ Performance: Inefficient → optimized
```

---

**RESULTADO:** Implementação sistemática das regras de refatoração que transformará o output atual para alcançar a qualidade e eficiência do test_output, sem simples cópia, mas através de processo estruturado e validado.
