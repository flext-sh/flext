# inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.4.0.xlsx` \n**Data de conversão:** 2025-05-15T14:38:58.237556 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.4.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento define o mapeamento entre o layout exportado pelo WMS (Warehouse Management System) e os campos esperados pelo Oracle Fusion Inventory Management Cloud para processamento de “receipt advice” de Purchase Orders e de RMAs.

1. Estrutura de cabeçalho

   - Informações fixas ou geradas automaticamente: versão do documento, sistema de origem, código do ambiente, data/hora (timestamp) e identificador da mensagem.
   - Dados de contexto do pedido: número do PO, código de instalação (facility), código da empresa, fornecedor (ou cliente, no caso de RMA), tipo de ação (CREATE/UPDATE/CANCEL), datas de emissão e de entrega esperada, tipo de documento (PO ou RMA) e campos livres para customização.
   - Informações adicionais do parceiro comercial: nome e identificador do fornecedor/cliente, site de abastecimento (erp_vendorsiteid).

2. Estrutura de linhas (detail)
   - Cada linha contém um índice sequencial, código de ação, referência ao item (código alternativo que concatena número e revisão), quantidade a receber e código de item fornecido pelo fornecedor.
   - Possibilidade de detalhamento de embalagens padrão (pre-pack), unidades de medida, custo unitário e demais campos customizáveis.
   - Associação ao cronograma de linha do pedido original, por meio da concatenação de número de linha e número de agendamento.
   - Espaço para até 15 atributos de inventário (invn_attr_a…invn_attr_o) e outros campos livres para dados internos ou complementares.

Em resumo, o arquivo serve como referência para transformar cada coluna do WMS no elemento correspondente na API de recebimento de pedido do Fusion, garantindo que todas as informações obrigatórias (PO, datas, fornecedor, quantidades, etc.) sejam corretamente transferidas e formatadas.

## Conteúdo extraído

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: 24D, Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: Set using IntegrationProperties. By default 'PP' , Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "purchase_order", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: current-dateTime(), Notes: Unique WMS interface message identifier.

WMS Column: po_nbr, Format: string, Max: 30, REQD?: X, INV Column for PO: DocumentNumber, INV Column for RMA as PO: DocumentNumber, Format.1: string, Max.1: 150.0, Notes:
WMS Column: facility_code, Format: string, Max: 20, REQD?: X, INV Column for PO: OrganizationCode, INV Column for RMA as PO: OrganizationCode, Format.1: string, Max.1: 18.0, Notes:
WMS Column: company_code, Format: string, Max: 20, REQD?: X, INV Column for PO: Set using IntegrationProperties. By default 'PP' , INV Column for RMA as PO: Set using IntegrationProperties. By default 'PP' , Format.1: , Max.1: , Notes: ($selfProperties/nsmpr14:properties/nsmpr14:company_code)
WMS Column: vendor_code, Format: string, Max: 20, REQD?: X, INV Column for PO: SupplierId, INV Column for RMA as PO: CustomerId, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: action_code, Format: string, Max: 10, REQD?: X, INV Column for PO: ActionCode, INV Column for RMA as PO: ActionCode, Format.1: string, Max.1: 25.0, Notes: For Fusion CREATE or CANCEL action we use UPDATE action in WMS
WMS Column: ord_date, Format: date, Max: 14, REQD?: X, INV Column for PO: DocumentCreationDate, INV Column for RMA as PO: DocumentCreationDate, Format.1: datetime, Max.1: , Notes: substring-before (DocumentCreationDate, "." )
WMS Column: ref_nbr, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: RMAHeaderId, Format.1: , Max.1: , Notes:
WMS Column: po_type, Format: string, Max: 50, REQD?: X, INV Column for PO: SourceDocumentTypeCode - PO, INV Column for RMA as PO: SourceDocumentTypeCode - RMA, Format.1: string, Max.1: 25.0, Notes:
WMS Column: delivery_date, Format: date, Max: 14, REQD?: X, INV Column for PO: ExpectedReceiptDate, INV Column for RMA as PO: ExpectedReceiptDate, Format.1: datetime, Max.1: , Notes: substring-before (ExpectedReceiptDate, "." )
WMS Column: dept_code, Format: string, Max: 20, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: ship_date, Format: date, Max: 14, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cancel_date, Format: date, Max: 14, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_nbr, Format: string, Max: 30, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_name, Format: string, Max: 50, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_addr, Format: string, Max: 70, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_addr2, Format: string, Max: 40, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_addr3, Format: string, Max: 40, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: rma_nbr, Format: string, Max: 40, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: sold_to_legal_name, Format: string, Max: 240, REQD?: X, INV Column for PO: SoldToLegalEntityName, INV Column for RMA as PO: , Format.1: string, Max.1: 960.0, Notes:
WMS Column: erp_vendorid, Format: string, Max: 20, REQD?: X, INV Column for PO: SupplierId, INV Column for RMA as PO: CustomerId, Format.1: integer, Max.1: 18.0, Notes: supplier or vendor id
WMS Column: vendor_name, Format: string, Max: 250, REQD?: X, INV Column for PO: SupplierName, INV Column for RMA as PO: CustomerName, Format.1: string, Max.1: 1440.0, Notes: supplier or vendor name

