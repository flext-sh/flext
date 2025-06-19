# inv.wms.receipt-advice-for-ASN-mapping-23.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.receipt-advice-for-ASN-mapping-23.4.0.xlsx` \n**Data de conversão:** 2025-05-15T14:38:16.754329 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.receipt-advice-for-ASN-mapping-23.4.0.xlsx)**

---

## Sumário

## Resumo automático

Este material é a especificação de integração “Receipt Advice for ASN” (versão 23.4.0) entre o Oracle Fusion Inventory Cloud e um sistema WMS. Ele reúne três grandes blocos:

1. Questões em aberto e decisões tomadas
   • Ajustes de tamanho de campos quando há divergência entre Fusion e WMS.
   • Unicidade do identificador de remessa para evitar conflito quando dois fornecedores usam o mesmo número de ASN (solução baseada em ShipmentHeaderId + timestamp).
   • Regras de cancelamento de linha de ASN (optou-se por não permitir cancelamento automático no WMS após recebimento parcial – redução de quantidade esperada deve ser tratada manualmente).
   • Uso de campos customizados para transportar informações de Packing Slip, Waybill e demais atributos que não existem nativamente no WMS.
   • Tratamento de data esperada (diferença entre DateTime no Fusion e Date no WMS) e tolerância de data.
   • Definição de guard-rails para impedir criação ou atualização de ASN diretamente no WMS.
   • Fluxo de criação de PO vs. ASN, e necessidade de reenvio automático de notificações em caso de falhas.
   • Inclusão de dados de projeto, tarefa e país de origem (COO) no ASN via chamada adicional ao serviço de PO, para uso em recebimento.

2. Mapeamento do cabeçalho (ShipmentHeader)
   • Valores informacionais fixos: DocumentVersion, OriginSystem, ClientEnvCode, ParentCompanyCode.
   • Campos obrigatórios como Entity (“ib_shipment”), MessageId (ShipmentHeaderId), shipment_nbr, facility_code, company_code, action_code (“UPDATE”), ref_nbr (ShipmentNumber), shipment_type (“ASN” ou “ASBN”), shipped_date (truncado para data), vendor_info, entre outros.
   • Formatos, comprimentos máximos, tabelas de origem (ex.: RCV_SHIPMENT_HEADERS) e observações sobre cada coluna.

3. Mapeamento das linhas de detalhe (ShipmentLines e Serial/Lot)
   • Seq*nbr (ShipmentLineNumber), action_code (“CREATE”), lpn_nbr, item_alternate_code (ItemNumber + “~^~” + ItemRevision), shipped_qty (quantidade por lotes), po_nbr, pallet_nbr, expiry_date, batch_nbr (LotNumber), line_schedule_nbrs, uom, e dezenas de campos genéricos (cust_field**, cust*date**, cust*decimal**, invn*attr**).
   • Para rastreamento por série (“ib*shipment_serial_nbr”), lista de colunas específicas: action_code, facility_code, shipment_nbr, item_alternate_code, serial_nbr, batch_nbr, expiry_date, invn_attr*\*.

Complementa o documento um trecho sobre uso de REST API (receiptAdviceLines) com URLs de consulta e descrição dos campos, além de links para casos de teste no Confluence.

## Conteúdo extraído

Unnamed: 0: , Unnamed: 1: ASN Open Issues, Unnamed: 2: Owning Team, Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: WMS team needs to check on all columns where max size is marked Red. This indicates that there is a mismatch in the size between Fusion Apps and WMS Apps more specifically the max column size in fusion is larger than WMS max column size., Unnamed: 2: WMS, Unnamed: 3: Closed, Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Same shipment number by two different suppliers

    In WMS when two supplier's send the same ASN number then second ASN will fail and this needs to be corrected manually
    There is a possibility that when ASN1 is not received in WMS and ASN2 gets interfaced by another supplier(with same shipment number as AS1N), then WMS will override ASN1 as Shipment number is unique key in WMS.

