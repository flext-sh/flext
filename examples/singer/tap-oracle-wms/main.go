package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	_ "github.com/godror/godror"
)

// SingerMessage representa uma mensagem do protocolo Singer
type SingerMessage struct {
	Type   string                 `json:"type"`
	Record map[string]interface{} `json:"record,omitempty"`
	Schema map[string]interface{} `json:"schema,omitempty"`
	State  map[string]interface{} `json:"state,omitempty"`
	Stream string                 `json:"stream,omitempty"`
}

// OracleWMSConfig configuração para conexão Oracle WMS
type OracleWMSConfig struct {
	Host           string   `json:"host"`
	Port           int      `json:"port"`
	ServiceName    string   `json:"service_name"`
	SID            string   `json:"sid,omitempty"`
	Username       string   `json:"username"`
	Password       string   `json:"password"`
	Schemas        []string `json:"schemas"`
	Tables         []string `json:"tables,omitempty"`
	BatchSize      int      `json:"batch_size"`
	MaxConnections int      `json:"max_connections"`
	Timeout        int      `json:"timeout_seconds"`
	TLS            bool     `json:"tls"`
}

// TableInfo informações sobre uma tabela
type TableInfo struct {
	Schema      string
	Name        string
	Columns     []ColumnInfo
	PrimaryKeys []string
	RowCount    int64
}

// ColumnInfo informações sobre uma coluna
type ColumnInfo struct {
	Name     string
	Type     string
	Nullable bool
	Default  *string
}

// OracleWMSTap implementa um tap Singer para Oracle WMS
type OracleWMSTap struct {
	config *OracleWMSConfig
	db     *sql.DB
	tables []TableInfo
}

// NewOracleWMSTap cria um novo tap Oracle WMS
func NewOracleWMSTap(config *OracleWMSConfig) *OracleWMSTap {
	return &OracleWMSTap{
		config: config,
	}
}

// Connect conecta ao banco Oracle
func (t *OracleWMSTap) Connect() error {
	// Construir string de conexão Oracle
	connStr := t.buildConnectionString()

	var err error
	t.db, err = sql.Open("godror", connStr)
	if err != nil {
		return fmt.Errorf("failed to connect to Oracle: %w", err)
	}

	// Configurar pool de conexões
	t.db.SetMaxOpenConns(t.config.MaxConnections)
	t.db.SetMaxIdleConns(t.config.MaxConnections / 2)
	t.db.SetConnMaxLifetime(time.Hour)

	// Testar conexão
	ctx, cancel := t.getTimeoutContext()
	defer cancel()
	if err := t.db.PingContext(ctx); err != nil {
		return fmt.Errorf("failed to ping Oracle database: %w", err)
	}

	return nil
}

// buildConnectionString constrói a string de conexão Oracle
func (t *OracleWMSTap) buildConnectionString() string {
	var connStr strings.Builder

	// User credentials
	connStr.WriteString(fmt.Sprintf("%s/%s@", t.config.Username, t.config.Password))

	// Connection descriptor
	if t.config.SID != "" {
		// SID format
		connStr.WriteString(fmt.Sprintf("%s:%d:%s", t.config.Host, t.config.Port, t.config.SID))
	} else {
		// Service name format
		connStr.WriteString(fmt.Sprintf("%s:%d/%s", t.config.Host, t.config.Port, t.config.ServiceName))
	}

	// TLS/SSL options
	if t.config.TLS {
		connStr.WriteString("?ssl=true")
	}

	return connStr.String()
}

// getTimeoutContext cria um context com timeout
func (t *OracleWMSTap) getTimeoutContext() (context.Context, context.CancelFunc) {
	timeout := time.Duration(t.config.Timeout) * time.Second
	return context.WithTimeout(context.Background(), timeout)
}

// Discover emite o schema das tabelas Oracle WMS
func (t *OracleWMSTap) Discover() error {
	if err := t.loadTableMetadata(); err != nil {
		return fmt.Errorf("failed to load table metadata: %w", err)
	}

	// Emitir schema para cada tabela
	for _, table := range t.tables {
		schema := t.buildTableSchema(table)
		streamName := fmt.Sprintf("%s.%s", strings.ToLower(table.Schema), strings.ToLower(table.Name))

		message := SingerMessage{
			Type:   "SCHEMA",
			Stream: streamName,
			Schema: schema,
		}

		if err := t.emitMessage(message); err != nil {
			return err
		}
	}

	return nil
}

