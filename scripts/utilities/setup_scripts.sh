#!/usr/bin/env bash
###############################################################################
#  setups_scripts.sh — WORKSPACE BOOTSTRAP (Datacosmos © 2025)
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  License: MIT
###############################################################################
#  DESCRIÇÃO
#    Torna os scripts Python executáveis e cria symlinks convenientes em
#    scripts/bin. Agora o WORKSPACE_ROOT é calculado dinamicamente a partir
#    da pasta onde este script reside, evitando caminhos absolutos.
###############################################################################

set -euo pipefail

## ─── DETECTA O WORKSPACE ROOT ────────────────────────────────────────────────
#   • Assume que este script está em <root>/scripts/, então o parent é <root>.
#   • Se por algum motivo a estrutura mudar, tenta 'git rev-parse --show-toplevel'.

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
WORKSPACE_ROOT="$(dirname "$script_dir")"

# Fallback: uso dentro de submódulo Git ou layout diferente
if [ -z "$(test -f "${WORKSPACE_ROOT}/Makefile" && echo exists)" ]; then
    WORKSPACE_ROOT="$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null || true)"
fi

[[ -d "$WORKSPACE_ROOT" ]] || {
    echo "Error: Could not determine WORKSPACE_ROOT." >&2
    exit 1
}

SCRIPTS_DIR="${WORKSPACE_ROOT}/scripts"
BIN_DIR="${SCRIPTS_DIR}/bin"

echo "Setting up scripts in ${SCRIPTS_DIR} …"

## ─── GARANTE EXECUÇÃO A PARTIR DA RAIZ ───────────────────────────────────────
cd "${WORKSPACE_ROOT}"

## ─── PREPARA BIN E PERMISSÕES ────────────────────────────────────────────────
mkdir -p "${BIN_DIR}"

chmod +x "${SCRIPTS_DIR}/project_manage.py" \
    "${SCRIPTS_DIR}/scaffold_manage.py" \
    "${SCRIPTS_DIR}/git_manage.py"

ln -sf "${SCRIPTS_DIR}/project_manage.py" "${BIN_DIR}/flx_project-manage"
ln -sf "${SCRIPTS_DIR}/scaffold_manage.py" "${BIN_DIR}/scaffold-manage"
ln -sf "${SCRIPTS_DIR}/git_manage.py" "${BIN_DIR}/git-manage"

## ─── WRAPPERS DE COMANDO (ROOT EMBUTIDO) ─────────────────────────────────────
cat >"${BIN_DIR}/setup" <<EOF
#!/usr/bin/env bash
"${WORKSPACE_ROOT}/scripts/project_manage.py" setup "\$@"
EOF
chmod +x "${BIN_DIR}/setup"

cat >"${BIN_DIR}/status" <<EOF
#!/usr/bin/env bash
"${WORKSPACE_ROOT}/scripts/project_manage.py" status "\$@"
EOF
chmod +x "${BIN_DIR}/status"

cat >"${BIN_DIR}/scaffold" <<EOF
#!/usr/bin/env bash
"${WORKSPACE_ROOT}/scripts/scaffold_manage.py" "\$@"
EOF
chmod +x "${BIN_DIR}/scaffold"

cat >"${BIN_DIR}/git-op" <<EOF
#!/usr/bin/env bash
"${WORKSPACE_ROOT}/scripts/git_manage.py" "\$@"
EOF
chmod +x "${BIN_DIR}/git-op"

cat >"${BIN_DIR}/setup-venv" <<EOF
#!/usr/bin/env bash
"${WORKSPACE_ROOT}/scripts/setup_venv.sh" "\$@"
EOF
chmod +x "${BIN_DIR}/setup-venv"

## ─── EXPORTA PATH NO .bashrc SE NECESSÁRIO ───────────────────────────────────
BASHRC="${HOME}/.bashrc"
BIN_PATH_EXPORT="export PATH=\"${BIN_DIR}:\$PATH\""

if [ -z "$(grep -F "${BIN_DIR}" "${BASHRC}")" ]; then
    printf '\n# pyauto workspace scripts\n%s\n' "${BIN_PATH_EXPORT}" >>"${BASHRC}"
    echo "Added ${BIN_DIR} to PATH in ${BASHRC}.  Run 'source ${BASHRC}' to apply."
else
    echo "${BIN_DIR} is already in PATH."
fi

## ─── RESUMO ──────────────────────────────────────────────────────────────────
cat <<EOM

Setup complete! Available commands:
    flx_project-manage   – Manage projects
    scaffold-manage  – Manage scaffolds
    git-manage       – Git operations
    setup            – Initial workspace setup
    status           – Show flx_project status
    scaffold         – Scaffold shorthand
    git-op           – Git shorthand
    setup-venv        – Setup virtual environment

EOM