It is proposed to use the Document Number + Supplier Name + Shipped date from fusion to WMS. This will be unique.
WMS Team needs to confirm if they are ok and the partical sceanrios like scanning the Shipment Number will work out if INV passes ShipmentNumber + SupplierName + ShippedDate, Unnamed: 2: WMS, Unnamed: 3: Closed, Unnamed: 4: Decision is to use ShipmentHeaderId + DateTime (12)
Unnamed: 0: , Unnamed: 1: Is carrier information available in WMS. This information is available in Fusion. - WMS team (Ram) to check and confirm. We would also need the carrier setup in WMS to handle this., Unnamed: 2: WMS, Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Single ASN line can be canceled or the entire ASN can be canceled. For each line, we send one CancelAsnNotification event containing the ASN line Id. In Fusion, we allow ASN line to be canceled even if it has been received (partially of course). If ASN is created for 10 each, user receives 6 each and uses the cancel line action, then the remaining 4 each is canceled and will not be received. But WMS does not allow cancelation after receiving.

Option 1: WMS allows Cancellation of the ASN line even after the line has been partially received.
Option 2: We go the same path as RMA. Ultimately canecllation of ASN line means a decrease in the quantity expected. So in Fusion the line is cancelled and the same line will need to be manually verified in WMS or else the line will remain open without any further receipts., Unnamed: 2: INV/WMS, Unnamed: 3: Closed, Unnamed: 4: Mike feedback is use Option 2
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: RMA Discussions/Assumptions, Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: What about Packing Slip and Waybill No? Fusion has this information for ASN and is considered important.
Decision: WMS does not have dedicated attributes to capture this information. We can utilize the custom fields to map if required on top of the out of box integration, Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Expected Receipt date is Date Type in WMS and is dateTime in Fsuion. Apart from thatin in WMS org scenario we document that the Date tolerance is set very high or set the date tolernace action to None to avoid getting errors at time of Receipt confirmation., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: WMS user should not be given the privilege's to create ASN creation in WMS and this should be documented in the integration guide. This concern is valid for all other documents too. WMS to think of some gurad rail to prevent updates creation of the documents that it epectes from Fusion side to avoid any reconciliation issues. Some kind of a setting to indicate that WMS facilty is using Fusion INV. To be put on the roadmap., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: PO gets interfaced to WMS by the virtue of Receipt Advice. ASN gets interfaced to WMS by a different integrations. PO should get created/Interfaced in/to WMS before ASN gets interfaced/created. This should be true most of the times as the PO gets created first in fusion and then only ASN can be created. But in a corner case the the ASN information reaches WMS first then

    WMS fails the ASN creation
    Reprocess the ASN with in WMS, so that the ASN gets created in WMS.
    FA will not be able to reprocess the ASN with the current architecture.
    In case some one clears the failed records, ASN can be created manually in WMS.

    The abilty of the Fusion to re-raise the ASN notification has to be listed in Backlog. , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:

Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: We cannot add new lines to the ASN document once created and the ASN lines cannot be modified too. Only few attributes on the header like waybill, packing slip, weights can be modified after creating ASN. And these attributes are of no interest to a WMS. So, on updating "select" attributes in the ASN header, no event is sent., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: We donot have the Inventory Tracking Attributes in ASN REST. We need to pass the Project/Task/COO to WMS for them to be able to Receive against the Project/Task against the shipment.
1.Project and task should not be able to change at the time of Receipt. WMS might need to introduce some feature to lock it down. For now its is dealt with a SOP documentation. 2. Few option evaluated.
a) Project and Task information needed by WMS on ASN Line so the ASN callback service needs to send this.
b) WMS team needs to derive this information from the PO reference passed. - Ram says technically not possible as they will never know which attributes are configured for the Project/Task out of the WMS INV tracking attributes.
c)WMS calls another API call to retrive the Project and Task from RA/PO level - INV uses this oprion on INV UI - Ram mentions this needs to be evaluated for bulk data scenarios as this might be expensive.

Decision: The proposal is to customize the out of box integration to call the PO Service to retrieve the Project/Task information.

