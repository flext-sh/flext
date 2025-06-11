# inv.wms.update-shipment-request-for-sales-and-transfer-orders-mapping-24.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.update-shipment-request-for-sales-and-transfer-orders-mapping-24.4.0.xlsx`  \n**Data de conversão:** 2025-05-15T14:41:38.107944  \n**Tipo:** .xlsx  \n**[Download original](reference/wms_solutions/mappings/inv.wms.update-shipment-request-for-sales-and-transfer-orders-mapping-24.4.0.xlsx)**

---

## Sumário



## Resumo automático

Este é um guia de mapeamento para a integração “Update Shipment Request” (versão 24.4.0) entre um WMS e a API REST do Oracle Fusion Inventory Management Cloud. Nele são especificados:

1. Cabeçalho da mensagem  
   - Versão do documento, sistema de origem, código de ambiente e empresa, identificador único e carimbo de data‐hora.  
   - Tipo de entidade (“order” ou “stage_order”) e sinalizador assíncrono.

2. Campos de nível de pedido  
   - Códigos de instalação (facility_code), empresa, número e tipo de pedido.  
   - Datas (solicitação, agendamento, expiração), cliente (nome, endereço, contato) e referências (ref_nbr, customer_po_nbr, sales_order_nbr).  
   - Códigos de rota, transportadora, serviço, método de pagamento, canal de venda, prioridades, instruções especiais e diversos campos personalizados (cust_field_1…5, cust_date_1…5, cust_number_1…5, cust_decimal_1…5, cust_short_text_1…12, cust_long_text_1…3).

3. Estrutura de lista de linhas de envio  
   - Cada pedido é tratado como um único detalhe (seq_nbr=1).  
   - Para cada item: código alternativo (união de item e sufixo), quantidade requisitada (ord_qty), unidade de medida (uom), preço unitário e preço de venda.  
   - Dados adicionais: lote, número de contêiner, atributos de inventário (invn_attr_a…o), instruções de linha codificadas, campos de voucher, palete, bloqueio, números seriais, código de barras, declarações de valor aduaneiro, referências de origem (erp_source_line_ref, erp_source_shipment_ref) e tolerâncias de envio.

4. Lógica de transformação e validações  
   - Campos obrigatórios versus opcionais, formatos (string, número, data, decimal, booleano), tamanhos máximos e regras de concatenação (por exemplo, “Order‐OrderLine” ou “Item~^~”).  
   - Extração de datas e tempos, decodificação de notas em Base64, seleção de UOM a partir do nome (“Ea” → “UNITS”, “Cases” → “CASES”, “Packs” → “PACKS”).  
   - Ações suportadas (CANCEL, CHANGEORG), fluxos de criação, atualização e exclusão de solicitações de envio.

5. Controle de bloqueio para atualização de status  
   - Em caso de “shipment request for update”, são incluídos lock_code fixo (“WSH_SR_LOCK_FOR_UPDATE”), comentário padrão e flag de autocriação de bloqueio.

Em suma, o documento detalha todos os campos, regras de preenchimento e mapeamentos necessários para atualizar solicitações de embarque de pedidos de venda e transferência via WMS para o Oracle Inventory.

## Conteúdo extraído

WMS Column: DocumentVersion, Format: string, Required?: , Value: "24.4.0", Notes: Informational only.
WMS Column: OriginSystem, Format: string, Required?: , Value: "Oracle Fusion Inventory Management", Notes: Informational only.
WMS Column: ClientEnvCode, Format: string, Required?: , Value: "24D", Notes: Informational only.
WMS Column: ParentCompanyCode, Format: string, Required?: , Value: Integration Properties, be default "PP", Notes: Informational only.
WMS Column: Entity, Format: string, Required?: X, Value: "order", Notes: WMS interface entity code.
WMS Column: TimeStamp, Format: string, Required?: , Value: fn:current-dateTime(), Notes: iso format: yyyy-mm-ddTHH:MM:SS
WMS Column: MessageId, Format: string, Required?: X, Value: fn:current-dateTime(), Notes: Unique interface messgae identifier.

