#!/usr/bin/env bash
###############################################################################
#  dismiss_assert_alerts.sh  —  v2.1
#  Autor   : Marlon Costa <marlon.costa@datacosmos.com.br>
#  Licença : Apache-2.0
###############################################################################
set -euo pipefail

#──────────────────═[ Config ]═───────────────────────────────────────────────
GH_REPO="${GH_REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
PER_PAGE="${PER_PAGE:-100}"
SEARCH_PATTERN="${SEARCH_PATTERN:-assert}"
DISMISS_REASON="${DISMISS_REASON:-used in tests}"
DISMISS_COMMENT="${DISMISS_COMMENT:-Automated dismissal – code only used in tests}"

#──────────────────═[ Checks ]═───────────────────────────────────────────────
for cmd in gh jq; do
  command -v "$cmd" >/dev/null || {
    echo "❌  $cmd não encontrado." >&2
    exit 1
  }
done

echo "🔐  Verificando acesso a ${GH_REPO}…"
page0=$(gh api -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${GH_REPO}/code-scanning/alerts?per_page=1" 2>/dev/null)

if [ -z "$page0" ]; then
  case "$page0" in
  *"HTTP 404"*)
    echo "❗  404 Not Found — possivelmente:\n" \
      "    • Code-Scanning não habilitado\n" \
      "    • Token sem escopo security_events/repo\n" \
      "    • Repositório inexistente ou privado\n" >&2
    exit 1
    ;;
  *"HTTP 401"*)
    echo "❗  401 Unauthorized — execute 'gh auth login' ou verifique o token." >&2
    exit 1
    ;;
  *)
    echo "$page0" >&2
    exit 1
    ;;
  esac
fi

#──────────────────═[ Funções ]═──────────────────────────────────────────────
dismiss_alert() {
  local number="$1"
  gh api --silent -X PATCH "repos/${GH_REPO}/code-scanning/alerts/${number}" \
    -H "Accept: application/vnd.github+json" \
    -F state=dismissed \
    -F dismissed_reason="${DISMISS_REASON}" \
    -F dismissed_comment="${DISMISS_COMMENT}"
  echo "✔︎  Alert #${number} dismisssed"
}

#──────────────────═[ Paginação ]═────────────────────────────────────────────
echo "🔍  Procurando alertas contendo "${SEARCH_PATTERN}"…"
page=1 dismissed=0

while :; do
  echo "📄  Página ${page}"
  resp=$(gh api --silent \
    "repos/${GH_REPO}/code-scanning/alerts" \
    -F state=open -F per_page="${PER_PAGE}" -F page="${page}" \
    -H "Accept: application/vnd.github+json") || break

  count=$(jq 'length' <<<"$resp")
  [[ "$count" -eq 0 ]] && break

  mapfile -t ids < <(
    jq -r --arg re "(?i)${SEARCH_PATTERN}" '
      .[] | select(
        (.rule.description | test($re)) or
        (.rule.name        | test($re)) or
        (.rule.id          | test($re)) or
        (.most_recent_instance.message.text // "" | test($re))
      ) | .number' <<<"$resp"
  )

  for id in "${ids[@]}"; do
    dismiss_alert "$id"
    ((dismissed++))
  done

  ((page++))
done

echo "🎉  Concluído – ${dismissed} alerta(s) descartado(s)."
