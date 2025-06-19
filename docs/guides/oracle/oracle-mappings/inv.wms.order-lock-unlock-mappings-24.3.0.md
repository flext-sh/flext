# inv.wms.order-lock-unlock-mappings-24.3.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/inv.wms.order-lock-unlock-mappings-24.3.0.xlsx` \n**Data de conversão:** 2025-05-15T14:37:53.222643 \n**Tipo:** .xlsx \n**[Download original](reference/wms_solutions/mappings/inv.wms.order-lock-unlock-mappings-24.3.0.xlsx)**

---

## Sumário

## Resumo automático

Este documento descreve o mapeamento entre campos do WMS e colunas da interface de Inventário para as operações de bloqueio (lock) e desbloqueio (unlock) de linhas de pedido. Principais pontos:

• orderdtl**ship_request_line**in → ShipmentLine
• lock_code → ExceptionCode
• lock_description → ExceptionName
– Valor padrão se vazio: “Shipment Line on Hold for Update”
• comments → ExceptionComments
– Valor padrão se vazio: “The shipment line was placed on hold by a shipment request for update”
• autocreate_lock_flg → True
• Chamadas de API:
– bulk_lock → ActionType = “APPLY_HOLD” (LOCK)
– bulk_Unlock → ActionType = “RELEASE_HOLD” (RELEASELOCK)
• Indica sucesso quando o elemento failure_count na resposta XML é igual a 0.

## Conteúdo extraído

WMS Column: orderdtl**ship_request_line**in, Format: , Max: , REQD?: , INV Column: ShipmentLine, Format.1: , Max.1: , Notes:
WMS Column: lock_code, Format: , Max: , REQD?: , INV Column: ExceptionCode, Format.1: , Max.1: , Notes:
WMS Column: lock_description, Format: , Max: , REQD?: , INV Column: ExceptionName, Format.1: , Max.1: , Notes: if empty:
Shipment Line on Hold for Update
WMS Column: comments, Format: , Max: , REQD?: , INV Column: ExceptionComments, Format.1: , Max.1: , Notes: if empty:
The shipment line was placed on hold by a shipment request for update
WMS Column: autocreate_lock_flg, Format: , Max: , REQD?: , INV Column: True, Format.1: , Max.1: , Notes:
WMS Column: API ->bulk_lock, Format: , Max: , REQD?: , INV Column: ActionType = "LOCK"
ActionType = "APPLY_HOLD", Format.1: , Max.1: , Notes:
WMS Column: API->bulk_Unlock, Format: , Max: , REQD?: , INV Column: ActionType = "RELEASELOCK"
ActionType = "RELEASE_HOLD", Format.1: , Max.1: , Notes:
WMS Column: , Format: , Max: , REQD?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: Response Back To Fusion, Format: , Max: , REQD?: , INV Column: , Format.1: , Max.1: , Notes:
WMS Column: Status, Format: , Max: , REQD?: , INV Column: Success, Format.1: , Max.1: , Notes: If -> $ValidateAndLockAPICall/nsmpr0:executeResponse/nsmpr1:response-wrapper/nsmpr1:failure_count = '0'
