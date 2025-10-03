# FLEXT-MELTANO DETAILED ARCHITECTURE PLAN

## **ANÁLISE COMPLETA DE DEPENDÊNCIAS**

### **FLEXT-CORE OFERECE:**

```python
# Result Pattern (Railway-oriented programming)
FlextResult[T] com .value/.unwrap_or() modernos
FlextResult.ok(), FlextResult.fail(), .map(), .flat_map()

# Domain Foundation
FlextModels
FlextService, FlextPlugin, FlextContainer

# Configuration & Types
FlextConfig, FlextSingerConfig, FlextDatabaseConfig
FlextModels.EntityId, FlextModels.Timestamp, FlextModels.Metadata

# Observability & Logging
FlextLogger, FlextLogger(), structured logging
FlextObservabilityConfig
```

### **SINGER SDK OFERECE:**

```python
# Core Classes
Tap, Target, Stream, Sink, SQLSink, BatchSink
typing (StringType, DateTimeType, etc.)
OAuthAuthenticator, get_tap_test_class

# Plugin Development
class MyTap(Tap):
    def discover_streams(self) -> list[Stream]
    def get_records(self, context: dict) -> Iterator[dict]
```

### **MELTANO OFERECE:**

```python
# Project Management
from meltano.core.project import Project
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginType

# CLI Integration
meltano install, run, invoke, test, etc.
```

### **DBT OFERECE:**

```python
# Direct Execution
from dbt.cli.main import dbtRunner
runner = dbtRunner()
runner.invoke(["run", "--models", "my_model"])
```

### **FLEXCORE (GO) PRECISA:**

```go
// HTTP Bridge Endpoints
POST /meltano/execute
POST /dbt/run
POST /pipeline/run
GET /plugins/list

// Plugin System Integration
type FlextMeltanoPlugin interface {
    Execute(ctx context.Context, params map[string]interface{}) error
}
```

## **ARQUITETURA DETALHADA**

### **FUNÇÃO 1: WRAPPERS (Adaptação flext-core)**

#### **singer.py - Singer SDK → flext-core**

```python
class MeltanoSingerWrapper:
    """Wrapper principal - adapta Singer SDK para padrões flext-core"""

    def create_tap(self, tap_class: type[Tap], config: dict) -> FlextResult[Tap]:
        """Cria tap Singer usando FlextResult pattern"""

    def create_target(self, target_class: type[Target], config: dict) -> FlextResult[Target]:
        """Cria target Singer usando FlextResult pattern"""

    def run_elt_pipeline(self, tap: Tap, target: Target) -> FlextResult[PipelineResult]:
        """Executa pipeline ELT completo com observabilidade flext-core"""

    def discover_catalog(self, tap: Tap) -> FlextResult[FlextCatalog]:
        """Descobre catálogo e adapta para tipos flext-core"""

class FlextSingerAdapter:
    """Adaptador de tipos Singer → FLEXT"""

    def adapt_catalog(self, singer_catalog: dict) -> FlextResult[FlextCatalog]:
        """Converte singer catalog para FlextCatalog"""

    def adapt_schema(self, singer_schema: dict) -> FlextResult[FlextSchema]:
        """Converte singer schema para FlextSchema"""

    def adapt_records(self, singer_records: Iterator[dict]) -> Iterator[FlextRecord]:
        """Converte singer records para FlextRecord"""
```

#### **bridge.py - Meltano Core → flext-core**

```python
class MeltanoBridge:
    """Bridge principal - adapta Meltano Core para padrões flext-core"""

    def initialize_project(self, project_root: Path) -> FlextResult[MeltanoProject]:
        """Inicializa projeto Meltano usando Project()"""

    def discover_plugins(self, hub_service: MeltanoHubService) -> FlextResult[list[FlextPlugin]]:
        """Descobre plugins do hub e adapta para FlextPlugin"""

    def install_plugin(self, project: Project, plugin_type: PluginType, name: str) -> FlextResult[bool]:
        """Instala plugin usando CLI meltano"""

    def list_installed_plugins(self, project: Project) -> FlextResult[list[FlextPlugin]]:
        """Lista plugins instalados"""

class FlextMeltanoAdapter:
    """Adaptador de tipos Meltano → FLEXT"""

    def adapt_plugin(self, meltano_plugin: dict) -> FlextResult[FlextPlugin]:
        """Converte meltano plugin para FlextPlugin"""

    def adapt_project_config(self, meltano_config: dict) -> FlextResult[FlextProjectConfig]:
        """Converte configuração meltano para FlextProjectConfig"""
```

