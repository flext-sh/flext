# wms.inv.receipt-confirmation-for-PO-RMA-TO-SupplierASN-mapping-24.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/wms.inv.receipt-confirmation-for-PO-RMA-TO-SupplierASN-mapping-24.4.0.xlsx` \n**Data de conversão:** 2025-05-15T14:42:44.788288 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/wms.inv.receipt-confirmation-for-PO-RMA-TO-SupplierASN-mapping-24.4.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento é um guia de mapeamento para o processo de “confirmação de recebimento” entre o WMS e o Oracle Fusion, contemplando três cenários principais – Recebimento de PO, Recebimento de RMA (incluindo RMA como IB Shipment) e Transfer Order (TO) – e descrevendo:

1. Endpoints REST
   • POST /receivingReceiptRequests – envia o header e linhas do receipt advice
   • POST /receivingReceiptTransactionRequests – envia as transações de recebimento (ajustes, correções, rejeições, etc.)
   • GET /receivingTransactionsHistory – recupera o parentTransactionId necessário para atualizar transações no Fusion
   • GET activeSubinventories – obtém LocationId para ShipToLocationId

2. Estrutura de payload e query parameters
   • Campos comuns de header:
    – id (GUID), path, operation (“create”), InsertAndProcessFlag (“true”)
    – ReceiptSourceCode (VENDOR/CUSTOMER/TRANSFER ORDER), SourceDocumentCode (PO/RMA), TransactionType/AutoTransactCode (“RECEIVE”)
    – OrganizationCode (facility_code), ExternalSystemTransactionReference (MessageId ou group_nbr+seq_nbr)
   • Campos de linha:
    – DocumentNumber (po_nbr ou shipment_nbr), DocumentLineNumber, DocumentShipmentLineNumber
    – Quantity (orig_qty/adj_qty), UOMCode (com lógica para “UNITS” vs. unit_of_measure), SubInventory (prev_erp_bucket/current_erp_bucket/ref_value_16)
    – ItemNumber e ItemRevision (extraídos de item_alternate_code), ShipmentHeaderId/LineId (substring de ref_value_9), SoldToLegalEntity (ref_value_7)
    – ExternalSystemPackingUnit (lpn_nbr ou to_container_nbr), ShipToLocationId (LocationId), DestinationTypeCode
   • Blocos condicionais para lotes e números de série, quando o SKU for lot-tracked, serial-tracked ou ambos

3. Transformações e regras de extração
   • Uso de ref_value_X e substring-before/after com delimitador “~^~” para obter IDs de Receipt Advice, Shipment, linhas e quantidades
   • Definição de TransactionType (“CORRECT”, “REJECT” ou “DELIVER”) com base no código de atividade
   • Seleção de orig_qty ou adj_qty conforme tipo de transação (recebimento normal, ajuste, rejeição, correção)

4. Parâmetros de consulta para GET
   • Para PO: PONumber, POLineNumber, ItemNumber, OrganizationCode, ExternalSystemPackingUnit, TransactionTypeCode
   • Para RMA: ReceiptAdviceHeaderId, ReceiptAdviceLineId, ItemNumber, OrganizationCode, ExternalSystemPackingUnit, TransactionTypeCode
   • Para TO: ShipmentHeaderId, ShipmentLineId, ItemNumber, OrganizationCode, ExternalSystemPackingUnit, TransactionTypeCode

5. URLs de referência
   • API de Receipt Requests
   • API de Receipt Transactions
   • API de Transaction History

Em suma, o documento detalha cada campo do XML/JSON de integração, seus formatos, tamanhos máximos, valores fixos ou de lookup, as transformações necessárias e a sequência de chamadas REST para orquestrar a confirmação de recebimento no Oracle Fusion a partir do WMS.

## Conteúdo extraído

