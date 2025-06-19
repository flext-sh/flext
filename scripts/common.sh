#!/usr/bin/env bash
###############################################################################
#  common.sh — Funções utilitárias e variáveis globais
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  License: MIT
###############################################################################
set -Eeuo pipefail

# ‣ Work-space
# shellcheck disable=SC2034
WORKSPACE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

# ‣ Detecção dinâmica de projetos (mesma lógica do Makefile)
EXCLUDE_DIRS="reference docs logs scripts reports schemas temp_workflows junit src tests"

# Função para detectar projetos dinamicamente
detect_projects() {
	local projects=()
	while IFS= read -r -d '' project_dir; do
		projects+=("$project_dir")
	done < <(find "${WORKSPACE_ROOT}" \
		-mindepth 1 \
		-maxdepth 1 \
		-type d \
		-not -name ".*" \
		$(printf -- '-not -name "%s" ' "$EXCLUDE_DIRS") \
		-exec test -f {}/pyproject.toml \; \
		-print0 |
		sort -z)

	printf '%s\n' "${projects[@]}"
}

# shellcheck disable=SC2034
PROJECTS=($(detect_projects))

# ‣ Cores
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'
BLUE=$'\033[0;34m'
NC=$'\033[0m'

# ‣ Ferramentas e Diretórios
# Usa especificamente Python 3.13
PYTHON_VERSION="3.13"
PYTHON="python${PYTHON_VERSION}"
POETRY="poetry"
VENV_DIR="${WORKSPACE_ROOT}/.venv"
VENV_BIN="${VENV_DIR}/bin"
# shellcheck disable=SC2034
VENV_PYTHON="${VENV_BIN}/python"
VENV_PIP="${VENV_BIN}/pip"
VENV_POETRY="${VENV_BIN}/poetry"

# ‣ Ferramentas essenciais
ESSENTIAL_TOOLS=(
	"pytest"
	"black"
	"isort"
	"ruff"
	"mypy"
	"flake8"
	"bandit"
	"pyupgrade"
	"autoflake"
	"refurb"
)

# ‣ Utilitário simples de log
log() { printf "${GREEN}%s${NC}\n" "$*"; }
warn() { printf "${YELLOW}%s${NC}\n" "$*"; }
err() { printf "${RED}%s${NC}\n" "$*" >&2; }
info() { printf "${CYAN}%s${NC}\n" "$*"; }
header() { printf "${BLUE}=== %s ===${NC}\n" "$*"; }

