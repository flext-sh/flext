#!/usr/bin/env bash
###############################################################################
#  setup_venv.sh — Gerenciamento unificado do ambiente virtual
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  License: MIT
###############################################################################
set -Eeuo pipefail
source "$(dirname "$0")/common.sh"

# ‣ Funções de ajuda
usage() {
    cat <<EOF
Uso: $0 <comando> [opções]

Comandos:
  create         Cria um novo ambiente virtual com Python ${PYTHON_VERSION}
  clean          Remove o ambiente virtual atual
  rebuild        Remove e recria o ambiente virtual (clean + create)
  install        Instala as dependências no ambiente virtual
  install-dev    Instala as dependências de desenvolvimento
  verify         Verifica se o ambiente virtual está correto e funcional
  check-tools    Verifica e instala ferramentas essenciais
  status         Mostra o status do ambiente virtual
  check-lock     Verifica se poetry.lock está sincronizado com pyproject.toml
  update-lock    Atualiza poetry.lock se necessário
  force-lock     Força regeneração do poetry.lock

Exemplos:
  $0 create      # Cria um novo ambiente virtual
  $0 install-dev # Instala dependências de desenvolvimento
  $0 rebuild     # Reconstrói completamente o ambiente virtual
  $0 force-lock  # Força regeneração do poetry.lock
EOF
    exit 1
}

# ‣ Função para mostrar o status do ambiente virtual
show_status() {
    header "Status do Ambiente Virtual"

    # Verifica Python no sistema
    if [ -n "$(command -v "${PYTHON}" 2>/dev/null)" ]; then
        log "Python ${PYTHON_VERSION} encontrado: $(${PYTHON} --version 2>&1)"
    else
        err "Python ${PYTHON_VERSION} não encontrado no sistema."
    fi

    # Verifica ambiente virtual
    if [[ -d "${VENV_DIR}" && -f "${VENV_BIN}/python" ]]; then
        log "Ambiente virtual: ${VENV_DIR}"
        log "Versão Python no venv: $(${VENV_BIN}/python --version 2>&1)"

        # Verifica Poetry
        if [[ -f "${VENV_BIN}/poetry" ]]; then
            log "Poetry: $(${VENV_BIN}/poetry --version 2>&1)"
        else
            warn "Poetry não instalado no ambiente virtual."
        fi

        # Verifica ferramentas
        info "Ferramentas instaladas:"
        for tool in "${ESSENTIAL_TOOLS[@]}"; do
            if [[ -f "${VENV_BIN}/${tool}" ]]; then
                if [ -n "$("${VENV_BIN}/${tool}" --version 2>/dev/null)" ]; then
                    version=$("${VENV_BIN}/${tool}" --version 2>&1 | head -n 1)
                    echo "  ✓ ${tool}: ${version}"
                else
                    echo "  ✓ ${tool} (sem versão disponível)"
                fi
            else
                echo "  ✗ ${tool} (não instalado no ambiente virtual)"
            fi
        done
    else
        warn "Ambiente virtual não encontrado ou incompleto."
    fi
}

# ‣ Funções para gerenciamento do poetry.lock
check_poetry_lock() {
    header "Verificando Poetry Lock"
    
    # Ativa o ambiente virtual
    source "${VENV_DIR}/bin/activate" || {
        err "Não foi possível ativar o ambiente virtual."
        return 1
    }
    
    # Verifica se o Poetry está disponível
    if [ -z "$(command -v poetry)" ]; then
        err "Poetry não está disponível. Execute 'create_venv' primeiro."
        return 1
    fi
    
    check_and_update_poetry_lock false
}

update_poetry_lock() {
    header "Atualizando Poetry Lock"
    
    # Ativa o ambiente virtual
    source "${VENV_DIR}/bin/activate" || {
        err "Não foi possível ativar o ambiente virtual."
        return 1
    }
    
    # Verifica se o Poetry está disponível
    if [ -z "$(command -v poetry)" ]; then
        err "Poetry não está disponível. Execute 'create_venv' primeiro."
        return 1
    fi
    
    check_and_update_poetry_lock false
}

force_poetry_lock() {
    header "Forçando Regeneração do Poetry Lock"
    
    # Ativa o ambiente virtual
    source "${VENV_DIR}/bin/activate" || {
        err "Não foi possível ativar o ambiente virtual."
        return 1
    }
    
    # Verifica se o Poetry está disponível
    if [ -z "$(command -v poetry)" ]; then
        err "Poetry não está disponível. Execute 'create_venv' primeiro."
        return 1
    fi
    
    check_and_update_poetry_lock true
}

# ‣ Processamento de comandos
if [[ $# -eq 0 ]]; then
    usage
fi

cmd="$1"
shift || true

case "${cmd}" in
create)
    create_venv
    ;;
clean)
    clean_venv
    ;;
rebuild)
    rebuild_venv
    ;;
install)
    install_deps false
    ;;
install-dev)
    install_deps true
    ;;
verify)
    if check_venv; then
        log "Ambiente virtual está correto e funcional."
        exit 0
    else
        err "Ambiente virtual precisa ser recriado."
        exit 1
    fi
    ;;
check-tools)
    verify_tools
    ;;
status)
    show_status
    ;;
check-lock)
    check_poetry_lock
    ;;
update-lock)
    update_poetry_lock
    ;;
force-lock)
    force_poetry_lock
    ;;
*)
    err "Comando desconhecido: ${cmd}"
    usage
    ;;
esac
