"""Pipeline views for listing and detailing project pipelines."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

import grpc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView
from flx_grpc.client import FlxGrpcClientBase
from google.protobuf import empty_pb2

if TYPE_CHECKING:
    from flx_grpc.proto import flx_pb2
else:
    from flx_grpc.proto import flx_pb2


class FlxPipelineGrpcClient(FlxGrpcClientBase):
    r"""FlxPipelineGrpcClient - Client Implementation.

    Implementa cliente para comunicação com serviços externos. Fornece interface simplificada para integrações.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    list_pipelines(): Método específico da classe
    get_pipeline(): Obtém dados

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = FlxPipelineGrpcClient()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """gRPC client for pipeline-related operations."""

    def list_pipelines(self) -> list[dict[str, Any]]:
        """Fetch a list of all pipelines."""
        try:
            with self._create_channel() as channel:
                stub = self._create_stub(channel)
                response = stub.ListPipelines(empty_pb2.Empty())
                return [self._format_pipeline(p) for p in response.pipelines]
        except grpc.RpcError:
            return []

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
        """Fetch details for a single pipeline."""
        try:
            with self._create_channel() as channel:
                stub = self._create_stub(channel)
                request = flx_pb2.GetPipelineRequest(id=pipeline_id)
                response = stub.GetPipeline(request)
                return self._format_pipeline(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def _format_pipeline(self, pipeline: flx_pb2.Pipeline) -> dict[str, Any]:
        """Format a pipeline message."""
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "plugin_namespace": pipeline.plugin_namespace,
            "extractor": pipeline.extractor,
            "loader": pipeline.loader,
            "transform": pipeline.transform,
            "interval": pipeline.interval,
            "state": pipeline.state,
            "last_run_at": (
                pipeline.last_run_at.ToDatetime()
                if pipeline.HasField("last_run_at")
                else None
            ),
            "next_run_at": (
                pipeline.next_run_at.ToDatetime()
                if pipeline.HasField("next_run_at")
                else None
            ),
        }


@functools.lru_cache(maxsize=1)
def get_grpc_client() -> FlxPipelineGrpcClient:
    """Get a cached instance of the pipeline gRPC client."""
    return FlxPipelineGrpcClient()


class PipelineListView(LoginRequiredMixin, TemplateView):
    r"""PipelineListView - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    get_context_data(): Obtém dados

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PipelineListView()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """View to display a list of all pipelines."""

    template_name = "pipelines/list.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Fetch pipeline list and add to context."""
        context = super().get_context_data(**kwargs)
        client = get_grpc_client()
        context["pipelines"] = client.list_pipelines()
        return context


class PipelineDetailView(LoginRequiredMixin, TemplateView):
    r"""PipelineDetailView - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    get_context_data(): Obtém dados

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PipelineDetailView()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """View to display details of a single pipeline."""

    template_name = "pipelines/detail.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Fetch pipeline details and add to context."""
        context = super().get_context_data(**kwargs)
        pipeline_id = self.kwargs["pipeline_id"]
        client = get_grpc_client()
        pipeline = client.get_pipeline(str(pipeline_id))
        if not pipeline:
            msg = "Pipeline not found"
            raise Http404(msg)
        context["pipeline"] = pipeline
        return context
