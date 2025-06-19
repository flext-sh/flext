# wms.inv.shipment-confirmation-for-sales-orders-mapping-23.1.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/wms.inv.shipment-confirmation-for-sales-orders-mapping-23.1.0.xlsx` \n**Data de conversão:** 2025-05-15T14:42:55.183355 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/wms.inv.shipment-confirmation-for-sales-orders-mapping-23.1.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento é uma especificação de mapeamento (versão 23.1.0) para a integração entre um WMS e o serviço REST “Shipment Transaction Requests” da Oracle Cloud SCM, usado na confirmação de remessas de pedidos de venda em lote. Nele são definidos:

• Estrutura geral do payload
 – Campos de cabeçalho: id, path (“/shipmentTransactionRequests”), operation (“create”), ActionCode (“CreateAndConfirmShipment”).
 – Array shipments contendo, para cada parada ou carga:
 • Shipment (identificador de remessa)
 • ShipFromOrganizationCode (filial), BillOfLading, Waybill
 • GrossWeight/WeightUOMCode e Volume/VolumeUOMCode (com possibilidade de usar unidades definidas em propriedade de integração)
 • ActualShipDate, ExternalSystemTransactionReference, CarrierNumber, ModeOfTransportCode, ServiceLevelCode

• Unidades de embalagem
 – outerPackingUnits e innerPackingUnits, cada um com PackingUnit (número de pallet ou LPN), PackingUnitType (definido por propriedade), GrossWeight, Volume e suas UOMs

• Linhas embarcadas (packedLines)
 – ShipmentLine (nº da linha), Item (código alternativo), ShippedQuantity/ShippedQuantityUOMCode (considerando propriedade de UOM), RequestedQuantityToConsume, LoadingSequence, TrackingNumber, Subinventory

• Rastreamento de lote e série
 – Se o SKU for controlado por lote: array lots com Lot, Subinventory, Quantity
 – Se for controlado por série: array serials com FromSerialNumber, ToSerialNumber, Subinventory

• Regras e observações de formatação
 – Tamanhos máximos de campos, obrigatoriedade, concatenações (por exemplo load_manifest_nbr+“-”+seq_nbr ou shipto_zip)
 – Uso de propriedades de integração para definições padrão de UOM e tipos de embalagem
 – Suporte a cenários de múltiplos pontos de entrega no fluxo Parcel

Finalmente, o documento cita links para a documentação oficial do serviço REST e para casos de teste de batch processing, servindo de guia para desenvolvimento ou configuração do conector entre o WMS e o Oracle SCM.

## Conteúdo extraído

INV -REST: parts, Format: , Max: , WMS Column: , Format.1: , Max.1: , REQD?: , Notes:
INV -REST: id, Format: , Max: , WMS Column: unique id within payload for batch processing, Format.1: , Max.1: , REQD?: , Notes: position ()
INV -REST: path, Format: , Max: , WMS Column: "/shipmentTransactionRequests", Format.1: , Max.1: , REQD?: , Notes:
INV -REST: operation, Format: , Max: , WMS Column: "create", Format.1: , Max.1: , REQD?: , Notes:
INV -REST: payload, Format: , Max: , WMS Column: , Format.1: , Max.1: , REQD?: , Notes:
INV -REST: ActionCode, Format: string, Max: , WMS Column: CreateAndConfirmShipment, Format.1: , Max.1: , REQD?: , Notes:
INV -REST: shipments, Format: , Max: , WMS Column: , Format.1: , Max.1: , REQD?: , Notes:
INV -REST: Shipment, Format: String, Max: 30.0, WMS Column: load_manifest_nbr+"-"+seq_nbr (for Load flow)
load_manifest_nbr+"-"+shipto_zip (for Parcel flow), Format.1: String, Max.1: , REQD?: , Notes: In Parcel flow, to support multi stop scenario, Shipment mapping uses shipto_zip
INV -REST: ShipFromOrganizationCode, Format: String, Max: 240.0, WMS Column: facility_code, Format.1: String, Max.1: 20.0, REQD?: , Notes:
INV -REST: BillOfLading, Format: String, Max: 50.0, WMS Column: stop_bol_nbr, Format.1: String, Max.1: 30.0, REQD?: , Notes:
INV -REST: GrossWeight, Format: Number, Max: , WMS Column: total_weight, Format.1: Number, Max.1: , REQD?: , Notes: Sum of Container weight for the stop
INV -REST: WeightUOMCode, Format: String, Max: 25.0, WMS Column: weight_uom_code, Format.1: , Max.1: , REQD?: , Notes: Integration property "consider_wt_vol_uom_from_property" =" yes" use weight_uom from integration properties(default is "Lbs"), else use weight_uom_code from weight_uom_code.
INV -REST: Volume, Format: Number, Max: , WMS Column: total_volume, Format.1: Number, Max.1: , REQD?: , Notes: Sum of Container volume for the stop
INV -REST: VolumeUOMCode, Format: String, Max: 25.0, WMS Column: volume_uom_code, Format.1: , Max.1: , REQD?: , Notes: Integration property "consider_wt_vol_uom_from_property = yes" use volume_uom from integration properties(default is "FT3"), else use volume_uom_code from volume_uom_code.
INV -REST: Waybill, Format: String, Max: 30.0, WMS Column: pro_nbr, Format.1: String, Max.1: 30.0, REQD?: , Notes:
INV -REST: ActualShipDate, Format: datetime, Max: , WMS Column: sched_delivery_date, Format.1: date, Max.1: , REQD?: , Notes:
INV -REST: ExternalSystemTransactionReference, Format: String, Max: 100.0, WMS Column: load_manifest_nbr+"-"+seq_nbr, Format.1: , Max.1: , REQD?: , Notes:
INV -REST: CarrierNumber, Format: String, Max: 30.0, WMS Column: carrier_nbr, Format.1: String, Max.1: 20.0, REQD?: , Notes:
INV -REST: ModeOfTransportCode, Format: String, Max: 30.0, WMS Column: carrier_type, Format.1: String, Max.1: 255.0, REQD?: , Notes:
INV -REST: ServiceLevelCode, Format: string, Max: 30.0, WMS Column: std_carrier_service_code, Format.1: String, Max.1: 30.0, REQD?: , Notes:

INV -REST: outerPackingUnits, Format: , Max: , WMS Column: , Format.1: , Max.1: , Notes:
INV -REST: PackingUnit, Format: , Max: , WMS Column: pallet_nbr, Format.1: , Max.1: , Notes:
INV -REST: PackingUnitType, Format: , Max: , WMS Column: outer_packing_unit_type from Integration property (Default - Pallet), Format.1: , Max.1: , Notes: $selfProperties/nsmpr4:properties/nsmpr4:outer_packing_unit_type
This field's value should to pre-existing in Fusion
INV -REST: innerPackingUnits, Format: , Max: , WMS Column: , Format.1: , Max.1: , Notes:
INV -REST: PackingUnit, Format: , Max: , WMS Column: ob_lpn_nbr, Format.1: , Max.1: , Notes:
INV -REST: PackingUnitType, Format: , Max: , WMS Column: inner_packing_unit_type from Integration property (Default - WMS_OBLPN), Format.1: , Max.1: , Notes: $selfProperties/nsmpr4:properties/nsmpr4:inner_packing_unit_type
This field's value should to pre-existing in Fusion
INV -REST: GrossWeight, Format: Number, Max: , WMS Column: ob_lpn_weight, Format.1: Number, Max.1: , Notes:
INV -REST: GrossWeightUOMcode, Format: , Max: , WMS Column: weight_uom_code, Format.1: , Max.1: , Notes: Integration property "consider_wt_vol_uom_from_property = yes" use weight_uom from integration properties(default is "Lbs"), else use weight_uom_code from weight_uom_code.
INV -REST: Volume, Format: Number, Max: , WMS Column: ob_lpn_volume, Format.1: Number, Max.1: , Notes:
INV -REST: VolumeUOMCode, Format: String, Max: 25.0, WMS Column: volume_uom_code, Format.1: , Max.1: , Notes: Integration property "consider_wt_vol_uom_from_property = yes" use volume_uom from integration properties (default is "FT3"), else use volume_uom_code from volume_uom_code.
INV -REST: packedLines, Format: , Max: , WMS Column: , Format.1: , Max.1: , Notes:
INV -REST: ShipmentLine, Format: Integer, Max: , WMS Column: ship_request_line, Format.1: String, Max.1: 30.0, Notes:
INV -REST: Item, Format: String, Max: 240.0, WMS Column: item_alternate_code+'~^~', Format.1: String, Max.1: 130.0, Notes: item_alternate_code+'~^~'
INV -REST: ShippedQuantity, Format: Number, Max: , WMS Column: shipped_qty, Format.1: Number, Max.1: , Notes:
INV -REST: ShippedQuantityUOMCode, Format: Number, Max: , WMS Column: shipped_uom, Format.1: , Max.1: , Notes: Integration property "consider_qty_uom_from_property = yes and shipped_uom='UNITS'" use shipped_quantity_uom from integration properties(default is "Ea"), else use shipped_uom from shipped_uom.
INV -REST: RequestedQuantityToConsume, Format: , Max: , WMS Column: order_qty_to_consume, Format.1: , Max.1: , Notes:
INV -REST: LoadingSequence, Format: String, Max: 80.0, WMS Column: ob_stop.seq_nbr, Format.1: , Max.1: , Notes:
INV -REST: TrackingNumber, Format: String, Max: 30.0, WMS Column: tracking_nbr, Format.1: String, Max.1: , Notes:
INV -REST: Subinventory, Format: String, Max: 10.0, WMS Column: erp_bucket, Format.1: , Max.1: , Notes:
INV -REST: lots, Format: , Max: , WMS Column: , Format.1: , Max.1: , Notes: This below section will be populated if it’s a Lot tracked SKU
INV -REST: lots/Lot, Format: String, Max: 80.0, WMS Column: batch_nbr, Format.1: String, Max.1: 25.0, Notes:
INV -REST: lots/Subinventory, Format: String, Max: 10.0, WMS Column: erp_bucket, Format.1: , Max.1: , Notes:
INV -REST: lots/Quantity, Format: Number, Max: , WMS Column: shipped_qty, Format.1: Number, Max.1: , Notes:
INV -REST: serials, Format: , Max: , WMS Column: , Format.1: , Max.1: , Notes: This below section will be populated if it’s a serial tracked SKU
INV -REST: serials/FromSerialNumber, Format: String, Max: 80.0, WMS Column: serial_nbr, Format.1: String, Max.1: 255.0, Notes:
INV -REST: serials/ToSerialNumber, Format: String, Max: 80.0, WMS Column: serial_nbr, Format.1: String, Max.1: 255.0, Notes:
INV -REST: serials/Subinventory, Format: String, Max: 10.0, WMS Column: erp_bucket, Format.1: , Max.1: , Notes:

Unnamed: 0: , Unnamed: 1:
Unnamed: 0: , Unnamed: 1: REST API - Shipment Transaction Requests (Batch processing)
Document Link - <https://confluence.oraclecorp.com/confluence/pages/viewpage.action?spaceKey=FMM&title=Shipping+REST+Services+19.04+Test+Cases> (Batch )
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22b/fasrp/api-inventory-management-shipment-transaction-requests.html>
