package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // PostgreSQL driver
	"github.com/pkg/errors"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	gormlogger "gorm.io/gorm/logger"
)

// DB interface para abstrair operações de banco
type DB interface {
	Query(query string, args ...interface{}) (*sql.Rows, error)
	QueryRow(query string, args ...interface{}) *sql.Row
	QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error)
	QueryRowContext(ctx context.Context, query string, args ...interface{}) *sql.Row
	Exec(query string, args ...interface{}) (sql.Result, error)
	ExecContext(ctx context.Context, query string, args ...interface{}) (sql.Result, error)
	Prepare(query string) (*sql.Stmt, error)
	PrepareContext(ctx context.Context, query string) (*sql.Stmt, error)
	Begin() (*sql.Tx, error)
	BeginTx(ctx context.Context, opts *sql.TxOptions) (*sql.Tx, error)
	Close() error
	Ping() error
	PingContext(ctx context.Context) error
}

// Connection gerencia a conexão com o banco de dados
type Connection struct {
	db     *sql.DB
	gormDB *gorm.DB
	sqlxDB *sqlx.DB
	config *config.DatabaseConfig
	logger logging.Logger
}

// NewConnection cria uma nova conexão com o banco
func NewConnection(cfg *config.DatabaseConfig, logger logging.Logger) (*Connection, error) {
	if cfg.Driver == "memory" {
		// Para desenvolvimento, retorna uma conexão mock ou em memória
		return &Connection{
			config: cfg,
			logger: logger,
		}, nil
	}

	// Construir DSN para PostgreSQL
	dsn := buildPostgresDSN(cfg)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, errors.Wrap(err, "opening PostgreSQL database connection")
	}

	// Configurar connection pool
	db.SetMaxOpenConns(cfg.MaxOpenConns)
	db.SetMaxIdleConns(cfg.MaxIdleConns)
	db.SetConnMaxLifetime(cfg.ConnMaxLifetime)
	db.SetConnMaxIdleTime(cfg.ConnMaxIdleTime)

	// Testar conexão
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		db.Close()
		return nil, errors.Wrap(err, "establishing database connectivity during health check")
	}

	// Initialize GORM with the same database connection
	var gormDB *gorm.DB
	var sqlxDB *sqlx.DB

	if cfg.Driver == "postgres" {
		// Initialize GORM
		gormLogger := gormlogger.New(
			&gormLoggerAdapter{logger: logger},
			gormlogger.Config{
				SlowThreshold:             200 * time.Millisecond,
				LogLevel:                  gormlogger.Warn,
				IgnoreRecordNotFoundError: true,
				Colorful:                  false,
			},
		)

		gormDialector := postgres.New(postgres.Config{
			Conn: db,
		})

		var err error
		gormDB, err = gorm.Open(gormDialector, &gorm.Config{
			Logger: gormLogger,
		})
		if err != nil {
			db.Close()
			return nil, errors.Wrap(err, "initializing GORM")
		}

		// Initialize SQLX with the same database connection
		sqlxDB = sqlx.NewDb(db, "postgres")

		// Auto-migrate GORM models from persistence package
		// Models will be migrated by the repository when first used
		logger.Info("GORM and SQLX initialized successfully")
	}

	logger.Info("Database connection established successfully",
		logging.F("host", cfg.Host),
		logging.F("port", cfg.Port),
		logging.F("database", cfg.Database),
		logging.F("gorm_enabled", gormDB != nil),
		logging.F("sqlx_enabled", sqlxDB != nil),
	)

	return &Connection{
		db:     db,
		gormDB: gormDB,
		sqlxDB: sqlxDB,
		config: cfg,
		logger: logger,
	}, nil
}

// GetDB retorna a instância do banco de dados
func (c *Connection) GetDB() DB {
	if c.db == nil {
		// Para modo memory, retorna uma implementação mock
		return &MockDB{}
	}
	return c.db
}

// GetGormDB retorna a instância GORM do banco de dados
func (c *Connection) GetGormDB() *gorm.DB {
	return c.gormDB
}