WMS Column: seq_nbr, Format: number, Max: , REQD?: X, INV Column for PO: <sequence>, INV Column for RMA as PO: <sequence>, Format.1: , Max.1: , Notes: Auto-Generated: position()
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column for PO: ActionCode, INV Column for RMA as PO: ActionCode, Format.1: string, Max.1: 25, Notes: For Fusion CANCEL action, WMS uses DELETE otherwise as it is mapped to ActionCode of Fusion
WMS Column: item_alternate_code, Format: string, Max: 130.0, REQD?: X, INV Column for PO: ItemNumber + "~^~" + ItemRevision, INV Column for RMA as PO: ItemNumber + "~^~" + ItemRevision, Format.1: string, Max.1: 300-18, Notes: concat (ItemNumber, "~^~", ItemRevision)
WMS Column: item_part_a, Format: string, Max: 30.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_b, Format: string, Max: 30.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_c, Format: string, Max: 20.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_d, Format: string, Max: 20.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_e, Format: string, Max: 10.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_f, Format: string, Max: 10.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_code, Format: string, Max: 30.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio, Format: number, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_total_units, Format: number, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: ord_qty, Format: number, Max: , REQD?: X, INV Column for PO: Quantity, INV Column for RMA as PO: Quantity, Format.1: number, Max.1: , Notes:
WMS Column: unit_cost, Format: number, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: vendor_item_code, Format: string, Max: 50.0, REQD?: X, INV Column for PO: SupplierItemNumber, INV Column for RMA as PO: SupplierItemNumber, Format.1: string, Max.1: 1200, Notes:
WMS Column: internal_misc_n1, Format: string, Max: 9.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: internal_misc_a1, Format: string, Max: 100.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: unit_retail, Format: number, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 50.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 50.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 50.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 50.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio_seq, Format: number, Max: , REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: item_barcode, Format: string, Max: 40.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: uom, Format: string, Max: 10.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: line_schedule_nbrs, Format: string, Max: 30.0, REQD?: X, INV Column for PO: DocumentLineNumber + "~^~" + DocumentScheduleNumber, INV Column for RMA as PO: RMAHeaderId + "~^~" + ns31:RMALineId, Format.1: string, Max.1: 150-150, Notes: concat (DocumentLineNumber, "~^~", DocumentScheduleNumber) - For PO
concat (RMAHeaderId,"~^~", RMALineId) - For RMA
WMS Column: invn_attr_a, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_b, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_c, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_d, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_e, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_f, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_g, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_h, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_i, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_j, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_k, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_l, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_m, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_n, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_o, Format: string, Max: 75.0, REQD?: , INV Column for PO: , INV Column for RMA as PO: , Format.1: , Max.1: , Notes:
WMS Column: erp_vendorsiteid, Format: string, Max: 250.0, REQD?: X, INV Column for PO: SupplierSiteId, INV Column for RMA as PO: , Format.1: integer, Max.1: 18, Notes:
