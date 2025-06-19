# inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.1.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.1.0.xlsx` \n**Data de conversão:** 2025-05-15T14:38:40.579352 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.1.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento descreve o mapeamento dos dados de aviso de recebimento (receipt advice) entre o sistema WMS e o Oracle Fusion Inventory Management Cloud (versão 23.1.0) para pedidos de compra e devoluções (RMA).

Resumo dos principais pontos:

1. Cabeçalho da mensagem

   - Campos informacionais (ex.: versão do documento, sistema de origem, ambiente do cliente).
   - Identificação obrigatória da entidade (“purchase_order”), timestamp ISO e MessageId.
   - Dados do pedido: número do PO, filial, código da empresa, fornecedor, ação (CREATE/UPDATE/CANCEL), datas (criação, entrega, cancelamento), tipo de documento, além de até cinco campos personalizados e informações de cliente/vendedor.

2. Linhas de detalhe

   - Cada linha recebe um número de sequência gerado automaticamente.
   - Campos obrigatórios: código de ação, código alternativo do item (concatenação de número e revisão), quantidade ordenada, código do item pelo fornecedor e programação de linha (linha~agenda).
   - Vários campos opcionais para custos, códigos de embalagem, atributos internos, atributos de inventário e campos customizados.
   - Informações de unidade de medida, código de barras, razão de pré-embalagem e demais extensões de atributos.

3. Para cada campo, o documento especifica:
   - Nome no WMS e no Fusion, formato (string, data, número), tamanho máximo, se é obrigatório e regras de transformação (concatenações, extração de parte da data, uso de propriedades de integração).

Esse mapeamento garante que todos os dados necessários do WMS sejam corretamente traduzidos para os campos do Oracle Fusion durante o processamento de avisos de recebimento de pedidos e RMA.

## Conteúdo extraído

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "23.1.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: 23A, Notes: Informational only.
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
