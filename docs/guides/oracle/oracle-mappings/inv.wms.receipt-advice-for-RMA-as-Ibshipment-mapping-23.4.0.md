# inv.wms.receipt-advice-for-RMA-as-Ibshipment-mapping-23.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.receipt-advice-for-RMA-as-Ibshipment-mapping-23.4.0.xlsx` \n**Data de conversão:** 2025-05-15T14:39:37.820117 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.receipt-advice-for-RMA-as-Ibshipment-mapping-23.4.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento é um guia de mapeamento entre o WMS (Sistema de Gestão de Armazém) e o Oracle Fusion Inventory para o processamento de Recebimento de RMA como Inbound Shipment. Os principais pontos são:

1. Cabeçalho do Mensagem (Header)

   - Campos informacionais: DocumentVersion (24.4.0), OriginSystem, ClientEnvCode, ParentCompanyCode, TimeStamp e MessageId (identificador único).
   - Entity identifica o tipo de interface: “ib_shipment” ou “ib_shipment_serial_nbr”.
   - Ação (action_code) define CREATE, UPDATE ou DELETE.

2. Mapeamento de Campos de Cabeçalho de Envio (Shipment Headers)

   - shipment_nbr → RCV_SHIPMENT_HEADERS.RA_DOCUMENT_NUMBER (RMA Number).
   - facility_code → RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID.
   - company_code fixo (“PP”).
   - ref_nbr → SOURCE_DOCUMENT_NUMBER (ordem de venda original).
   - shipment_type sempre “RMA”.
   - shipped_date → RA_DOC_CREATION_DATE.
   - Vários campos livres (cust_field_x, cust_date_x etc.) para customizações.

3. Mapeamento de Linhas de Envio (Shipment Lines)

   - seq_nbr → LINE_NUMBER.
   - item_alternate_code concatena ItemNumber e ItemRevision.
   - shipped_qty → RA_QUANTITY_EXPECTED.
   - batch_nbr (lot number) e expiry_date mapeados para supply de lotes.
   - receipt_advice_line reúne RMAHeaderId e RMALineId para unicidade por lote.
   - Vários atributos de inventário e campos customizáveis.

4. Mapeamento de Números de Série

   - Uma entidade separada (“ib_shipment_serial_nbr”).
   - Campos obrigatórios: facility_code, shipment_nbr, item_alternate_code, serial_nbr.

5. Tamanhos de Campo e Ajustes

   - Identificação de discrepâncias de comprimento entre WMS e Fusion (marcadas em vermelho).
   - Decisões de manter tamanhos maiores no Fusion e documentar limitações em dispositivos móveis.

6. Discussões, Decisões e Premissas de RMA

   - Novo RMA deve ser criado para cada adição de linha; não se adicionam linhas a um RMA existente.
   - Diminuir quantidade via cancelamento não atualiza WMS automaticamente; documenta-se que seria preciso “auto-verify” no WMS.
   - Reenvio (resend) da mensagem sobrescreve o inbound shipment completo; recomenda-se documentar uso cuidadoso dessa opção.
   - Não há suporte a SKU não antecipado em RMA.

7. Integração REST API
   - Exemplo de URL para consulta de receiptAdviceLines filtrando por ExternalSystemGroupId.
   - Endpoints de descrição de metadados (“describe”) para obter detalhes de tipos, comprimentos e obrigatoriedade de campos.

Em suma, o documento padroniza todos os campos necessários, suas regras de validação e tratamentos especiais para intercâmbio de informações de RMA entre o WMS e o Oracle Fusion Inventory Cloud.

## Conteúdo extraído

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "24D", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "ib_shipment", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: External System Group Id, Notes: Unique WMS interface message identifier.