INV Column: id, Format: , Max: , WMS Column for PO: Unique ID for Batch processing, WMS Column for RMA: Unique ID for Batch processing, WMS Column for RMA as IB Shipment: Unique ID for Batch processing, WMS column for TO: Unique ID for Batch processing, Format.1: , Max.1: , Notes: generate-guid()
INV Column: path , Format: , Max: , WMS Column for PO: /receivingReceiptRequests, WMS Column for RMA: /receivingReceiptRequests, WMS Column for RMA as IB Shipment: /receivingReceiptRequests, WMS column for TO: /receivingReceiptRequests, Format.1: , Max.1: , Notes: Part of REST API needs to be configured as path
INV Column: operation, Format: , Max: , WMS Column for PO: "create", WMS Column for RMA: "create", WMS Column for RMA as IB Shipment: "create", WMS column for TO: "create", Format.1: , Max.1: , Notes:
INV Column: ReceiptSourceCode, Format: string, Max: 25.0, WMS Column for PO: "VENDOR", WMS Column for RMA: "CUSTOMER", WMS Column for RMA as IB Shipment: "VENDOR", WMS column for TO: "TRANSFER ORDER", Format.1: , Max.1: , Notes: Below mapping comes under payload node
INV Column: OrganizationCode, Format: string, Max: 18.0, WMS Column for PO: facility_code, WMS Column for RMA: facility_code, WMS Column for RMA as IB Shipment: facility_code, WMS column for TO: facility_code, Format.1: string, Max.1: 20.0, Notes:
INV Column: ShipmentNumber, Format: integer, Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS column for TO: shipment_nbr, Format.1: integer, Max.1: , Notes: shipment_nbr
INV Column: VendorId, Format: integer, Max: 18.0, WMS Column for PO: ref_value_14, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS column for TO: , Format.1: string, Max.1: 250.0, Notes: For receiving IHT-1/72 its ref 14 & for split IHT-34/35 its ref 13 (erp_vendorid)
INV Column: VendorSiteId, Format: integer, Max: 18.0, WMS Column for PO: ref_value_15, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS column for TO: , Format.1: string, Max.1: 250.0, Notes: For receiving IHT-1/72 its ref 15 & for split IHT-34/35 its ref 14 (erp_vendorsiteid)
INV Column: CustomerId, Format: string, Max: 30.0, WMS Column for PO: ref_value_13 or ref_value_14, WMS Column for RMA: ref_value_2 (origin_code), WMS Column for RMA as IB Shipment: , WMS column for TO: , Format.1: string, Max.1: 250.0, Notes: For receiving IHT-1/72 its ref 14 & for split IHT-34/35 its ref 13 (erp_vendorid)
INV Column: InsertAndProcessFlag, Format: boolean, Max: , WMS Column for PO: "true", WMS Column for RMA: "true", WMS Column for RMA as IB Shipment: "true", WMS column for TO: "true", Format.1: , Max.1: , Notes:
INV Column: ReceiptSourceCode, Format: string, Max: 25.0, WMS Column for PO: "VENDOR", WMS Column for RMA: "CUSTOMER", WMS Column for RMA as IB Shipment: "CUSTOMER", WMS column for TO: TRANSFER ORDER, Format.1: , Max.1: , Notes:
INV Column: SourceDocumentCode, Format: string, Max: 25.0, WMS Column for PO: "PO", WMS Column for RMA: "RMA", WMS Column for RMA as IB Shipment: "PO", WMS column for TO: TRANSFER ORDER, Format.1: string, Max.1: , Notes:
INV Column: TransactionType, Format: string, Max: 25.0, WMS Column for PO: "RECEIVE", WMS Column for RMA: "RECEIVE", WMS Column for RMA as IB Shipment: "RECEIVE", WMS column for TO: "RECEIVE", Format.1: , Max.1: , Notes:
INV Column: AutoTransactCode, Format: string, Max: 25.0, WMS Column for PO: "RECEIVE", WMS Column for RMA: "RECEIVE", WMS Column for RMA as IB Shipment: "RECEIVE", WMS column for TO: "RECEIVE", Format.1: , Max.1: , Notes:
INV Column: OrganizationCode, Format: string, Max: 18.0, WMS Column for PO: facility_code, WMS Column for RMA: facility_code, WMS Column for RMA as IB Shipment: facility_code, WMS column for TO: facility_code, Format.1: string, Max.1: 20.0, Notes:
INV Column: DocumentNumber, Format: string, Max: 30.0, WMS Column for PO: po_nbr, WMS Column for RMA: po_nbr, WMS Column for RMA as IB Shipment: po_nbr, WMS column for TO: shipment_nbr, Format.1: string, Max.1: 30.0, Notes: if ref_value_6 = 'PO' then po_nbr else shipment_nbr
INV Column: DocumentLineNumber, Format: integer, Max: 18.0, WMS Column for PO: ref_value_8 or ref_value_9, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS column for TO: , Format.1: string, Max.1: 250.0, Notes: if ref_value_6 = 'PO' then ref_value_8 else 9
INV Column: DocumentShipmentLineNumber, Format: integer, Max: 18.0, WMS Column for PO: substring of ref_value_8 or ref_value_9, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS column for TO: , Format.1: string, Max.1: , Notes: if ref_value_6 = 'PO' then ref_value_8's sub string after '~^~'
else ref_value_9's substring after '~^~'
INV Column: ReceiptAdviceHeaderId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: substring of ref_value_8 , WMS Column for RMA as IB Shipment: shipment_nbr, WMS column for TO: shipment_nbr, Format.1: string, Max.1: , Notes: substring-before( ref_value_8, "~^~")
INV Column: ReceiptAdviceLineId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: substring of ref_value_8 , WMS Column for RMA as IB Shipment: substring of ref_value_8 , WMS column for TO: , Format.1: string, Max.1: , Notes: substring-after( ref_value_8, "~^~")
INV Column: ItemRevision, Format: string, Max: 18.0, WMS Column for PO: substring of item_alternate_code, WMS Column for RMA: substring of item_alternate_code, WMS Column for RMA as IB Shipment: substring of item_alternate_code, WMS column for TO: substring of item_alternate_code, Format.1: string, Max.1: , Notes: substring-after( item_alternate_code, "~^~")
INV Column: ItemNumber , Format: string, Max: 300.0, WMS Column for PO: substring of item_alternate_code, WMS Column for RMA: substring of item_alternate_code, WMS Column for RMA as IB Shipment: substring of item_alternate_code, WMS column for TO: substring of item_alternate_code, Format.1: string, Max.1: 130.0, Notes: substring-before( item_alternate_code, "~^~")
INV Column: Quantity, Format: number, Max: , WMS Column for PO: adj_qty, WMS Column for RMA: adj_qty, WMS Column for RMA as IB Shipment: adj_qty, WMS column for TO: adj_qty, Format.1: decimal, Max.1: , Notes:
INV Column: UOMCode, Format: string, Max: 25.0, WMS Column for PO: qty_uom_code, WMS Column for RMA: qty_uom_code, WMS Column for RMA as IB Shipment: qty_uom_code, WMS column for TO: qty_uom_code, Format.1: , Max.1: , Notes: If integration property "consider_qty_uom_from_property = yes and qty_uom_code='UNITS'" use unit_of_measure from integration properties(default is 'Ea'), else use qty_uom_code.
INV Column: SoldToLegalEntity, Format: string, Max: 240.0, WMS Column for PO: ref_value_7, WMS Column for RMA: ref_value_7, WMS Column for RMA as IB Shipment: ref_value_7, WMS column for TO: , Format.1: string, Max.1: 250.0, Notes: sold_to_legal_name
INV Column: SubInventory, Format: string, Max: 10.0, WMS Column for PO: prev_erp_bucket or ref_value_16 or current_erp_bucket, WMS Column for RMA: prev_erp_bucket or ref_value_16 or current_erp_bucket, WMS Column for RMA as IB Shipment: prev_erp_bucket or ref_value_16 or current_erp_bucket, WMS column for TO: prev_erp_bucket or ref_value_16 or current_erp_bucket, Format.1: string, Max.1: 100.0, Notes: For receiving IHT-1/72 its ref 16 & for split IHT-34/35 its prev_erp_bucket
INV Column: ShipToLocationId, Format: integer, Max: , WMS Column for PO: LocationId, WMS Column for RMA: LocationId, WMS Column for RMA as IB Shipment: LocationId, WMS column for TO: LocationId, Format.1: , Max.1: , Notes:
INV Column: ExternalSystemPackingUnit, Format: string, Max: 150.0, WMS Column for PO: lpn_nbr or to_container_nbr, WMS Column for RMA: lpn_nbr or to_container_nbr, WMS Column for RMA as IB Shipment: lpn_nbr or to_container_nbr, WMS column for TO: lpn_nbr or to_container_nbr, Format.1: string, Max.1: 30.0, Notes: For receiving IHT-1/72 its lpn_nbr & for split IHT-34/35 its to_container_nbr
INV Column: ExternalSystemTransactionReference, Format: string, Max: 300.0, WMS Column for PO: MessageId, WMS Column for RMA: MessageId, WMS Column for RMA as IB Shipment: MessageId, WMS column for TO: MessageId, Format.1: , Max.1: , Notes:
INV Column: ShipmentHeaderId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: substring of ref_value_9 (RAL), WMS column for TO: substring of ref_value_9 (RAL), Format.1: string, Max.1: , Notes: substring-before (ref_value_9, &quot;~^~&quot; )
INV Column: ShipmentLineId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: substring of ref_value_9 (RAL), WMS column for TO: substring of ref_value_9 (RAL), Format.1: string, Max.1: , Notes: substring-after (ref_value_9, &quot;~^~&quot; )
INV Column: DestinationTypeCode, Format: string, Max: 25.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: RECEIVING, WMS column for TO: RECEIVING, Format.1: string, Max.1: , Notes:

INV Column: id, Format: , Max: , WMS Column for PO: Unique ID for Batch processing, WMS Column for RMA: Unique ID for Batch processing, WMS Column for RMA as IB Shipment: Unique ID for Batch processing, WMS Column for TO: Unique ID for Batch processing, Format.1: , Max.1: , Notes: generate-guid()
INV Column: path , Format: , Max: , WMS Column for PO: /receivingReceiptTransactionRequests, WMS Column for RMA: /receivingReceiptTransactionRequests, WMS Column for RMA as IB Shipment: /receivingReceiptTransactionRequests, WMS Column for TO: /receivingReceiptTransactionRequests, Format.1: , Max.1: , Notes: Part of REST API needs to be configured as path
INV Column: operation, Format: , Max: , WMS Column for PO: "create", WMS Column for RMA: "create", WMS Column for RMA as IB Shipment: "create", WMS Column for TO: "create", Format.1: , Max.1: , Notes:
INV Column: OrganizationCode, Format: string, Max: 18.0, WMS Column for PO: facility_code, WMS Column for RMA: facility_code, WMS Column for RMA as IB Shipment: facility_code, WMS Column for TO: facility_code, Format.1: string, Max.1: 20.0, Notes:
INV Column: InsertAndProcessFlag, Format: boolean, Max: , WMS Column for PO: "true", WMS Column for RMA: "true", WMS Column for RMA as IB Shipment: "true", WMS Column for TO: "true", Format.1: , Max.1: , Notes:
INV Column: DocumentLineNumber, Format: integer, Max: 18.0, WMS Column for PO: ref_value_8 or ref_value_9, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: , Format.1: string, Max.1: 250.0, Notes: if ref_value_6 = 'PO' then ref_value_8 else 9
INV Column: DocumentNumber, Format: string, Max: 30.0, WMS Column for PO: po_nbr, WMS Column for RMA: po_nbr, WMS Column for RMA as IB Shipment: po_nbr, WMS Column for TO: shipment_nbr, Format.1: string, Max.1: 30.0, Notes: if ref_value_6 = 'PO' then po_nbr else shipment_nbr
INV Column: DocumentShipmentLineNumber, Format: integer, Max: 18.0, WMS Column for PO: substring of ref_value_8 or ref_value_9, WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: seq_nbr, Format.1: string, Max.1: , Notes: if ref_value_6 = 'PO' then ref_value_8's sub string after '~^~'
else ref_value_9's substring after '~^~'
INV Column: ReceiptAdviceHeaderId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: substring of ref_value_8 , WMS Column for RMA as IB Shipment: substring of ref_value_8 , WMS Column for TO: , Format.1: string, Max.1: , Notes: substring-before( ref_value_8, "~^~")
INV Column: ReceiptAdviceLineId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: substring of ref_value_8 , WMS Column for RMA as IB Shipment: substring of ref_value_8 , WMS Column for TO: , Format.1: string, Max.1: , Notes: substring-after( ref_value_8, "~^~")
INV Column: CustomerId, Format: integer, Max: 18.0, WMS Column for PO: vendor_code, WMS Column for RMA: vendor_code, WMS Column for RMA as IB Shipment: vendor_code, WMS Column for TO: vendor_code, Format.1: string, Max.1: , Notes:
INV Column: ItemRevision, Format: string, Max: 18.0, WMS Column for PO: substring of item_alternate_code, WMS Column for RMA: substring of item_alternate_code, WMS Column for RMA as IB Shipment: substring of item_alternate_code, WMS Column for TO: substring of item_alternate_code, Format.1: string, Max.1: , Notes: substring-after( item_alternate_code, "~^~")
INV Column: ItemNumber , Format: string, Max: 300.0, WMS Column for PO: substring of item_alternate_code, WMS Column for RMA: substring of item_alternate_code, WMS Column for RMA as IB Shipment: substring of item_alternate_code, WMS Column for TO: substring of item_alternate_code, Format.1: string, Max.1: 130.0, Notes: substring-before( item_alternate_code, "~^~")
INV Column: Quantity, Format: number, Max: , WMS Column for PO: adj_qty or orig_qty, WMS Column for RMA: adj_qty or orig_qty, WMS Column for RMA as IB Shipment: adj_qty or orig_qty, WMS Column for TO: adj_qty or orig_qty, Format.1: decimal, Max.1: , Notes: if IHT activity is 4 adj_qty else orig_qty
INV Column: UOMCode, Format: string, Max: 25.0, WMS Column for PO: qty_uom_code, WMS Column for RMA: qty_uom_code, WMS Column for RMA as IB Shipment: qty_uom_code, WMS Column for TO: qty_uom_code, Format.1: , Max.1: , Notes: If integration property "consider_qty_uom_from_property = yes and qty_uom_code='UNITS'" use unit_of_measure from integration properties(default is 'Ea'), else use qty_uom_code.
INV Column: ReceiptSourceCode, Format: string, Max: 25.0, WMS Column for PO: "VENDOR", WMS Column for RMA: "CUSTOMER", WMS Column for RMA as IB Shipment: "VENDOR", WMS Column for TO: "TRANSFER ORDER", Format.1: , Max.1: , Notes:
INV Column: SoldToLegalEntity, Format: string, Max: 240.0, WMS Column for PO: ref_value_7, WMS Column for RMA: ref_value_7, WMS Column for RMA as IB Shipment: ref_value_7, WMS Column for TO: ref_value_7, Format.1: string, Max.1: 250.0, Notes: sold_to_legal_name
INV Column: SourceDocumentCode, Format: string, Max: 25.0, WMS Column for PO: ref_value_6/ref_value_3, WMS Column for RMA: ref_value_6/ref_value_3, WMS Column for RMA as IB Shipment: "PO", WMS Column for TO: "TRANSFER ORDER", Format.1: string, Max.1: , Notes: "PO" or "RMA"
INV Column: TransactionType, Format: string, Max: 25.0, WMS Column for PO: "CORRECT" or "REJECT" or "DELIVER", WMS Column for RMA: "CORRECT" or "REJECT" or "DELIVER", WMS Column for RMA as IB Shipment: "CORRECT" or "REJECT" or "DELIVER", WMS Column for TO: "CORRECT" or "REJECT" or "DELIVER", Format.1: , Max.1: , Notes: When activity code=2/4/16/17 then "CORRECT"
When activity code=14 then "REJECT"
else "DELIVER"
INV Column: SubInventory, Format: string, Max: 10.0, WMS Column for PO: prev_erp_bucket or current_erp_bucket, WMS Column for RMA: prev_erp_bucket or current_erp_bucket, WMS Column for RMA as IB Shipment: prev_erp_bucket or current_erp_bucket, WMS Column for TO: prev_erp_bucket or current_erp_bucket, Format.1: , Max.1: , Notes: When Activity Code = 4/16/17 and adj_qty < 0 (negative adjustment) or Activity Code = 14/2 then prev_erp_bucket
othewise current_erp_bucket
INV Column: ParentTransactionId, Format: integer, Max: 18.0, WMS Column for PO: TransactionId we get in response of receivingTransactionsHistory GET API, WMS Column for RMA: TransactionId we get in response of receivingTransactionsHistory GET API, WMS Column for RMA as IB Shipment: TransactionId we get in response of receivingTransactionsHistory GET API, WMS Column for TO: TransactionId we get in response of receivingTransactionsHistory GET API, Format.1: , Max.1: , Notes: <xsl:value-of xml:id="id_122" select="$receivingTransactionsHistory/nsmpr3:executeResponse/ns31:response-wrapper/ns31:items/ns31:TransactionId"/>
INV Column: ExternalSystemPackingUnit, Format: string, Max: , WMS Column for PO: lpn_nbr or to_container_nbr, WMS Column for RMA: lpn_nbr or to_container_nbr, WMS Column for RMA as IB Shipment: lpn_nbr or to_container_nbr, WMS Column for TO: lpn_nbr or to_container_nbr, Format.1: , Max.1: , Notes:
INV Column: ExternalSystemTransactionReference, Format: string, Max: 300.0, WMS Column for PO: group_nbr+seq_nbr, WMS Column for RMA: group_nbr+seq_nbr, WMS Column for RMA as IB Shipment: group_nbr+seq_nbr, WMS Column for TO: group_nbr+seq_nbr, Format.1: , Max.1: , Notes:
INV Column: ShipmentHeaderId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: ref_value_9, WMS Column for TO: ref_value_9, Format.1: string, Max.1: , Notes: substring-before (ref_value_9, &quot;~^~&quot; )
INV Column: ShipmentLineId, Format: integer, Max: 18.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: ref_value_9, WMS Column for TO: ref_value_9, Format.1: string, Max.1: , Notes: substring-after (ref_value_9, &quot;~^~&quot; )
INV Column: DefaultLotsAndSerialNumbersFromASNFlag, Format: boolean, Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: false , WMS Column for TO: , Format.1: , Max.1: , Notes:
INV Column: ASNLineNumber, Format: , Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: seq_nbr, WMS Column for TO: , Format.1: , Max.1: , Notes:
INV Column: DestinationTypeCode, Format: string, Max: 25.0, WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: INVENTORY, Format.1: string, Max.1: , Notes: For QC Reject flow for TO, this needs to be RECEIVING
INV Column: lotItemLots, Format: , Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: , Format.1: , Max.1: , Notes: This block will appear only if SKU is Lot tracked.
INV Column: LotNumber, Format: string, Max: 80.0, WMS Column for PO: ref_value_4/ref_value_1, WMS Column for RMA: ref_value_4/ref_value_1, WMS Column for RMA as IB Shipment: ref_value_4/ref_value_1, WMS Column for TO: ref_value_4/ref_value_1, Format.1: string, Max.1: , Notes:
INV Column: TransactionQuantity, Format: number, Max: , WMS Column for PO: orig_qty/adj_qty, WMS Column for RMA: orig_qty/adj_qty, WMS Column for RMA as IB Shipment: orig_qty/adj_qty, WMS Column for TO: orig_qty/adj_qty, Format.1: decimal, Max.1: , Notes:
INV Column: LotExpirationDate, Format: date, Max: , WMS Column for PO: ref_value_5/ref_value_2, WMS Column for RMA: ref_value_5/ref_value_2, WMS Column for RMA as IB Shipment: ref_value_5/ref_value_2, WMS Column for TO: ref_value_5/ref_value_2, Format.1: date, Max.1: , Notes:
INV Column: serialItemSerials, Format: , Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: , Format.1: , Max.1: , Notes: This block will be added for Serial tracked SKU
INV Column: FromSerialNumber, Format: string, Max: 80.0, WMS Column for PO: serial_nbr, WMS Column for RMA: serial_nbr, WMS Column for RMA as IB Shipment: serial_nbr, WMS Column for TO: serial_nbr, Format.1: string, Max.1: , Notes:
INV Column: ToSerialNumber, Format: string, Max: 80.0, WMS Column for PO: serial_nbr, WMS Column for RMA: serial_nbr, WMS Column for RMA as IB Shipment: serial_nbr, WMS Column for TO: serial_nbr, Format.1: string, Max.1: , Notes:
INV Column: lotSerialItemLots, Format: , Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: , Format.1: , Max.1: , Notes: This block will be added for Lot & Serial tracked SKU
INV Column: LotNumber, Format: string, Max: 80.0, WMS Column for PO: ref_value_4/ref_value_1, WMS Column for RMA: ref_value_4/ref_value_1, WMS Column for RMA as IB Shipment: ref_value_4/ref_value_1, WMS Column for TO: ref_value_4/ref_value_1, Format.1: string, Max.1: , Notes:
INV Column: TransactionQuantity, Format: number, Max: , WMS Column for PO: orig_qty/adj_qty, WMS Column for RMA: orig_qty/adj_qty, WMS Column for RMA as IB Shipment: orig_qty/adj_qty, WMS Column for TO: orig_qty/adj_qty, Format.1: decimal, Max.1: , Notes:
INV Column: LotExpirationDate, Format: date, Max: , WMS Column for PO: ref_value_5/ref_value_2, WMS Column for RMA: ref_value_5/ref_value_2, WMS Column for RMA as IB Shipment: ref_value_5/ref_value_2, WMS Column for TO: ref_value_5/ref_value_2, Format.1: date, Max.1: , Notes:
INV Column: lotSerialItemSerials, Format: , Max: , WMS Column for PO: , WMS Column for RMA: , WMS Column for RMA as IB Shipment: , WMS Column for TO: , Format.1: , Max.1: , Notes:
INV Column: FromSerialNumber, Format: string, Max: 80.0, WMS Column for PO: serial_nbr, WMS Column for RMA: serial_nbr, WMS Column for RMA as IB Shipment: serial_nbr, WMS Column for TO: serial_nbr, Format.1: string, Max.1: , Notes:
INV Column: ToSerialNumber, Format: string, Max: 80.0, WMS Column for PO: serial_nbr, WMS Column for RMA: serial_nbr, WMS Column for RMA as IB Shipment: serial_nbr, WMS Column for TO: serial_nbr, Format.1: string, Max.1: , Notes:

Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: QueryParameters for PO flow, Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: PONumber, Unnamed: 2: po_nbr, Unnamed: 3: if ref_value_6 = 'PO' po_nbr
Unnamed: 0: , Unnamed: 1: ItemNumber, Unnamed: 2: substring of item_alternate_code, Unnamed: 3: substring-before( item_alternate_code, "~^~")
Unnamed: 0: , Unnamed: 1: OrganizationCode, Unnamed: 2: facility_code, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ExternalSystemPackingUnit, Unnamed: 2: lpn_nbr/to_container_nbr, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: POLineNumber, Unnamed: 2: substring of ref_value_8, Unnamed: 3: substring-before(ref_value_8, "~^~")
Unnamed: 0: , Unnamed: 1: TransactionTypeCode, Unnamed: 2: RECEIVE, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: QueryParameters for RMA flow, Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ReceiptAdviceHeaderId, Unnamed: 2: ReceiptAdviceHeaderId, Unnamed: 3: if ref_value_6 = 'RMA' then substring-before( concat(ref_value_8, ref_value_9) "~^~")
Unnamed: 0: , Unnamed: 1: ItemNumber, Unnamed: 2: substring of item_alternate_code, Unnamed: 3: substring-before( item_alternate_code, "~^~")
Unnamed: 0: , Unnamed: 1: OrganizationCode, Unnamed: 2: facility_code, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ExternalSystemPackingUnit, Unnamed: 2: lpn_nbr/to_container_nbr, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ReceiptAdviceLineId, Unnamed: 2: substring of concat(ref_value_8 and ref_value_9, Unnamed: 3: sunstring-after(concat(ref_value_8, ref_value_9), "~^~")
Unnamed: 0: , Unnamed: 1: TransactionTypeCode, Unnamed: 2: RECEIVE, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: QueryParameters for TO flow, Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ShipmentHeaderId, Unnamed: 2: substring of ref_value_9, Unnamed: 3: substring-before (ref_value_9, "~^~" )
Unnamed: 0: , Unnamed: 1: ShipmentLineId, Unnamed: 2: substring of ref_value_9, Unnamed: 3: substring-after (ref_value_9, "~^~" )
Unnamed: 0: , Unnamed: 1: ItemNumber, Unnamed: 2: substring of item_alternate_code, Unnamed: 3: substring-before (item_alternate_code, "~^~" )
Unnamed: 0: , Unnamed: 1: OrganizationCode, Unnamed: 2: facility_code, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: ExternalSystemPackingUnit, Unnamed: 2: lpn_nbr/to_container_nbr, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: TransactionTypeCode, Unnamed: 2: RECEIVE, Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3:
Unnamed: 0: , Unnamed: 1: We update WMS PA transaction in Fusion by using REST API - receivingReceiptTransactionRequests (POST). This API requires a parameter - parentTransactionId (this is a transactionId on Receipt Advice Line in Fusion).
To get parenTransactionId, we use this GET request - receivingTransactionsHistory with above query parameter., Unnamed: 2: , Unnamed: 3:

Unnamed: 0: , Unnamed: 1: Query Parameters, Unnamed: 2:
Unnamed: 0: , Unnamed: 1: SecondaryInventoryName, Unnamed: 2: ref_value_16 or current_erp_bucket or prev_erp_bucket
Unnamed: 0: , Unnamed: 1: OrganizationCode, Unnamed: 2: facility_code
Unnamed: 0: , Unnamed: 1: SubinventoryType, Unnamed: 2: Receiving
Unnamed: 0: , Unnamed: 1: , Unnamed: 2:
Unnamed: 0: , Unnamed: 1: activeSubinvetories (GET) call used to get the location details from the fusion. And ShipToLocationId mapped to the LocationId in fusion, Unnamed: 2:

Unnamed: 0: , Unnamed: 1:
Unnamed: 0: , Unnamed: 1:
Unnamed: 0: , Unnamed: 1:
Unnamed: 0: , Unnamed: 1: Following are the API & Document URLS:
Unnamed: 0: , Unnamed: 1: Receiving API - receivingReceiptRequests
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-receiving-receipt-requests.html>
Unnamed: 0: , Unnamed: 1: Post receiving API - receivingReceiptTransactionsRequests
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-requests-receiving-transactions.html>
Unnamed: 0: , Unnamed: 1: Get TransactionId API - receivingTransactionsHistory
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-receiving-transactions-history.html>
