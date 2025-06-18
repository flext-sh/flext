"""Gerador automático de métodos baseado na declaração da API."""

from collections.abc import Callable
from typing import Any

try:
    from .api_declarative import OIC_API, ApiEndpoint, HttpMethod
except ImportError:
    from api_declarative import OIC_API, ApiEndpoint, HttpMethod


class ApiMethodGenerator:
    """Gerador de métodos dinâmicos baseado na declaração da API."""

    def __init__(self, adapter_instance: Any = None) -> None:
        self.adapter = adapter_instance
        self._generated_methods: dict[str, Callable] = {}

    def generate_method(self, group_name: str, endpoint: ApiEndpoint) -> Callable:
        """Gera método dinâmico para um endpoint."""

        def dynamic_method(**kwargs) -> Any:
            return self._execute_endpoint(group_name, endpoint, **kwargs)

        # Configura metadados do método
        dynamic_method.__name__ = endpoint.name
        dynamic_method.__doc__ = self._generate_docstring(endpoint)

        return dynamic_method

    def _execute_endpoint(
        self,
        group_name: str,
        endpoint: ApiEndpoint,
        **kwargs,
    ) -> Any:
        """Executa um endpoint dinamicamente."""
        if not self.adapter:
            msg = "Adapter não configurado"
            raise RuntimeError(msg)

        # Constrói path com parâmetros
        path = self._build_path(group_name, endpoint, kwargs)

        # Extrai parâmetros de query
        params = self._extract_query_params(endpoint, kwargs)

        # Extrai dados do body
        body_data = self._extract_body_data(endpoint, kwargs)

        # Executa baseado no método HTTP
        if endpoint.method == HttpMethod.GET:
            return self.adapter.get(path, params)
        if endpoint.method == HttpMethod.POST:
            return self.adapter.post(path, body_data)
        if endpoint.method == HttpMethod.PUT:
            return self.adapter.put(path, body_data)
        if endpoint.method == HttpMethod.DELETE:
            return self.adapter.delete(path)
        if endpoint.method == HttpMethod.PATCH:
            return self.adapter.patch(path, body_data)
        msg = f"Método HTTP não suportado: {endpoint.method}"
        raise ValueError(msg)

    def _build_path(
        self,
        group_name: str,
        endpoint: ApiEndpoint,
        kwargs: dict[str, Any],
    ) -> str:
        """Constrói path substituindo parâmetros."""
        # Obtém o grupo e combina base_path com endpoint path
        group = OIC_API.groups.get(group_name)
        if not group:
            msg = f"Grupo '{group_name}' não encontrado"
            raise ValueError(msg)

        # Combina base_path do grupo com o path do endpoint
        full_path = group.base_path + endpoint.path

        # Substitui parâmetros de path
        for param in endpoint.get_path_params():
            if param.name in kwargs:
                full_path = full_path.replace(
                    f"{{{param.name}}}",
                    str(kwargs[param.name]),
                )
            elif param.required:
                msg = f"Parâmetro obrigatório '{param.name}' não fornecido"
                raise ValueError(msg)

        return full_path

    def _extract_query_params(
        self,
        endpoint: ApiEndpoint,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Extrai parâmetros de query."""
        params = {}

        for param in endpoint.get_query_params():
            if param.name in kwargs:
                params[param.name] = kwargs[param.name]
            elif param.required:
                msg = f"Parâmetro obrigatório '{param.name}' não fornecido"
                raise ValueError(msg)
            elif param.default is not None:
                params[param.name] = param.default

        return params

    def _extract_body_data(
        self,
        endpoint: ApiEndpoint,
        kwargs: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Extrai dados do body."""
        body_params = endpoint.get_body_params()
        if not body_params:
            return None

        # Se há apenas um parâmetro de body, usa ele diretamente
        if len(body_params) == 1:
            param = body_params[0]
            if param.name in kwargs:
                return kwargs[param.name]
            if param.required:
                msg = f"Parâmetro obrigatório '{param.name}' não fornecido"
                raise ValueError(msg)
            return param.default

        # Se há múltiplos parâmetros, constrói dict
        body_data = {}
        for param in body_params:
            if param.name in kwargs:
                body_data[param.name] = kwargs[param.name]
            elif param.required:
                msg = f"Parâmetro obrigatório '{param.name}' não fornecido"
                raise ValueError(msg)
            elif param.default is not None:
                body_data[param.name] = param.default

        return body_data if body_data else None

    def _generate_docstring(self, endpoint: ApiEndpoint) -> str:
        """Gera docstring para o método."""
        doc = f"{endpoint.description}\n\n"

        if endpoint.parameters:
            doc += "Args:\n"
            for param in endpoint.parameters:
                required_str = "" if param.required else ", optional"
                default_str = (
                    f" (default: {param.default})" if param.default is not None else ""
                )
                doc += f"    {param.name} ({param.param_type}{required_str}): {param.description}{default_str}\n"

        doc += f"\nReturns:\n    {endpoint.response_type}: Response data\n"

        if endpoint.tags:
            doc += f"\nTags: {', '.join(endpoint.tags)}\n"

        return doc


class DynamicApiMixin:
    """Mixin que adiciona métodos dinâmicos baseados na declaração da API."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._api_generator = ApiMethodGenerator(self)
        self._inject_api_methods()

    def _inject_api_methods(self) -> None:
        """Injeta métodos da API na instância."""
        for group_name, group in OIC_API.groups.items():
            for endpoint in group.endpoints:
                method = self._api_generator.generate_method(group_name, endpoint)
                setattr(self, endpoint.name, method)

    def list_available_methods(self) -> list[dict[str, str]]:
        """Lista todos os métodos disponíveis."""
        methods = []
        for group_name, group in OIC_API.groups.items():
            methods.extend(
                {
                    "group": group_name,
                    "name": endpoint.name,
                    "method": endpoint.method.value,
                    "path": endpoint.path,
                    "description": endpoint.description,
                }
                for endpoint in group.endpoints
            )
        return methods

    def get_method_info(self, method_name: str) -> dict[str, Any] | None:
        """Obtém informações sobre um método específico."""
        for group_name, group in OIC_API.groups.items():
            for endpoint in group.endpoints:
                if endpoint.name == method_name:
                    return {
                        "group": group_name,
                        "name": endpoint.name,
                        "method": endpoint.method.value,
                        "path": endpoint.path,
                        "description": endpoint.description,
                        "parameters": [
                            {
                                "name": p.name,
                                "type": p.param_type,
                                "required": p.required,
                                "description": p.description,
                                "default": p.default,
                            }
                            for p in endpoint.parameters
                        ],
                    }
        return None


class ApiMethodValidator:
    """Validador de métodos da API."""

    @staticmethod
    def validate_parameters(endpoint: ApiEndpoint, kwargs: dict[str, Any]) -> list[str]:
        """Valida parâmetros fornecidos."""
        # Verifica parâmetros obrigatórios
        errors = [
            f"Parâmetro obrigatório '{param.name}' não fornecido"
            for param in endpoint.parameters
            if param.required and param.name not in kwargs
        ]

        # Verifica parâmetros extras
        valid_param_names = {p.name for p in endpoint.parameters}
        errors.extend(
            f"Parâmetro inválido '{param_name}'"
            for param_name in kwargs
            if param_name not in valid_param_names
        )

        return errors

    @staticmethod
    def get_required_parameters(endpoint: ApiEndpoint) -> list[str]:
        """Retorna lista de parâmetros obrigatórios."""
        return [p.name for p in endpoint.parameters if p.required]

    @staticmethod
    def get_optional_parameters(endpoint: ApiEndpoint) -> list[str]:
        """Retorna lista de parâmetros opcionais."""
        return [p.name for p in endpoint.parameters if not p.required]


def create_api_documentation() -> str:
    """Cria documentação completa da API."""
    doc = "# Oracle Integration Cloud API - Documentação Completa\n\n"

    for group in OIC_API.groups.values():
        doc += f"## {group.name.title()}\n"
        doc += f"{group.description}\n"
        doc += f"Base Path: `{group.base_path}`\n\n"

        for endpoint in group.endpoints:
            doc += f"### {endpoint.name}\n"
            doc += f"**{endpoint.method.value}** `{endpoint.path}`\n\n"
            doc += f"{endpoint.description}\n\n"

            if endpoint.parameters:
                doc += "**Parâmetros:**\n"
                for param in endpoint.parameters:
                    required = "✓" if param.required else "○"
                    default = (
                        f" (default: `{param.default}`)"
                        if param.default is not None
                        else ""
                    )
                    doc += f"- {required} `{param.name}` ({param.param_type}): {param.description}{default}\n"
                doc += "\n"

            doc += "---\n\n"

    return doc


def print_api_summary() -> None:
    """Imprime resumo da API."""
    sum(len(group.endpoints) for group in OIC_API.groups.values())

    for group in OIC_API.groups.values():
        for _endpoint in group.endpoints[:3]:  # Mostra apenas os primeiros 3
            pass
        if len(group.endpoints) > 3:
            pass


if __name__ == "__main__":
    print_api_summary()
