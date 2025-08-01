package connectors

import (
	"context"
	"crypto/tls"
	"fmt"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/go-ldap/ldap/v3"
	"github.com/google/uuid"
)

// LDAPConnector provides real LDAP connectivity
type LDAPConnector struct {
	config *LDAPConfig
	conn   *ldap.Conn
	logger logging.Logger
}

// LDAPConfig holds LDAP connection configuration
type LDAPConfig struct {
	Host              string        `json:"host"`
	Port              int           `json:"port"`
	UseSSL            bool          `json:"use_ssl"`
	UseTLS            bool          `json:"use_tls"`
	SkipTLSVerify     bool          `json:"skip_tls_verify"`
	BindDN            string        `json:"bind_dn"`
	BindPassword      string        `json:"bind_password"`
	BaseDN            string        `json:"base_dn"`
	SearchFilter      string        `json:"search_filter"`
	Attributes        []string      `json:"attributes"`
	TimeLimit         int           `json:"time_limit"`
	SizeLimit         int           `json:"size_limit"`
	ConnectionTimeout time.Duration `json:"connection_timeout"`
	ReadTimeout       time.Duration `json:"read_timeout"`
	WriteTimeout      time.Duration `json:"write_timeout"`
}

// LDAPEntry represents an LDAP directory entry
type LDAPEntry struct {
	DN         string                 `json:"dn"`
	Attributes map[string][]string    `json:"attributes"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// LDAPSearchResult represents the result of an LDAP search
type LDAPSearchResult struct {
	Entries    []*LDAPEntry `json:"entries"`
	TotalCount int          `json:"total_count"`
	PageSize   int          `json:"page_size"`
	PageToken  string       `json:"page_token,omitempty"`
}

// LDAPOperationResult represents the result of an LDAP operation
type LDAPOperationResult struct {
	Success   bool                   `json:"success"`
	Message   string                 `json:"message"`
	ErrorCode int                    `json:"error_code,omitempty"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// NewLDAPConnector creates a new LDAP connector
func NewLDAPConnector(config *LDAPConfig, logger logging.Logger) (*LDAPConnector, error) {
	if config == nil {
		return nil, fmt.Errorf("LDAP config cannot be nil")
	}

	// Set defaults
	if config.Port == 0 {
		if config.UseSSL {
			config.Port = 636
		} else {
			config.Port = 389
		}
	}
	if config.TimeLimit == 0 {
		config.TimeLimit = 30
	}
	if config.SizeLimit == 0 {
		config.SizeLimit = 1000
	}
	if config.ConnectionTimeout == 0 {
		config.ConnectionTimeout = 10 * time.Second
	}

	connector := &LDAPConnector{
		config: config,
		logger: logger,
	}

	return connector, nil
}

// Connect establishes connection to LDAP server
func (lc *LDAPConnector) Connect(ctx context.Context) error {
	address := fmt.Sprintf("%s:%d", lc.config.Host, lc.config.Port)

	lc.logger.Info("Connecting to LDAP server",
		logging.F("address", address),
		logging.F("use_ssl", lc.config.UseSSL),
		logging.F("use_tls", lc.config.UseTLS),
	)

	conn, err := lc.establishConnection(address)
	if err != nil {
		return err
	}

	if err := lc.configureConnection(conn); err != nil {
		conn.Close()
		return err
	}

	lc.conn = conn
	lc.logger.Info("Successfully connected to LDAP server")
	return nil
}

// establishConnection creates the initial LDAP connection
func (lc *LDAPConnector) establishConnection(address string) (*ldap.Conn, error) {
	if lc.config.UseSSL {
		return lc.dialSSLConnection(address)
	}
	return ldap.Dial("tcp", address)
}

// dialSSLConnection creates an SSL connection
func (lc *LDAPConnector) dialSSLConnection(address string) (*ldap.Conn, error) {
	tlsConfig := &tls.Config{
		InsecureSkipVerify: lc.config.SkipTLSVerify,
	}
	conn, err := ldap.DialTLS("tcp", address, tlsConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to LDAP server: %w", err)
	}
	return conn, nil
}

// configureConnection configures TLS and authentication for the connection
func (lc *LDAPConnector) configureConnection(conn *ldap.Conn) error {
	if err := lc.configureTLS(conn); err != nil {
		return err
	}
	return lc.authenticate(conn)
}

// configureTLS configures StartTLS if needed
func (lc *LDAPConnector) configureTLS(conn *ldap.Conn) error {
	if !lc.config.UseSSL && lc.config.UseTLS {
		tlsConfig := &tls.Config{
			InsecureSkipVerify: lc.config.SkipTLSVerify,
		}
		if err := conn.StartTLS(tlsConfig); err != nil {
			return fmt.Errorf("failed to start TLS: %w", err)
		}
	}
	return nil
}

// authenticate performs LDAP bind if credentials are provided
func (lc *LDAPConnector) authenticate(conn *ldap.Conn) error {
	if lc.config.BindDN != "" {
		if err := conn.Bind(lc.config.BindDN, lc.config.BindPassword); err != nil {
			return fmt.Errorf("failed to bind to LDAP: %w", err)
		}
	}
	return nil
}

// Search performs LDAP search operation
func (lc *LDAPConnector) Search(ctx context.Context, baseDN, filter string, attributes []string) (*LDAPSearchResult, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	searchParams := lc.prepareSearchParameters(baseDN, filter, attributes)
	searchRequest := lc.buildSearchRequest(searchParams)

	lc.logSearchOperation(searchParams)

	result, err := lc.conn.Search(searchRequest)
	if err != nil {
		return nil, fmt.Errorf("LDAP search failed: %w", err)
	}

	return lc.buildSearchResult(result, searchParams), nil
}

// SearchParameters holds normalized search parameters
type SearchParameters struct {
	BaseDN     string
	Filter     string
	Attributes []string
	SizeLimit  int
	TimeLimit  int
}

// prepareSearchParameters normalizes and validates search parameters
func (lc *LDAPConnector) prepareSearchParameters(baseDN, filter string, attributes []string) *SearchParameters {
	if baseDN == "" {
		baseDN = lc.config.BaseDN
	}
	if filter == "" {
		filter = lc.config.SearchFilter
		if filter == "" {
			filter = "(objectClass=*)"
		}
	}
	if len(attributes) == 0 {
		attributes = lc.config.Attributes
	}

	return &SearchParameters{
		BaseDN:     baseDN,
		Filter:     filter,
		Attributes: attributes,
		SizeLimit:  lc.config.SizeLimit,
		TimeLimit:  lc.config.TimeLimit,
	}
}

// buildSearchRequest creates an LDAP search request
func (lc *LDAPConnector) buildSearchRequest(params *SearchParameters) *ldap.SearchRequest {
	return ldap.NewSearchRequest(
		params.BaseDN,
		ldap.ScopeWholeSubtree,
		ldap.NeverDerefAliases,
		params.SizeLimit,
		params.TimeLimit,
		false,
		params.Filter,
		params.Attributes,
		nil,
	)
}

// logSearchOperation logs the search operation details
func (lc *LDAPConnector) logSearchOperation(params *SearchParameters) {
	lc.logger.Debug("Performing LDAP search",
		logging.F("base_dn", params.BaseDN),
		logging.F("filter", params.Filter),
		logging.F("attributes", params.Attributes),
	)
}

// buildSearchResult converts LDAP result to our format
func (lc *LDAPConnector) buildSearchResult(result *ldap.SearchResult, params *SearchParameters) *LDAPSearchResult {
	entries := lc.convertEntries(result.Entries)

	lc.logger.Info("LDAP search completed",
		logging.F("entries_found", len(entries)),
		logging.F("filter", params.Filter),
	)

	return &LDAPSearchResult{
		Entries:    entries,
		TotalCount: len(entries),
		PageSize:   params.SizeLimit,
	}
}

// convertEntries converts LDAP entries to our format
func (lc *LDAPConnector) convertEntries(ldapEntries []*ldap.Entry) []*LDAPEntry {
	entries := make([]*LDAPEntry, len(ldapEntries))
	for i, entry := range ldapEntries {
		entries[i] = lc.convertSingleEntry(entry)
	}
	return entries
}

// convertSingleEntry converts a single LDAP entry to our format
func (lc *LDAPConnector) convertSingleEntry(entry *ldap.Entry) *LDAPEntry {
	attrs := make(map[string][]string)
	for _, attr := range entry.Attributes {
		attrs[attr.Name] = attr.Values
	}

	return &LDAPEntry{
		DN:         entry.DN,
		Attributes: attrs,
		Metadata: map[string]interface{}{
			"search_time": time.Now(),
			"entry_id":    uuid.New().String(),
		},
	}
}

// Add creates a new LDAP entry
func (lc *LDAPConnector) Add(ctx context.Context, dn string, attributes map[string][]string) (*LDAPOperationResult, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	addRequest := ldap.NewAddRequest(dn, nil)

	for attr, values := range attributes {
		addRequest.Attribute(attr, values)
	}

	lc.logger.Debug("Adding LDAP entry",
		logging.F("dn", dn),
		logging.F("attributes", len(attributes)),
	)

	err := lc.conn.Add(addRequest)
	if err != nil {
		return &LDAPOperationResult{
			Success:   false,
			Message:   fmt.Sprintf("Failed to add entry: %v", err),
			ErrorCode: ldap.LDAPResultOperationsError,
		}, err
	}

	lc.logger.Info("LDAP entry added successfully", logging.F("dn", dn))

	return &LDAPOperationResult{
		Success: true,
		Message: "Entry added successfully",
		Metadata: map[string]interface{}{
			"dn":         dn,
			"added_at":   time.Now(),
			"attr_count": len(attributes),
		},
	}, nil
}

// Modify updates an existing LDAP entry
func (lc *LDAPConnector) Modify(ctx context.Context, dn string, modifications map[string][]string) (*LDAPOperationResult, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	modifyRequest := ldap.NewModifyRequest(dn, nil)

	for attr, values := range modifications {
		modifyRequest.Replace(attr, values)
	}

	lc.logger.Debug("Modifying LDAP entry",
		logging.F("dn", dn),
		logging.F("modifications", len(modifications)),
	)

	err := lc.conn.Modify(modifyRequest)
	if err != nil {
		return &LDAPOperationResult{
			Success:   false,
			Message:   fmt.Sprintf("Failed to modify entry: %v", err),
			ErrorCode: ldap.LDAPResultOperationsError,
		}, err
	}

	lc.logger.Info("LDAP entry modified successfully", logging.F("dn", dn))

	return &LDAPOperationResult{
		Success: true,
		Message: "Entry modified successfully",
		Metadata: map[string]interface{}{
			"dn":          dn,
			"modified_at": time.Now(),
			"mod_count":   len(modifications),
		},
	}, nil
}

// Delete removes an LDAP entry
func (lc *LDAPConnector) Delete(ctx context.Context, dn string) (*LDAPOperationResult, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	deleteRequest := ldap.NewDelRequest(dn, nil)

	lc.logger.Debug("Deleting LDAP entry", logging.F("dn", dn))

	err := lc.conn.Del(deleteRequest)
	if err != nil {
		return &LDAPOperationResult{
			Success:   false,
			Message:   fmt.Sprintf("Failed to delete entry: %v", err),
			ErrorCode: ldap.LDAPResultOperationsError,
		}, err
	}

	lc.logger.Info("LDAP entry deleted successfully", logging.F("dn", dn))

	return &LDAPOperationResult{
		Success: true,
		Message: "Entry deleted successfully",
		Metadata: map[string]interface{}{
			"dn":         dn,
			"deleted_at": time.Now(),
		},
	}, nil
}

// PagedSearch performs paginated LDAP search
func (lc *LDAPConnector) PagedSearch(ctx context.Context, baseDN, filter string, attributes []string, pageSize int, cookie []byte) (*LDAPSearchResult, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	pagedParams := lc.preparePagedSearchParameters(baseDN, filter, attributes, pageSize)
	searchRequest := lc.buildPagedSearchRequest(pagedParams)

	result, err := lc.conn.SearchWithPaging(searchRequest, uint32(pagedParams.PageSize))
	if err != nil {
		return nil, fmt.Errorf("paged LDAP search failed: %w", err)
	}

	return lc.buildPagedSearchResult(result, pagedParams), nil
}

// PagedSearchParameters holds parameters for paged search
type PagedSearchParameters struct {
	*SearchParameters
	PageSize int
}

// preparePagedSearchParameters normalizes parameters for paged search
func (lc *LDAPConnector) preparePagedSearchParameters(baseDN, filter string, attributes []string, pageSize int) *PagedSearchParameters {
	baseParams := lc.prepareSearchParameters(baseDN, filter, attributes)

	if pageSize <= 0 {
		pageSize = 100
	}

	return &PagedSearchParameters{
		SearchParameters: baseParams,
		PageSize:         pageSize,
	}
}

// buildPagedSearchRequest creates a paged search request
func (lc *LDAPConnector) buildPagedSearchRequest(params *PagedSearchParameters) *ldap.SearchRequest {
	return ldap.NewSearchRequest(
		params.BaseDN,
		ldap.ScopeWholeSubtree,
		ldap.NeverDerefAliases,
		0, // No size limit for paged search
		params.TimeLimit,
		false,
		params.Filter,
		params.Attributes,
		[]ldap.Control{ldap.NewControlPaging(uint32(params.PageSize))},
	)
}

// buildPagedSearchResult builds the result for paged search
func (lc *LDAPConnector) buildPagedSearchResult(result *ldap.SearchResult, params *PagedSearchParameters) *LDAPSearchResult {
	entries := lc.convertPagedEntries(result.Entries, params.PageSize)

	return &LDAPSearchResult{
		Entries:    entries,
		TotalCount: len(entries),
		PageSize:   params.PageSize,
	}
}

// convertPagedEntries converts entries for paged search with additional metadata
func (lc *LDAPConnector) convertPagedEntries(ldapEntries []*ldap.Entry, pageSize int) []*LDAPEntry {
	entries := make([]*LDAPEntry, len(ldapEntries))
	for i, entry := range ldapEntries {
		entries[i] = lc.convertPagedEntry(entry, pageSize)
	}
	return entries
}

// convertPagedEntry converts a single entry for paged search
func (lc *LDAPConnector) convertPagedEntry(entry *ldap.Entry, pageSize int) *LDAPEntry {
	attrs := make(map[string][]string)
	for _, attr := range entry.Attributes {
		attrs[attr.Name] = attr.Values
	}

	return &LDAPEntry{
		DN:         entry.DN,
		Attributes: attrs,
		Metadata: map[string]interface{}{
			"search_time": time.Now(),
			"entry_id":    uuid.New().String(),
			"page_size":   pageSize,
		},
	}
}

// TestConnection tests the LDAP connection
func (lc *LDAPConnector) TestConnection(ctx context.Context) error {
	if lc.conn == nil {
		return lc.Connect(ctx)
	}

	// Test with a simple search
	searchRequest := ldap.NewSearchRequest(
		"",
		ldap.ScopeBaseObject,
		ldap.NeverDerefAliases,
		1,
		5,
		false,
		"(objectClass=*)",
		[]string{"1.1"}, // No attributes
		nil,
	)

	_, err := lc.conn.Search(searchRequest)
	if err != nil {
		return fmt.Errorf("connection test failed: %w", err)
	}

	return nil
}

// GetSchema retrieves LDAP schema information
func (lc *LDAPConnector) GetSchema(ctx context.Context) (map[string]interface{}, error) {
	if lc.conn == nil {
		return nil, fmt.Errorf("not connected to LDAP server")
	}

	// Search for schema
	searchRequest := ldap.NewSearchRequest(
		"cn=schema",
		ldap.ScopeBaseObject,
		ldap.NeverDerefAliases,
		1,
		30,
		false,
		"(objectClass=*)",
		[]string{"objectClasses", "attributeTypes", "ldapSyntaxes"},
		nil,
	)

	result, err := lc.conn.Search(searchRequest)
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve schema: %w", err)
	}

	schema := make(map[string]interface{})
	if len(result.Entries) > 0 {
		entry := result.Entries[0]
		for _, attr := range entry.Attributes {
			schema[attr.Name] = attr.Values
		}
	}

	return schema, nil
}

// Close closes the LDAP connection
func (lc *LDAPConnector) Close() error {
	if lc.conn != nil {
		lc.conn.Close()
		lc.conn = nil
		lc.logger.Info("LDAP connection closed")
	}
	return nil
}

// GetConnectionInfo returns connection information
func (lc *LDAPConnector) GetConnectionInfo() map[string]interface{} {
	return map[string]interface{}{
		"host":       lc.config.Host,
		"port":       lc.config.Port,
		"use_ssl":    lc.config.UseSSL,
		"use_tls":    lc.config.UseTLS,
		"base_dn":    lc.config.BaseDN,
		"connected":  lc.conn != nil,
		"bind_dn":    lc.config.BindDN,
		"time_limit": lc.config.TimeLimit,
		"size_limit": lc.config.SizeLimit,
	}
}
