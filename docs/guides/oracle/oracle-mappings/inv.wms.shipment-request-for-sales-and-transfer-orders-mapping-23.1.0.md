# inv.wms.shipment-request-for-sales-and-transfer-orders-mapping-23.1.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.shipment-request-for-sales-and-transfer-orders-mapping-23.1.0.xlsx` \n**Data de conversão:** 2025-05-15T14:40:17.620447 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.shipment-request-for-sales-and-transfer-orders-mapping-23.1.0.xlsx)**

---

## Sumário

## Resumo automático

O documento é a especificação de mapeamento da interface WMS (versão 23.1.0) para requisição de expedição de pedidos de venda e de transferência. Ele está dividido em duas partes principais:

1. Cabeçalho (Header):
   • Campos informacionais (DocumentVersion, OriginSystem, ClientEnvCode, ParentCompanyCode)
   • Controle da mensagem (Entity, TimeStamp, MessageId)
   • Valores fixos ou vindos de propriedades de integração

2. Linhas de detalhe (Detail Lines):
   • Identificação de instalação e empresa (facility_code, company_code)
   • Dados do pedido (order_nbr, order_type, ord_date, req_ship_date, sales_order_nbr, customer_po_nbr etc.)
   • Informações de cliente e destinatário (nome, endereço, contato, canal de venda)
   • Transporte e roteirização (action_code, ship_via_code, carrier_account_nbr, group_ref, externally_planned_load_flg etc.)
   • Itens e quantidades (item_alternate_code, ord_qty, uom, cost, sale_price, batch_nbr, serial_nbr)
   • Instruções, campos customizados e atributos adicionais (spl_instr, vas_group_code, cust_field_1…cust_field_5, invn_attr_a…invn_attr_o, vouchers, tolerâncias de embarque etc.)
   • Definições de formato, tamanho máximo e obrigatoriedade para cada coluna
   • Regras de transformação (extração de data antes do “T”, concatenação de campos, flags booleanas)

Além disso, o documento faz referência aos recursos REST API de Inventário da Oracle para consulta ou alteração de linhas de expedição, incluindo links para a documentação oficial.

## Conteúdo extraído

WMS Column: DocumentVersion, Format: string, Required?: , Value: "23.1.0", Notes: Informational only.
WMS Column: OriginSystem, Format: string, Required?: , Value: "Oracle Fusion Inventory Management Cloud", Notes: Informational only.
WMS Column: ClientEnvCode, Format: string, Required?: , Value: "23A", Notes: Informational only.
WMS Column: ParentCompanyCode, Format: string, Required?: , Value: Integration Properties, by default "PP", Notes: Informational only. (Hardcode)
WMS Column: Entity, Format: string, Required?: X, Value: "order", Notes: WMS interface entity code.
WMS Column: TimeStamp, Format: string, Required?: , Value: fn:current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, Format: string, Required?: X, Value: fn:current-dateTime(), Notes: Unique interface messgae identifier.

