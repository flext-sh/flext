#!/bin/bash
# Script para remoção de comentários # ignore conforme FASE 1.1 do guia
# Remove comentários que silenciam warnings ao invés de corrigir problemas reais

echo "🧹 Removendo comentários # ignore conforme refatoração arquitetural..."

# Contador de arquivos processados
processed=0
total_removed=0

# Função para remover ignores de um arquivo
remove_ignores_from_file() {
    local file="$1"
    local temp_file
    temp_file=$(mktemp)
    local removed_count=0
    
    # Contar quantos ignores existem antes
    local before_count
    before_count=$(grep -c "ignore\|# noqa\|# pylint:\|# mypy:" "$file" 2>/dev/null || echo 0)
    
    if [ "$before_count" -gt 0 ]; then
        echo "  📁 $file (encontrados: $before_count ignores)"
        
        # Remover diferentes tipos de comentários ignore usando sed
        sed -E '
            # Removerignore e variações
            s/[[:space:]]*#[[:space:]]*type:[[:space:]]*ignore(\[[^]]*\])?[[:space:]]*//g
            
            # Remover # noqa e variações  
            s/[[:space:]]*#[[:space:]]*noqa([^[:space:]]*)?[[:space:]]*//g
            
            # Remover # pylint: disable e variações
            s/[[:space:]]*#[[:space:]]*pylint:[[:space:]]*disable=[^[:space:]]*[[:space:]]*//g
            
            # Remover # mypy: ignore e variações
            s/[[:space:]]*#[[:space:]]*mypy:[[:space:]]*ignore[[:space:]]*//g
            
            # Limpar linhas que ficaram vazias ou só com espaços
            /^[[:space:]]*$/d
            
        ' "$file" > "$temp_file"
        
        # Verificar se houve mudanças
        if ! cmp -s "$file" "$temp_file"; then
            mv "$temp_file" "$file"
            removed_count=$before_count
            ((total_removed += removed_count))
            echo "    ✅ Removidos $removed_count comentários ignore"
        else
            rm "$temp_file"
            echo "    ⚠️  Nenhum ignore removido (possíveis falsos positivos)"
        fi
    fi
    
    ((processed++))
}

# Encontrar todos os arquivos Python com comentários ignore
echo "🔍 Procurando arquivos Python com comentários ignore..."

# Processar arquivos que contêm comentários ignore
while IFS= read -r -d '' file; do
    # Verificar se o arquivo contém comentários ignore
    if grep -q "ignore\|# noqa\|# pylint:\|# mypy:" "$file" 2>/dev/null; then
        remove_ignores_from_file "$file"
    fi
done < <(find . -path "./.venv" -prune -o -path "./*/.venv" -prune -o -path "./.git" -prune -o -name "*.py" -type f -print0 2>/dev/null)

echo ""
echo "📊 ESTATÍSTICAS FINAIS:"
echo "  Arquivos processados: $processed"
echo "  Total de ignores removidos: $total_removed"

if [ "$total_removed" -gt 0 ]; then
    echo ""
    echo "⚠️  IMPORTANTE: Comentários ignore foram removidos!"
    echo "   Agora é necessário corrigir os problemas reais que eles silenciavam."
    echo "   Execute os seguintes comandos para identificar os problemas:"
    echo ""
    echo "   # Verificar erros de tipo (MyPy)"
    echo "   find . -name '*.py' -exec python -m mypy {} \\; 2>/dev/null"
    echo ""
    echo "   # Verificar problemas de lint"
    echo "   find . -name '*.py' -exec python -m pylint {} \\; 2>/dev/null"
    echo ""
    echo "   # Verificar erros de sintaxe"
    echo "   find . -name '*.py' -exec python -m py_compile {} \\; 2>&1"
    echo ""
else
    echo "✅ Nenhum comentário ignore encontrado para remover."
fi

echo "✅ Limpeza de comentários ignore concluída!" 
