package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/go-ldap/ldap/v3"
)

// SingerMessage representa uma mensagem do protocolo Singer
type SingerMessage struct {
	Type   string                 `json:"type"`
	Record map[string]interface{} `json:"record,omitempty"`
	Schema map[string]interface{} `json:"schema,omitempty"`
	State  map[string]interface{} `json:"state,omitempty"`
	Stream string                 `json:"stream,omitempty"`
}

// LDAPConfig configuração para conexão LDAP
type LDAPConfig struct {
	Host       string `json:"host"`
	Port       int    `json:"port"`
	BindDN     string `json:"bind_dn"`
	BindPass   string `json:"bind_password"`
	BaseDN     string `json:"base_dn"`
	Filter     string `json:"filter"`
	Attributes []string `json:"attributes"`
	PageSize   int    `json:"page_size"`
	TLS        bool   `json:"tls"`
}

// LDAPTap implementa um tap Singer para LDAP
type LDAPTap struct {
	config *LDAPConfig
	conn   *ldap.Conn
}

// NewLDAPTap cria um novo tap LDAP
func NewLDAPTap(config *LDAPConfig) *LDAPTap {
	return &LDAPTap{
		config: config,
	}
}

// Connect conecta ao servidor LDAP
func (t *LDAPTap) Connect() error {
	var err error
	address := fmt.Sprintf("%s:%d", t.config.Host, t.config.Port)

	if t.config.TLS {
		t.conn, err = ldap.DialTLS("tcp", address, nil)
	} else {
		t.conn, err = ldap.Dial("tcp", address)
	}

	if err != nil {
		return fmt.Errorf("failed to connect to LDAP: %w", err)
	}

	// Autenticar se credenciais fornecidas
	if t.config.BindDN != "" {
		err = t.conn.Bind(t.config.BindDN, t.config.BindPass)
		if err != nil {
			return fmt.Errorf("failed to bind to LDAP: %w", err)
		}
	}

	return nil
}

// Discover emite o schema dos dados LDAP
func (t *LDAPTap) Discover() error {
	schema := map[string]interface{}{
		"type": "object",
		"properties": map[string]interface{}{
			"dn": map[string]interface{}{
				"type": "string",
				"description": "Distinguished Name",
			},
			"attributes": map[string]interface{}{
				"type": "object",
				"description": "LDAP attributes",
			},
			"extracted_at": map[string]interface{}{
				"type": "string",
				"format": "date-time",
				"description": "Extraction timestamp",
			},
		},
	}

	message := SingerMessage{
		Type:   "SCHEMA",
		Stream: "ldap_entries",
		Schema: schema,
	}

	return t.emitMessage(message)
}

// Sync extrai dados do LDAP e os emite como registros Singer
func (t *LDAPTap) Sync() error {
	// Configurar busca
	searchRequest := ldap.NewSearchRequest(
		t.config.BaseDN,
		ldap.ScopeWholeSubtree,
		ldap.NeverDerefAliases,
		0, // sem limite de tamanho
		0, // sem limite de tempo
		false,
		t.config.Filter,
		t.config.Attributes,
		nil,
	)

	// Executar busca paginada se configurado
	if t.config.PageSize > 0 {
		return t.syncPaged(searchRequest)
	}

	// Busca simples
	searchResult, err := t.conn.Search(searchRequest)
	if err != nil {
		return fmt.Errorf("LDAP search failed: %w", err)
	}

	// Processar entradas
	for _, entry := range searchResult.Entries {
		if err := t.emitEntry(entry); err != nil {
			return err
		}
	}

	return nil
}