// loadTableMetadata carrega metadados das tabelas
func (t *OracleWMSTap) loadTableMetadata() error {
	ctx, cancel := t.getTimeoutContext()
	defer cancel()

	// Query para obter informações das tabelas
	query := `
		SELECT 
			t.owner,
			t.table_name,
			c.column_name,
			c.data_type,
			c.nullable,
			c.data_default,
			CASE WHEN pk.column_name IS NOT NULL THEN 'Y' ELSE 'N' END as is_primary_key
		FROM all_tables t
		JOIN all_tab_columns c ON t.owner = c.owner AND t.table_name = c.table_name
		LEFT JOIN (
			SELECT cc.owner, cc.table_name, cc.column_name
			FROM all_cons_columns cc
			JOIN all_constraints con ON cc.owner = con.owner 
				AND cc.constraint_name = con.constraint_name
			WHERE con.constraint_type = 'P'
		) pk ON c.owner = pk.owner AND c.table_name = pk.table_name AND c.column_name = pk.column_name
		WHERE t.owner IN (` + t.buildSchemaList() + `)
		` + t.buildTableFilter() + `
		ORDER BY t.owner, t.table_name, c.column_id
	`

	rows, err := t.db.QueryContext(ctx, query)
	if err != nil {
		return fmt.Errorf("failed to query table metadata: %w", err)
	}
	defer rows.Close()

	// Processar resultados
	tableMap := make(map[string]*TableInfo)

	for rows.Next() {
		var schema, tableName, columnName, dataType, nullable, isPK string
		var dataDefault sql.NullString

		err := rows.Scan(&schema, &tableName, &columnName, &dataType, &nullable, &dataDefault, &isPK)
		if err != nil {
			return fmt.Errorf("failed to scan row: %w", err)
		}

		tableKey := fmt.Sprintf("%s.%s", schema, tableName)
		table, exists := tableMap[tableKey]
		if !exists {
			table = &TableInfo{
				Schema:      schema,
				Name:        tableName,
				Columns:     []ColumnInfo{},
				PrimaryKeys: []string{},
			}
			tableMap[tableKey] = table
		}

		// Adicionar coluna
		column := ColumnInfo{
			Name:     columnName,
			Type:     dataType,
			Nullable: nullable == "Y",
		}
		if dataDefault.Valid {
			column.Default = &dataDefault.String
		}
		table.Columns = append(table.Columns, column)

		// Adicionar chave primária
		if isPK == "Y" {
			table.PrimaryKeys = append(table.PrimaryKeys, columnName)
		}
	}

	// Converter mapa para slice
	t.tables = make([]TableInfo, 0, len(tableMap))
	for _, table := range tableMap {
		// Obter contagem de linhas
		table.RowCount = t.getTableRowCount(table.Schema, table.Name)
		t.tables = append(t.tables, *table)
	}

	return nil
}

// buildSchemaList constrói lista de schemas para a query
func (t *OracleWMSTap) buildSchemaList() string {
	schemas := make([]string, len(t.config.Schemas))
	for i, schema := range t.config.Schemas {
		schemas[i] = fmt.Sprintf("'%s'", strings.ToUpper(schema))
	}
	return strings.Join(schemas, ", ")
}

// buildTableFilter constrói filtro de tabelas
func (t *OracleWMSTap) buildTableFilter() string {
	if len(t.config.Tables) == 0 {
		return ""
	}

	tables := make([]string, len(t.config.Tables))
	for i, table := range t.config.Tables {
		tables[i] = fmt.Sprintf("'%s'", strings.ToUpper(table))
	}

	return fmt.Sprintf("AND t.table_name IN (%s)", strings.Join(tables, ", "))
}

// getTableRowCount obtém contagem de linhas de uma tabela
func (t *OracleWMSTap) getTableRowCount(schema, table string) int64 {
	ctx, cancel := t.getTimeoutContext()
	defer cancel()
	query := fmt.Sprintf("SELECT COUNT(*) FROM %s.%s", schema, table)

	var count int64
	err := t.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		// Se falhar, retornar 0
		return 0
	}

	return count
}

// buildTableSchema constrói schema Singer para uma tabela
func (t *OracleWMSTap) buildTableSchema(table TableInfo) map[string]interface{} {
	properties := make(map[string]interface{})

	// Adicionar colunas
	for _, column := range table.Columns {
		columnSchema := map[string]interface{}{
			"type": t.mapOracleTypeToSinger(column.Type),
		}

		if !column.Nullable {
			columnSchema["required"] = true
		}

		if column.Default != nil {
			columnSchema["default"] = *column.Default
		}

		properties[strings.ToLower(column.Name)] = columnSchema
	}

	// Adicionar metadados
	properties["_extracted_at"] = map[string]interface{}{
		"type":        "string",
		"format":      "date-time",
		"description": "Data extraction timestamp",
	}

	schema := map[string]interface{}{
		"type":       "object",
		"properties": properties,
		"description": fmt.Sprintf("Oracle WMS table %s.%s with %d rows", table.Schema, table.Name, table.RowCount),
	}

	// Adicionar informações de chave primária
	if len(table.PrimaryKeys) > 0 {
		primaryKeys := make([]string, len(table.PrimaryKeys))
		for i, pk := range table.PrimaryKeys {
			primaryKeys[i] = strings.ToLower(pk)
		}
		schema["key_properties"] = primaryKeys
	}

	return schema
}

// mapOracleTypeToSinger mapeia tipos Oracle para tipos Singer
func (t *OracleWMSTap) mapOracleTypeToSinger(oracleType string) string {
	oracleType = strings.ToUpper(oracleType)

	switch {
	case strings.Contains(oracleType, "VARCHAR"), strings.Contains(oracleType, "CHAR"), strings.Contains(oracleType, "CLOB"):
		return "string"
	case strings.Contains(oracleType, "NUMBER"), strings.Contains(oracleType, "DECIMAL"):
		return "number"
	case strings.Contains(oracleType, "INTEGER"), strings.Contains(oracleType, "INT"):
		return "integer"
	case strings.Contains(oracleType, "DATE"), strings.Contains(oracleType, "TIMESTAMP"):
		return "string" // Singer represents dates as strings
	case strings.Contains(oracleType, "BLOB"), strings.Contains(oracleType, "RAW"):
		return "string" // Binary data as base64 string
	default:
		return "string" // Default to string for unknown types
	}
}

// Sync extrai dados das tabelas Oracle WMS
func (t *OracleWMSTap) Sync() error {
	if err := t.loadTableMetadata(); err != nil {
		return fmt.Errorf("failed to load table metadata: %w", err)
	}

	// Processar cada tabela
	for _, table := range t.tables {
		if err := t.syncTable(table); err != nil {
			return fmt.Errorf("failed to sync table %s.%s: %w", table.Schema, table.Name, err)
		}
	}

	return nil
}

// syncTable extrai dados de uma tabela específica
func (t *OracleWMSTap) syncTable(table TableInfo) error {
	streamName := fmt.Sprintf("%s.%s", strings.ToLower(table.Schema), strings.ToLower(table.Name))

	// Construir query SELECT
	columns := make([]string, len(table.Columns))
	for i, column := range table.Columns {
		columns[i] = column.Name
	}

	query := fmt.Sprintf("SELECT %s FROM %s.%s", strings.Join(columns, ", "), table.Schema, table.Name)

	// Executar query com processamento em lotes
	return t.executeBatchQuery(query, streamName, table.Columns)
}

// executeBatchQuery executa query em lotes
func (t *OracleWMSTap) executeBatchQuery(query, streamName string, columns []ColumnInfo) error {
	ctx, cancel := t.getTimeoutContext()
	defer cancel()

	rows, err := t.db.QueryContext(ctx, query)
	if err != nil {
		return fmt.Errorf("failed to execute query: %w", err)
	}
	defer rows.Close()

	// Preparar buffers para scan
	values := make([]interface{}, len(columns))
	scriptValues := make([]sql.NullString, len(columns))
	for i := range values {
		values[i] = &scriptValues[i]
	}

	batchCount := 0
	for rows.Next() {
		// Scan row
		err := rows.Scan(values...)
		if err != nil {
			return fmt.Errorf("failed to scan row: %w", err)
		}

		// Construir record
		record := make(map[string]interface{})
		for i, column := range columns {
			columnName := strings.ToLower(column.Name)
			if scriptValues[i].Valid {
				// Converter valor baseado no tipo
				record[columnName] = t.convertValue(scriptValues[i].String, column.Type)
			} else {
				record[columnName] = nil
			}
		}

		// Adicionar timestamp de extração
		record["_extracted_at"] = time.Now().UTC().Format(time.RFC3339)

		// Emitir record
		message := SingerMessage{
			Type:   "RECORD",
			Stream: streamName,
			Record: record,
		}

		if err := t.emitMessage(message); err != nil {
			return err
		}

		batchCount++
		if batchCount%t.config.BatchSize == 0 {
			// Log progress for large tables
			log.Printf("Processed %d records from %s", batchCount, streamName)
		}
	}

	return rows.Err()
}

