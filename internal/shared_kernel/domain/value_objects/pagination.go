package value_objects

import (
	"fmt"
	"strconv"
)

// Pagination representa os parâmetros de paginação
type Pagination struct {
	Page     int   `json:"page" validate:"min=1"`
	PageSize int   `json:"page_size" validate:"min=1,max=100"`
	Total    int64 `json:"total"`
	Pages    int   `json:"pages"`
}

// NewPagination cria uma nova instância de paginação
func NewPagination(page, pageSize int) *Pagination {
	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 10
	}
	if pageSize > 100 {
		pageSize = 100
	}

	return &Pagination{
		Page:     page,
		PageSize: pageSize,
	}
}

// ParsePagination cria paginação a partir de parâmetros de string
func ParsePagination(pageStr, pageSizeStr string) *Pagination {
	page, _ := strconv.Atoi(pageStr)
	pageSize, _ := strconv.Atoi(pageSizeStr)
	return NewPagination(page, pageSize)
}

// SetTotal define o total de itens e calcula o número de páginas
func (p *Pagination) SetTotal(total int64) {
	p.Total = total
	if total == 0 {
		p.Pages = 0
		return
	}

	p.Pages = int((total + int64(p.PageSize) - 1) / int64(p.PageSize))
}

// Offset calcula o offset para queries de banco
func (p *Pagination) Offset() int {
	return (p.Page - 1) * p.PageSize
}

// Limit retorna o limite para queries de banco
func (p *Pagination) Limit() int {
	return p.PageSize
}

// HasNext verifica se há próxima página
func (p *Pagination) HasNext() bool {
	return p.Page < p.Pages
}

// HasPrev verifica se há página anterior
func (p *Pagination) HasPrev() bool {
	return p.Page > 1
}

// NextPage retorna o número da próxima página
func (p *Pagination) NextPage() int {
	if p.HasNext() {
		return p.Page + 1
	}
	return p.Page
}

// PrevPage retorna o número da página anterior
func (p *Pagination) PrevPage() int {
	if p.HasPrev() {
		return p.Page - 1
	}
	return p.Page
}

// Validate valida os valores de paginação
func (p *Pagination) Validate() error {
	if p.Page < 1 {
		return fmt.Errorf("page must be greater than 0")
	}
	if p.PageSize < 1 {
		return fmt.Errorf("page_size must be greater than 0")
	}
	if p.PageSize > 100 {
		return fmt.Errorf("page_size must be less than or equal to 100")
	}
	return nil
}

// PaginatedResult representa um resultado paginado
type PaginatedResult[T any] struct {
	Data       []T         `json:"data"`
	Pagination *Pagination `json:"pagination"`
}

// NewPaginatedResult cria um novo resultado paginado
func NewPaginatedResult[T any](data []T, pagination *Pagination) *PaginatedResult[T] {
	return &PaginatedResult[T]{
		Data:       data,
		Pagination: pagination,
	}
}

// IsEmpty verifica se o resultado está vazio
func (pr *PaginatedResult[T]) IsEmpty() bool {
	return len(pr.Data) == 0
}

// Count retorna o número de itens na página atual
func (pr *PaginatedResult[T]) Count() int {
	return len(pr.Data)
}

// Sort representa opções de ordenação
type Sort struct {
	Field string `json:"field" validate:"required"`
	Order string `json:"order" validate:"oneof=asc desc"`
}

// NewSort cria uma nova instância de ordenação
func NewSort(field, order string) *Sort {
	if order != "asc" && order != "desc" {
		order = "asc"
	}

	return &Sort{
		Field: field,
		Order: order,
	}
}

// IsAscending verifica se a ordenação é ascendente
func (s *Sort) IsAscending() bool {
	return s.Order == "asc"
}

// IsDescending verifica se a ordenação é descendente
func (s *Sort) IsDescending() bool {
	return s.Order == "desc"
}

// ToSQL converte para formato SQL
func (s *Sort) ToSQL() string {
	return fmt.Sprintf("%s %s", s.Field, s.Order)
}

// Filter representa um filtro genérico
type Filter struct {
	Field    string      `json:"field" validate:"required"`
	Operator string      `json:"operator" validate:"oneof=eq ne gt gte lt lte like in"`
	Value    interface{} `json:"value" validate:"required"`
}

// NewFilter cria um novo filtro
func NewFilter(field, operator string, value interface{}) *Filter {
	return &Filter{
		Field:    field,
		Operator: operator,
		Value:    value,
	}
}

// Validate valida o filtro
func (f *Filter) Validate() error {
	if f.Field == "" {
		return fmt.Errorf("field is required")
	}
	if f.Operator == "" {
		return fmt.Errorf("operator is required")
	}
	if f.Value == nil {
		return fmt.Errorf("value is required")
	}
	return nil
}

// QueryOptions representa opções de consulta
type QueryOptions struct {
	Pagination *Pagination `json:"pagination,omitempty"`
	Sort       []Sort      `json:"sort,omitempty"`
	Filters    []Filter    `json:"filters,omitempty"`
}

// NewQueryOptions cria novas opções de consulta
func NewQueryOptions() *QueryOptions {
	return &QueryOptions{
		Pagination: NewPagination(1, 10),
		Sort:       make([]Sort, 0),
		Filters:    make([]Filter, 0),
	}
}

// WithPagination define opções de paginação
func (qo *QueryOptions) WithPagination(page, pageSize int) *QueryOptions {
	qo.Pagination = NewPagination(page, pageSize)
	return qo
}

// WithSort define opções de ordenação
func (qo *QueryOptions) WithSort(field, order string) *QueryOptions {
	qo.Sort = append(qo.Sort, *NewSort(field, order))
	return qo
}

// WithFilter adiciona um filtro
func (qo *QueryOptions) WithFilter(field, operator string, value interface{}) *QueryOptions {
	qo.Filters = append(qo.Filters, *NewFilter(field, operator, value))
	return qo
}

// Validate valida as opções de consulta
func (qo *QueryOptions) Validate() error {
	if qo.Pagination != nil {
		if err := qo.Pagination.Validate(); err != nil {
			return fmt.Errorf("pagination validation failed: %w", err)
		}
	}

	for i, filter := range qo.Filters {
		if err := filter.Validate(); err != nil {
			return fmt.Errorf("filter %d validation failed: %w", i, err)
		}
	}

	return nil
}

// Page representa um conjunto de resultados paginados
type Page[T any] struct {
	Items      []T   `json:"items"`
	TotalItems int64 `json:"total_items"`
	TotalPages int   `json:"total_pages"`
	Page       int   `json:"page"`
	PageSize   int   `json:"page_size"`
	HasNext    bool  `json:"has_next"`
	HasPrev    bool  `json:"has_prev"`
}

// NewPage cria uma nova página paginada
func NewPage[T any](items []T, totalItems int64, pagination *Pagination) *Page[T] {
	if pagination == nil {
		pagination = NewPagination(1, 20)
	}

	totalPages := int((totalItems + int64(pagination.PageSize) - 1) / int64(pagination.PageSize))

	return &Page[T]{
		Items:      items,
		TotalItems: totalItems,
		TotalPages: totalPages,
		Page:       pagination.Page,
		PageSize:   pagination.PageSize,
		HasNext:    pagination.Page < totalPages,
		HasPrev:    pagination.Page > 1,
	}
}

// IsEmpty verifica se a página está vazia
func (p *Page[T]) IsEmpty() bool {
	return len(p.Items) == 0
}

// Count retorna o número de itens na página atual
func (p *Page[T]) Count() int {
	return len(p.Items)
}
