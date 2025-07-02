package connectors

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/godror/godror"
	"github.com/google/uuid"
)

// OracleConnector provides real Oracle database connectivity
type OracleConnector struct {
	config *OracleConfig
	db     *sql.DB
	logger logging.Logger
}

// OracleConfig holds Oracle connection configuration
type OracleConfig struct {
	Host               string        `json:"host"`
	Port               int           `json:"port"`
	ServiceName        string        `json:"service_name"`
	SID                string        `json:"sid"`
	Username           string        `json:"username"`
	Password           string        `json:"password"`
	ConnectString      string        `json:"connect_string"`
	Wallet             string        `json:"wallet"`
	WalletPassword     string        `json:"wallet_password"`
	MaxOpenConns       int           `json:"max_open_conns"`
	MaxIdleConns       int           `json:"max_idle_conns"`
	ConnMaxLifetime    time.Duration `json:"conn_max_lifetime"`
	ConnectionTimeout  time.Duration `json:"connection_timeout"`
	CommandTimeout     time.Duration `json:"command_timeout"`
	FetchArraySize     int           `json:"fetch_array_size"`
	PrefetchRows       int           `json:"prefetch_rows"`
	PrefetchMemory     int           `json:"prefetch_memory"`
	StmtCacheSize      int           `json:"stmt_cache_size"`
	EnableEvents       bool          `json:"enable_events"`
	Timezone           string        `json:"timezone"`
	Charset            string        `json:"charset"`
	NCharset           string        `json:"ncharset"`
}

// OracleQueryResult represents the result of an Oracle query
type OracleQueryResult struct {
	Columns    []string                 `json:"columns"`
	Rows       []map[string]interface{} `json:"rows"`
	RowCount   int                      `json:"row_count"`
	QueryTime  time.Duration            `json:"query_time"`
	Metadata   map[string]interface{}   `json:"metadata"`
}

// OracleExecutionResult represents the result of an Oracle command execution
type OracleExecutionResult struct {
	Success       bool                   `json:"success"`
	RowsAffected  int64                  `json:"rows_affected"`
	LastInsertID  int64                  `json:"last_insert_id,omitempty"`
	ExecutionTime time.Duration          `json:"execution_time"`
	Message       string                 `json:"message"`
	ErrorCode     int                    `json:"error_code,omitempty"`
	Metadata      map[string]interface{} `json:"metadata"`
}