Please note that COO information is on the ASN service already.
, Unnamed: 2: <https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=1657906878>
issue # 11., Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Single ASN line can be canceled or the entire ASN can be canceled. For each line, we send one CancelAsnNotification event containing the ASN line Id. In Fusion, we allow ASN line to be canceled even if it has been received (partially of course). If ASN is created for 10 each, user receives 6 each and uses the cancel line action, then the remaining 4 each is canceled and will not be received. But WMS does not allow cancelation after receiving.

Option 1: WMS allows Cancellation of the ASN line even after the line has been partially received.
Option 2: We go the same path as RMA. Ultimately canecllation of ASN line means a decrease in the quantity expected. So in Fusion the line is cancelled and the same line will need to be manually verified in WMS or else the line will remain open without any further receipts.

Decision: Option 2, Unnamed: 2: <https://confluence.oraclecorp.com/confluence/display/SCESG/WMS+Cloud+-+Inventory+Cloud+Integration+Working+Group+Meeting+Notes>, Unnamed: 3: , Unnamed: 4:

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24D", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "ib_shipment", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: ShipmentHeadersId, Notes: Unique WMS interface message identifier.

WMS Column: shipment_nbr, Format: string, Max: 30.0, REQD?: X, INV Column: ShipmentHeaderId, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID , Format.1: string, Max.1: 27.0, Notes: , Unnamed: 9:
WMS Column: facility_code, Format: string, Max: 20.0, REQD?: X, INV Column: ShipToOrganizationCode, Table Column: RCV_SHIPMENT_HEADERS.SHIP_TO_ORG_ID, Format.1: string, Max.1: 18.0, Notes: Single ASN can have only one destination org for all lines hence we can get this from header level too., Unnamed: 9:
WMS Column: company_code, Format: string, Max: 20.0, REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Notes: Hard-coded. Updated by customer., Unnamed: 9:
WMS Column: trailer_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: UPDATE, Table Column: , Format.1: string, Max.1: 7.0, Notes: , Unnamed: 9:
WMS Column: ref_nbr, Format: string, Max: 50.0, REQD?: X, INV Column: ShipmentNumber, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_NUM, Format.1: string, Max.1: 30.0, Notes: , Unnamed: 9:
WMS Column: shipment_type, Format: string, Max: 20.0, REQD?: X, INV Column: ASNType, Table Column: Value = "ASN" or "ASBN", Format.1: string, Max.1: 25.0, Notes: , Unnamed: 9:
WMS Column: load_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: manifest_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: trailer_type, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: vendor_info, Format: string, Max: 30.0, REQD?: , INV Column: SupplierId, Table Column: RCV_SHIPMENT_HEADERS. VENDOR_ID (the (corrosponding code coulmns), Format.1: String, Max.1: 15.0, Notes: In the later releases we will change this to Supplier Number to be inline with the change to the PO mapping, Unnamed: 9:
WMS Column: origin_info, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: origin_code, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: orig_shipped_units, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lock_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: shipped_date, Format: date, Max: 14.0, REQD?: X, INV Column: ShippedDate, Table Column: RCV_SHIPMENT_HEADERS.SHIPPED_DATE, Format.1: DateTime, Max.1: , Notes: Date and Time at RCV side and WMS side has only Date, Unnamed: 9: FA will truncate to Date only
WMS Column: orig_shipped_lpns, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_1, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_2, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_3, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_4, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_5, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: sold_to_legal_name, Format: string, Max: 240.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: returned_from_facility_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_1, Format: date, Max: 250.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_2, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_3, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_4, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_5, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_4, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_5, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_6, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_7, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_8, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_9, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_10, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_11, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_12, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:

WMS Column: seq_nbr, Format: number, Max: 9.0, REQD?: X, INV Column:

ShipmentLineNumber
, Table Column: RCV_SHIPMENT_LINES.SHIPMENT_LINE_NUM , Format.1: number, Max.1: 18, Notes: Will this need to be unique? As for same line number we can have multiple lots and in that case we will have the same line number repeated for each lot., Unnamed: 9:
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Notes: HARD CODED TO CREATE as we donot raise events at time of update/cancel of ASN. Also new line cannot be added to ASN. Update is not done on Quantity etc., Unnamed: 9:
WMS Column: lpn_nbr, Format: string, Max: 30.0, REQD?: , INV Column: SourcePackingUnit, Table Column: INV_LICENSE_PLATE_NUMBERS.LICENSE_PLATE_NUMBER(corrosponding to RCV_SHIPMENT_LINES.ASN_LPN_ID), Format.1: string, Max.1: 30, Notes: This is the innermost packing unit, Unnamed: 9:
WMS Column: lpn_weight, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lpn_volume, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_alternate_code, Format: string, Max: 130.0, REQD?: , INV Column: ItemNumber + "~^~" + ItemRevision, Table Column: RCV_SHIPMENT_LINES.ITEM_ID (corrosponding Item Number) + RCV_SHIPMENT_LINES.ITEM_REVISION, Format.1: string, Max.1: 300, Notes: Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Item Number., Unnamed: 9:
WMS Column: item_part_a, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_part_b, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_part_c, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_part_d, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_part_e, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_part_f, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pre_pack_code, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pre_pack_ratio, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pre_pack_total_units, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_a, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_b, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_c, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: shipped_qty, Format: decimal, Max: , REQD?: X, INV Column: QuantityShipped/lots.Quantity, Table Column: RCV_SHIPMENT_LINES.QUANTITY_SHIPPED/RCV_LOTS_SUPPLY.quantity, Format.1: number, Max.1: , Notes: If LOTs are present loop , Unnamed: 9:
WMS Column: priority_date, Format: date, Max: 14.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: po_nbr, Format: string, Max: 30.0, REQD?: , INV Column: PONumber, Table Column: RCV_SHIPMENT_LINES. PO_HEADER_ID (PO Number for this ID), Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pallet_nbr, Format: string, Max: 30.0, REQD?: , INV Column: PackingUnit (from PackingUnit resource), Table Column: , Format.1: string, Max.1: 30, Notes: PackingUnit when the parentLPNId is null. This is the outermost packing unit., Unnamed: 9:
WMS Column: putaway_type, Format: string, Max: 15.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: expiry_date, Format: date, Max: 14.0, REQD?: , INV Column: LotExpirationDate, Table Column: INV_LOT_NUMBER.LOT_EXPIRATION_DATE, Format.1: date, Max.1: , Notes: , Unnamed: 9:
WMS Column: batch_nbr, Format: string, Max: 25.0, REQD?: , INV Column: LotNumber, Table Column: RCV_LOTS_SUPPLY.LOT_NUM, Format.1: string, Max.1: 80, Notes: One lot per shipment line.
Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Lot Number. The issue is w.r.t the space available on the hand held and whether the 80 char lotr number will fit on to the screen of the hand held.

, Unnamed: 9:
WMS Column: recv_xdock_facility_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_1, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_2, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_3, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_4, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_field_5, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lpn_is_physical_pallet_flg, Format: boolean, Max: 5.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: po_seq_nbr, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: line_schedule_nbrs, Format: string, Max: 30.0, REQD?: X, INV Column: (POLineNumber + "~^~" + POScheduleNumber), Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pre_pack_ratio_seq, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lpn_lock_code, Format: string, Max: 15.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: item_barcode, Format: string, Max: 40.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: uom, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: INV to populate UOM Code during 22D, Unnamed: 9:
WMS Column: lpn_length, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lpn_width, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: lpn_height, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: dtl_rcv_flg, Format: boolean, Max: 5.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_d, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_e, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_f, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_g, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: receipt_advice_line, Format: string, Max: 36.0, REQD?: , INV Column: ShipmentHeaderId+ "~^~" + ShipmentlineId, Table Column: RCV SHIPMENTLINES.SHIPMENTHEADERID +
RCV SHIPMENTLINES.SHIPMENTLINEID, Format.1: string, Max.1: 18-18, Notes: This combination + Lot is unique, Unnamed: 9: WMS team is increasing the max length
WMS Column: invn_attr_h, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_i, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_j, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_k, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_l, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_m, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_n, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: invn_attr_o, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_1, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_2, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_3, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_4, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_date_5, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_decimal_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_number_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_long_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_4, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_5, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_6, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_7, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_8, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_9, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_10, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_11, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: cust_short_text_12, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24D", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "ib_shipment_serial_nbr", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: ShipmentHeadersId, Notes: Unique WMS interface message identifier.

WMS Column: action_code, Format: String, Max: 10.0, REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Comments: Hardcoded to Create
WMS Column: facility_code, Format: String, Max: 20.0, REQD?: X, INV Column: ShipToOrganizationCode, Table Column: RCV_SHIPMENT_HEADERS.SHIP_TO_ORG_ID, Format.1: number, Max.1: 18, Comments:
WMS Column: company_code, Format: String, Max: 20.0, REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Comments:
WMS Column: shipment_nbr, Format: String, Max: 30.0, REQD?: X, INV Column: ShipmentHeaderId
, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID , Format.1: string, Max.1: 18, Comments:
WMS Column: lpn_nbr, Format: String, Max: 30.0, REQD?: , INV Column: SourcePackingUnit (from the Line level), Table Column: , Format.1: , Max.1: , Comments: Innermost packing Unit
WMS Column: item_part_a, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_part_b, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_part_c, Format: String, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_part_d, Format: String, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_part_e, Format: String, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_part_f, Format: String, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: item_alternate_code, Format: String, Max: 130.0, REQD?: X, INV Column: ItemNumber + "~^~" + ItemRevision, Table Column: RCV_SHIPMENT_LINES.ITEM_ID (corrosponding Item Number) + RCV_SHIPMENT_LINES.ITEM_REVISION, Format.1: string, Max.1: 300, Comments: Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Item Number.
WMS Column: serial_nbr, Format: String, Max: 40.0, REQD?: X, INV Column: SerialNumber, Table Column: RCV_SERIALS_SUPPLY.SERIAL_NUM, Format.1: string, Max.1: 80, Comments: Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Serial Number. The issue is w.r.t the space available on the hand held and whether the 80 char lotr number will fit on to the screen of the hand held.
WMS Column: batch_nbr, Format: String, Max: 25.0, REQD?: , INV Column: LotNumber, Table Column: RCV_LOTS_SUPPLY.LOT_NUM, Format.1: string, Max.1: 80, Comments:
Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Lot Number. The issue is w.r.t the space available on the hand held and whether the 80 char lotr number will fit on to the screen of the hand held.

WMS Column: expiry_date, Format: Date, Max: 14.0, REQD?: , INV Column: ExpirationDate, Table Column: , Format.1: date, Max.1: , Comments:
WMS Column: invn_attr_a, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_b, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_c, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_d, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_e, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_f, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_g, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_h, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_i, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_j, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_k, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_l, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_m, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_n, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: invn_attr_o, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments:
WMS Column: po_nbr, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: Its already at the ib shipment dtl level- Not Needed confirmed by Ram
WMS Column: po_seq_nbr, Format: Integer, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: Its already at the ib shipment dtl level- Not Needed confirmed by Ram
WMS Column: receipt_advice_line, Format: String, Max: 36.0, REQD?: , INV Column: ShipmentHeaderId+ "~^~" + ShipmentlineId , Table Column: RCV SHIPMENTLINES.SHIPMENTHEADERID +
RCV SHIPMENTLINES.SHIPMENTLINEID, Format.1: string, Max.1: 18-18, Comments: ShipmentHeaderId+ "~^~" + ShipmentlineId +Lot will be unique

Unnamed: 0: , Unnamed: 1: , Unnamed: 2: REST API Receipt Advice
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: GET API URL - <https://fuscdrmsmc47-fa-ext.us.oracle.com/fscmRestApi/resources/latest/receiptAdviceLines?q=ExternalSystemGroupId=300100191032801>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: Document Link - <https://confluence.oraclecorp.com/confluence/display/FMM/Developer+Test+Cases+for+Manage+Receipt+Advice+REST+-+Sprint+4>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: GET API URL Describe - <https://fuscdrmsmc143-fa-ext.us.oracle.com/fscmRestApi/resources/latest/receiptAdviceLines/describe>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: Describe URL gives all the fileds with their descriptions like max-length, type of variable etc.