WMS Column: facility_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): OrganizationCode/key, INV Column (REST API - TO): OrganizationCode/key, Format.1: string, Max.1: 18.0, Notes:
WMS Column: company_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): company_code, INV Column (REST API - TO): company_code, Format.1: , Max.1: , Notes: Self Properties  - Default value is set as "PP"
WMS Column: order_nbr, Format: string, Max: 30.0, Required?: X, INV Column (REST API - SO): ShipmentLine, INV Column (REST API - TO): ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: order_type, Format: string, Max: 25.0, Required?: X, INV Column (REST API - SO): OrderTypeCode, INV Column (REST API - TO): OrderTypeCode, Format.1: string , Max.1: 30.0, Notes:
WMS Column: ord_date, Format: date, Max: 14.0, Required?: X, INV Column (REST API - SO): RequestedDate, INV Column (REST API - TO): RequestedDate, Format.1: datetime, Max.1: , Notes:
WMS Column: exp_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: req_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): ScheduledShipDate /RequestedDate, INV Column (REST API - TO): ScheduledShipDate /RequestedDate, Format.1: datetime, Max.1: , Notes:
WMS Column: dest_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): DestinationOrganizationCode, Format.1: , Max.1: , Notes:
WMS Column: cust_name, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): SoldToCustomer, INV Column (REST API - TO): SoldToCustomer, Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_addr, Format: string, Max: 70.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr2, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr3, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column (REST API - SO): ActionType /'CANCEL', INV Column (REST API - TO): ActionType /'CANCEL', Format.1: , Max.1: , Notes:
WMS Column: route_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_city, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_state, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_zip, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_country, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_phone_nbr, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): SoldToContactPhone, INV Column (REST API - TO): SoldToContactPhone, Format.1: string, Max.1: 40.0, Notes:
WMS Column: cust_email, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToEmail, INV Column (REST API - TO): SoldToEmail, Format.1: string, Max.1: , Notes:
WMS Column: cust_contact, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToContact, INV Column (REST API - TO): SoldToContact, Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: shipto_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): DestinationOrganizationCode, Format.1: , Max.1: , Notes:
WMS Column: shipto_name, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): ShipToCustomer, INV Column (REST API - TO): ShipToCustomer, Format.1: string, Max.1: 360.0, Notes:
WMS Column: shipto_addr, Format: string, Max: 70.0, Required?: , INV Column (REST API - SO): ShipToAddress1, INV Column (REST API - TO): ShipToAddress1, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_addr2, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): ShipToAddress2, INV Column (REST API - TO): ShipToAddress2, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_addr3, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): ShipToAddress3, INV Column (REST API - TO): ShipToAddress3, Format.1: string, Max.1: 240.0, Notes:
WMS Column: shipto_city, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ShipToCity, INV Column (REST API - TO): ShipToCity, Format.1: , Max.1: , Notes:
WMS Column: shipto_state, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ShipToState, INV Column (REST API - TO): ShipToState, Format.1: string, Max.1: 120.0, Notes:
WMS Column: shipto_zip, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): ShipToPostalCode, INV Column (REST API - TO): ShipToPostalCode, Format.1: string, Max.1: 60.0, Notes:
WMS Column: shipto_country, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): ShipToCountry, INV Column (REST API - TO): ShipToCountry, Format.1: string, Max.1: 120.0, Notes: Mapping changed from shiptocounty to shiptocountry in 21A
WMS Column: shipto_phone_nbr, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): ShipToContactPhone, INV Column (REST API - TO): ShipToContactPhone, Format.1: string, Max.1: 40.0, Notes:
WMS Column: shipto_email, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): ShipToFax, INV Column (REST API - TO): ShipToFax, Format.1: string, Max.1: , Notes:
WMS Column: shipto_contact, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): ShipToContact, INV Column (REST API - TO): ShipToContact, Format.1: string, Max.1: 360.0, Notes:
WMS Column: dest_company_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: priority, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ship_via_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: string, Max.1: 30.0, Notes:
WMS Column: carrier_account_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: payment_method, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: host_allocation_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: customer_po_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): CustomerPONumber, INV Column (REST API - TO): CustomerPONumber, Format.1: string, Max.1: 50.0, Notes:
WMS Column: sales_order_nbr, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): Order + "-" + OrderLine, INV Column (REST API - TO): Order + "-" + OrderLine, Format.1: , Max.1: , Notes: SalesOrder is the ERP or Order Management order number:
concat (ns27:Order, &quot;-&quot;, ns27:OrderLine )
WMS Column: sales_channel, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: dest_dept_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: start_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: stop_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: spl_instr, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: vas_group_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: currency_code, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): CurrencyCode, INV Column (REST API - TO): CurrencyCode, Format.1: , Max.1: , Notes: CurrencyCode is not populated if ActionType = CHANGEORG
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
WMS Column: erp_source_hdr_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceOrder, INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: erp_source_system_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceSystemId, INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: group_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): ShipmentSet, INV Column (REST API - TO): ShipmentSet, Format.1: string, Max.1: 150.0, Notes:
WMS Column: externally_planned_load_flg, Format: boolean, Max: , Required?: , INV Column (REST API - SO): True/False, INV Column (REST API - TO): True/False, Format.1: , Max.1: , Notes: "True" if TransportationPlanningStatusCode = "PENDING"
WMS Column: carrier_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): CarrierNumber, INV Column (REST API - TO): CarrierNumber, Format.1: string, Max.1: 30.0, Notes:
WMS Column: carrier_type, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): ModeOfTransportCode, INV Column (REST API - TO): ModeOfTransportCode, Format.1: string, Max.1: 80.0, Notes:
WMS Column: std_carrier_service_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ServiceLevelCode, INV Column (REST API - TO): ServiceLevelCode, Format.1: string, Max.1: 30.0, Notes:

WMS Column: seq_nbr, Format: number, Max: 9.0, Required?: X, INV Column: "1", Format.1: , Max.1: , Notes: Hard-coded. Per design, each order has a single detail.
WMS Column: item_alternate_code, Format: string, Max: 130.0, Required?: X, INV Column: Item + "~^~", Format.1: , Max.1: , Notes: concat (nsmpr2:Item, "~^~" )
WMS Column: item_part_a, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_b, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_c, Format: string, Max: 20.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_d, Format: string, Max: 20.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_e, Format: string, Max: 10.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_part_f, Format: string, Max: 10.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_code, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio, Format: number, Max: , Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio_seq, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_total_units, Format: decimal, Max: , Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: ord_qty, Format: decimal, Max: , Required?: X, INV Column: RequestedQuantity, Format.1: number, Max.1: , Notes:
WMS Column: req_cntr_nbr, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column: ActionType/'CANCEL', Format.1: , Max.1: , Notes:
WMS Column: batch_nbr, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_a, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_b, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_c, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cost, Format: decimal, Max: , Required?: X, INV Column: UnitPrice, Format.1: integer, Max.1: , Notes:
WMS Column: sale_price, Format: decimal, Max: , Required?: X, INV Column: SellingPrice, Format.1: integer, Max.1: , Notes:
WMS Column: po_nbr, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: shipment_nbr, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_a, Format: string, Max: 20.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_b, Format: string, Max: 20.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_c, Format: string, Max: 20.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr_1, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: host_ob_lpn_nbr, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: spl_instr, Format: string, Max: 255.0, Required?: , INV Column: NoteTxt, Format.1: attachment?, Max.1: , Notes: If "LINE_SHIPPING_INSTRUCTIONS" = NoteTypeCode
WMS Column: vas_activity_code, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 1000.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 1000.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: voucher_nbr, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: voucher_amount, Format: decimal, Max: 11.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: voucher_exp_date, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: req_pallet_nbr, Format: string, Max: 30.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: string, Max: 15.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: serial_nbr, Format: string, Max: 40.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: item_barcode, Format: string, Max: 40.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: uom, Format: string, Max: 10.0, Required?: , INV Column: "UNITS"/"CASES"/"PACKS", Format.1: , Max.1: , Notes: "UNITS'" if OrderedQuantityUOMName = "Ea"
"CASES" if OrderedQuantityUOMName = "Cases"
"PACKS" if OrderedQuantityUOMName = "Packs"
WMS Column: cust_date_1, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_2, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_3, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_4, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_date_5, Format: date, Max: 14.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_1, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_2, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_3, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_4, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_number_5, Format: number, Max: 9.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_1, Format: decimal, Max: 9.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_2, Format: decimal, Max: 9.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_3, Format: decimal, Max: 9.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_4, Format: decimal, Max: 9.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_5, Format: decimal, Max: 9.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_1, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_2, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_3, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_4, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_5, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_6, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_7, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_8, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_9, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_10, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_11, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_12, Format: string, Max: 25.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_1, Format: string, Max: 1000.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_2, Format: string, Max: 1000.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_3, Format: string, Max: 1000.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_d, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_e, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_f, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_g, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: ship_request_line, Format: string, Max: 30.0, Required?: , INV Column: ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: unit_declared_value, Format: decimal, Max: 10.2, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_h, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_i, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_j, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_k, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_l, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_m, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_n, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_o, Format: string, Max: 75.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: erp_source_line_ref, Format: string, Max: 150.0, Required?: , INV Column: SourceOrderLine, Format.1: , Max.1: , Notes:
WMS Column: erp_source_shipment_ref, Format: string, Max: 150.0, Required?: , INV Column: SourceOrderFulfillmentLine, Format.1: , Max.1: , Notes: substring( Source Order Fulfillment Line, 0.0, last-index-within-string( Source Order Fulfillment Line, ".") + 1.0)
WMS Column: erp_fulfillment_line_ref, Format: number, Max: 18.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: sales_order_line_ref, Format: string, Max: 150.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: sales_order_schedule_ref, Format: string, Max: 150.0, Required?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: min_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column: UnderShipTolerancePercentage, Format.1: , Max.1: , Notes:  '0' if ShippingToleranceBehavior = "REQUESTEDQUANTITY" else UnderShipTolerancePercentage
WMS Column: max_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column: OverShipTolerancePercentage, Format.1: , Max.1: , Notes:

