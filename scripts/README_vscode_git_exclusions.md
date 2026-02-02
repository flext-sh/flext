# VSCode Git Exclusions Setup

Este documento explica como configurar o VSCode para excluir arquivos que não estão rastreados pelo git dos lints e validações.

## Problema

Por padrão, o VSCode executa lints (Pylance, Ruff, etc.) em todos os arquivos Python do workspace, incluindo:
- Arquivos temporários
- Arquivos de cache
- Arquivos ignorados pelo .gitignore
- Arquivos não rastreados pelo git

Isso pode causar:
- Lentidão na análise
- Falsos positivos nos lints
- Análise de arquivos que não fazem parte do projeto

## Solução

### Configuração Automática

Execute o script para configurar automaticamente:

```bash
# Via Makefile (recomendado)
make vscode-update

# Ou diretamente
python scripts/update_vscode_git_exclusions.py
```

Este script:
1. Identifica arquivos não rastreados pelo git
2. Gera padrões de exclusão apropriados
3. Atualiza `.vscode/settings.json` automaticamente

### Configurações Aplicadas

O script configura as seguintes exclusões no VSCode:

#### Python Analysis Exclusions
```json
"python.analysis.exclude": [
    "**/node_modules",
    "**/__pycache__",
    "**/.mypy_cache",
    "**/.ruff_cache",
    "**/.pytest_cache",
    "**/.pylance_cache",
    "**/build",
    "**/dist",
    "**/*.egg-info",
    "**/.venv",
    "**/venv",
    // ... e mais padrões
]
```

#### Ruff Exclusions
```json
"ruff.exclude": [
    // Mesmas exclusões do Python analysis
]
```

#### File Watcher Exclusions
```json
"files.watcherExclude": {
    "node_modules": true,
    "__pycache__": true,
    ".mypy_cache": true,
    // ... e mais
}
```

## Benefícios

- ✅ **Performance**: Lints executam apenas em arquivos relevantes
- ✅ **Precisão**: Menos falsos positivos
- ✅ **Foco**: Análise concentrada no código do projeto
- ✅ **Automático**: Script identifica arquivos não rastreados
- ✅ **Manutenível**: Makefile integration para updates fáceis

## Uso Contínuo

### Atualização Manual
Sempre que adicionar/remover arquivos do git:

```bash
make vscode-update
```

### Verificação
Para verificar se as configurações estão aplicadas:

1. Abra o VSCode
2. Vá em `File > Preferences > Settings`
3. Procure por "python.analysis.exclude"
4. Verifique se as exclusões estão configuradas

## Troubleshooting

### Script não encontra arquivos
Se o script não encontrar arquivos não rastreados, ele usa padrões padrão do .gitignore.

### VSCode não aplica as configurações
- Feche e reabra o VSCode
- Execute `Developer: Reload Window` no Command Palette

### Exclusões muito agressivas
Edite `.vscode/settings.json` manualmente para ajustar os padrões de exclusão.

## Arquivos Afetados

- `.vscode/settings.json` - Configurações do VSCode
- `scripts/update_vscode_git_exclusions.py` - Script de atualização
- `Makefile` - Target `vscode-update` adicionado

## Comandos Úteis

```bash
# Ver arquivos rastreados pelo git
git ls-files | head -20

# Ver arquivos não rastreados
git ls-files --others --exclude-standard

# Ver status do git
git status --porcelain
```