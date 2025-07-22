"""Sistema de logging avançado para operações críticas."""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from flext_tools.utils.colors import Colors, print_colored


class LogLevel(Enum):
    """Níveis de log para operações críticas."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"  # Eventos de segurança
    OPERATION = "OPERATION"  # Início/fim de operações
    BACKUP = "BACKUP"  # Operações de backup
    ROLLBACK = "ROLLBACK"  # Operações de rollback


@dataclass
class LogEntry:
    """Entrada de log estruturada."""

    timestamp: str
    level: str
    operation_type: str
    session_id: str | None
    project: str | None
    message: str
    details: dict[str, Any]
    duration_ms: int | None = None
    backup_id: str | None = None
    safety_level: str | None = None


class DetailedLogger:
    """Logger detalhado para operações críticas com rastreabilidade completa."""

    def __init__(
        self,
        log_dir: Path | None = None,
        session_id: str | None = None,
        enable_console: bool = True,
        enable_file: bool = True,
    ) -> None:
        self.log_dir = log_dir or Path.cwd() / ".flext_logs"
        self.log_dir.mkdir(exist_ok=True)

        self.session_id = session_id or self._generate_session_id()
        self.enable_console = enable_console
        self.enable_file = enable_file

        # Arquivos de log
        self.session_log_file = self.log_dir / f"session_{self.session_id}.json"
        self.operations_log_file = self.log_dir / f"operations_{self.session_id}.json"
        self.security_log_file = self.log_dir / "security.json"

        # Controle de operações
        self.current_operation: dict[str, Any] | None = None
        self.operation_start_time: float | None = None

        # Buffer para melhor performance
        self.log_buffer: list[LogEntry] = []
        self.buffer_size = 50

        self._setup_logging()
        self._log_session_start()

    def _generate_session_id(self) -> str:
        """Gera ID único para sessão."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    def _setup_logging(self) -> None:
        """Configura logging padrão do Python."""
        if self.enable_file:
            # Handler para arquivo geral
            file_handler = logging.FileHandler(
                self.log_dir / f"general_{self.session_id}.log",
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)

            # Formatter detalhado
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)

            # Aplica ao root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)

    def _log_session_start(self) -> None:
        """Registra início da sessão."""
        self.log(
            LogLevel.OPERATION,
            "SESSION_START",
            "Sessão de logging iniciada",
            {
                "session_id": self.session_id,
                "log_dir": str(self.log_dir),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def start_operation(
        self,
        operation_type: str,
        description: str,
        project: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Inicia rastreamento de operação crítica.

        Args:
            operation_type: Tipo da operação (ADD_DEPS, UPDATE_VERSIONS, etc)
            description: Descrição da operação
            project: Projeto sendo modificado
            details: Detalhes específicos da operação

        """
        if self.current_operation:
            self.warning(
                "OPERATION_OVERLAP",
                f"Nova operação iniciada sem finalizar: {operation_type}",
                {"previous_operation": self.current_operation},
            )

        self.current_operation = {
            "type": operation_type,
            "description": description,
            "project": project,
            "start_time": time.time(),
            "details": details or {},
        }
        self.operation_start_time = time.time()

        self.log(
            LogLevel.OPERATION,
            operation_type,
            f"🚀 INÍCIO: {description}",
            {
                "project": project,
                "operation_details": details or {},
                "session_id": self.session_id,
            },
        )

    def end_operation(
        self,
        success: bool = True,
        result_details: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        """Finaliza rastreamento de operação.

        Args:
            success: Se operação foi bem-sucedida
            result_details: Detalhes do resultado
            error_message: Mensagem de erro se falhou

        """
        if not self.current_operation:
            self.warning(
                "OPERATION_END_WITHOUT_START",
                "Tentativa de finalizar operação sem início",
                {"result_details": result_details},
            )
            return

        duration_ms = int(
            (time.time() - (self.operation_start_time or time.time())) * 1000,
        )

        level = LogLevel.OPERATION if success else LogLevel.ERROR
        status = "✅ SUCESSO" if success else "❌ FALHA"

        log_details = {
            "operation_type": self.current_operation["type"],
            "project": self.current_operation["project"],
            "duration_ms": duration_ms,
            "success": success,
            "start_details": self.current_operation["details"],
            "result_details": result_details or {},
        }

        if error_message:
            log_details["error_message"] = error_message

        self.log(
            level,
            self.current_operation["type"],
            f"{status}: {self.current_operation['description']} ({duration_ms}ms)",
            log_details,
            duration_ms=duration_ms,
        )

        # Salva operação completa no log de operações
        self._save_operation_log(
            self.current_operation,
            success,
            duration_ms,
            result_details,
            error_message,
        )

        self.current_operation = None
        self.operation_start_time = None

    def log_security_event(
        self,
        event_type: str,
        description: str,
        risk_level: str,
        details: dict[str, Any],
        action_taken: str | None = None,
    ) -> None:
        """Registra evento de segurança crítico.

        Args:
            event_type: Tipo do evento (BLOCKED_PACKAGE, SUSPICIOUS_OPERATION, etc)
            description: Descrição do evento
            risk_level: Nível de risco (LOW, MEDIUM, HIGH, CRITICAL)
            details: Detalhes específicos
            action_taken: Ação tomada em resposta

        """
        security_details = {
            "event_type": event_type,
            "risk_level": risk_level,
            "details": details,
            "action_taken": action_taken,
            "session_id": self.session_id,
        }

        self.log(
            LogLevel.SECURITY,
            event_type,
            f"🛡️ SEGURANÇA [{risk_level}]: {description}",
            security_details,
            safety_level=risk_level,
        )

        # Log específico de segurança
        self._save_security_log(
            event_type,
            description,
            risk_level,
            details,
            action_taken,
        )

    def log_backup_operation(
        self,
        backup_type: str,
        backup_id: str,
        files_backed_up: list[str],
        success: bool = True,
        error_message: str | None = None,
    ) -> None:
        """Registra operação de backup.

        Args:
            backup_type: Tipo de backup (FILE, PROJECT, SESSION)
            backup_id: ID único do backup
            files_backed_up: Lista de arquivos incluídos
            success: Se backup foi bem-sucedido
            error_message: Mensagem de erro se falhou

        """
        status = "✅" if success else "❌"

        self.log(
            LogLevel.BACKUP,
            backup_type,
            f"{status} BACKUP: {backup_id} ({len(files_backed_up)} arquivos)",
            {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "files_count": len(files_backed_up),
                "files_backed_up": files_backed_up,
                "success": success,
                "error_message": error_message,
                "session_id": self.session_id,
            },
            backup_id=backup_id,
        )

    def log_dependency_change(
        self,
        project: str,
        dependency: str,
        action: str,  # ADD, REMOVE, UPDATE
        old_version: str | None = None,
        new_version: str | None = None,
        category: str | None = None,
    ) -> None:
        """Registra mudança específica de dependência.

        Args:
            project: Nome do projeto
            dependency: Nome da dependência
            action: Ação realizada
            old_version: Versão anterior (para UPDATE)
            new_version: Nova versão
            category: Categoria (runtime, dev, test)

        """
        change_details = {
            "dependency": dependency,
            "action": action,
            "old_version": old_version,
            "new_version": new_version,
            "category": category,
            "project": project,
        }

        version_info = ""
        if action == "UPDATE" and old_version and new_version:
            version_info = f" ({old_version} → {new_version})"
        elif new_version:
            version_info = f" ({new_version})"

        self.log(
            LogLevel.INFO,
            "DEPENDENCY_CHANGE",
            f"📦 {action}: {dependency}{version_info} em {project}",
            change_details,
        )

    def log_validation_result(
        self,
        validation_type: str,
        target: str,
        passed: bool,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        """Registra resultado de validação.

        Args:
            validation_type: Tipo de validação
            target: Alvo da validação
            passed: Se validação passou
            warnings: Lista de warnings
            errors: Lista de erros

        """
        status = "✅ PASSOU" if passed else "❌ FALHOU"

        self.log(
            LogLevel.INFO if passed else LogLevel.WARNING,
            "VALIDATION",
            f"{status}: {validation_type} para {target}",
            {
                "validation_type": validation_type,
                "target": target,
                "passed": passed,
                "warnings": warnings or [],
                "errors": errors or [],
                "warning_count": len(warnings or []),
                "error_count": len(errors or []),
            },
        )

    def log(
        self,
        level: LogLevel,
        operation_type: str,
        message: str,
        details: dict[str, Any],
        duration_ms: int | None = None,
        backup_id: str | None = None,
        safety_level: str | None = None,
    ) -> None:
        """Método principal de logging.

        Args:
            level: Nível do log
            operation_type: Tipo da operação
            message: Mensagem principal
            details: Detalhes estruturados
            duration_ms: Duração em milissegundos
            backup_id: ID de backup relacionado
            safety_level: Nível de segurança

        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            operation_type=operation_type,
            session_id=self.session_id,
            project=details.get("project"),
            message=message,
            details=details,
            duration_ms=duration_ms,
            backup_id=backup_id,
            safety_level=safety_level,
        )

        # Console output com cores
        if self.enable_console:
            self._print_console_log(entry)

        # Adiciona ao buffer
        self.log_buffer.append(entry)

        # Flush buffer se necessário
        if len(self.log_buffer) >= self.buffer_size:
            self._flush_buffer()

    def debug(
        self,
        operation_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log de debug."""
        self.log(LogLevel.DEBUG, operation_type, message, details or {})

    def info(
        self,
        operation_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log de informação."""
        self.log(LogLevel.INFO, operation_type, message, details or {})

    def warning(
        self,
        operation_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log de warning."""
        self.log(LogLevel.WARNING, operation_type, message, details or {})

    def error(
        self,
        operation_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log de erro."""
        self.log(LogLevel.ERROR, operation_type, message, details or {})

    def critical(
        self,
        operation_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log crítico."""
        self.log(LogLevel.CRITICAL, operation_type, message, details or {})

    def _print_console_log(self, entry: LogEntry) -> None:
        """Imprime log no console com cores."""
        if not self.enable_console:
            return

        # Cores por nível
        level_colors = {
            "DEBUG": Colors.CYAN,
            "INFO": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED,
            "SECURITY": Colors.MAGENTA,
            "OPERATION": Colors.BLUE,
            "BACKUP": Colors.CYAN,
            "ROLLBACK": Colors.YELLOW,
        }

        color = level_colors.get(entry.level, Colors.GRAY)

        # Formato: [TIMESTAMP] LEVEL | MESSAGE
        timestamp = entry.timestamp.split("T")[1][:8]  # HH:MM:SS
        print_colored(f"[{timestamp}] {entry.level:8s} | {entry.message}", color)

        # Detalhes importantes em linha extra
        if entry.level in {"ERROR", "CRITICAL", "SECURITY"} and "error_message" in entry.details:
            print_colored(
                f"         ERROR   | {entry.details['error_message']}",
                Colors.RED,
            )

    def _flush_buffer(self) -> None:
        """Salva buffer no arquivo."""
        if not self.enable_file or not self.log_buffer:
            return

        # Anexa ao arquivo de sessão
        entries_dict = [asdict(entry) for entry in self.log_buffer]

        # Lê arquivo existente se houver
        existing_entries = []
        try:
            with Path(self.session_log_file).open(encoding="utf-8") as f:
                existing_entries = json.load(f)
        except (json.JSONDecodeError, Exception):
            existing_entries = []

        # Adiciona novas entradas
        existing_entries.extend(entries_dict)

        # Salva arquivo atualizado
        with Path(self.session_log_file).open("w", encoding="utf-8") as f:
            json.dump(existing_entries, f, indent=2, ensure_ascii=False)

        self.log_buffer.clear()

    def _save_operation_log(
        self,
        operation: dict[str, Any],
        success: bool,
        duration_ms: int,
        result_details: dict[str, Any] | None,
        error_message: str | None,
    ) -> None:
        """Salva log específico de operações."""
        if not self.enable_file:
            return

        operation_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "operation_type": operation["type"],
            "description": operation["description"],
            "project": operation["project"],
            "duration_ms": duration_ms,
            "success": success,
            "start_details": operation["details"],
            "result_details": result_details or {},
            "error_message": error_message,
        }

        # Lê operações existentes
        existing_operations = []
        try:
            with Path(self.operations_log_file).open(encoding="utf-8") as f:
                existing_operations = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            existing_operations = []

        existing_operations.append(operation_entry)

        # Salva arquivo atualizado
        with Path(self.operations_log_file).open("w", encoding="utf-8") as f:
            json.dump(existing_operations, f, indent=2, ensure_ascii=False)

    def _save_security_log(
        self,
        event_type: str,
        description: str,
        risk_level: str,
        details: dict[str, Any],
        action_taken: str | None,
    ) -> None:
        """Salva log específico de segurança."""
        if not self.enable_file:
            return

        security_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "description": description,
            "risk_level": risk_level,
            "details": details,
            "action_taken": action_taken,
        }

        # Lê eventos existentes
        existing_events = []
        try:
            with Path(self.security_log_file).open(encoding="utf-8") as f:
                existing_events = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            existing_events = []

        existing_events.append(security_entry)

        # Salva arquivo atualizado
        with Path(self.security_log_file).open("w", encoding="utf-8") as f:
            json.dump(existing_events, f, indent=2, ensure_ascii=False)

    def close(self) -> None:
        """Finaliza sessão de logging."""
        # Flush buffer final
        self._flush_buffer()

        # Log de encerramento
        self.log(
            LogLevel.OPERATION,
            "SESSION_END",
            "Sessão de logging finalizada",
            {
                "session_id": self.session_id,
                "duration": time.time() - (self.operation_start_time or time.time()),
            },
        )

        # Flush final
        self._flush_buffer()

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        if exc_type:
            self.error(
                "SESSION_ERROR",
                f"Sessão finalizada com erro: {exc_type.__name__}",
                {
                    "exception_type": exc_type.__name__,
                    "exception_message": str(exc_val),
                    "traceback": str(exc_tb),
                },
            )
        self.close()


# Instância global para conveniência
_global_logger: DetailedLogger | None = None


def get_logger(
    session_id: str | None = None,
    log_dir: Path | None = None,
) -> DetailedLogger:
    """Obtém logger global ou cria novo."""
    global _global_logger

    if _global_logger is None:
        _global_logger = DetailedLogger(session_id=session_id, log_dir=log_dir)

    return _global_logger


def set_global_logger(logger: DetailedLogger) -> None:
    """Define logger global."""
    global _global_logger
    _global_logger = logger


def log_operation(
    operation_type: str,
    description: str,
    project: str | None = None,
    details: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator para logging automático de operações."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger()
            logger.start_operation(operation_type, description, project, details)

            try:
                result = func(*args, **kwargs)
                logger.end_operation(
                    success=True,
                    result_details={"result": str(result)},
                )
                return result
            except Exception as e:
                logger.end_operation(success=False, error_message=str(e))
                raise

        return wrapper

    return decorator