// convertValue converte valor baseado no tipo Oracle
func (t *OracleWMSTap) convertValue(value, oracleType string) interface{} {
	oracleType = strings.ToUpper(oracleType)

	switch {
	case strings.Contains(oracleType, "NUMBER"), strings.Contains(oracleType, "DECIMAL"):
		if strings.Contains(value, ".") {
			if f, err := strconv.ParseFloat(value, 64); err == nil {
				return f
			}
		} else {
			if i, err := strconv.ParseInt(value, 10, 64); err == nil {
				return i
			}
		}
	case strings.Contains(oracleType, "INTEGER"), strings.Contains(oracleType, "INT"):
		if i, err := strconv.ParseInt(value, 10, 64); err == nil {
			return i
		}
	}

	// Default: return as string
	return value
}

// emitMessage emite uma mensagem Singer para stdout
func (t *OracleWMSTap) emitMessage(message SingerMessage) error {
	data, err := json.Marshal(message)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	fmt.Println(string(data))
	return nil
}

// Close fecha a conexão com o banco
func (t *OracleWMSTap) Close() error {
	if t.db != nil {
		return t.db.Close()
	}
	return nil
}

// TestConnection testa a conexão Oracle
func (t *OracleWMSTap) TestConnection() error {
	if err := t.Connect(); err != nil {
		return err
	}
	defer t.Close()

	// Teste simples: consultar versão do Oracle
	ctx, cancel := t.getTimeoutContext()
	defer cancel()
	var version string
	err := t.db.QueryRowContext(ctx, "SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1").Scan(&version)
	if err != nil {
		return fmt.Errorf("failed to query Oracle version: %w", err)
	}

	log.Printf("Connected to Oracle: %s", version)
	return nil
}

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Usage: tap-oracle-wms [--discover|--test|--config config.json]")
	}

	switch os.Args[1] {
	case "--discover":
		if len(os.Args) < 4 || os.Args[2] != "--config" {
			log.Fatal("Usage: tap-oracle-wms --discover --config config.json")
		}

		configFile := os.Args[3]
		config, err := loadConfig(configFile)
		if err != nil {
			log.Fatal(err)
		}

		tap := NewOracleWMSTap(config)
		if err := tap.Connect(); err != nil {
			log.Fatal(err)
		}
		defer tap.Close()

		if err := tap.Discover(); err != nil {
			log.Fatal(err)
		}

	case "--test":
		if len(os.Args) < 4 || os.Args[2] != "--config" {
			log.Fatal("Usage: tap-oracle-wms --test --config config.json")
		}

		configFile := os.Args[3]
		config, err := loadConfig(configFile)
		if err != nil {
			log.Fatal(err)
		}

		tap := NewOracleWMSTap(config)
		if err := tap.TestConnection(); err != nil {
			log.Fatal(err)
		}
		fmt.Println("Connection test successful")

	case "--config":
		if len(os.Args) < 3 {
			log.Fatal("Usage: tap-oracle-wms --config config.json")
		}

		configFile := os.Args[2]
		config, err := loadConfig(configFile)
		if err != nil {
			log.Fatal(err)
		}

		tap := NewOracleWMSTap(config)
		if err := tap.Connect(); err != nil {
			log.Fatal(err)
		}
		defer tap.Close()

		if err := tap.Sync(); err != nil {
			log.Fatal(err)
		}

	default:
		log.Fatal("Unknown command. Use --discover, --test, or --config")
	}
}

// loadConfig carrega configuração do arquivo JSON
func loadConfig(filename string) (*OracleWMSConfig, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config OracleWMSConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	// Valores padrão
	if config.Port == 0 {
		config.Port = 1521
	}
	if config.BatchSize == 0 {
		config.BatchSize = 1000
	}
	if config.MaxConnections == 0 {
		config.MaxConnections = 10
	}
	if config.Timeout == 0 {
		config.Timeout = 30
	}

	return &config, nil
}