// syncPaged executa busca paginada
func (t *LDAPTap) syncPaged(searchRequest *ldap.SearchRequest) error {
	pagingControl := ldap.NewControlPaging(uint32(t.config.PageSize))
	searchRequest.Controls = []ldap.Control{pagingControl}

	for {
		searchResult, err := t.conn.Search(searchRequest)
		if err != nil {
			return fmt.Errorf("LDAP paged search failed: %w", err)
		}

		// Processar entradas da página atual
		for _, entry := range searchResult.Entries {
			if err := t.emitEntry(entry); err != nil {
				return err
			}
		}

		// Verificar se há mais páginas
		updatedControls := ldap.FindControl(searchResult.Controls, ldap.ControlTypePaging)
		if updatedControls == nil {
			break
		}

		pagingResult := updatedControls.(*ldap.ControlPaging)
		if len(pagingResult.Cookie) == 0 {
			break
		}

		// Configurar próxima página
		pagingControl.SetCookie(pagingResult.Cookie)
	}

	return nil
}

// emitEntry emite uma entrada LDAP como registro Singer
func (t *LDAPTap) emitEntry(entry *ldap.Entry) error {
	// Construir mapa de atributos
	attributes := make(map[string]interface{})
	for _, attr := range entry.Attributes {
		if len(attr.Values) == 1 {
			attributes[attr.Name] = attr.Values[0]
		} else {
			attributes[attr.Name] = attr.Values
		}
	}

	// Criar registro
	record := map[string]interface{}{
		"dn":           entry.DN,
		"attributes":   attributes,
		"extracted_at": time.Now().UTC().Format(time.RFC3339),
	}

	message := SingerMessage{
		Type:   "RECORD",
		Stream: "ldap_entries",
		Record: record,
	}

	return t.emitMessage(message)
}

// emitMessage emite uma mensagem Singer para stdout
func (t *LDAPTap) emitMessage(message SingerMessage) error {
	data, err := json.Marshal(message)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	fmt.Println(string(data))
	return nil
}

// Close fecha a conexão LDAP
func (t *LDAPTap) Close() error {
	if t.conn != nil {
		t.conn.Close()
	}
	return nil
}

// TestConnection testa a conexão LDAP
func (t *LDAPTap) TestConnection() error {
	if err := t.Connect(); err != nil {
		return err
	}
	defer t.Close()

	// Teste simples: buscar apenas o base DN
	searchRequest := ldap.NewSearchRequest(
		t.config.BaseDN,
		ldap.ScopeBaseObject,
		ldap.NeverDerefAliases,
		1, // limite de 1 resultado
		5, // timeout de 5 segundos
		false,
		"(objectClass=*)",
		[]string{"dn"},
		nil,
	)

	_, err := t.conn.Search(searchRequest)
	return err
}

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Usage: tap-ldap [--discover|--test|--config config.json]")
	}

	switch os.Args[1] {
	case "--discover":
		// Para discovery, usar configuração padrão
		config := &LDAPConfig{}
		tap := NewLDAPTap(config)
		if err := tap.Discover(); err != nil {
			log.Fatal(err)
		}

	case "--test":
		if len(os.Args) < 4 || os.Args[2] != "--config" {
			log.Fatal("Usage: tap-ldap --test --config config.json")
		}

		configFile := os.Args[3]
		config, err := loadConfig(configFile)
		if err != nil {
			log.Fatal(err)
		}

		tap := NewLDAPTap(config)
		if err := tap.TestConnection(); err != nil {
			log.Fatal(err)
		}
		fmt.Println("Connection test successful")

	case "--config":
		if len(os.Args) < 3 {
			log.Fatal("Usage: tap-ldap --config config.json")
		}

		configFile := os.Args[2]
		config, err := loadConfig(configFile)
		if err != nil {
			log.Fatal(err)
		}

		tap := NewLDAPTap(config)
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
func loadConfig(filename string) (*LDAPConfig, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config LDAPConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	// Valores padrão
	if config.Port == 0 {
		if config.TLS {
			config.Port = 636
		} else {
			config.Port = 389
		}
	}
	if config.Filter == "" {
		config.Filter = "(objectClass=*)"
	}
	if config.PageSize == 0 {
		config.PageSize = 1000
	}

	return &config, nil
}
