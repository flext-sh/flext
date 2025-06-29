import datetime
from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import (
    descriptor as _descriptor,
)
from google.protobuf import (
    message as _message,
)
from google.protobuf import (
    struct_pb2 as _struct_pb2,
)
from google.protobuf import (
    timestamp_pb2 as _timestamp_pb2,
)
from internal.invalid import (
    containers as _containers,
)
from internal.invalid import (
    enum_type_wrapper as _enum_type_wrapper,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    STATUS_PENDING: _ClassVar[Status]
    STATUS_RUNNING: _ClassVar[Status]
    STATUS_SUCCESS: _ClassVar[Status]
    STATUS_FAILED: _ClassVar[Status]
    STATUS_CANCELLED: _ClassVar[Status]

class PluginType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLUGIN_TYPE_UNSPECIFIED: _ClassVar[PluginType]
    PLUGIN_TYPE_EXTRACTOR: _ClassVar[PluginType]
    PLUGIN_TYPE_LOADER: _ClassVar[PluginType]
    PLUGIN_TYPE_TRANSFORMER: _ClassVar[PluginType]
    PLUGIN_TYPE_ORCHESTRATOR: _ClassVar[PluginType]
    PLUGIN_TYPE_UTILITY: _ClassVar[PluginType]

class MeltanoJobState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MELTANO_JOB_STATE_UNSPECIFIED: _ClassVar[MeltanoJobState]
    MELTANO_JOB_STATE_IDLE: _ClassVar[MeltanoJobState]
    MELTANO_JOB_STATE_RUNNING: _ClassVar[MeltanoJobState]
    MELTANO_JOB_STATE_SUCCESS: _ClassVar[MeltanoJobState]
    MELTANO_JOB_STATE_FAIL: _ClassVar[MeltanoJobState]
    MELTANO_JOB_STATE_CANCELLED: _ClassVar[MeltanoJobState]

class MeltanoExecutionMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MELTANO_EXECUTION_MODE_UNSPECIFIED: _ClassVar[MeltanoExecutionMode]
    MELTANO_EXECUTION_MODE_SYNC: _ClassVar[MeltanoExecutionMode]
    MELTANO_EXECUTION_MODE_ASYNC: _ClassVar[MeltanoExecutionMode]

STATUS_UNSPECIFIED: Status
STATUS_PENDING: Status
STATUS_RUNNING: Status
STATUS_SUCCESS: Status
STATUS_FAILED: Status
STATUS_CANCELLED: Status
PLUGIN_TYPE_UNSPECIFIED: PluginType
PLUGIN_TYPE_EXTRACTOR: PluginType
PLUGIN_TYPE_LOADER: PluginType
PLUGIN_TYPE_TRANSFORMER: PluginType
PLUGIN_TYPE_ORCHESTRATOR: PluginType
PLUGIN_TYPE_UTILITY: PluginType
MELTANO_JOB_STATE_UNSPECIFIED: MeltanoJobState
MELTANO_JOB_STATE_IDLE: MeltanoJobState
MELTANO_JOB_STATE_RUNNING: MeltanoJobState
MELTANO_JOB_STATE_SUCCESS: MeltanoJobState
MELTANO_JOB_STATE_FAIL: MeltanoJobState
MELTANO_JOB_STATE_CANCELLED: MeltanoJobState
MELTANO_EXECUTION_MODE_UNSPECIFIED: MeltanoExecutionMode
MELTANO_EXECUTION_MODE_SYNC: MeltanoExecutionMode
MELTANO_EXECUTION_MODE_ASYNC: MeltanoExecutionMode

class SystemStats(_message.Message):
    __slots__ = (
        "active_pipelines",
        "total_executions",
        "success_rate",
        "uptime_seconds",
        "cpu_usage",
        "memory_usage",
        "active_connections",
    )
    ACTIVE_PIPELINES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CPU_USAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USAGE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    active_pipelines: int
    total_executions: int
    success_rate: float
    uptime_seconds: int
    cpu_usage: float
    memory_usage: float
    active_connections: int
    def __init__(
        self,
        active_pipelines: int | None = ...,
        total_executions: int | None = ...,
        success_rate: float | None = ...,
        uptime_seconds: int | None = ...,
        cpu_usage: float | None = ...,
        memory_usage: float | None = ...,
        active_connections: int | None = ...,
    ) -> None: ...

class HealthStatus(_message.Message):
    __slots__ = ("healthy", "components", "timestamp")

    class ComponentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ComponentHealth
        def __init__(
            self,
            key: str | None = ...,
            value: ComponentHealth | _Mapping | None = ...,
        ) -> None: ...

    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    components: _containers.MessageMap[str, ComponentHealth]
    timestamp: _timestamp_pb2.Timestamp
    def __init__(
        self,
        healthy: bool = ...,
        components: _Mapping[str, ComponentHealth] | None = ...,
        timestamp: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class ComponentHealth(_message.Message):
    __slots__ = ("name", "healthy", "message", "metadata")

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    NAME_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    healthy: bool
    message: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        name: str | None = ...,
        healthy: bool = ...,
        message: str | None = ...,
        metadata: _Mapping[str, str] | None = ...,
    ) -> None: ...

class SystemInfo(_message.Message):
    __slots__ = (
        "version",
        "environment",
        "python_version",
        "meltano_version",
        "features",
    )

    class FeaturesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    VERSION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    MELTANO_VERSION_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    version: str
    environment: str
    python_version: str
    meltano_version: str
    features: _containers.ScalarMap[str, str]
    def __init__(
        self,
        version: str | None = ...,
        environment: str | None = ...,
        python_version: str | None = ...,
        meltano_version: str | None = ...,
        features: _Mapping[str, str] | None = ...,
    ) -> None: ...

class Pipeline(_message.Message):
    __slots__ = (
        "id",
        "name",
        "description",
        "extractor",
        "loader",
        "transform",
        "config",
        "schedule",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
        "last_status",
        "last_run",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    LOADER_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_STATUS_FIELD_NUMBER: _ClassVar[int]
    LAST_RUN_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    extractor: str
    loader: str
    transform: str
    config: _struct_pb2.Struct
    schedule: str
    is_active: bool
    created_by: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    last_status: Status
    last_run: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: str | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        extractor: str | None = ...,
        loader: str | None = ...,
        transform: str | None = ...,
        config: _struct_pb2.Struct | _Mapping | None = ...,
        schedule: str | None = ...,
        is_active: bool = ...,
        created_by: str | None = ...,
        created_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        updated_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        last_status: Status | str | None = ...,
        last_run: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class ListPipelinesRequest(_message.Message):
    __slots__ = ("limit", "offset", "filter", "sort_by", "descending")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    DESCENDING_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    filter: str
    sort_by: str
    descending: bool
    def __init__(
        self,
        limit: int | None = ...,
        offset: int | None = ...,
        filter: str | None = ...,
        sort_by: str | None = ...,
        descending: bool = ...,
    ) -> None: ...

class ListPipelinesResponse(_message.Message):
    __slots__ = ("pipelines", "total", "limit", "offset")
    PIPELINES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    pipelines: _containers.RepeatedCompositeFieldContainer[Pipeline]
    total: int
    limit: int
    offset: int
    def __init__(
        self,
        pipelines: _Iterable[Pipeline | _Mapping] | None = ...,
        total: int | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> None: ...

class GetPipelineRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class CreatePipelineRequest(_message.Message):
    __slots__ = (
        "name",
        "description",
        "extractor",
        "loader",
        "transform",
        "config",
        "schedule",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    LOADER_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    extractor: str
    loader: str
    transform: str
    config: _struct_pb2.Struct
    schedule: str
    def __init__(
        self,
        name: str | None = ...,
        description: str | None = ...,
        extractor: str | None = ...,
        loader: str | None = ...,
        transform: str | None = ...,
        config: _struct_pb2.Struct | _Mapping | None = ...,
        schedule: str | None = ...,
    ) -> None: ...

class UpdatePipelineRequest(_message.Message):
    __slots__ = (
        "id",
        "name",
        "description",
        "extractor",
        "loader",
        "transform",
        "config",
        "schedule",
        "is_active",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    LOADER_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    extractor: str
    loader: str
    transform: str
    config: _struct_pb2.Struct
    schedule: str
    is_active: bool
    def __init__(
        self,
        id: str | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        extractor: str | None = ...,
        loader: str | None = ...,
        transform: str | None = ...,
        config: _struct_pb2.Struct | _Mapping | None = ...,
        schedule: str | None = ...,
        is_active: bool = ...,
    ) -> None: ...

class DeletePipelineRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class RunPipelineRequest(_message.Message):
    __slots__ = ("pipeline_id", "full_refresh", "env_vars")

    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    FULL_REFRESH_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    full_refresh: bool
    env_vars: _containers.ScalarMap[str, str]
    def __init__(
        self,
        pipeline_id: str | None = ...,
        full_refresh: bool = ...,
        env_vars: _Mapping[str, str] | None = ...,
    ) -> None: ...

class Execution(_message.Message):
    __slots__ = (
        "id",
        "pipeline_id",
        "status",
        "started_at",
        "finished_at",
        "duration_seconds",
        "error_message",
        "metadata",
        "records_processed",
        "triggered_by",
    )

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RECORDS_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    pipeline_id: str
    status: Status
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    duration_seconds: int
    error_message: str
    metadata: _containers.ScalarMap[str, str]
    records_processed: int
    triggered_by: str
    def __init__(
        self,
        id: str | None = ...,
        pipeline_id: str | None = ...,
        status: Status | str | None = ...,
        started_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        finished_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        duration_seconds: int | None = ...,
        error_message: str | None = ...,
        metadata: _Mapping[str, str] | None = ...,
        records_processed: int | None = ...,
        triggered_by: str | None = ...,
    ) -> None: ...

class GetExecutionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class ListExecutionsRequest(_message.Message):
    __slots__ = ("pipeline_id", "limit", "offset", "status", "start_date", "end_date")
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    limit: int
    offset: int
    status: Status
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(
        self,
        pipeline_id: str | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
        status: Status | str | None = ...,
        start_date: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        end_date: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class ListExecutionsResponse(_message.Message):
    __slots__ = ("executions", "total", "limit", "offset")
    EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    executions: _containers.RepeatedCompositeFieldContainer[Execution]
    total: int
    limit: int
    offset: int
    def __init__(
        self,
        executions: _Iterable[Execution | _Mapping] | None = ...,
        total: int | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> None: ...

class CancelExecutionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class StreamExecutionRequest(_message.Message):
    __slots__ = ("execution_id",)
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    def __init__(self, execution_id: str | None = ...) -> None: ...

class ExecutionUpdate(_message.Message):
    __slots__ = (
        "execution_id",
        "type",
        "message",
        "timestamp",
        "progress",
        "status",
        "metadata",
    )

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    type: str
    message: str
    timestamp: _timestamp_pb2.Timestamp
    progress: float
    status: Status
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        execution_id: str | None = ...,
        type: str | None = ...,
        message: str | None = ...,
        timestamp: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        progress: float | None = ...,
        status: Status | str | None = ...,
        metadata: _Mapping[str, str] | None = ...,
    ) -> None: ...

class Plugin(_message.Message):
    __slots__ = (
        "name",
        "type",
        "variant",
        "version",
        "description",
        "installed",
        "settings",
        "installed_at",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VARIANT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    variant: str
    version: str
    description: str
    installed: bool
    settings: _struct_pb2.Struct
    installed_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        name: str | None = ...,
        type: PluginType | str | None = ...,
        variant: str | None = ...,
        version: str | None = ...,
        description: str | None = ...,
        installed: bool = ...,
        settings: _struct_pb2.Struct | _Mapping | None = ...,
        installed_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class ListPluginsRequest(_message.Message):
    __slots__ = ("type", "installed_only")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_ONLY_FIELD_NUMBER: _ClassVar[int]
    type: PluginType
    installed_only: bool
    def __init__(self, type: PluginType | str | None = ..., installed_only: bool = ...) -> None: ...

class ListPluginsResponse(_message.Message):
    __slots__ = ("plugins", "total")
    PLUGINS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    plugins: _containers.RepeatedCompositeFieldContainer[Plugin]
    total: int
    def __init__(
        self,
        plugins: _Iterable[Plugin | _Mapping] | None = ...,
        total: int | None = ...,
    ) -> None: ...

class InstallPluginRequest(_message.Message):
    __slots__ = ("name", "type", "variant")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VARIANT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    variant: str
    def __init__(
        self,
        name: str | None = ...,
        type: PluginType | str | None = ...,
        variant: str | None = ...,
    ) -> None: ...

class UninstallPluginRequest(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    def __init__(self, name: str | None = ..., type: PluginType | str | None = ...) -> None: ...

class GetPluginConfigRequest(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    def __init__(self, name: str | None = ..., type: PluginType | str | None = ...) -> None: ...

class UpdatePluginConfigRequest(_message.Message):
    __slots__ = ("name", "type", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    config: _struct_pb2.Struct
    def __init__(
        self,
        name: str | None = ...,
        type: PluginType | str | None = ...,
        config: _struct_pb2.Struct | _Mapping | None = ...,
    ) -> None: ...

class PluginConfig(_message.Message):
    __slots__ = ("name", "type", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: PluginType
    config: _struct_pb2.Struct
    def __init__(
        self,
        name: str | None = ...,
        type: PluginType | str | None = ...,
        config: _struct_pb2.Struct | _Mapping | None = ...,
    ) -> None: ...

class State(_message.Message):
    __slots__ = ("id", "data", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    data: _struct_pb2.Struct
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: str | None = ...,
        data: _struct_pb2.Struct | _Mapping | None = ...,
        updated_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class GetStateRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class SetStateRequest(_message.Message):
    __slots__ = ("id", "data")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    data: _struct_pb2.Struct
    def __init__(
        self,
        id: str | None = ...,
        data: _struct_pb2.Struct | _Mapping | None = ...,
    ) -> None: ...

class ClearStateRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class Schedule(_message.Message):
    __slots__ = ("id", "pipeline_id", "cron", "is_active", "next_run", "last_run")
    ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    CRON_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    NEXT_RUN_FIELD_NUMBER: _ClassVar[int]
    LAST_RUN_FIELD_NUMBER: _ClassVar[int]
    id: str
    pipeline_id: str
    cron: str
    is_active: bool
    next_run: _timestamp_pb2.Timestamp
    last_run: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: str | None = ...,
        pipeline_id: str | None = ...,
        cron: str | None = ...,
        is_active: bool = ...,
        next_run: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        last_run: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class ListSchedulesRequest(_message.Message):
    __slots__ = ("pipeline_id", "active_only")
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    active_only: bool
    def __init__(self, pipeline_id: str | None = ..., active_only: bool = ...) -> None: ...

class ListSchedulesResponse(_message.Message):
    __slots__ = ("schedules", "total")
    SCHEDULES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    schedules: _containers.RepeatedCompositeFieldContainer[Schedule]
    total: int
    def __init__(
        self,
        schedules: _Iterable[Schedule | _Mapping] | None = ...,
        total: int | None = ...,
    ) -> None: ...

class CreateScheduleRequest(_message.Message):
    __slots__ = ("pipeline_id", "cron")
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    CRON_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    cron: str
    def __init__(self, pipeline_id: str | None = ..., cron: str | None = ...) -> None: ...

class UpdateScheduleRequest(_message.Message):
    __slots__ = ("id", "cron", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    CRON_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    cron: str
    is_active: bool
    def __init__(
        self,
        id: str | None = ...,
        cron: str | None = ...,
        is_active: bool = ...,
    ) -> None: ...

class DeleteScheduleRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: str | None = ...) -> None: ...

class MeltanoProject(_message.Message):
    __slots__ = (
        "name",
        "environment",
        "project_root",
        "configuration",
        "is_initialized",
        "created_at",
        "updated_at",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROOT_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IS_INITIALIZED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    environment: str
    project_root: str
    configuration: _struct_pb2.Struct
    is_initialized: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        name: str | None = ...,
        environment: str | None = ...,
        project_root: str | None = ...,
        configuration: _struct_pb2.Struct | _Mapping | None = ...,
        is_initialized: bool = ...,
        created_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        updated_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
    ) -> None: ...

class InitializeMeltanoProjectRequest(_message.Message):
    __slots__ = ("project_name", "environment", "force")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    environment: str
    force: bool
    def __init__(
        self,
        project_name: str | None = ...,
        environment: str | None = ...,
        force: bool = ...,
    ) -> None: ...

class LoadMeltanoProjectRequest(_message.Message):
    __slots__ = ("project_name", "environment")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    environment: str
    def __init__(self, project_name: str | None = ..., environment: str | None = ...) -> None: ...

class RunMeltanoPipelineRequest(_message.Message):
    __slots__ = (
        "project_name",
        "pipeline_definition",
        "environment",
        "execution_mode",
        "env_vars",
    )

    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_MODE_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    pipeline_definition: _struct_pb2.Struct
    environment: str
    execution_mode: MeltanoExecutionMode
    env_vars: _containers.ScalarMap[str, str]
    def __init__(
        self,
        project_name: str | None = ...,
        pipeline_definition: _struct_pb2.Struct | _Mapping | None = ...,
        environment: str | None = ...,
        execution_mode: MeltanoExecutionMode | str | None = ...,
        env_vars: _Mapping[str, str] | None = ...,
    ) -> None: ...

class MeltanoExecution(_message.Message):
    __slots__ = (
        "execution_id",
        "project_name",
        "pipeline_name",
        "state",
        "started_at",
        "finished_at",
        "duration_seconds",
        "error_message",
        "result_data",
        "environment",
    )
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    project_name: str
    pipeline_name: str
    state: MeltanoJobState
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    duration_seconds: int
    error_message: str
    result_data: _struct_pb2.Struct
    environment: str
    def __init__(
        self,
        execution_id: str | None = ...,
        project_name: str | None = ...,
        pipeline_name: str | None = ...,
        state: MeltanoJobState | str | None = ...,
        started_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        finished_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        duration_seconds: int | None = ...,
        error_message: str | None = ...,
        result_data: _struct_pb2.Struct | _Mapping | None = ...,
        environment: str | None = ...,
    ) -> None: ...

class GetMeltanoJobStatusRequest(_message.Message):
    __slots__ = ("project_name", "job_id")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_id: str
    def __init__(self, project_name: str | None = ..., job_id: str | None = ...) -> None: ...

class MeltanoJobStatus(_message.Message):
    __slots__ = (
        "job_id",
        "run_id",
        "state",
        "started_at",
        "last_heartbeat_at",
        "payload",
        "metadata",
    )
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    run_id: str
    state: MeltanoJobState
    started_at: _timestamp_pb2.Timestamp
    last_heartbeat_at: _timestamp_pb2.Timestamp
    payload: str
    metadata: _struct_pb2.Struct
    def __init__(
        self,
        job_id: str | None = ...,
        run_id: str | None = ...,
        state: MeltanoJobState | str | None = ...,
        started_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        last_heartbeat_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        payload: str | None = ...,
        metadata: _struct_pb2.Struct | _Mapping | None = ...,
    ) -> None: ...

class ListMeltanoJobsRequest(_message.Message):
    __slots__ = ("project_name", "state", "run_id", "limit", "offset")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    state: MeltanoJobState
    run_id: str
    limit: int
    offset: int
    def __init__(
        self,
        project_name: str | None = ...,
        state: MeltanoJobState | str | None = ...,
        run_id: str | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> None: ...

class ListMeltanoJobsResponse(_message.Message):
    __slots__ = ("jobs", "total", "limit", "offset")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[MeltanoJobStatus]
    total: int
    limit: int
    offset: int
    def __init__(
        self,
        jobs: _Iterable[MeltanoJobStatus | _Mapping] | None = ...,
        total: int | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> None: ...

class GetMeltanoStateRequest(_message.Message):
    __slots__ = ("project_name", "state_id", "use_cache")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_ID_FIELD_NUMBER: _ClassVar[int]
    USE_CACHE_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    state_id: str
    use_cache: bool
    def __init__(
        self,
        project_name: str | None = ...,
        state_id: str | None = ...,
        use_cache: bool = ...,
    ) -> None: ...

class MeltanoState(_message.Message):
    __slots__ = ("state_id", "state_data", "version", "updated_at", "backend")
    STATE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_DATA_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    BACKEND_FIELD_NUMBER: _ClassVar[int]
    state_id: str
    state_data: _struct_pb2.Struct
    version: str
    updated_at: _timestamp_pb2.Timestamp
    backend: str
    def __init__(
        self,
        state_id: str | None = ...,
        state_data: _struct_pb2.Struct | _Mapping | None = ...,
        version: str | None = ...,
        updated_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        backend: str | None = ...,
    ) -> None: ...

class SetMeltanoStateRequest(_message.Message):
    __slots__ = ("project_name", "state_id", "state_data", "create_backup")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_DATA_FIELD_NUMBER: _ClassVar[int]
    CREATE_BACKUP_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    state_id: str
    state_data: _struct_pb2.Struct
    create_backup: bool
    def __init__(
        self,
        project_name: str | None = ...,
        state_id: str | None = ...,
        state_data: _struct_pb2.Struct | _Mapping | None = ...,
        create_backup: bool = ...,
    ) -> None: ...

class GetMeltanoJobStatisticsRequest(_message.Message):
    __slots__ = ("project_name", "days")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    days: int
    def __init__(self, project_name: str | None = ..., days: int | None = ...) -> None: ...

class MeltanoJobStatistics(_message.Message):
    __slots__ = (
        "period_days",
        "total_jobs",
        "state_counts",
        "success_rate",
        "generated_at",
        "cutoff_date",
    )

    class StateCountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: str | None = ..., value: int | None = ...) -> None: ...

    PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_JOBS_FIELD_NUMBER: _ClassVar[int]
    STATE_COUNTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    CUTOFF_DATE_FIELD_NUMBER: _ClassVar[int]
    period_days: int
    total_jobs: int
    state_counts: _containers.ScalarMap[str, int]
    success_rate: float
    generated_at: _timestamp_pb2.Timestamp
    cutoff_date: str
    def __init__(
        self,
        period_days: int | None = ...,
        total_jobs: int | None = ...,
        state_counts: _Mapping[str, int] | None = ...,
        success_rate: float | None = ...,
        generated_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        cutoff_date: str | None = ...,
    ) -> None: ...

class CleanupStaleMeltanoJobsRequest(_message.Message):
    __slots__ = ("project_name", "heartbeat_timeout_minutes", "dry_run")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_TIMEOUT_MINUTES_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    heartbeat_timeout_minutes: int
    dry_run: bool
    def __init__(
        self,
        project_name: str | None = ...,
        heartbeat_timeout_minutes: int | None = ...,
        dry_run: bool = ...,
    ) -> None: ...

class MeltanoJobCleanupResult(_message.Message):
    __slots__ = (
        "dry_run",
        "stale_jobs_found",
        "jobs_cleaned",
        "heartbeat_timeout_minutes",
        "cleaned_at",
        "cleaned_job_ids",
    )
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    STALE_JOBS_FOUND_FIELD_NUMBER: _ClassVar[int]
    JOBS_CLEANED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_TIMEOUT_MINUTES_FIELD_NUMBER: _ClassVar[int]
    CLEANED_AT_FIELD_NUMBER: _ClassVar[int]
    CLEANED_JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    dry_run: bool
    stale_jobs_found: int
    jobs_cleaned: int
    heartbeat_timeout_minutes: int
    cleaned_at: _timestamp_pb2.Timestamp
    cleaned_job_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        dry_run: bool = ...,
        stale_jobs_found: int | None = ...,
        jobs_cleaned: int | None = ...,
        heartbeat_timeout_minutes: int | None = ...,
        cleaned_at: datetime.datetime | _timestamp_pb2.Timestamp | _Mapping | None = ...,
        cleaned_job_ids: _Iterable[str] | None = ...,
    ) -> None: ...

class RunMeltanoCommandRequest(_message.Message):
    __slots__ = ("project_name", "command_args", "environment", "env_vars")

    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: str | None = ..., value: str | None = ...) -> None: ...

    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ARGS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    command_args: _containers.RepeatedScalarFieldContainer[str]
    environment: str
    env_vars: _containers.ScalarMap[str, str]
    def __init__(
        self,
        project_name: str | None = ...,
        command_args: _Iterable[str] | None = ...,
        environment: str | None = ...,
        env_vars: _Mapping[str, str] | None = ...,
    ) -> None: ...

class MeltanoCommandResult(_message.Message):
    __slots__ = ("return_code", "stdout", "stderr", "duration_seconds", "command")
    RETURN_CODE_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: int
    command: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        return_code: int | None = ...,
        stdout: str | None = ...,
        stderr: str | None = ...,
        duration_seconds: int | None = ...,
        command: _Iterable[str] | None = ...,
    ) -> None: ...