#### **dbt.py - DBT Core → flext-core**

```python
class MeltanoDbtWrapper:
    """Wrapper principal - adapta DBT Core para padrões flext-core"""

    def create_runner(self, project_dir: Path) -> FlextResult[dbtRunner]:
        """Cria dbtRunner usando FlextResult pattern"""

    def run_models(self, runner: dbtRunner, models: FlextTypes.StringList) -> FlextResult[DbtRunResult]:
        """Executa modelos DBT com observabilidade flext-core"""

    def test_models(self, runner: dbtRunner, models: FlextTypes.StringList) -> FlextResult[DbtTestResult]:
        """Testa modelos DBT com resultado estruturado"""

    def compile_project(self, runner: dbtRunner) -> FlextResult[DbtCompileResult]:
        """Compila projeto DBT"""

class FlextDbtAdapter:
    """Adaptador de tipos DBT → FLEXT"""

    def adapt_run_results(self, dbt_results: dict) -> FlextResult[FlextDbtResults]:
        """Converte resultados DBT para FlextDbtResults"""

    def adapt_manifest(self, dbt_manifest: dict) -> FlextResult[FlextDbtManifest]:
        """Converte manifest DBT para FlextDbtManifest"""
```

### **FUNÇÃO 2: RUNTIME (Go Bridge)**

#### **execution.py - Executor Principal**

```python
class FlextMeltanoExecutor:
    """Executor principal para runtime via subprocess"""

    def __init__(self, config: FlextMeltanoConfig):
        self.singer_wrapper = MeltanoSingerWrapper()
        self.dbt_wrapper = MeltanoDbtWrapper()
        self.meltano_bridge = MeltanoBridge()

    def execute_meltano_command(self, command: FlextTypes.StringList) -> FlextResult[ExecutionResult]:
        """Executa comando meltano via subprocess"""

    def run_singer_pipeline(self, tap_name: str, target_name: str) -> FlextResult[PipelineResult]:
        """Executa pipeline Singer completo"""

    def run_dbt_command(self, command: FlextTypes.StringList, project_dir: Path) -> FlextResult[DbtResult]:
        """Executa comando DBT"""

    def execute(self, operation: Callable) -> FlextResult[str]:  # retorna job_id
        """Executa operação assíncrona e retorna job_id"""

    def get_execution_status(self, job_id: str) -> FlextResult[ExecutionStatus]:
        """Consulta status de execução assíncrona"""
```

#### **adapter.py - Go Bridge**

```python
class FlextMeltanoBridge:
    """Bridge para comunicação Go ↔ Python (JSON API)"""

    def __init__(self):
        self.executor = FlextMeltanoExecutor()

    # Endpoints para FlexCore (Go)
    def get_version(self) -> FlextTypes.StringDict:
        """GET /meltano/version - JSON response"""

    def list_plugins(self) -> FlextTypes.Dict:
        """GET /meltano/plugins - JSON response"""

    def run_pipeline(self, tap_name: str, target_name: str, config: dict) -> FlextTypes.Dict:
        """POST /meltano/pipeline/run - JSON response"""

    def run_dbt(self, command: str, args: FlextTypes.StringList, project_dir: str) -> FlextTypes.Dict:
        """POST /dbt/run - JSON response"""

    def get_job_status(self, job_id: str) -> FlextTypes.Dict:
        """GET /jobs/{job_id}/status - JSON response"""

# Bridge CLI Script para FlexCore
def main():
    """CLI script chamado pelo FlexCore Go"""
    bridge = FlextMeltanoBridge()

    if sys.argv[1] == "version":
        print(json.dumps(bridge.get_version()))
    elif sys.argv[1] == "run_pipeline":
        result = bridge.run_pipeline(sys.argv[2], sys.argv[3], {})
        print(json.dumps(result))
    # etc...
```

#### **cli.py - Interface CLI Direta**

```python
class FlextMeltanoCli:
    """Interface CLI para uso direto (não bridge)"""

    def run_command(self, args: FlextTypes.StringList) -> FlextResult[CliResult]:
        """Executa comando CLI direto"""

    def run_interactive(self) -> None:
        """Modo interativo para desenvolvimento"""

    def get_help(self) -> str:
        """Ajuda detalhada de comandos"""
```

### **FUNÇÃO 3: BASE COMPONENTS (Para projetos flext-\*)**