// GetSqlxDB retorna a instância SQLX do banco de dados
func (c *Connection) GetSqlxDB() *sqlx.DB {
	return c.sqlxDB
}

// Close fecha a conexão com o banco
func (c *Connection) Close() error {
	if c.db != nil {
		return c.db.Close()
	}
	return nil
}

// HealthCheck verifica se o banco está saudável
func (c *Connection) HealthCheck(ctx context.Context) error {
	if c.db == nil {
		return nil // Memory mode sempre saudável
	}

	return c.db.PingContext(ctx)
}

// GetStats retorna estatísticas da conexão
func (c *Connection) GetStats() sql.DBStats {
	if c.db == nil {
		return sql.DBStats{}
	}
	return c.db.Stats()
}

// buildPostgresDSN constrói a string de conexão PostgreSQL
func buildPostgresDSN(cfg *config.DatabaseConfig) string {
	return fmt.Sprintf(
		"host=%s port=%d user=%s dbname=%s sslmode=%s",
		cfg.Host,
		cfg.Port,
		cfg.Username,
		cfg.Database,
		cfg.SSLMode,
	) + getPasswordParam(cfg.Password)
}

// getPasswordParam adiciona password se fornecido
func getPasswordParam(password string) string {
	if password != "" {
		return " password=" + password
	}
	return ""
}

// Transaction executa uma operação em transação
func (c *Connection) Transaction(ctx context.Context, fn func(*sql.Tx) error) error {
	if c.db == nil {
		// Para memory mode, executa diretamente
		return fn(nil)
	}

	tx, err := c.db.BeginTx(ctx, nil)
	if err != nil {
		return errors.Wrap(err, "beginning database transaction")
	}

	defer func() {
		if p := recover(); p != nil {
			tx.Rollback()
			panic(p)
		}
	}()

	if err := fn(tx); err != nil {
		tx.Rollback()
		return err
	}

	if err := tx.Commit(); err != nil {
		return errors.Wrap(err, "committing database transaction")
	}

	return nil
}

// MockDB implementação mock para desenvolvimento
type MockDB struct{}

func (m *MockDB) Query(query string, args ...interface{}) (*sql.Rows, error) {
	return nil, fmt.Errorf("mock database - query not implemented")
}

func (m *MockDB) QueryRow(query string, args ...interface{}) *sql.Row {
	return nil
}

func (m *MockDB) QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error) {
	return nil, fmt.Errorf("mock database - query not implemented")
}

func (m *MockDB) QueryRowContext(ctx context.Context, query string, args ...interface{}) *sql.Row {
	return nil
}

func (m *MockDB) Exec(query string, args ...interface{}) (sql.Result, error) {
	return &MockResult{}, nil
}

func (m *MockDB) ExecContext(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
	return &MockResult{}, nil
}

func (m *MockDB) Prepare(query string) (*sql.Stmt, error) {
	return nil, fmt.Errorf("mock database - prepare not implemented")
}

func (m *MockDB) PrepareContext(ctx context.Context, query string) (*sql.Stmt, error) {
	return nil, fmt.Errorf("mock database - prepare not implemented")
}

func (m *MockDB) Begin() (*sql.Tx, error) {
	return nil, fmt.Errorf("mock database - begin not implemented")
}

func (m *MockDB) BeginTx(ctx context.Context, opts *sql.TxOptions) (*sql.Tx, error) {
	return nil, fmt.Errorf("mock database - begin not implemented")
}

func (m *MockDB) Close() error {
	return nil
}

func (m *MockDB) Ping() error {
	return nil
}

func (m *MockDB) PingContext(ctx context.Context) error {
	return nil
}

// MockResult implementação mock do sql.Result
type MockResult struct{}

func (m *MockResult) LastInsertId() (int64, error) {
	return 1, nil
}

func (m *MockResult) RowsAffected() (int64, error) {
	return 1, nil
}

// gormLoggerAdapter adapts our logger to GORM's logger interface
type gormLoggerAdapter struct {
	logger logging.Logger
}

func (g *gormLoggerAdapter) Printf(format string, v ...interface{}) {
	g.logger.Debug(fmt.Sprintf(format, v...))
}
