#!/usr/bin/env bash
###############################################################################
#  project_runner.sh — Executa um comando em cada projeto com logs
#  Usage: 
#    project_runner.sh [opções] <comando>
#
#  Opções:
#    -p, --flx_project <nome>     Executar apenas no projeto especificado
#    -l, --log-dir <dir>      Diretório para armazenar logs (padrão: workspace/logs/YYYYMMDD_HHMMSS)
#    -s, --silent             Modo silencioso (não mostra saída detalhada)
#    -c, --continue-on-error  Continuar mesmo se um projeto falhar
#    -h, --help               Mostra esta ajuda
#
#  Exemplos:
#    ./scripts/project_runner.sh "pytest -q"
#    ./scripts/project_runner.sh --flx_project pyapix "black ."
#    ./scripts/project_runner.sh --log-dir /tmp/logs "ruff check"
###############################################################################
set -Eeuo pipefail
source "$(dirname "$0")/common.sh"

# Valores padrão
TARGET_PROJECT=""
LOG_DIR="${WORKSPACE_ROOT}/logs/$(date +"%Y%m%d_%H%M%S")"
SILENT=false
CONTINUE_ON_ERROR=false
COMMAND=""

# Função de ajuda
show_help() {
    cat << EOF
Uso: $(basename "$0") [opções] <comando>

Opções:
  -p, --flx_project <nome>     Executar apenas no projeto especificado
  -l, --log-dir <dir>      Diretório para armazenar logs (padrão: workspace/logs/YYYYMMDD_HHMMSS)
  -s, --silent             Modo silencioso (não mostra saída detalhada)
  -c, --continue-on-error  Continuar mesmo se um projeto falhar
  -h, --help               Mostra esta ajuda

Exemplos:
  ./scripts/project_runner.sh "pytest -q"
  ./scripts/project_runner.sh --flx_project pyapix "black ."
  ./scripts/project_runner.sh --log-dir /tmp/logs "ruff check"
EOF
    exit 0
}

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--flx_project)
            TARGET_PROJECT="$2"
            shift 2
            ;;
        -l|--log-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        -s|--silent)
            SILENT=true
            shift
            ;;
        -c|--continue-on-error)
            CONTINUE_ON_ERROR=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            # Captura o comando e todos os argumentos restantes
            COMMAND="$*"
            break
            ;;
    esac
done

# Verificar se um comando foi fornecido
if [[ -z "$COMMAND" ]]; then
    err "Nenhum comando fornecido."
    show_help
    exit 1
fi

COMMAND_NAME=$(echo "$COMMAND" | awk '{print $1}')

# Cria o diretório de logs se não existir
mkdir -p "$LOG_DIR"
if [[ "$SILENT" == "false" ]]; then
    info "Logs serão gravados em: $LOG_DIR"
fi

# Função para executar comando em um projeto
run_command_in_project() {
    local project_path="$1"
    local project_name=$(basename "$project_path")
    local log_file="${LOG_DIR}/${project_name}.log"
    
    if [[ "$SILENT" == "false" ]]; then
        warn "▶ Executando em $project_name..."
    fi
    
    # Executa o comando no projeto e redireciona saída para o arquivo de log
    (cd "$project_path" && eval "$COMMAND") > "$log_file" 2>&1
    exit_code=$?
    
    # Sempre mostra as últimas 5 linhas do log se o arquivo não estiver vazio
    if [[ -s "$log_file" ]]; then
        if [[ "$SILENT" == "false" ]]; then
            echo -e "\n${CYAN}Últimas 5 linhas:${NC}"
            tail -5 "$log_file" | sed 's/^/  /'
        fi
    fi
    
    # Determina o status baseado no exit code e conteúdo
    if [[ $exit_code -eq 0 ]]; then
        # Verifica se houve alguma saída significativa
        if [[ -s "$log_file" ]] && grep -q -E "(error|failed|Error|Failed)" "$log_file" 2>/dev/null; then
            warn "⚠ $project_name: SKIP (warnings/issues encontrados)"
        else
            log "✓ $project_name: SUCESSO"
        fi
    else
        err "✗ $project_name: FALHA (código $exit_code)"
    fi
    
    if [[ "$SILENT" == "false" ]]; then
        info "  Log completo: $log_file"
        echo ""
    fi
    
    return $exit_code
}

# Executa em um projeto específico ou em todos
if [[ -n "$TARGET_PROJECT" ]]; then
    project_path="${WORKSPACE_ROOT}/${TARGET_PROJECT}"
    
    if [ -z "$(test -d "$project_path" && echo exists)" ]; then
        err "Projeto '$TARGET_PROJECT' não encontrado no workspace"
        exit 1
    fi
    
    if [[ "$SILENT" == "false" ]]; then
        header "Executando $COMMAND_NAME em $TARGET_PROJECT"
    fi
    
    run_command_in_project "$project_path"
    exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        if [[ "$SILENT" == "false" ]]; then
            log "✓ Comando executado com sucesso em $TARGET_PROJECT"
        fi
        exit 0
    else
        err "✗ Comando falhou em $TARGET_PROJECT"
        exit $exit_code
    fi
else
    if [[ "$SILENT" == "false" ]]; then
        header "Executando $COMMAND_NAME em todos os projetos"
    fi
    
    failed_projects=()
    
    for flx_project in "${PROJECTS[@]}"; do
        if [[ -d "$flx_project" ]]; then
            if run_command_in_project "$flx_project"; then
                : # Comando bem-sucedido, não faz nada
            elif [[ "$CONTINUE_ON_ERROR" == "true" ]]; then
                failed_projects+=("$(basename "$flx_project")")
            else
                failed_projects+=("$(basename "$flx_project")")
                break
            fi
        else
            if [[ "$SILENT" == "false" ]]; then
                warn "⚠ $(basename "$flx_project") (diretório inexistente)"
            fi
        fi
    done
    
    if [[ "$SILENT" == "false" ]]; then
        echo ""
    fi
    
    if [[ ${#failed_projects[@]} -eq 0 ]]; then
        if [[ "$SILENT" == "false" ]]; then
            log "✓ Comando executado com sucesso em todos os projetos"
            log "✓ Logs disponíveis em: $LOG_DIR"
        fi
        exit 0
    else
        err "✗ Comando falhou em ${#failed_projects[@]} projeto(s): ${failed_projects[*]}"
        if [[ "$SILENT" == "false" ]]; then
            err "  Logs disponíveis em: $LOG_DIR"
        fi
        exit 1
    fi
fi