// OracleTableInfo represents Oracle table information
type OracleTableInfo struct {
	TableName   string                 `json:"table_name"`
	Owner       string                 `json:"owner"`
	Columns     []OracleColumnInfo     `json:"columns"`
	Indexes     []OracleIndexInfo      `json:"indexes"`
	Constraints []OracleConstraintInfo `json:"constraints"`
	RowCount    int64                  `json:"row_count"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// OracleColumnInfo represents Oracle column information
type OracleColumnInfo struct {
	ColumnName   string `json:"column_name"`
	DataType     string `json:"data_type"`
	DataLength   int    `json:"data_length"`
	DataPrecision *int  `json:"data_precision,omitempty"`
	DataScale    *int   `json:"data_scale,omitempty"`
	Nullable     string `json:"nullable"`
	DefaultValue *string `json:"default_value,omitempty"`
	ColumnID     int    `json:"column_id"`
}

// OracleIndexInfo represents Oracle index information
type OracleIndexInfo struct {
	IndexName  string   `json:"index_name"`
	IndexType  string   `json:"index_type"`
	Uniqueness string   `json:"uniqueness"`
	Columns    []string `json:"columns"`
}

// OracleConstraintInfo represents Oracle constraint information
type OracleConstraintInfo struct {
	ConstraintName string   `json:"constraint_name"`
	ConstraintType string   `json:"constraint_type"`
	Columns        []string `json:"columns"`
	RefTable       *string  `json:"ref_table,omitempty"`
	RefColumns     []string `json:"ref_columns,omitempty"`
}

// NewOracleConnector creates a new Oracle connector
func NewOracleConnector(config *OracleConfig, logger logging.Logger) (*OracleConnector, error) {
	if config == nil {
		return nil, fmt.Errorf("Oracle config cannot be nil")
	}

	// Set defaults
	if config.Port == 0 {
		config.Port = 1521
	}
	if config.MaxOpenConns == 0 {
		config.MaxOpenConns = 25
	}
	if config.MaxIdleConns == 0 {
		config.MaxIdleConns = 5
	}
	if config.ConnMaxLifetime == 0 {
		config.ConnMaxLifetime = 5 * time.Minute
	}
	if config.ConnectionTimeout == 0 {
		config.ConnectionTimeout = 30 * time.Second
	}
	if config.CommandTimeout == 0 {
		config.CommandTimeout = 60 * time.Second
	}
	if config.FetchArraySize == 0 {
		config.FetchArraySize = 1000
	}
	if config.StmtCacheSize == 0 {
		config.StmtCacheSize = 40
	}

	connector := &OracleConnector{
		config: config,
		logger: logger,
	}

	return connector, nil
}

// Connect establishes connection to Oracle database
func (oc *OracleConnector) Connect(ctx context.Context) error {
	var dsn string

	if oc.config.ConnectString != "" {
		// Use provided connect string
		dsn = fmt.Sprintf("%s/%s@%s", oc.config.Username, oc.config.Password, oc.config.ConnectString)
	} else {
		// Build connect string
		var connectString string
		if oc.config.ServiceName != "" {
			connectString = fmt.Sprintf("%s:%d/%s", oc.config.Host, oc.config.Port, oc.config.ServiceName)
		} else if oc.config.SID != "" {
			connectString = fmt.Sprintf("%s:%d:%s", oc.config.Host, oc.config.Port, oc.config.SID)
		} else {
			return fmt.Errorf("either service_name or sid must be provided")
		}
		dsn = fmt.Sprintf("%s/%s@%s", oc.config.Username, oc.config.Password, connectString)
	}

	oc.logger.Info("Connecting to Oracle database",
		logging.F("host", oc.config.Host),
		logging.F("port", oc.config.Port),
		logging.F("service_name", oc.config.ServiceName),
		logging.F("username", oc.config.Username),
	)

	// Open connection using standard sql.Open with DSN
	db, err := sql.Open("godror", dsn)
	if err != nil {
		return fmt.Errorf("failed to open Oracle database connection: %w", err)
	}

	// Configure connection pool
	db.SetMaxOpenConns(oc.config.MaxOpenConns)
	db.SetMaxIdleConns(oc.config.MaxIdleConns)
	db.SetConnMaxLifetime(oc.config.ConnMaxLifetime)

	// Test connection
	ctx, cancel := context.WithTimeout(ctx, oc.config.ConnectionTimeout)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		db.Close()
		return fmt.Errorf("failed to connect to Oracle database: %w", err)
	}

	oc.db = db
	oc.logger.Info("Successfully connected to Oracle database")
	return nil
}

// Query executes a SELECT query and returns results
func (oc *OracleConnector) Query(ctx context.Context, query string, args ...interface{}) (*OracleQueryResult, error) {
	if oc.db == nil {
		return nil, fmt.Errorf("not connected to Oracle database")
	}

	startTime := time.Now()

	oc.logger.Debug("Executing Oracle query",
		logging.F("query", query),
		logging.F("args", args),
	)

	ctx, cancel := context.WithTimeout(ctx, oc.config.CommandTimeout)
	defer cancel()

	rows, err := oc.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("query execution failed: %w", err)
	}
	defer rows.Close()

	// Get column information
	columns, err := rows.Columns()
	if err != nil {
		return nil, fmt.Errorf("failed to get columns: %w", err)
	}

	columnTypes, err := rows.ColumnTypes()
	if err != nil {
		return nil, fmt.Errorf("failed to get column types: %w", err)
	}

	// Prepare result storage
	var resultRows []map[string]interface{}
	values := make([]interface{}, len(columns))
	valuePtrs := make([]interface{}, len(columns))

	for i := range columns {
		valuePtrs[i] = &values[i]
	}

	// Scan rows
	for rows.Next() {
		err := rows.Scan(valuePtrs...)
		if err != nil {
			return nil, fmt.Errorf("failed to scan row: %w", err)
		}

		row := make(map[string]interface{})
		for i, col := range columns {
			val := values[i]
			
			// Handle Oracle-specific types
			if val != nil {
				switch v := val.(type) {
				case []byte:
					// Convert bytes to string for CLOB/VARCHAR2
					row[col] = string(v)
				case godror.Number:
					// Convert Oracle NUMBER to string (simplified for compatibility)
					row[col] = v.String()
				default:
					row[col] = val
				}
			} else {
				row[col] = nil
			}
		}
		resultRows = append(resultRows, row)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration error: %w", err)
	}

	queryTime := time.Since(startTime)

	result := &OracleQueryResult{
		Columns:   columns,
		Rows:      resultRows,
		RowCount:  len(resultRows),
		QueryTime: queryTime,
		Metadata: map[string]interface{}{
			"column_types": oc.buildColumnTypeInfo(columnTypes),
			"executed_at":  startTime,
			"query_id":     uuid.New().String(),
		},
	}

	oc.logger.Info("Oracle query completed",
		logging.F("rows_returned", len(resultRows)),
		logging.F("query_time", queryTime.String()),
	)

	return result, nil
}

// Execute executes an INSERT, UPDATE, DELETE, or DDL statement
func (oc *OracleConnector) Execute(ctx context.Context, query string, args ...interface{}) (*OracleExecutionResult, error) {
	if oc.db == nil {
		return nil, fmt.Errorf("not connected to Oracle database")
	}

	startTime := time.Now()

	oc.logger.Debug("Executing Oracle command",
		logging.F("query", query),
		logging.F("args", args),
	)

	ctx, cancel := context.WithTimeout(ctx, oc.config.CommandTimeout)
	defer cancel()

	result, err := oc.db.ExecContext(ctx, query, args...)
	executionTime := time.Since(startTime)

	if err != nil {
		return &OracleExecutionResult{
			Success:       false,
			ExecutionTime: executionTime,
			Message:       fmt.Sprintf("Execution failed: %v", err),
			ErrorCode:     -1,
			Metadata: map[string]interface{}{
				"executed_at": startTime,
				"query_id":    uuid.New().String(),
			},
		}, err
	}

	rowsAffected, _ := result.RowsAffected()
	lastInsertID, _ := result.LastInsertId()

	execResult := &OracleExecutionResult{
		Success:       true,
		RowsAffected:  rowsAffected,
		LastInsertID:  lastInsertID,
		ExecutionTime: executionTime,
		Message:       "Command executed successfully",
		Metadata: map[string]interface{}{
			"executed_at": startTime,
			"query_id":    uuid.New().String(),
		},
	}

	oc.logger.Info("Oracle command completed",
		logging.F("rows_affected", rowsAffected),
		logging.F("execution_time", executionTime.String()),
	)

	return execResult, nil
}

// GetTableInfo retrieves detailed table information
func (oc *OracleConnector) GetTableInfo(ctx context.Context, owner, tableName string) (*OracleTableInfo, error) {
	if oc.db == nil {
		return nil, fmt.Errorf("not connected to Oracle database")
	}

	tableInfo := &OracleTableInfo{
		TableName: tableName,
		Owner:     owner,
		Metadata:  make(map[string]interface{}),
	}

	// Get column information
	columns, err := oc.getTableColumns(ctx, owner, tableName)
	if err != nil {
		return nil, fmt.Errorf("failed to get table columns: %w", err)
	}
	tableInfo.Columns = columns

	// Get index information
	indexes, err := oc.getTableIndexes(ctx, owner, tableName)
	if err != nil {
		return nil, fmt.Errorf("failed to get table indexes: %w", err)
	}
	tableInfo.Indexes = indexes

	// Get constraint information
	constraints, err := oc.getTableConstraints(ctx, owner, tableName)
	if err != nil {
		return nil, fmt.Errorf("failed to get table constraints: %w", err)
	}
	tableInfo.Constraints = constraints

	// Get row count
	rowCount, err := oc.getTableRowCount(ctx, owner, tableName)
	if err != nil {
		oc.logger.Warn("Failed to get table row count", logging.F("error", err.Error()))
		rowCount = -1
	}
	tableInfo.RowCount = rowCount

	return tableInfo, nil
}

// getTableColumns retrieves column information for a table
func (oc *OracleConnector) getTableColumns(ctx context.Context, owner, tableName string) ([]OracleColumnInfo, error) {
	query := `
		SELECT column_name, data_type, data_length, data_precision, data_scale, 
		       nullable, data_default, column_id
		FROM all_tab_columns 
		WHERE owner = :1 AND table_name = :2 
		ORDER BY column_id
	`

	rows, err := oc.db.QueryContext(ctx, query, owner, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var columns []OracleColumnInfo
	for rows.Next() {
		var col OracleColumnInfo
		var dataDefault sql.NullString
		var dataPrecision, dataScale sql.NullInt64

		err := rows.Scan(&col.ColumnName, &col.DataType, &col.DataLength,
			&dataPrecision, &dataScale, &col.Nullable, &dataDefault, &col.ColumnID)
		if err != nil {
			return nil, err
		}

		if dataPrecision.Valid {
			precision := int(dataPrecision.Int64)
			col.DataPrecision = &precision
		}
		if dataScale.Valid {
			scale := int(dataScale.Int64)
			col.DataScale = &scale
		}
		if dataDefault.Valid {
			col.DefaultValue = &dataDefault.String
		}

		columns = append(columns, col)
	}

	return columns, nil
}

// getTableIndexes retrieves index information for a table
func (oc *OracleConnector) getTableIndexes(ctx context.Context, owner, tableName string) ([]OracleIndexInfo, error) {
	query := `
		SELECT DISTINCT i.index_name, i.index_type, i.uniqueness
		FROM all_indexes i
		WHERE i.owner = :1 AND i.table_name = :2
	`

	rows, err := oc.db.QueryContext(ctx, query, owner, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var indexes []OracleIndexInfo
	for rows.Next() {
		var idx OracleIndexInfo
		err := rows.Scan(&idx.IndexName, &idx.IndexType, &idx.Uniqueness)
		if err != nil {
			return nil, err
		}

		// Get index columns
		colQuery := `
			SELECT column_name 
			FROM all_ind_columns 
			WHERE index_owner = :1 AND index_name = :2 
			ORDER BY column_position
		`
		colRows, err := oc.db.QueryContext(ctx, colQuery, owner, idx.IndexName)
		if err != nil {
			continue
		}

		var columns []string
		for colRows.Next() {
			var colName string
			if err := colRows.Scan(&colName); err == nil {
				columns = append(columns, colName)
			}
		}
		colRows.Close()

		idx.Columns = columns
		indexes = append(indexes, idx)
	}

	return indexes, nil
}

// getTableConstraints retrieves constraint information for a table
func (oc *OracleConnector) getTableConstraints(ctx context.Context, owner, tableName string) ([]OracleConstraintInfo, error) {
	query := `
		SELECT constraint_name, constraint_type, r_owner, r_constraint_name
		FROM all_constraints 
		WHERE owner = :1 AND table_name = :2
	`

	rows, err := oc.db.QueryContext(ctx, query, owner, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var constraints []OracleConstraintInfo
	for rows.Next() {
		var constraint OracleConstraintInfo
		var rOwner, rConstraintName sql.NullString

		err := rows.Scan(&constraint.ConstraintName, &constraint.ConstraintType,
			&rOwner, &rConstraintName)
		if err != nil {
			return nil, err
		}

		// Get constraint columns
		colQuery := `
			SELECT column_name 
			FROM all_cons_columns 
			WHERE owner = :1 AND constraint_name = :2 
			ORDER BY position
		`
		colRows, err := oc.db.QueryContext(ctx, colQuery, owner, constraint.ConstraintName)
		if err != nil {
			continue
		}

		var columns []string
		for colRows.Next() {
			var colName string
			if err := colRows.Scan(&colName); err == nil {
				columns = append(columns, colName)
			}
		}
		colRows.Close()

		constraint.Columns = columns
		constraints = append(constraints, constraint)
	}

	return constraints, nil
}

// getTableRowCount gets approximate row count for a table
func (oc *OracleConnector) getTableRowCount(ctx context.Context, owner, tableName string) (int64, error) {
	query := `SELECT num_rows FROM all_tables WHERE owner = :1 AND table_name = :2`
	
	var count sql.NullInt64
	err := oc.db.QueryRowContext(ctx, query, owner, tableName).Scan(&count)
	if err != nil {
		return 0, err
	}

	if count.Valid {
		return count.Int64, nil
	}
	
	return 0, fmt.Errorf("table statistics not available")
}

// buildColumnTypeInfo builds column type information
func (oc *OracleConnector) buildColumnTypeInfo(columnTypes []*sql.ColumnType) []map[string]interface{} {
	var typeInfo []map[string]interface{}
	
	for _, ct := range columnTypes {
		info := map[string]interface{}{
			"name":     ct.Name(),
			"type":     ct.DatabaseTypeName(),
			"nullable": true,
		}

		if length, ok := ct.Length(); ok {
			info["length"] = length
		}
		if precision, scale, ok := ct.DecimalSize(); ok {
			info["precision"] = precision
			info["scale"] = scale
		}
		if nullable, ok := ct.Nullable(); ok {
			info["nullable"] = nullable
		}

		typeInfo = append(typeInfo, info)
	}

	return typeInfo
}

// TestConnection tests the Oracle connection
func (oc *OracleConnector) TestConnection(ctx context.Context) error {
	if oc.db == nil {
		return oc.Connect(ctx)
	}

	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	return oc.db.PingContext(ctx)
}

// GetVersion retrieves Oracle database version
func (oc *OracleConnector) GetVersion(ctx context.Context) (string, error) {
	if oc.db == nil {
		return "", fmt.Errorf("not connected to Oracle database")
	}

	var version string
	err := oc.db.QueryRowContext(ctx, "SELECT banner FROM v$version WHERE rownum = 1").Scan(&version)
	if err != nil {
		return "", fmt.Errorf("failed to get Oracle version: %w", err)
	}

	return version, nil
}

// Close closes the Oracle connection
func (oc *OracleConnector) Close() error {
	if oc.db != nil {
		err := oc.db.Close()
		oc.db = nil
		oc.logger.Info("Oracle connection closed")
		return err
	}
	return nil
}

// GetConnectionInfo returns connection information
func (oc *OracleConnector) GetConnectionInfo() map[string]interface{} {
	return map[string]interface{}{
		"host":            oc.config.Host,
		"port":            oc.config.Port,
		"service_name":    oc.config.ServiceName,
		"sid":             oc.config.SID,
		"username":        oc.config.Username,
		"connected":       oc.db != nil,
		"max_open_conns":  oc.config.MaxOpenConns,
		"max_idle_conns":  oc.config.MaxIdleConns,
		"fetch_array_size": oc.config.FetchArraySize,
		"charset":         oc.config.Charset,
		"timezone":        oc.config.Timezone,
	}
}