WMS Column: shipment_nbr, Format: string, Max: 30.0, REQD?: X, INV Column: DocumentNumber, Table Column: RCV_SHIPMENT_HEADERS.RA_DOCUMENT_NUMBER, Format.1: string, Max.1: 27.0, Notes:
WMS Column: facility_code, Format: string, Max: 20.0, REQD?: X, INV Column: OrganizationCode, Table Column: RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID, Format.1: string, Max.1: 18.0, Notes: The same RMA Header can have multiple lines across various To Organizations. So in that case multiple shipment headers need to be created for each group of TO_ORGANIZATION_ID
WMS Column: company_code, Format: string, Max: 20.0, REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Notes: Hard-coded. Updated by customer.
WMS Column: trailer_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: "UPDATE", Table Column: RCV_SHIPMENT_HEADERS.RA_LAST_ACTION_CODE, Format.1: string, Max.1: 7.0, Notes: CREATE/UPDATE/DELETE
WMS Column: ref_nbr, Format: string, Max: 50.0, REQD?: X, INV Column: OriginalSourceOrderNumber, Table Column: RCV_SHIPMENT_HEADERS.SOURCE_DOCUMENT_NUMBER, Format.1: number, Max.1: 18.0, Notes: Still to be anlayzed if its possible to do that. The idea is to send the Sales Order Number information for the RMA document where we have the reference rma lines.
WMS Column: shipment_type, Format: string, Max: 20.0, REQD?: X, INV Column: SourceDocumentTypeCode, Table Column: Value = "RMA", Format.1: string, Max.1: 25.0, Notes: Over Receipt should not be allowed
WMS Column: load_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: manifest_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: trailer_type, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: vendor_info, Format: date, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: origin_info, Format: string, Max: 30.0, REQD?: , INV Column: CustomerName, Table Column: HZ_PARTIES.CUSTOMER_PARTY_NAME, Format.1: , Max.1: , Notes:
WMS Column: origin_code, Format: string, Max: 10.0, REQD?: , INV Column: CustomerId, Table Column: RCV_SHIPMENT_LINES.CUSTOMER_ID, Format.1: , Max.1: , Notes:
WMS Column: orig_shipped_units, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: shipped_date, Format: date, Max: 14.0, REQD?: X, INV Column: DocumentCreationDate, Table Column: RCV_SHIPMENT_HEADERS.RA_DOC_CREATION_DATE, Format.1: DateTime, Max.1: , Notes: FA will truncate
WMS Column: orig_shipped_lpns, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: sold_to_legal_name, Format: string, Max: 240.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: returned_from_facility_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_1, Format: date, Max: 250.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_2, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_3, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_4, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_5, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_1, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_2, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_3, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_4, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_5, Format: number, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_1, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_2, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_3, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_4, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_5, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_6, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_7, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_8, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_9, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_10, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_11, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_12, Format: string, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:

WMS Column: seq_nbr, Format: number, Max: 9.0, REQD?: X, INV Column: ShipmentLineNumber, Table Column: RCV_SHIPMENT_LINES.LINE_NUMBER , Format.1: number, Max.1: 18, Notes: Will this need to be unique? As for same line number we can have multiple lots and in that case we will have the same line number repeated for each lot., Unnamed: 9:
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: ActionCode, Table Column: RCV_SHIPMENT_HEADERS.RA_LAST_ACTION_CODE, Format.1: , Max.1: , Notes: CREATE/CANCEL/UPDATE, Unnamed: 9:
WMS Column: lpn_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: string, Max.1: 30, Notes: No LPN information for RMA, Unnamed: 9:
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
WMS Column: shipped_qty, Format: decimal, Max: , REQD?: X, INV Column: Quantity, Table Column: RCV_SHIPMENT_LINES.RA_QUANTITY_EXPECTED, Format.1: number, Max.1: , Notes: , Unnamed: 9:
WMS Column: priority_date, Format: date, Max: 14.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: po_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: pallet_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: string, Max.1: 30, Notes: No LPN information for RMA, Unnamed: 9:
WMS Column: putaway_type, Format: string, Max: 15.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes: , Unnamed: 9:
WMS Column: expiry_date, Format: date, Max: 14.0, REQD?: , INV Column: ExpirationDate, Table Column: INV_LOT_NUMBERS.LOT_EXPIRATION_DATE, Format.1: date, Max.1: , Notes: , Unnamed: 9:
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
WMS Column: receipt_advice_line, Format: string, Max: 30.0, REQD?: , INV Column: RMAHeaderId + "~^~" + ns31:RMALineId, Table Column: RCV SHIPMENTLINES.SHIPMENTHEADERID +
RCV SHIPMENTLINES.SHIPMENTLINEID, Format.1: string, Max.1: 18-18, Notes: concat (RMAHeaderId,"~^~", RMALineId) - For RMA. Please note that (RMAHeaderId,"~^~", RMALineId) + LotNumber will be unique as for the same RMA line you can have more than 1 lot numbers and in that case there will be multiple lines in ib Shipment Detail i.e. one per lot number., Unnamed: 9: WMS is expanding the size.
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