WMS Column: async_flg, Format: , Max: , Required?: , INV Column (REST API - SO): false , INV Column (REST API - TO): false , Format.1: , Max.1: , Notes:
WMS Column: header, Format: , Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: entity, Format: string, Max: , Required?: , INV Column (REST API - SO): stage_order, INV Column (REST API - TO): stage_order, Format.1: , Max.1: , Notes: WMS interface entity code.
WMS Column: facility_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): OrganizationCode, INV Column (REST API - TO): OrganizationCode, Format.1: string, Max.1: 18.0, Notes:
WMS Column: company_code, Format: string, Max: 20.0, Required?: X, INV Column (REST API - SO): company_code, INV Column (REST API - TO): company_code, Format.1: , Max.1: , Notes: Integration Properties, by default "PP"
WMS Column: messageid, Format: string, Max: , Required?: , INV Column (REST API - SO): fn:current-dateTime(), INV Column (REST API - TO): fn:current-dateTime(), Format.1: , Max.1: , Notes: Unique interface messgae identifier.
WMS Column: document_version, Format: string, Max: , Required?: , INV Column (REST API - SO): "24.4.0", INV Column (REST API - TO): "24.4.0", Format.1: , Max.1: , Notes: Informational only.
WMS Column: origin_system, Format: string, Max: , Required?: , INV Column (REST API - SO): "Oracle Fusion Inventory Management Cloud", INV Column (REST API - TO): "Oracle Fusion Inventory Management Cloud", Format.1: , Max.1: , Notes: Informational only.
WMS Column: client_env_code, Format: string, Max: , Required?: , INV Column (REST API - SO): "24D", INV Column (REST API - TO): "24D", Format.1: , Max.1: , Notes: Informational only.
WMS Column: stage_order_list, Format: , Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: order_nbr, Format: string, Max: 30.0, Required?: X, INV Column (REST API - SO): ShipmentLine, INV Column (REST API - TO): ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: order_type, Format: string, Max: 25.0, Required?: X, INV Column (REST API - SO): OrderTypeCode, INV Column (REST API - TO): OrderTypeCode, Format.1: string , Max.1: 30.0, Notes:
WMS Column: ord_date, Format: date, Max: 14.0, Required?: X, INV Column (REST API - SO): RequestedDate, INV Column (REST API - TO): RequestedDate, Format.1: datetime, Max.1: , Notes: substring-before (ns27:RequestedDate, &quot;T&quot; ) - We extract date part from FA field as WMS ord_date is date type
WMS Column: exp_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: req_ship_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): ScheduledShipDate /RequestedDate, INV Column (REST API - TO): ScheduledShipDate /RequestedDate, Format.1: datetime, Max.1: , Notes: substring-before (ns27:ScheduledShipDate, &quot;T&quot; ) -  We extract date part from FA field as WMS req_ship_date is date type
WMS Column: dest_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): destinationorganizationcode, Format.1: , Max.1: , Notes:
WMS Column: cust_name, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): SoldToCustomer, INV Column (REST API - TO): SoldToCustomer, Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_addr, Format: string, Max: 70.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr2, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_addr3, Format: string, Max: 100.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr, Format: string, Max: 50.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column (REST API - SO): ActionType /'CANCEL', INV Column (REST API - TO): ActionType /'CANCEL', Format.1: , Max.1: , Notes: This integration is used for create action only as we have different Integration () for updating shipment
WMS Column: route_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_city, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_state, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_zip, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_country, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_phone_nbr, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): SoldToContactPhone, INV Column (REST API - TO): SoldToContactPhone, Format.1: string, Max.1: 40.0, Notes:
WMS Column: cust_email, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToEmail, INV Column (REST API - TO): SoldToEmail, Format.1: string, Max.1: , Notes:
WMS Column: cust_contact, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): SoldToContact, INV Column (REST API - TO): SoldToContact, Format.1: string, Max.1: 360.0, Notes:
WMS Column: cust_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: shipto_facility_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): DestinationOrganizationCode, Format.1: , Max.1: , Notes:
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
WMS Column: erp_source_hdr_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceOrder, INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: erp_source_system_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceSystemId, INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: group_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): ShipmentSet, INV Column (REST API - TO): ShipmentSet, Format.1: string, Max.1: 150.0, Notes:
WMS Column: externally_planned_load_flg, Format: boolean, Max: , Required?: , INV Column (REST API - SO): True/False, INV Column (REST API - TO): True/False, Format.1: , Max.1: , Notes: "True" if TransportationPlanningStatusCode = "PENDING"
WMS Column: carrier_code, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): CarrierNumber, INV Column (REST API - TO): CarrierNumber, Format.1: string, Max.1: 30.0, Notes:
WMS Column: carrier_type, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): ModeOfTransportCode, INV Column (REST API - TO): ModeOfTransportCode, Format.1: string, Max.1: 80.0, Notes:
WMS Column: std_carrier_service_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ServiceLevelCode, INV Column (REST API - TO): ServiceLevelCode, Format.1: string, Max.1: 30.0, Notes:
WMS Column: stage_order_hdr_instr_list, Format: , Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: stage_order_dtl_list, Format: , Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: seq_nbr, Format: number, Max: 9.0, Required?: X, INV Column (REST API - SO): "1", INV Column (REST API - TO): "1", Format.1: , Max.1: , Notes: Hard-coded. Per design, each order has a single detail.
WMS Column: action_code, Format: string, Max: 10.0, Required?: X, INV Column (REST API - SO): ActionType/'CANCEL', INV Column (REST API - TO): ActionType/'CANCEL', Format.1: , Max.1: , Notes:
WMS Column: item_alternate_code, Format: string, Max: 130.0, Required?: X, INV Column (REST API - SO): Item + "~^~", INV Column (REST API - TO): Item + "~^~", Format.1: string, Max.1: , Notes: concat (nsmpr2:Item, "~^~" )
WMS Column: item_part_a, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_part_b, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_part_c, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_part_d, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_part_e, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_part_f, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio, Format: number, Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_ratio_seq, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: pre_pack_total_units, Format: decimal, Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ord_qty, Format: decimal, Max: , Required?: X, INV Column (REST API - SO): RequestedQuantity, INV Column (REST API - TO): RequestedQuantity, Format.1: number, Max.1: , Notes:
WMS Column: stage_order_dtl_required_serial_nbr, Format: , Max: , Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: req_cntr_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: batch_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_a, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_b, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_c, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_d, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_e, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_f, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_g, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_h, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_i, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_j, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_k, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_l, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_m, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_n, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: invn_attr_o, Format: string, Max: 75.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cost, Format: decimal, Max: , Required?: X, INV Column (REST API - SO): UnitPrice, INV Column (REST API - TO): UnitPrice, Format.1: integer, Max.1: , Notes:
WMS Column: sale_price, Format: decimal, Max: , Required?: X, INV Column (REST API - SO): SellingPrice, INV Column (REST API - TO): SellingPrice, Format.1: integer, Max.1: , Notes:
WMS Column: po_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: shipment_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_a, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_b, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: dest_facility_attr_c, Format: string, Max: 20.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ref_nbr_1, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: host_ob_lpn_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: spl_instr, Format: string, Max: 255.0, Required?: , INV Column (REST API - SO): NoteTxt, INV Column (REST API - TO): NoteTxt, Format.1: attachment?, Max.1: , Notes: <xsl:for-each xml:id="id_267" select="ns27:notes">
 <xsl:if xml:id="id_268" test="ns27:NoteTypeCode =  &quot;LINE_SHIPPING_INSTRUCTIONS&quot;">
        <xsl:value-of xml:id="id_269" select="oraext:decodeBase64 (ns27:NoteTxt )"/>
 </xsl:if>
 </xsl:for-each>

