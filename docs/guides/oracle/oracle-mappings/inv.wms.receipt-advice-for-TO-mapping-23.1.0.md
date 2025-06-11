# inv.wms.receipt-advice-for-TO-mapping-23.1.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.receipt-advice-for-TO-mapping-23.1.0.xlsx`  \n**Data de conversão:** 2025-05-15T14:39:48.641667  \n**Tipo:** .xlsx  \n**[Download original](reference/wms_solutions/mappings/inv.wms.receipt-advice-for-TO-mapping-23.1.0.xlsx)**

---

## Sumário



## Resumo automático

Este arquivo define o mapeamento da mensagem de “receipt advice” de Transfer Order (TO) gerada pelo WMS para as tabelas do Oracle Fusion Inventory Management Cloud.

Principais pontos:  
• Campos informativos de cabeçalho (fixos): versão do documento, sistema de origem, ambiente cliente, código da empresa.  
• Campos obrigatórios de cabeçalho: entidade (“ib_shipment”), identificador da mensagem, número do envio (shipment_nbr → RCV_SHIPMENT_HEADERS.SHIPMENT_NUM), código da unidade receptora (facility_code → RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID), código da empresa (“PP”), ação (“CREATE”), referência interna (ref_nbr → SHIPMENT_HEADER_ID), tipo de recebimento (“TRANSFER ORDER”) e data de envio.  
• Campos obrigatórios de linha: sequência da linha (seq_nbr → SHIPMENT_LINE_ID), ação (“CREATE”), código do item (item_alternate_code → RCV_SHIPMENT_LINES.ITEM_ID) e quantidade recebida (shipped_qty → quantity_shipped).  
• Diversos campos opcionais para unidades logísticas (LPN, pallet), lote, validade, UOM e atributos de inventário (invn_attr_a…invn_attr_o).  
• Estrutura para customizações (cust_field_1–5, cust_date_1–5, cust_decimal_1–5, cust_number_1–5, cust_short_text_1–12, cust_long_text_1–3).  
• Geração de identificador de linha de recebimento (receipt_advice_line = HEADER_ID + “~^~” + LINE_ID) para distinguir linhas idênticas.  
• Em outra entidade (“ib_shipment_serial_nbr”), mapeia também números de série (serial_nbr → RCV_SERIALS_SUPPLY.SERIAL_NUM) e seus atributos.  

Esse layout garante que o WMS entregue ao Oracle Fusion todos os dados necessários para processar o recebimento de TO de forma consistente nas tabelas RCV_SHIPMENT_HEADERS, RCV_SHIPMENT_LINES, RCV_LOTS_SUPPLY e RCV_SERIALS_SUPPLY.

## Conteúdo extraído

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "23.1.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "23A", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "ib_shipment", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: External System Group Id, Notes: Unique WMS interface message identifier.

WMS Column: shipment_nbr, Format: string, Max: 30.0, REQD?: X, INV Column: DocumentNumber, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_NUM, Format.1: string, Max.1: 80.0, Notes:
WMS Column: facility_code, Format: string, Max: 20.0, REQD?: X, INV Column: OrganizationCode, Table Column: RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID, Format.1: string, Max.1: 18.0, Notes:
WMS Column: company_code, Format: string, Max: 20.0, REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Notes: Hard-coded. Updated by customer.
WMS Column: trailer_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr, Format: string, Max: 50.0, REQD?: X, INV Column: IntransitShipmentHeaderId, Table Column:  RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID, Format.1: number, Max.1: 18.0, Notes:
WMS Column: shipment_type, Format: string, Max: 20.0, REQD?: X, INV Column: ReceiptSourceCode, Table Column:  RCV_SHIPMENT_LINES.SOURCE_DOCUMENT_CODE, Format.1: string, Max.1: 25.0, Notes: TRANSFER ORDER
WMS Column: load_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: manifest_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: trailer_type, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: vendor_info, Format: date, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: origin_info, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: origin_code, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: orig_shipped_units, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: shipped_date, Format: date, Max: 14.0, REQD?: X, INV Column: , Table Column: , Format.1: , Max.1: , Notes:
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

