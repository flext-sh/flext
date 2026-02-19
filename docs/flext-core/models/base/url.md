# Url (`FlextModels.Base.Url`)


<!-- TOC START -->
- [Visão geral](#viso-geral)
- [Contrato](#contrato)
- [Arquitetura e dependências](#arquitetura-e-dependncias)
- [Situação atual no repositório](#situao-atual-no-repositrio)
- [Oportunidades de integração](#oportunidades-de-integrao)
- [Integrações atuais (strings que deveriam virar `Url`)](#integraes-atuais-strings-que-deveriam-virar-url)
- [Extensões planejadas](#extenses-planejadas)
- [Pontos fortes x riscos](#pontos-fortes-x-riscos)
- [Backlog recomendado](#backlog-recomendado)
<!-- TOC END -->

## Visão geral

Objeto de valor imutável que encapsula URLs HTTP/HTTPS com validação do Pydantic v2 (`HttpUrl`). Disponível em `flext_core/_models/base.py` e exposto por `FlextModels.Url`. Apesar de ainda não ter sido adotado, ele foi criado para ser o “tipo oficial” dos endpoints usados em APIs internas, taps/targets Singer e integrações observability.

## Contrato

- Herda `FlextModelsEntity.Value`, garantindo imutabilidade, comparação por valor e hash estável.
- Campo único `url: HttpUrl` (aceita apenas esquemas `http` e `https`; normaliza host/path/porta; valida TLD e credenciais conforme regras do Pydantic v2).
- Por ser value object, se integra facilmente com `FlextModels.Collections.Options` e pode ser usado em dicionários/cache sem risco de mutação.

## Arquitetura e dependências

- Depende apenas do namespace Entity e do tipo `HttpUrl`. Não exige `u`, então pode ser importado por qualquer módulo sem risco de ciclos.
- Foi planejado para conviver com `FlextSettings` (`flext_core/config.py`) — onde hoje lidamos com `str` vindos de variáveis de ambiente.
- As configurações de endpoints espalhadas pelos projetos (ex.: `flext-api/config.py`, `flext-target-oracle/configuration.py`, `flext-observability/config.py`) poderiam trocar `str` por `FlextModels.Url` dando validação automática.

## Situação atual no repositório

- A busca `rg -n "FlextModels\.Url" --glob "*.py" --glob "!*tests*"` retorna apenas a declaração do modelo; não há consumidores em `src/`.
- Isso implica que hoje qualquer alteração em endpoints precisa ser validada manualmente — risco alto para ambientes multi-tenant.

## Oportunidades de integração

1. **`flext-api`**: arquivos `flext-api/src/flext_api/config.py` e `.../settings.py` possuem diversas URLs (documentação, swagger, auth). Substituir os campos `str` por `FlextModels.Url` eliminaria validações personalizadas.
2. **Targets Singer**: `flext-target-oracle/target_commands.py` e seus congêneres definem endpoints do Oracle REST Data Services; esses valores poderiam ser `FlextModels.Url`, permitindo serialização e logging padronizado.
3. **Observability/Webhooks**: projetos `flext-observability` e `flext-plugin` enviam dados para webhooks externos; `Url` garantiria que apenas HTTP/HTTPS fosse aceito antes de acionar requests.

## Integrações atuais (strings que deveriam virar `Url`)

- `flext-api/src/flext_api/config.py:31-70` declara `base_url: str = Field(default=FlextApiConstants.DEFAULT_BASE_URL)` e validações repetidas; `Url` eliminaria repetição.
- `flext-api/src/flext_api/models.py:248-470` contém múltiplos campos `documentation_url`, `swagger_url`, `openapi_url` que poderiam ser `FlextModels.Url`.
- `flext-target-oracle/src/flext_target_oracle/config.py` e `models.py` (pelas ocorrências `rg -n "https"`) armazenam endpoints de Oracle REST Data Services como `str`.
- `flext-observability/src/...` e `flext-plugin/src/...` mantêm webhooks/URLs externas; `Url` garantiria validação centralizada antes de enviar eventos.

## Extensões planejadas

- **Protocolos adicionais**: muitos projetos (LDAP taps, Oracle OIC) usam esquemas não suportados por `HttpUrl`. Uma subclasse (`EndpointUrl`) deveria aceitar `ldap`, `ldaps`, `wss`, `oracle` usando `StrictStr` + validadores custom.
- **Factories**: helpers como `Url.from_env("SERVICE_URL")` ou `Url.from_config(FlextSettings, "registry_url")` para eliminar repetição de parsing.
- **Listas de permissão**: integrar `FlextSettings`/`u.Validation` para validar hostnames contra uma allowlist (evita endpoints externos inesperados).

## Pontos fortes x riscos

- **Fortes**: validação automática, imutabilidade, interoperável com `Value` (hash, equality), apropriado para serialização/documentação.
- **Riscos**: sem adoção, o modelo envelhece sem feedback; restrito a HTTP/HTTPS; ausência de convertes (de dict/config) torna migração mais custosa.

## Backlog recomendado

1. Mapear campos `str` que representam URLs (usar `rg -n "http" flext-*/config.py`) e priorizar migração por criticidade (API pública > targets > ferramentas internas).
2. Adicionar `FlextModels.EndpointUrl` com suporte a protocolos adicionais e apontar o README deste namespace para a extensão.
3. Documentar guidelines: “todo endpoint exposto externamente deve usar `FlextModels.Url` ou derivados” e atualizar `AGENTS` caso exista.
4. Criar testes integrados em `flext-core/examples/00_single_import_demo.py` demonstrando o uso de `Url` junto com `FlextModels.Metadata` para registrar endpoints em `FlextRegistry`.