WMS Column: vas_activity_code, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_1, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_2, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_3, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_4, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_field_5, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: voucher_nbr, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: voucher_amount, Format: decimal, Max: 11.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: voucher_exp_date, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: req_pallet_nbr, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: string, Max: 15.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: serial_nbr, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: item_barcode, Format: string, Max: 40.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: uom, Format: string, Max: 10.0, Required?: , INV Column (REST API - SO): "UNITS"/"CASES"/"PACKS", INV Column (REST API - TO): "UNITS"/"CASES"/"PACKS", Format.1: , Max.1: , Notes: "UNITS'" if OrderedQuantityUOMName = "Ea"
"CASES" if OrderedQuantityUOMName = "Cases"
"PACKS" if OrderedQuantityUOMName = "Packs"
WMS Column: cust_date_1, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_2, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_3, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_4, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_date_5, Format: date, Max: 14.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_1, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_2, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_3, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_4, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_number_5, Format: number, Max: 9.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_1, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_2, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_3, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_4, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_decimal_5, Format: decimal, Max: 9.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_short_text_1, Format: string, Max: 25.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
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
WMS Column: cust_long_text_1, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_2, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: cust_long_text_3, Format: string, Max: 1000.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: ship_request_line, Format: string, Max: 30.0, Required?: , INV Column (REST API - SO): ShipmentLine, INV Column (REST API - TO): ShipmentLine, Format.1: integer, Max.1: 18.0, Notes:
WMS Column: unit_declared_value, Format: decimal, Max: 10.2, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: erp_source_line_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceOrderLine, INV Column (REST API - TO): SourceOrderLine, Format.1: , Max.1: , Notes:
WMS Column: erp_source_shipment_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): SourceOrderFulfillmentLine, INV Column (REST API - TO): SourceOrderFulfillmentLine, Format.1: , Max.1: , Notes: substring( Source Order Fulfillment Line, 0.0, last-index-within-string( Source Order Fulfillment Line, ".") + 1.0)
WMS Column: erp_fulfillment_line_ref, Format: number, Max: 18.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: sales_order_line_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: sales_order_schedule_ref, Format: string, Max: 150.0, Required?: , INV Column (REST API - SO): , INV Column (REST API - TO): , Format.1: , Max.1: , Notes:
WMS Column: min_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column (REST API - SO): 0 or UnderShipTolerancePercentage, INV Column (REST API - TO): 0 or UnderShipTolerancePercentage, Format.1: , Max.1: , Notes: 0 when ShippingToleranceBehavior = "REQUESTEDQUANTITY" otherwise UnderShipTolerancePercentage
WMS Column: max_shipping_tolerance_percentage, Format: , Max: , Required?: , INV Column (REST API - SO): OverShipTolerancePercentage, INV Column (REST API - TO): OverShipTolerancePercentage, Format.1: , Max.1: , Notes:

WMS Column: lock_code, Format: string, Required?: , Value: "WSH_SR_LOCK_FOR_UPDATE", Notes:
WMS Column: comments, Format: string, Required?: , Value: "The shipment line was placed on hold by a shipment request for update.", Notes:
WMS Column: autocreate_lock_flag, Format: string, Required?: , Value: True, Notes:
WMS Column: , Format: , Required?: , Value: , Notes:
WMS Column: , Format: , Required?: , Value: Looks like ActionType = CHANGORG is DELETE flow else UPDATE flow of SR, Notes:
