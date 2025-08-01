package database

import (
	"context"
	"database/sql"
	"embed"
	"fmt"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/logging"
)

//go:embed migrations/*.sql
var migrationFiles embed.FS

// Migration representa uma migration de banco de dados
type Migration struct {
	Version     int
	Name        string
	Description string
	SQL         string
	AppliedAt   *time.Time
}

// Migrator gerencia as migrations do banco de dados
type Migrator struct {
	db     DB
	logger logging.Logger
}

// NewMigrator cria um novo migrator
func NewMigrator(db DB, logger logging.Logger) *Migrator {
	return &Migrator{
		db:     db,
		logger: logger,
	}
}

// Run executa todas as migrations pendentes
func (m *Migrator) Run(ctx context.Context) error {
	m.logger.Info("Starting database migrations")

	// Criar tabela de migrations se não existir
	if err := m.createMigrationsTable(ctx); err != nil {
		return fmt.Errorf("failed to create migrations table: %w", err)
	}

	// Carregar migrations do filesystem
	availableMigrations, err := m.loadMigrations()
	if err != nil {
		return fmt.Errorf("failed to load migrations: %w", err)
	}

	// Verificar quais migrations já foram aplicadas
	appliedMigrations, err := m.getAppliedMigrations(ctx)
	if err != nil {
		return fmt.Errorf("failed to get applied migrations: %w", err)
	}

	// Determinar migrations pendentes
	pendingMigrations := m.getPendingMigrations(availableMigrations, appliedMigrations)

	if len(pendingMigrations) == 0 {
		m.logger.Info("No pending migrations found")
		return nil
	}

	// Aplicar migrations pendentes
	for _, migration := range pendingMigrations {
		if err := m.applyMigration(ctx, migration); err != nil {
			return fmt.Errorf("failed to apply migration %d_%s: %w",
				migration.Version, migration.Name, err)
		}

		m.logger.Info("Applied migration",
			logging.F("version", migration.Version),
			logging.F("name", migration.Name),
		)
	}

	m.logger.Info("Database migrations completed successfully",
		logging.F("applied_count", len(pendingMigrations)),
	)

	return nil
}

// Status retorna o status das migrations
func (m *Migrator) Status(ctx context.Context) ([]*Migration, error) {
	// Carregar migrations disponíveis
	availableMigrations, err := m.loadMigrations()
	if err != nil {
		return nil, fmt.Errorf("failed to load migrations: %w", err)
	}

	// Verificar quais foram aplicadas
	appliedMigrations, err := m.getAppliedMigrations(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get applied migrations: %w", err)
	}

	// Combinar informações
	for _, migration := range availableMigrations {
		if appliedTime, exists := appliedMigrations[migration.Version]; exists {
			migration.AppliedAt = &appliedTime
		}
	}

	return availableMigrations, nil
}

// createMigrationsTable cria a tabela para controle de migrations
func (m *Migrator) createMigrationsTable(ctx context.Context) error {
	query := `
		CREATE TABLE IF NOT EXISTS schema_migrations (
			version INTEGER PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
		);
	`

	_, err := m.db.ExecContext(ctx, query)
	return err
}

// loadMigrations carrega todas as migrations do filesystem
func (m *Migrator) loadMigrations() ([]*Migration, error) {
	files, err := migrationFiles.ReadDir("migrations")
	if err != nil {
		return nil, fmt.Errorf("failed to read migrations directory: %w", err)
	}

	var migrations []*Migration

	for _, file := range files {
		if !strings.HasSuffix(file.Name(), ".sql") {
			continue
		}

		migration, err := m.parseMigrationFile(file.Name())
		if err != nil {
			m.logger.Warn("Skipping invalid migration file",
				logging.F("file", file.Name()),
				logging.F("error", err.Error()),
			)
			continue
		}

		migrations = append(migrations, migration)
	}

	// Ordenar por versão
	sort.Slice(migrations, func(i, j int) bool {
		return migrations[i].Version < migrations[j].Version
	})

	return migrations, nil
}