#### **base.py - Services Base**

```python
class FlextMeltanoBaseService(FlextService):
    """Base service para todos os serviços Meltano"""

    def __init__(self, config: FlextMeltanoConfig):
        super().__init__()
        self.config = config
        self.logger = FlextLogger(self.__class__.__name__)

    @abstractmethod
    def validate_configuration(self) -> FlextResult[bool]:
        """Valida configuração do serviço"""

    @abstractmethod
    def get_health_status(self) -> FlextResult[HealthStatus]:
        """Status de saúde do serviço"""

class FlextMeltanoTapService(FlextMeltanoBaseService):
    """Base service para taps Singer - usado em flext-tap-*"""

    def __init__(self, tap_class: type[Tap], config: FlextMeltanoConfig):
        super().__init__(config)
        self.tap_class = tap_class
        self.singer_wrapper = MeltanoSingerWrapper()

    def discover_streams(self) -> FlextResult[list[FlextStream]]:
        """Descobre streams disponíveis"""

    def sync_stream(self, stream: FlextStream, state: dict) -> FlextResult[Iterator[FlextRecord]]:
        """Sincroniza stream específico"""

    def get_catalog(self) -> FlextResult[FlextCatalog]:
        """Retorna catálogo de streams"""

class FlextMeltanoTargetService(FlextMeltanoBaseService):
    """Base service para targets Singer - usado em flext-target-*"""

    def __init__(self, target_class: type[Target], config: FlextMeltanoConfig):
        super().__init__(config)
        self.target_class = target_class
        self.singer_wrapper = MeltanoSingerWrapper()

    def process_records(self, stream_name: str, records: Iterator[FlextRecord]) -> FlextResult[ProcessResult]:
        """Processa records de um stream"""

    def flush_buffer(self) -> FlextResult[bool]:
        """Força escrita de buffer"""

class FlextMeltanoDbtService(FlextMeltanoBaseService):
    """Base service para projetos DBT - usado em flext-dbt-*"""

    def __init__(self, project_dir: Path, config: FlextMeltanoConfig):
        super().__init__(config)
        self.project_dir = project_dir
        self.dbt_wrapper = MeltanoDbtWrapper()

    def run_models(self, models: FlextTypes.StringList) -> FlextResult[DbtRunResult]:
        """Executa modelos específicos"""

    def test_models(self, models: FlextTypes.StringList) -> FlextResult[DbtTestResult]:
        """Testa modelos específicos"""

    def generate_docs(self) -> FlextResult[bool]:
        """Gera documentação DBT"""
```

#### **plugins.py - Plugin Base Classes**

```python
class FlextTapPlugin(FlextPlugin):
    """Plugin base para taps - usado em flext-tap-*"""

    def __init__(self, plugin_config: FlextPluginConfig):
        super().__init__(plugin_config)
        self.tap_service = FlextMeltanoTapService(self.get_tap_class(), plugin_config)

    @abstractmethod
    def get_tap_class(self) -> type[Tap]:
        """Retorna classe Singer Tap específica"""

    def discover(self) -> FlextResult[FlextCatalog]:
        """Plugin discover interface"""
        return self.tap_service.get_catalog()

    def sync(self, catalog: FlextCatalog, state: dict) -> FlextResult[Iterator[FlextMessage]]:
        """Plugin sync interface"""

class FlextTargetPlugin(FlextPlugin):
    """Plugin base para targets - usado em flext-target-*"""

    def __init__(self, plugin_config: FlextPluginConfig):
        super().__init__(plugin_config)
        self.target_service = FlextMeltanoTargetService(self.get_target_class(), plugin_config)

    @abstractmethod
    def get_target_class(self) -> type[Target]:
        """Retorna classe Singer Target específica"""

    def process_messages(self, messages: Iterator[FlextMessage]) -> FlextResult[ProcessResult]:
        """Plugin process interface"""

class FlextDbtPlugin(FlextPlugin):
    """Plugin base para DBT - usado em flext-dbt-*"""

    def __init__(self, plugin_config: FlextPluginConfig):
        super().__init__(plugin_config)
        self.dbt_service = FlextMeltanoDbtService(plugin_config.project_dir, plugin_config)

    def run_transformation(self, models: FlextTypes.StringList) -> FlextResult[TransformResult]:
        """Plugin transformation interface"""
```

## **INTEGRATION PATTERNS**

### **Para flext-tap-oracle:**

