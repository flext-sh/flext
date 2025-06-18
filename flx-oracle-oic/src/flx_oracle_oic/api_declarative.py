"""Implementação declarativa da API Oracle Integration Cloud
Baseada em padrões para maximizar reutilização.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HttpMethod(Enum):
    """Métodos HTTP suportados."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ApiParameter:
    """Parâmetro de API."""

    name: str
    param_type: str  # "path", "query", "body"
    required: bool = True
    description: str = ""
    default: Any = None


@dataclass
class ApiEndpoint:
    """Endpoint de API declarativo."""

    name: str
    method: HttpMethod
    path: str
    description: str
    parameters: list[ApiParameter] = field(default_factory=list)
    response_type: str = "dict"
    tags: list[str] = field(default_factory=list)

    def get_path_params(self) -> list[ApiParameter]:
        """Retorna parâmetros de path."""
        return [p for p in self.parameters if p.param_type == "path"]

    def get_query_params(self) -> list[ApiParameter]:
        """Retorna parâmetros de query."""
        return [p for p in self.parameters if p.param_type == "query"]

    def get_body_params(self) -> list[ApiParameter]:
        """Retorna parâmetros de body."""
        return [p for p in self.parameters if p.param_type == "body"]


@dataclass
class ApiGroup:
    """Grupo de endpoints relacionados."""

    name: str
    base_path: str
    description: str
    endpoints: list[ApiEndpoint] = field(default_factory=list)

    def add_endpoint(self, endpoint: ApiEndpoint) -> None:
        """Adiciona endpoint ao grupo."""
        self.endpoints.append(endpoint)