// parseMigrationFile faz o parse de um arquivo de migration
func (m *Migrator) parseMigrationFile(filename string) (*Migration, error) {
	// Extrair versão e nome do arquivo (ex: 001_initial_schema.sql)
	nameWithoutExt := strings.TrimSuffix(filename, ".sql")
	parts := strings.SplitN(nameWithoutExt, "_", 2)

	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid migration filename format: %s", filename)
	}

	version, err := strconv.Atoi(parts[0])
	if err != nil {
		return nil, fmt.Errorf("invalid version in filename %s: %w", filename, err)
	}

	name := parts[1]

	// Ler conteúdo do arquivo
	content, err := migrationFiles.ReadFile(filepath.Join("migrations", filename))
	if err != nil {
		return nil, fmt.Errorf("failed to read migration file %s: %w", filename, err)
	}

	// Extrair descrição do comentário
	description := m.extractDescription(string(content))

	return &Migration{
		Version:     version,
		Name:        name,
		Description: description,
		SQL:         string(content),
	}, nil
}

// extractDescription extrai a descrição do comentário da migration
func (m *Migrator) extractDescription(content string) string {
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "-- Description:") {
			return strings.TrimSpace(strings.TrimPrefix(line, "-- Description:"))
		}
	}
	return ""
}

// getAppliedMigrations retorna as migrations já aplicadas
func (m *Migrator) getAppliedMigrations(ctx context.Context) (map[int]time.Time, error) {
	query := `SELECT version, applied_at FROM schema_migrations ORDER BY version`

	rows, err := m.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to query applied migrations: %w", err)
	}
	defer rows.Close()

	applied := make(map[int]time.Time)

	for rows.Next() {
		var version int
		var appliedAt time.Time

		if err := rows.Scan(&version, &appliedAt); err != nil {
			return nil, fmt.Errorf("failed to scan migration row: %w", err)
		}

		applied[version] = appliedAt
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating migration rows: %w", err)
	}

	return applied, nil
}

// getPendingMigrations determina quais migrations ainda não foram aplicadas
func (m *Migrator) getPendingMigrations(available []*Migration, applied map[int]time.Time) []*Migration {
	var pending []*Migration

	for _, migration := range available {
		if _, exists := applied[migration.Version]; !exists {
			pending = append(pending, migration)
		}
	}

	return pending
}

// applyMigration aplica uma migration específica
func (m *Migrator) applyMigration(ctx context.Context, migration *Migration) error {
	// Executar em transação para garantir atomicidade
	var tx *sql.Tx
	var err error

	// Check if database supports transactions
	if sqlDB, ok := m.db.(*sql.DB); ok {
		tx, err = sqlDB.BeginTx(ctx, nil)
		if err != nil {
			return fmt.Errorf("failed to begin transaction: %w", err)
		}
		defer func() {
			if p := recover(); p != nil {
				tx.Rollback()
				panic(p)
			}
		}()
	}

	// Executar SQL da migration
	if tx != nil {
		_, err = tx.ExecContext(ctx, migration.SQL)
	} else {
		_, err = m.db.ExecContext(ctx, migration.SQL)
	}

	if err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return fmt.Errorf("failed to execute migration SQL: %w", err)
	}

	// Registrar migration como aplicada
	insertQuery := `
		INSERT INTO schema_migrations (version, name, applied_at) 
		VALUES ($1, $2, NOW())
	`

	if tx != nil {
		_, err = tx.ExecContext(ctx, insertQuery, migration.Version, migration.Name)
	} else {
		_, err = m.db.ExecContext(ctx, insertQuery, migration.Version, migration.Name)
	}

	if err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return fmt.Errorf("failed to record migration: %w", err)
	}

	// Commit transação
	if tx != nil {
		if err := tx.Commit(); err != nil {
			return fmt.Errorf("failed to commit migration transaction: %w", err)
		}
	}

	return nil
}

// Reset remove todas as migrations (CUIDADO: só para desenvolvimento)
func (m *Migrator) Reset(ctx context.Context) error {
	m.logger.Warn("Resetting database - this will drop all tables!")

	// Lista de tabelas para dropar (ordem reversa das dependências)
	tables := []string{
		"step_executions",
		"pipeline_executions",
		"plugin_ports",
		"pipeline_steps",
		"domain_events",
		"plugins",
		"pipelines",
		"schema_migrations",
	}

	for _, table := range tables {
		query := fmt.Sprintf("DROP TABLE IF EXISTS %s CASCADE", table)
		if _, err := m.db.ExecContext(ctx, query); err != nil {
			m.logger.Warn("Failed to drop table",
				logging.F("table", table),
				logging.F("error", err.Error()),
			)
		} else {
			m.logger.Info("Dropped table", logging.F("table", table))
		}
	}

	m.logger.Info("Database reset completed")
	return nil
}