```python
from flext_meltano import FlextTapPlugin, MeltanoSingerWrapper
from singer_sdk import Tap

class OracleTap(Tap):
    # Singer SDK implementation
    pass

class FlextTapOracle(FlextTapPlugin):
    def get_tap_class(self) -> type[Tap]:
        return OracleTap
```

### **Para flext-dbt-oracle:**

```python
from flext_meltano import FlextMeltanoDbtService, MeltanoDbtWrapper

class FlextDbtOracle(FlextMeltanoDbtService):
    def __init__(self, project_dir: Path):
        super().__init__(project_dir, FlextMeltanoConfig())

    def run_oracle_models(self) -> FlextResult[DbtRunResult]:
        return self.run_models(["models/oracle/*.sql"])
```

### **Para FlexCore (Go):**

```go
// FlexCore chama Python bridge
func (s *MeltanoService) RunPipeline(tap, target string) error {
    cmd := exec.Command("python", "-m", "flext_meltano.adapter", "run_pipeline", tap, target)
    output, err := cmd.Output()

    var result map[string]interface{}
    json.Unmarshal(output, &result)

    if !result["success"].(bool) {
        return errors.New(result["error"].(string))
    }
    return nil
}
```

## **CLI USAGE PATTERNS**

### **Direct CLI:**

```bash
# Via flext-meltano CLI
python -m flext_meltano run --tap tap-oracle --target target-postgres
python -m flext_meltano dbt run --models models/oracle
python -m flext_meltano discover --tap tap-oracle

# Via bridge (called by FlexCore)
python -m flext_meltano.adapter version
python -m flext_meltano.adapter run_pipeline tap-oracle target-postgres
python -m flext_meltano.adapter run_dbt run --models models/oracle
```

### **Library Usage:**

```python
# Direct library usage
from flext_meltano import MeltanoSingerWrapper, FlextMeltanoExecutor

wrapper = MeltanoSingerWrapper()
tap_result = wrapper.create_tap(OracleTap, {"host": "localhost"})
target_result = wrapper.create_target(PostgresTarget, {"host": "localhost"})

if tap_result.is_success and target_result.is_success:
    pipeline_result = wrapper.run_elt_pipeline(tap_result.value, target_result.value)
    print(f"Records processed: {pipeline_result.value.records_processed}")
```

## **TESTING STRATEGY**

### **Real Integration Tests (NO MOCKS):**

```python
class TestMeltanoSingerWrapper:
    def test_create_real_tap(self):
        """Test com tap CSV real"""
        wrapper = MeltanoSingerWrapper()
        result = wrapper.create_tap(TapCSV, {"files": ["test.csv"]})
        assert result.is_success
        assert isinstance(result.value, Tap)

    def test_run_real_pipeline(self):
        """Test com pipeline CSV → JSONL real"""
        # Setup real files, run real pipeline, verify real output
```

### **FlexCore Integration Tests:**

```python
class TestFlextMeltanoBridge:
    def test_go_bridge_communication(self):
        """Test real communication with FlexCore"""
        # Start FlexCore server, call Python bridge, verify results
```

## **DEPLOYMENT ARCHITECTURE**

### **Library Distribution:**

```python
# flext-meltano installs as:
pip install flext-meltano

# Provides:
from flext_meltano import (
    # Wrappers
    MeltanoSingerWrapper, MeltanoDbtWrapper, MeltanoBridge,
    # Runtime
    FlextMeltanoExecutor, FlextMeltanoBridge, FlextMeltanoCli,
    # Base components
    FlextMeltanoTapService, FlextMeltanoTargetService, FlextMeltanoDbtService,
    FlextTapPlugin, FlextTargetPlugin, FlextDbtPlugin
)
```

### **FlexCore Integration:**

```go
// FlexCore loads flext-meltano as plugin
type FlextMeltanoPlugin struct {
    pythonPath string
    bridge     *PythonBridge
}

func (p *FlextMeltanoPlugin) Execute(ctx context.Context, params map[string]interface{}) error {
    return p.bridge.Call("run_pipeline", params)
}
```

This architecture provides:

1. ✅ **Complete wrapper** for Meltano/Singer SDK/DBT → flext-core
2. ✅ **Full runtime** execution via Go bridge
3. ✅ **Solid base** for all flext-(dbt|tap|target) projects
4. ✅ **Real implementations** without mocks
5. ✅ **Clean dependencies** following SOLID principles
6. ✅ **Modern patterns** (.value, .unwrap_or(), FlextResult)