# ‣ Função para validar Python
validate_python() {
	if [ -z "$(command -v "${PYTHON}")" ]; then
		err "Python ${PYTHON_VERSION} não encontrado no sistema."
		err "Por favor, instale Python ${PYTHON_VERSION} para continuar:"
		err "$ sudo dnf install python${PYTHON_VERSION}"
		return 1
	fi

	# Verifica se a versão é realmente 3.13.x
	local version
	version=$(${PYTHON} --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
	if [ "${version}" != "${PYTHON_VERSION}" ]; then
		err "Versão incorreta de Python. Necessário ${PYTHON_VERSION}, encontrado ${version}"
		return 1
	fi

	info "Usando $(${PYTHON} --version)"
	return 0
}

# ‣ Função para verificar ambiente virtual
check_venv() {
	# Verifica se o ambiente virtual existe
	if [ -z "$(test -d "${VENV_DIR}" && echo exists)" ]; then
		warn "Ambiente virtual não encontrado."
		return 1
	fi

	# Ativa o ambiente virtual
	source "${VENV_DIR}/bin/activate" 2>/dev/null || {
		warn "Não foi possível ativar o ambiente virtual."
		return 1
	}

	# Verifica se o python está funcionando
	if [ -z "$(python --version 2>&1)" ]; then
		warn "Python não está funcionando no ambiente virtual."
		return 1
	fi

	# Verifica se o pip está funcionando
	if [ -z "$(pip --version 2>&1)" ]; then
		warn "Pip não está funcionando no ambiente virtual."
		return 1
	fi

	# Verifica se o Poetry está instalado
	if [ -z "$(command -v poetry)" ]; then
		warn "Poetry não está instalado no ambiente virtual."
		return 1
	fi

	# Ambiente virtual está ok
	log "Ambiente virtual encontrado e funcionando."
	return 0
}

# ‣ Função para criar ambiente virtual
create_venv() {
	validate_python || return 1

	info "Criando ambiente virtual em ${VENV_DIR}..."
	rm -rf "${VENV_DIR}" 2>/dev/null || true

	# Criar ambiente virtual com isolamento completo
	"${PYTHON}" -m venv --upgrade-deps --copies "${VENV_DIR}" || {
		err "Falha ao criar ambiente virtual."
		return 1
	}

	info "Ativando ambiente virtual..."
	# Ativamos o ambiente virtual
	source "${VENV_DIR}/bin/activate" || {
		err "Falha ao ativar ambiente virtual."
		return 1
	}

	# Verifica se está realmente usando o Python do ambiente virtual
	VENV_PATH=$(which python)
	if [ "$VENV_PATH" != "${VENV_DIR}/bin/python" ]; then
		err "Ambiente virtual não está sendo usado corretamente."
		err "Path atual: $VENV_PATH"
		err "Esperado: ${VENV_DIR}/bin/python"
		return 1
	fi

	# Atualiza pip e instala pacotes básicos (força reinstalação)
	info "Atualizando pip e instalando pacotes básicos..."
	python -m pip install --upgrade --force-reinstall pip setuptools wheel || {
		err "Falha ao atualizar pip e instalar pacotes básicos."
		return 1
	}

	# Instala Poetry (força reinstalação)
	info "Instalando poetry..."
	python -m pip install --force-reinstall poetry || {
		err "Falha ao instalar poetry."
		return 1
	}

	# Verifica se o Poetry foi instalado corretamente no ambiente virtual
	POETRY_PATH=$(which poetry)
	if [ "$POETRY_PATH" != "${VENV_DIR}/bin/poetry" ]; then
		err "Poetry não foi instalado corretamente no ambiente virtual."
		err "Path do poetry: $POETRY_PATH"
		return 1
	fi

	log "Ambiente virtual criado com sucesso."
	return 0
}

# ‣ Função para verificar e atualizar poetry.lock se necessário
check_and_update_poetry_lock() {
	local force_update=${1:-false}

	# Vai para o diretório raiz do workspace
	cd "${WORKSPACE_ROOT}" || {
		err "Não foi possível acessar o diretório do workspace."
		return 1
	}

	# Verifica se pyproject.toml existe
	if [ -z "$(test -f "pyproject.toml" && echo exists)" ]; then
		warn "pyproject.toml não encontrado no diretório raiz."
		return 0
	fi

	# Se force_update for true, regenera o lock file
	if [[ ${force_update} == "true" ]]; then
		info "Forçando regeneração do poetry.lock..."
		poetry lock || {
			err "Falha ao regenerar poetry.lock."
			return 1
		}
		log "poetry.lock regenerado com sucesso."
		return 0
	fi

	# Verifica se poetry.lock existe
	if [ -z "$(test -f "poetry.lock" && echo exists)" ]; then
		info "poetry.lock não encontrado. Gerando..."
		poetry lock || {
			err "Falha ao gerar poetry.lock."
			return 1
		}
		log "poetry.lock gerado com sucesso."
		return 0
	fi

	# Verifica se pyproject.toml é mais recente que poetry.lock
	if [[ "pyproject.toml" -nt "poetry.lock" ]]; then
		info "pyproject.toml foi modificado após poetry.lock."
		info "Regenerando poetry.lock..."
		poetry lock || {
			err "Falha ao atualizar poetry.lock."
			return 1
		}
		log "poetry.lock atualizado com sucesso."
	else
		info "poetry.lock está sincronizado com pyproject.toml."
	fi

	return 0
}

# ‣ Função para instalar dependências com poetry
install_deps() {
	local dev=${1:-false}

	# Ativar ambiente virtual
	source "${VENV_DIR}/bin/activate" || {
		err "Não foi possível ativar o ambiente virtual."
		return 1
	}

	# Verifica se o Poetry está disponível
	if [ -z "$(command -v poetry)" ]; then
		err "Poetry não está disponível. Execute 'create_venv' primeiro."
		return 1
	fi

	# Verifica e atualiza poetry.lock se necessário
	check_and_update_poetry_lock || {
		err "Falha na verificação do poetry.lock."
		return 1
	}

	info "Instalando dependências via poetry..."

	# Vai para o diretório raiz do workspace
	cd "${WORKSPACE_ROOT}" || {
		err "Não foi possível acessar o diretório do workspace."
		return 1
	}

	# Instala dependências com ou sem dev
	if [[ ${dev} == "true" ]]; then
		poetry install --with dev || {
			err "Falha ao instalar dependências de desenvolvimento."
			return 1
		}
	else
		poetry install || {
			err "Falha ao instalar dependências."
			return 1
		}
	fi

	log "Dependências instaladas com sucesso."
	return 0
}

# ‣ Função para verificar e instalar ferramentas essenciais
verify_tools() {
	# Ativa o ambiente virtual
	source "${VENV_DIR}/bin/activate" 2>/dev/null || {
		err "Não foi possível ativar o ambiente virtual."
		err "Execute 'create_venv' primeiro."
		return 1
	}

	# Verifica se o Python está funcionando
	if [ -z "$(python --version 2>&1)" ]; then
		err "Python não está funcionando no ambiente virtual."
		err "Execute 'create_venv' primeiro."
		return 1
	fi

	info "Instalando ferramentas essenciais..."

	# Instala todas as ferramentas de uma vez
	python -m pip install pytest black isort ruff mypy flake8 bandit pyupgrade autoflake refurb || {
		err "Falha ao instalar ferramentas essenciais."
		return 1
	}

	log "Ferramentas essenciais instaladas com sucesso."
	return 0
}

# ‣ Função para limpar ambiente virtual
clean_venv() {
	info "Removendo ambiente virtual..."

	# Força a desativação do ambiente virtual
	if [[ -n ${VIRTUAL_ENV:-} ]]; then
		info "Desativando ambiente virtual..."
		unset VIRTUAL_ENV
		unset PYTHONPATH
		export PATH=$(echo "$PATH" | sed "s|${VENV_DIR}/bin:||g")
	fi

	# Remove o diretório do ambiente virtual com força
	if [[ -d ${VENV_DIR} ]]; then
		info "Removendo diretório ${VENV_DIR}..."
		rm -rf "${VENV_DIR}" 2>/dev/null || {
			# Se falhar, tenta com sudo ou força
			chmod -R 755 "${VENV_DIR}" 2>/dev/null || true
			rm -rf "${VENV_DIR}" 2>/dev/null || true
		}
	fi

	log "Ambiente virtual removido."
	return 0
}

# ‣ Função para recriar ambiente virtual e reinstalar tudo
rebuild_venv() {
	header "Reconstruindo ambiente virtual"

	# Limpa, cria e instala tudo novamente
	clean_venv || true
	create_venv || return 1
	install_deps true || return 1
	verify_tools || return 1

	log "Ambiente virtual reconstruído com sucesso!"
	return 0
}