WMS Column: seq_nbr, Format: number, Max: 9.0, REQD?: X, INV Column: IntransitShipmentLineId, Table Column:  RCV_SHIPMENT_LINES.SHIPMENT_LINE_ID, Format.1: number, Max.1: 18, Notes: Unique Number
WMS Column: action_code, Format: string, Max: 10.0, REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_nbr, Format: string, Max: 30.0, REQD?: , INV Column: ShippingPackingUnit, Table Column: Retrieved from Package, Format.1: string, Max.1: 30, Notes:
WMS Column: lpn_weight, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_volume, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_alternate_code, Format: string, Max: 130.0, REQD?: , INV Column: ItemNumber , Table Column:  RCV_SHIPMENT_LINES.ITEM_ID, Format.1: string, Max.1: 300, Notes:
WMS Column: item_part_a, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_b, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_c, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_d, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_e, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_f, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_code, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_total_units, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_a, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_b, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_c, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: shipped_qty, Format: decimal, Max: , REQD?: X, INV Column: Quantity, Table Column: RCV_SHIPMENT_LINES.quantity_shipped, Format.1: number, Max.1: , Notes:
WMS Column: priority_date, Format: date, Max: 14.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: po_nbr, Format: string, Max: 30.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: pallet_nbr, Format: string, Max: 30.0, REQD?: , INV Column: ShippingOutermostPackingUnit, Table Column: Retrieved from Package, Format.1: string, Max.1: 30, Notes:
WMS Column: putaway_type, Format: string, Max: 15.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: expiry_date, Format: date, Max: 14.0, REQD?: , INV Column: ExpirationDate, Table Column: , Format.1: date, Max.1: , Notes:
WMS Column: batch_nbr, Format: string, Max: 25.0, REQD?: , INV Column: LotNumber, Table Column: RCV_LOTS_SUPPLY.LOT_NUM, Format.1: string, Max.1: 80, Notes:
WMS Column: recv_xdock_facility_code, Format: string, Max: 20.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 50.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_is_physical_pallet_flg, Format: boolean, Max: 5.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: po_seq_nbr, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio_seq, Format: number, Max: 9.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_lock_code, Format: string, Max: 15.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: item_barcode, Format: string, Max: 40.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: uom, Format: string, Max: 10.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_length, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_width, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: lpn_height, Format: decimal, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: dtl_rcv_flg, Format: boolean, Max: 5.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_d, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_e, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_f, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_g, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: receipt_advice_line, Format: string, Max: 30.0, REQD?: , INV Column: IntransitShipmentHeaderId + "~^~" + IntransitShipmentLineId, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID+ RCV_SHIPMENT_LINES.SHIPMENT_LINE_ID, Format.1: string, Max.1: 18-18, Notes: concat (IntransitShipmentHeaderId, "~^~", IntransitShipmentLineId)
WMS Column: invn_attr_h, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_i, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_j, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_k, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_l, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_m, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_n, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_o, Format: string, Max: 75.0, REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_1, Format: date, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Notes:
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

WMS Column: DocumentVersion, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "23.1.0", Notes: Informational only.
WMS Column: OriginSystem, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "23A", Notes: Informational only.
WMS Column: ParentCompanyCode, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: "PP", Notes: Informational only.
WMS Column: Entity, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: "ib_shipment_serial_nbr", Notes: WMS interface entity code.
WMS Column: TimeStamp, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: , Value: current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, WMS Format: string, Fusion Format: , Fusion MaxLength: , Required?: X, Value: External System Group Id, Notes: Unique WMS interface message identifier.

WMS Column: action_code, Format: String, Max: , REQD?: X, INV Column: CREATE, Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: facility_code, Format: String, Max: , REQD?: X, INV Column: OrganizationCode, Table Column: RCV_SHIPMENT_LINES.TO_ORGANIZATION_ID, Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: company_code, Format: String, Max: , REQD?: X, INV Column: "PP", Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: shipment_nbr, Format: String, Max: , REQD?: X, INV Column: DocumentNumber, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_NUM, Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: lpn_nbr, Format: String, Max: , REQD?: , INV Column: ShippingPackingUnit, Table Column: Retrieved from Package, Format.1: string, Max.1: 30, Comments: , Unnamed: 9:
WMS Column: item_part_a, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_b, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_c, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_d, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_e, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_part_f, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: item_alternate_code, Format: String, Max: , REQD?: X, INV Column: ItemNumber , Table Column:  RCV_SHIPMENT_LINES.ITEM_ID, Format.1: string, Max.1: 300, Comments: , Unnamed: 9:
WMS Column: serial_nbr, Format: String, Max: , REQD?: X, INV Column: SerialNumber, Table Column: RCV_SERIALS_SUPPLY.SERIAL_NUM, Format.1: string, Max.1: 80, Comments: , Unnamed: 9:
WMS Column: batch_nbr, Format: String, Max: , REQD?: , INV Column: LotNumber, Table Column: RCV_LOTS_SUPPLY.LOT_NUM, Format.1: string, Max.1: 80, Comments: , Unnamed: 9:
WMS Column: expiry_date, Format: Date, Max: , REQD?: , INV Column: ExpirationDate, Table Column: , Format.1: date, Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_a, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_b, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_c, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_d, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_e, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_f, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_g, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_h, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_i, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_j, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_k, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_l, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_m, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_n, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: invn_attr_o, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: po_nbr, Format: String, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: po_seq_nbr, Format: Integer, Max: , REQD?: , INV Column: , Table Column: , Format.1: , Max.1: , Comments: , Unnamed: 9:
WMS Column: receipt_advice_line, Format: String, Max: , REQD?: , INV Column: IntransitShipmentHeaderId + "~^~" + IntransitShipmentLineId, Table Column: RCV_SHIPMENT_HEADERS.SHIPMENT_HEADER_ID+ RCV_SHIPMENT_LINES.SHIPMENT_LINE_ID, Format.1: string, Max.1: 18-18, Comments: concat (IntransitShipmentHeaderId, "~^~", IntransitShipmentLineId), Unnamed: 9: Required only when same SKU exists in multiple shipment lines for same shipment