WMS Column: facility_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): OrganizationCode, INV Column (REST API - TO): OrganizationCode, Format.1: string, Max.1: 18.0, Notes:
WMS Column: company_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): company_code, INV Column (REST API - TO): company_code, Format.1: , Max.1: , Notes: Integration Properties, by default "PP"
WMS Column: order_nbr, Format: string, Max: 30.0, Required?: X, INV Column (REST API - SO): ShipmentLine, INV Column (REST API - TO): ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: order_type, Format: string, Max: 25.0, Required?: X, INV Column (REST API - SO): OrderTypeCode, INV Column (REST API - TO): OrderTypeCode, Format.1: string , Max.1: 30.0, Notes:
WMS Column: ord_date, Format: date, Max: 14.0, Required?: X, INV Column (REST API - SO): RequestedDate, INV Column (REST API - TO): RequestedDate, Format.1: datetime, Max.1: , Notes: substring-before (ns27:RequestedDate, &quot;T&quot; ) - We extract date part from FA field as WMS ord_date is date type
WMS Column: exp_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: req_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): ScheduledShipDate, INV Column (REST API - TO): ScheduledShipDate, Format.1: datetime, Max.1: , Notes: substring-before (ns27:ScheduledShipDate, &quot;T&quot; ) - We extract date part from FA field as WMS req_ship_date is date type
WMS Column: dest_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): destinationorganizationcode, Format.1: , Max.1: , Notes:
WMS Column: cust_name, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): SoldToCustomer, INV Column (REST API - TO): , Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_addr, Format: string, Max: 70.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr2, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr3, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column (REST API - SO): CREATE, INV Column (REST API - TO): CREATE, Format.1: , Max.1: , Notes: This integration is used for create action only as we have different Integration () for updating shipment
WMS Column: route_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_city, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_state, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_zip, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_country, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_phone_nbr, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): SoldToContactPhone, INV Column (REST API - TO): SoldToContactPhone, Format.1: string, Max.1: 40.0, Notes:
WMS Column: cust_email, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToEmail, INV Column (REST API - TO): SoldToEmail, Format.1: string, Max.1: , Notes:
WMS Column: cust_contact, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToContact, INV Column (REST API - TO): SoldToContact, Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: shipto_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): destinationorganizationcode, Format.1: , Max.1: , Notes:
WMS Column: shipto_name, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): ShipToCustomer, INV Column (REST API - TO): ShipToCustomer, Format.1: string, Max.1: 360.0, Notes:
WMS Column: shipto_addr, Format: string, Max: 70.0, Required?: , INV Column (REST API - SO): ShipToAddress1, INV Column (REST API - TO): ShipToAddress1, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_addr2, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): ShipToAddress2, INV Column (REST API - TO): ShipToAddress2, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_addr3, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): ShipToAddress3, INV Column (REST API - TO): ShipToAddress3, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_city, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ShipToCity, INV Column (REST API - TO): ShipToCity, Format.1: string, Max.1: 60.0, Notes:
WMS Column: shipto_state, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ShipToState, INV Column (REST API - TO): ShipToState, Format.1: string, Max.1: 120.0, Notes:
WMS Column: shipto_zip, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): ShipToPostalCode, INV Column (REST API - TO): ShipToPostalCode, Format.1: string, Max.1: 60.0, Notes:
WMS Column: shipto_country, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): ShipToCountry, INV Column (REST API - TO): ShipToCountry, Format.1: string, Max.1: 120.0, Notes:
WMS Column: shipto_phone_nbr, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): ShipToContactPhone, INV Column (REST API - TO): ShipToContactPhone, Format.1: string, Max.1: 40.0, Notes:
WMS Column: shipto_email, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: shipto_contact, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): ShipToContact, INV Column (REST API - TO): ShipToContact, Format.1: string, Max.1: 360.0, Notes:
WMS Column: dest_company_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: priority, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ship_via_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: carrier_account_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: payment_method, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: host_allocation_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: customer_po_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): CustomerPONumber, INV Column (REST API - TO): CustomerPONumber, Format.1: string, Max.1: 50.0, Notes:
WMS Column: sales_order_nbr, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): concat( Order, "-", OrderLine), INV Column (REST API - TO): concat( Order, "-", OrderLine), Format.1: , Max.1: , Notes: SalesOrder is the ERP or Order Management order number:
concat (ns27:Order, &quot;-&quot;, ns27:OrderLine )
WMS Column: sales_channel, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: dest_dept_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: start_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: stop_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: spl_instr, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: vas_group_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: currency_code, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): CurrencyCode, INV Column (REST API - TO): CurrencyCode, Format.1: string, Max.1: 15.0, Notes:
WMS Column: stage_location_barcode, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ob_lpn_type, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: gift_msg, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: sched_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: customer_po_type, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: customer_vendor_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_1  , Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_2, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_3, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_4, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_5, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_1 , Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_2, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_3, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_4, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_5, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_1 , Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_2, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_3, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_4, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_5, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_1 , Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_2, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_3, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_4, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_5, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_6, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_7, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_8, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_9, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_10, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_11, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_12, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_1 , Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_2, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_3, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: order_nbr_to_replace, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: lpn_type_class, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: billto_carrier_account_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: duties_carrier_account_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: duties_payment_method, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: customs_broker_contact, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: erp_source_hdr_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: erp_source_system_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: group_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): ShipmentSet, INV Column (REST API - TO): ShipmentSet, Format.1: string, Max.1: 150.0, Notes:
WMS Column: externally_planned_load_flg, Format: boolean, Max: , Required?: , INV Column (REST API - SO): True/False, INV Column (REST API - TO): True/False, Format.1: , Max.1: , Notes: "True" if TransportationPlanningStatusCode = "PENDING"
WMS Column: carrier_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): CarrierNumber, INV Column (REST API - TO): CarrierNumber, Format.1: string, Max.1: 30.0, Notes:
WMS Column: carrier_type, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): ModeOfTransportCode, INV Column (REST API - TO): ModeOfTransportCode, Format.1: string, Max.1: 80.0, Notes:
WMS Column: std_carrier_service_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ServiceLevelCode, INV Column (REST API - TO): ServiceLevelCode, Format.1: string, Max.1: 30.0, Notes:

WMS Column: seq_nbr, Format: number, Max: 9.0, Required?: X, INV Column - SO & TO: "1", Format.1: , Max.1: , Notes: Hard-coded. Per design, each order has a single detail.
WMS Column: item_alternate_code, Format: string, Max: 130.0, Required?: X, INV Column - SO & TO: Item + "~^~", Format.1: string, Max.1: , Notes: concat (nsmpr2:Item, "~^~" )
WMS Column: item_part_a, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_b, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_c, Format: string, Max: 20.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_d, Format: string, Max: 20.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_e, Format: string, Max: 10.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_part_f, Format: string, Max: 10.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_code, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio, Format: number, Max: , Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio_seq, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_total_units, Format: decimal, Max: , Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: ord_qty, Format: decimal, Max: , Required?: X, INV Column - SO & TO: RequestedQuantity, Format.1: number, Max.1: , Notes:
WMS Column: req_cntr_nbr, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column - SO & TO: CREATE, Format.1: , Max.1: , Notes:
WMS Column: batch_nbr, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_a, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_b, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_c, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cost, Format: decimal, Max: , Required?: X, INV Column - SO & TO: UnitPrice, Format.1: integer, Max.1: , Notes:
WMS Column: sale_price, Format: decimal, Max: , Required?: X, INV Column - SO & TO: SellingPrice, Format.1: integer, Max.1: , Notes:
WMS Column: po_nbr, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: shipment_nbr, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_a, Format: string, Max: 20.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_b, Format: string, Max: 20.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_c, Format: string, Max: 20.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr_1, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: host_ob_lpn_nbr, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: spl_instr, Format: string, Max: 255.0, Required?: , INV Column - SO & TO: NoteTxt, Format.1: attachment?, Max.1: , Notes: <xsl:for-each XML:id="id_267" select="ns27:notes">
<xsl:if XML:id="id_268" test="ns27:NoteTypeCode = &quot;LINE_SHIPPING_INSTRUCTIONS&quot;">
<xsl:value-of XML:id="id_269" select="oraext:decodeBase64 (ns27:NoteTxt )"/>
</xsl:if>
</xsl:for-each>

WMS Column: vas_activity_code, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 1000.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 1000.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: voucher_nbr, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: voucher_amount, Format: decimal, Max: 11.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: voucher_exp_date, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: req_pallet_nbr, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: string, Max: 15.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: serial_nbr, Format: string, Max: 40.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: item_barcode, Format: string, Max: 40.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: uom, Format: string, Max: 10.0, Required?: , INV Column - SO & TO: "UNITS"/"CASES"/"PACKS", Format.1: , Max.1: , Notes: "UNITS'" if OrderedQuantityUOMName = "Ea"
"CASES" if OrderedQuantityUOMName = "Cases"
"PACKS" if OrderedQuantityUOMName = "Packs"
WMS Column: cust_date_1, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_2, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_3, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_4, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_5, Format: date, Max: 14.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_1, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_2, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_3, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_4, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_5, Format: number, Max: 9.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_1, Format: decimal, Max: 9.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_2, Format: decimal, Max: 9.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_3, Format: decimal, Max: 9.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_4, Format: decimal, Max: 9.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_5, Format: decimal, Max: 9.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_1, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_2, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_3, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_4, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_5, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_6, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_7, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_8, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_9, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_10, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_11, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_12, Format: string, Max: 25.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_1, Format: string, Max: 1000.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_2, Format: string, Max: 1000.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_3, Format: string, Max: 1000.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_d, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_e, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_f, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_g, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: ship_request_line, Format: string, Max: 30.0, Required?: , INV Column - SO & TO: ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: unit_declared_value, Format: decimal, Max: 10.2, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_h, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_i, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_j, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_k, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_l, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_m, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_n, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_o, Format: string, Max: 75.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: erp_source_line_ref, Format: string, Max: 150.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: erp_source_shipment_ref, Format: string, Max: 150.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: erp_fulfillment_line_ref, Format: number, Max: 18.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: sales_order_line_ref, Format: string, Max: 150.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: sales_order_schedule_ref, Format: string, Max: 150.0, Required?: , INV Column - SO & TO: , Format.1: , Max.1: , Notes:
WMS Column: min_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column - SO & TO: 0 or UnderShipTolerancePercentage, Format.1: , Max.1: , Notes: 0 when ShippingToleranceBehavior = "REQUESTEDQUANTITY" otherwise UnderShipTolerancePercentage
WMS Column: max_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column - SO & TO: OverShipTolerancePercentage, Format.1: , Max.1: , Notes:

Unnamed: 0: , Unnamed: 1: , Unnamed: 2:
Unnamed: 0: , Unnamed: 1: , Unnamed: 2: REST API - Shipment Line Change Request & Shipment Lines
Document Link
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22c/fasrp/op-fscmrestapi-resources-11.13.18.05-shipmentlines-shipmentline-get.html>
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22c/fasrp/api-inventory-management-shipment-line-change-requests.html>
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22c/fasrp/api-inventory-management-shipment-line-transaction-requests-shipment-lines.html>