WMS Column: DocumentVersion, WMS Format: string, Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Required?: , Value: "24D", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Required?: X, Value: "ib_shipment_serial_nbr", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Required?: X, Value: External System Group Id, Notes: Unique WMS interface message identifier.

WMS Column: action_code, Format: String, Max: 10.0, REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Comments: CREATE and DELETE, Unnamed: 9:
WMS Column: facility_code, Format: String, Max: 20.0, REQD?: X, INV Column: OrganizationCode, Table Column: RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID, Format.1: number, Max.1: 18, Comments: , Unnamed: 9:
WMS Column: company_code, Format: String, Max: 20.0, REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: shipment_nbr, Format: String, Max: 30.0, REQD?: X, INV Column: ShipmentHeaderId + date time (12 chars), Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID + datetime, Format.1: , Max.1: 18+, Comments: , Unnamed: 9:
WMS Column: lpn_nbr, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: string, Max.1: 30, Comments: NO Packing Unit information for RMA, Unnamed: 9:
WMS Column: item_part_a, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_b, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_c, Format: String, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_d, Format: String, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_e, Format: String, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_f, Format: String, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_alternate_code, Format: String, Max: 130.0, REQD?: X, INV Column: ItemNumber + "~^~" + ItemRevision, Table Column: RCV_SHIPMENT_LINES.ITEM_ID (corrosponding Item Number) + RCV_SHIPMENT_LINES.ITEM_REVISION, Format.1: string, Max.1: 300, Comments: Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Item Number., Unnamed: 9:
WMS Column: serial_nbr, Format: String, Max: 40.0, REQD?: X, INV Column: SerialNumber, Table Column: RCV_SERIALS_SUPPLY.SERIAL_NUM, Format.1: string, Max.1: 80, Comments: Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Serial Number. The issue is w.r.t the space available on the hand held and whether the 80 char lotr number will fit on to the screen of the hand held., Unnamed: 9:
WMS Column: batch_nbr, Format: String, Max: 25.0, REQD?: , INV Column: LotNumber, Table Column: RCV_LOTS_SUPPLY.LOT_NUM, Format.1: string, Max.1: 80, Comments:
Discussed with Mike and he is fine with the size mismatch and we can revisit once the customer has a use case for such a big length for Lot Number. The issue is w.r.t the space available on the hand held and whether the 80 char lotr number will fit on to the screen of the hand held.

, Unnamed: 9:
WMS Column: expiry_date, Format: Date, Max: 14.0, REQD?: , INV Column: ExpirationDate, Table Column: , Format.1: date, Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_a, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_b, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_c, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_d, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_e, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_f, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_g, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_h, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_i, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_j, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_k, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_l, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_m, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_n, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_o, Format: String, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: po_nbr, Format: String, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: po_seq_nbr, Format: Integer, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: receipt_advice_line, Format: String, Max: 30.0, REQD?: , INV Column: RMAHeaderId + "~^~" + ns31:RMALineId, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID+ RCV_SHIPMENT_LINES.SHIPMENT_LINE_ID, Format.1: string, Max.1: 18-18, Comments: concat (RMAHeaderId, "~^~", RMALineId), Unnamed: 9: WMS is going to expand the size.

Unnamed: 0: , Unnamed: 1: RMA Open Issues, Unnamed: 2: Owning team, Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: WMS team needs to check on all columns where max size is marked Red. This indicates that there is a mismatch in the size between Fusion Apps and WMS Apps more specifically the max column size in fusion is larger than WMS max column size., Unnamed: 2: WMS, Unnamed: 3: Closed, Unnamed: 4: The respective fields marked oin red are updated with the decision from WMS team.
Unnamed: 0: , Unnamed: 1: WMS Team needs to confirm if they are ok and the partical sceanrios like scanning the Shipment Number will work out if INV passes DocumentNumber + SysdateTime

New Dsicussion: The Shipment_nbr will be mapped only to DocumentNumber (RMA Number). It will be documented that any new lines should not be added to an existng RMA but a new RMA needs to be created. This is to cter to a shorfall in WMS where in case of resending the shipment the whole shipment will be overwritten.
Also with this approach the resend option will work fine and will not create a new shipment in WMS (In case of timestamp being appended it would have created a new document in WMS). But we need to document that the Resend option should not be used with the RMA Line Number, Unnamed: 2: WMS, Unnamed: 3: Closed, Unnamed: 4: Decision is to use the ShipmentHeaderid + runing sequence for mapping documentnumber.
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: RMA Discussions/Assumptions, Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Need to have Fusion RMA and line number and Original SO and Line number reference in WMS Inbound Shipment/Line level.
Per Mike: Original SO and Line number: Should/Nice to have... doesn't need to be part of this flext_project
Decision:
Short term: Use RMA+datetimestamp as the document reference for each payload coming from INV; Document that customers can additionally add the RMA and/or SO reference into the custom fields.
Longer Term: GAP: WMS to add document number and line number columns to the inbound shipment

, Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Fusion RMA allows updating(Only decreasing the quantity) the Returned quantity, whereas WMS wont allow any changes to IB Shipment once the receiving is started. For example: when the RMA got created for 10units and initially customer has returned 3units and later he can request for remaining quantity cancellation. This will lead to a mismatch between Fusion and WMS and this is the same behavior for PO integration.

    Option: If there is a quantity decrease / cancellation, could call the auto-verify the inbound order in WMS which blocks additional receipts
        This would block all of the receipts (i.e. other lines)
        Decision: the shorted quantity would be remain open in WMS even though it's closed in INV. We can document that if they don't want to see the open quantity in WMS, they would need to verify it. , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:

Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: For RMA in Fusion we cannot add a new line (Unreferenced Return) to an existing RMA. The user will need to create a new RMA to add any line. It should not be added to an existing RMA Document. This needs to be documented., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Unanticipated SKU will not be supported for RMA Shipment and should be documented., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
Unnamed: 0: , Unnamed: 1: Resend option for Receipt Advice should work without issues provided the Shipment in the WMS side is not in Receiving status. But the resend option should not be used with RMA Line number else it creaes an issue on WMS i.e. the WMS shipment will be overwritten with just this line., Unnamed: 2: , Unnamed: 3: , Unnamed: 4:

Unnamed: 0: , Unnamed: 1: , Unnamed: 2: REST API Receipt Advice
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: GET API URL - <https://fuscdrmsmc47-fa-ext.us.oracle.com/fscmRestApi/resources/latest/receiptAdviceLines?q=ExternalSystemGroupId=300100191032801>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: Document Link - <https://confluence.oraclecorp.com/confluence/display/FMM/Developer+Test+Cases+for+Manage+Receipt+Advice+REST+-+Sprint+4>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: GET API URL Describe - <https://fuscdrmsmc143-fa-ext.us.oracle.com/fscmRestApi/resources/latest/receiptAdviceLines/describe>
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: Describe URL gives all the fileds with their descriptions like max-length, type of variable etc.