class OicApiDeclaration:
    """Declaração completa da API OIC."""

    def __init__(self) -> None:
        self.groups: dict[str, ApiGroup] = {}
        self._build_api_declaration()

    def _build_api_declaration(self) -> None:
        """Constrói a declaração completa da API."""
        # INTEGRATION ENDPOINTS
        integration_group = ApiGroup(
            name="integrations",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de integrações",
        )

        # Padrão CRUD para integrações
        self._add_crud_endpoints(integration_group, "integrations", "integration")

        # Endpoints específicos de integração
        integration_group.add_endpoint(
            ApiEndpoint(
                name="activate_integration",
                method=HttpMethod.POST,
                path="/integrations/{id}/schedule/start",
                description="Ativa uma integração",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da integração"
                    )
                ],
            ),
        )

        integration_group.add_endpoint(
            ApiEndpoint(
                name="deactivate_integration",
                method=HttpMethod.POST,
                path="/integrations/{id}/schedule/stop",
                description="Desativa uma integração",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da integração"
                    )
                ],
            ),
        )

        integration_group.add_endpoint(
            ApiEndpoint(
                name="clone_integration",
                method=HttpMethod.POST,
                path="/integrations/{id}/clone",
                description="Clona uma integração",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da integração"
                    ),
                    ApiParameter(
                        "clone_request",
                        "body",
                        required=True,
                        description="Dados do clone",
                    ),
                ],
            ),
        )

        integration_group.add_endpoint(
            ApiEndpoint(
                name="get_activation_status",
                method=HttpMethod.GET,
                path="/integrations/{id}/activationStatus",
                description="Obtém status de ativação",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da integração"
                    )
                ],
            ),
        )

        integration_group.add_endpoint(
            ApiEndpoint(
                name="get_activation_errors",
                method=HttpMethod.GET,
                path="/integrations/{id}/activationErrors",
                description="Obtém erros de ativação",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da integração"
                    )
                ],
            ),
        )

        self.groups["integrations"] = integration_group

        # CONNECTIONS ENDPOINTS
        connections_group = ApiGroup(
            name="connections",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de conexões",
        )

        self._add_crud_endpoints(connections_group, "connections", "connection")

        # Endpoints específicos de conexão
        connections_group.add_endpoint(
            ApiEndpoint(
                name="test_connection",
                method=HttpMethod.POST,
                path="/connections/{id}/test",
                description="Testa uma conexão",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da conexão"
                    )
                ],
            ),
        )

        connections_group.add_endpoint(
            ApiEndpoint(
                name="validate_connection",
                method=HttpMethod.POST,
                path="/connections/{id}/validate",
                description="Valida uma conexão",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da conexão"
                    )
                ],
            ),
        )

        connections_group.add_endpoint(
            ApiEndpoint(
                name="get_connection_metadata",
                method=HttpMethod.GET,
                path="/connections/{id}/metadata",
                description="Obtém metadados da conexão",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da conexão"
                    )
                ],
            ),
        )

        self.groups["connections"] = connections_group

        # MONITORING ENDPOINTS
        monitoring_group = ApiGroup(
            name="monitoring",
            base_path="/ic/api/integration/v1/monitoring",
            description="Monitoramento e observabilidade",
        )

        # Instâncias
        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="get_instances",
                method=HttpMethod.GET,
                path="/instances",
                description="Lista instâncias de execução",
                parameters=[
                    *self._get_pagination_params(),
                    ApiParameter(
                        "integration",
                        "query",
                        required=False,
                        description="Filtro por integração",
                    ),
                    ApiParameter(
                        "status",
                        "query",
                        required=False,
                        description="Filtro por status",
                    ),
                    ApiParameter(
                        "fromTime",
                        "query",
                        required=False,
                        description="Data/hora inicial",
                    ),
                    ApiParameter(
                        "toTime", "query", required=False, description="Data/hora final"
                    ),
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="get_instance",
                method=HttpMethod.GET,
                path="/instances/{id}",
                description="Obtém detalhes de uma instância",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da instância"
                    )
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="abort_instance",
                method=HttpMethod.POST,
                path="/instances/{id}/abort",
                description="Aborta uma instância",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da instância"
                    )
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="get_activity_stream",
                method=HttpMethod.GET,
                path="/instances/{id}/activityStream",
                description="Obtém stream de atividades",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da instância"
                    )
                ],
            ),
        )

        # Erros
        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="get_errors",
                method=HttpMethod.GET,
                path="/errors",
                description="Lista erros",
                parameters=[
                    *self._get_pagination_params(),
                    ApiParameter(
                        "integration",
                        "query",
                        required=False,
                        description="Filtro por integração",
                    ),
                    ApiParameter(
                        "fromTime",
                        "query",
                        required=False,
                        description="Data/hora inicial",
                    ),
                    ApiParameter(
                        "toTime", "query", required=False, description="Data/hora final"
                    ),
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="get_error",
                method=HttpMethod.GET,
                path="/errors/{id}",
                description="Obtém detalhes de um erro",
                parameters=[
                    ApiParameter("id", "path", required=True, description="ID do erro")
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="resubmit_error",
                method=HttpMethod.POST,
                path="/errors/{id}/resubmit",
                description="Reenvia um erro",
                parameters=[
                    ApiParameter("id", "path", required=True, description="ID do erro")
                ],
            ),
        )

        monitoring_group.add_endpoint(
            ApiEndpoint(
                name="discard_error",
                method=HttpMethod.POST,
                path="/errors/{id}/discard",
                description="Descarta um erro",
                parameters=[
                    ApiParameter("id", "path", required=True, description="ID do erro")
                ],
            ),
        )

        self.groups["monitoring"] = monitoring_group

        # PACKAGES ENDPOINTS
        packages_group = ApiGroup(
            name="packages",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de pacotes",
        )

        self._add_crud_endpoints(packages_group, "packages", "package")

        packages_group.add_endpoint(
            ApiEndpoint(
                name="load_sample_packages",
                method=HttpMethod.POST,
                path="/packages/loadSamples",
                description="Carrega pacotes de exemplo",
                parameters=[],
            ),
        )

        self.groups["packages"] = packages_group

        # PROJECTS ENDPOINTS
        projects_group = ApiGroup(
            name="projects",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de projetos",
        )

        self._add_crud_endpoints(projects_group, "projects", "project")

        projects_group.add_endpoint(
            ApiEndpoint(
                name="clone_project",
                method=HttpMethod.POST,
                path="/projects/{id}/clone",
                description="Clona um projeto",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID do projeto"
                    ),
                    ApiParameter(
                        "clone_request",
                        "body",
                        required=True,
                        description="Dados do clone",
                    ),
                ],
            ),
        )

        projects_group.add_endpoint(
            ApiEndpoint(
                name="get_project_acl",
                method=HttpMethod.GET,
                path="/projects/{id}/acl",
                description="Obtém ACL do projeto",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID do projeto"
                    )
                ],
            ),
        )

        self.groups["projects"] = projects_group

        # LOOKUPS ENDPOINTS
        lookups_group = ApiGroup(
            name="lookups",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de lookups",
        )

        self._add_crud_endpoints(lookups_group, "lookups", "lookup", id_field="name")

        lookups_group.add_endpoint(
            ApiEndpoint(
                name="clone_lookup",
                method=HttpMethod.POST,
                path="/lookups/{name}/clone",
                description="Clona um lookup",
                parameters=[
                    ApiParameter(
                        "name", "path", required=True, description="Nome do lookup"
                    ),
                    ApiParameter(
                        "clone_request",
                        "body",
                        required=True,
                        description="Dados do clone",
                    ),
                ],
            ),
        )

        lookups_group.add_endpoint(
            ApiEndpoint(
                name="get_lookup_usage",
                method=HttpMethod.GET,
                path="/lookups/{name}/usage",
                description="Obtém uso do lookup",
                parameters=[
                    ApiParameter(
                        "name", "path", required=True, description="Nome do lookup"
                    )
                ],
            ),
        )

        self.groups["lookups"] = lookups_group

        # LIBRARIES ENDPOINTS
        libraries_group = ApiGroup(
            name="libraries",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de bibliotecas",
        )

        self._add_crud_endpoints(libraries_group, "libraries", "library")

        libraries_group.add_endpoint(
            ApiEndpoint(
                name="get_library_metadata",
                method=HttpMethod.GET,
                path="/libraries/{id}/metadata",
                description="Obtém metadados da biblioteca",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID da biblioteca"
                    )
                ],
            ),
        )

        self.groups["libraries"] = libraries_group

        # CERTIFICATES ENDPOINTS
        certificates_group = ApiGroup(
            name="certificates",
            base_path="/ic/api/integration/v1",
            description="Gerenciamento de certificados",
        )

        self._add_crud_endpoints(certificates_group, "certificates", "certificate")

        self.groups["certificates"] = certificates_group

        # ADAPTERS ENDPOINTS
        adapters_group = ApiGroup(
            name="adapters",
            base_path="/ic/api/adapters/v1",
            description="Gerenciamento de adaptadores",
        )

        adapters_group.add_endpoint(
            ApiEndpoint(
                name="get_adapter_bundles",
                method=HttpMethod.GET,
                path="/adapterBundles",
                description="Lista adapter bundles",
                parameters=self._get_pagination_params(),
            ),
        )

        adapters_group.add_endpoint(
            ApiEndpoint(
                name="get_adapter_bundle",
                method=HttpMethod.GET,
                path="/adapterBundles/{id}",
                description="Obtém adapter bundle",
                parameters=[
                    ApiParameter(
                        "id", "path", required=True, description="ID do adapter bundle"
                    )
                ],
            ),
        )

        self.groups["adapters"] = adapters_group

        # ENVIRONMENT ENDPOINTS
        environment_group = ApiGroup(
            name="environment",
            base_path="/ic/api/integration/v1",
            description="Configuração do ambiente",
        )

        environment_group.add_endpoint(
            ApiEndpoint(
                name="get_cors_domains",
                method=HttpMethod.GET,
                path="/environment/corsdomains",
                description="Lista domínios CORS",
                parameters=[],
            ),
        )

        environment_group.add_endpoint(
            ApiEndpoint(
                name="create_cors_domain",
                method=HttpMethod.POST,
                path="/environment/corsdomains",
                description="Cria domínio CORS",
                parameters=[
                    ApiParameter(
                        "domain_data",
                        "body",
                        required=True,
                        description="Dados do domínio",
                    ),
                ],
            ),
        )

        self.groups["environment"] = environment_group

    def _add_crud_endpoints(
        self,
        group: ApiGroup,
        resource: str,
        resource_singular: str,
        id_field: str = "id",
    ) -> None:
        """Adiciona endpoints CRUD padrão."""
        # GET /resource - Lista recursos
        group.add_endpoint(
            ApiEndpoint(
                name=f"get_{resource}",
                method=HttpMethod.GET,
                path=f"/{resource}",
                description=f"Lista {resource}",
                parameters=[
                    *self._get_pagination_params(),
                    ApiParameter(
                        "q", "query", required=False, description="Filtro de busca"
                    ),
                    ApiParameter(
                        "orderBy", "query", required=False, description="Ordenação"
                    ),
                ],
            ),
        )

        # GET /resource/{id} - Obtém recurso específico
        group.add_endpoint(
            ApiEndpoint(
                name=f"get_{resource_singular}",
                method=HttpMethod.GET,
                path=f"/{resource}/{{{id_field}}}",
                description=f"Obtém {resource_singular} específico",
                parameters=[
                    ApiParameter(
                        id_field,
                        "path",
                        required=True,
                        description=f"ID do {resource_singular}",
                    ),
                ],
            ),
        )

        # POST /resource - Cria recurso
        group.add_endpoint(
            ApiEndpoint(
                name=f"create_{resource_singular}",
                method=HttpMethod.POST,
                path=f"/{resource}",
                description=f"Cria {resource_singular}",
                parameters=[
                    ApiParameter(
                        f"{resource_singular}_data",
                        "body",
                        required=True,
                        description=f"Dados do {resource_singular}",
                    ),
                ],
            ),
        )

        # PUT /resource/{id} - Atualiza recurso
        group.add_endpoint(
            ApiEndpoint(
                name=f"update_{resource_singular}",
                method=HttpMethod.PUT,
                path=f"/{resource}/{{{id_field}}}",
                description=f"Atualiza {resource_singular}",
                parameters=[
                    ApiParameter(
                        id_field,
                        "path",
                        required=True,
                        description=f"ID do {resource_singular}",
                    ),
                    ApiParameter(
                        f"{resource_singular}_data",
                        "body",
                        required=True,
                        description=f"Dados do {resource_singular}",
                    ),
                ],
            ),
        )

        # DELETE /resource/{id} - Remove recurso
        group.add_endpoint(
            ApiEndpoint(
                name=f"delete_{resource_singular}",
                method=HttpMethod.DELETE,
                path=f"/{resource}/{{{id_field}}}",
                description=f"Remove {resource_singular}",
                parameters=[
                    ApiParameter(
                        id_field,
                        "path",
                        required=True,
                        description=f"ID do {resource_singular}",
                    ),
                ],
            ),
        )

        # POST /resource/archive - Exporta/arquiva recursos
        group.add_endpoint(
            ApiEndpoint(
                name=f"archive_{resource}",
                method=HttpMethod.POST,
                path=f"/{resource}/archive",
                description=f"Arquiva {resource}",
                parameters=[
                    ApiParameter(
                        "archive_request",
                        "body",
                        required=True,
                        description=f"Dados do arquivo de {resource}",
                    ),
                ],
            ),
        )

        # POST /resource/{id}/archive - Arquiva recurso específico
        group.add_endpoint(
            ApiEndpoint(
                name=f"archive_{resource_singular}",
                method=HttpMethod.POST,
                path=f"/{resource}/{{{id_field}}}/archive",
                description=f"Arquiva {resource_singular} específico",
                parameters=[
                    ApiParameter(
                        id_field,
                        "path",
                        required=True,
                        description=f"ID do {resource_singular}",
                    ),
                ],
            ),
        )

    def _get_pagination_params(self) -> list[ApiParameter]:
        """Retorna parâmetros padrão de paginação."""
        return [
            ApiParameter(
                "limit",
                "query",
                required=False,
                description="Limite de resultados",
                default=50,
            ),
            ApiParameter(
                "offset",
                "query",
                required=False,
                description="Offset para paginação",
                default=0,
            ),
        ]

    def get_group(self, name: str) -> ApiGroup | None:
        """Obtém grupo por nome."""
        return self.groups.get(name)

    def get_endpoint(self, group_name: str, endpoint_name: str) -> ApiEndpoint | None:
        """Obtém endpoint específico."""
        group = self.get_group(group_name)
        if not group:
            return None

        for endpoint in group.endpoints:
            if endpoint.name == endpoint_name:
                return endpoint
        return None

    def list_all_endpoints(self) -> list[tuple[str, str, ApiEndpoint]]:
        """Lista todos os endpoints disponíveis."""
        all_endpoints = []
        for group_name, group in self.groups.items():
            all_endpoints.extend(
                (group_name, endpoint.name, endpoint) for endpoint in group.endpoints
            )
        return all_endpoints


# Instância global da declaração da API
OIC_API = OicApiDeclaration()
