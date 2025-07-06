# ATUALIZAÇÃO DE USO - Caminho Correto para Scripts

**IMPORTANTE**: Para evitar problemas, sempre use o caminho completo `flext/scripts/qg` ao invés de apenas `scripts/qg`.

## 📝 **CAMINHOS ATUALIZADOS**

### **Comando Principal (Recomendado)**

```bash
# ✅ CORRETO - Use sempre o caminho completo
flext/scripts/qg --project flext-auth
flext/scripts/qg --file src/module.py

# ❌ EVITAR - Pode causar problemas
scripts/qg --project flext-auth
```

### **Sistema Enhanced**

```bash
# ✅ CORRETO
flext/scripts/qg_complete --enhanced --project flext-core
flext/scripts/qg_complete --standard --file src/arquivo.py

# ❌ EVITAR
scripts/qg_complete --enhanced --project flext-core
```

### **Verificação de Organização**

```bash
# ✅ CORRETO
python flext/scripts/verify_consolidation.py

# ❌ EVITAR
python scripts/verify_consolidation.py
```

## 🎯 **COMANDOS ATUALIZADOS PARA USO DIÁRIO**

```bash
# Melhorar projeto inteiro
flext/scripts/qg --project flext-auth

# Antes de commit
flext/scripts/qg --file src/meu_modulo.py

# Ver ajuda
flext/scripts/qg --help

# Verificar organização
python flext/scripts/verify_consolidation.py
```

## ✅ **DOCUMENTAÇÃO ATUALIZADA**

Toda a documentação foi atualizada para usar os caminhos corretos:

- ✅ `scripts/README.md` - Atualizado
- ✅ `scripts/FINAL_TRUTH_REPORT.md` - Atualizado
- ✅ `scripts/CONSOLIDATION_COMPLETE_REPORT.md` - Pendente

**Status**: Caminhos corrigidos e documentação atualizada para evitar problemas.
