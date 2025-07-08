# FLEXT Development Setup

## 🚀 **Professional Development Environment**

Este projeto segue **boas práticas Python** com editable installs para desenvolvimento.

### **1. CLONE E SETUP INICIAL**

```bash
git clone <repo>
cd flext
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows
```

### **2. INSTALAR FLEXT-CORE (BASE LIBRARY)**

```bash
# Install flext-core in editable mode (desenvolvimento)
pip install -e ./flext-core
```

### **3. INSTALAR PROJETO ESPECÍFICO**

```bash
# Para trabalhar em flext-api:
pip install -e ./flext-api

# Para trabalhar em flext-auth:  
pip install -e ./flext-auth

# Para trabalhar em flext-grpc:
pip install -e ./flext-grpc
```

### **4. VERIFICAR INSTALAÇÃO**

```bash
python -c "from flext_core import Entity, ValueObject, ServiceResult; print('✅ Setup OK!')"
```

## 🏗️ **ARQUITETURA DE DEPENDÊNCIAS**

```
flext-core (v0.6.0)     ← Base library
    ↑
    ├── flext-api       ← Depends on flext-core
    ├── flext-auth      ← Depends on flext-core  
    └── flext-grpc      ← Depends on flext-core
```

## 🔧 **DESENVOLVIMENTO**

### **Editar flext-core:**
- Mudanças são refletidas **imediatamente** em todos os projetos
- Não precisa reinstalar

### **Adicionar nova dependência ao flext-core:**
```bash
cd flext-core
# Edit pyproject.toml dependencies
pip install -e . --force-reinstall
```

### **Testes:**
```bash
cd flext-core && python -m pytest
cd flext-api && python -m pytest  
cd flext-auth && python -m pytest
cd flext-grpc && python -m pytest
```

## ⚡ **BENEFÍCIOS DESTA ABORDAGEM:**

- ✅ **Professional**: Segue padrões Python oficiais
- ✅ **Portável**: Funciona em qualquer ambiente
- ✅ **CI/CD Ready**: Compatível com pipelines
- ✅ **IDE Friendly**: IntelliSense/autocomplete funciona
- ✅ **Deployment Ready**: Preparado para produção
- ✅ **Versionamento**: Controle de versões adequado

## 🚫 **O QUE NÃO FAZEMOS:**

- ❌ `sys.path.insert()` hacks
- ❌ Imports via caminhos relativos
- ❌ Dependências hard-coded
- ❌ Gambiarras de desenvolvimento

---

**Esta é a maneira CERTA de fazer! 🎯**
