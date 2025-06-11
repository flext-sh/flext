# wms.inv.inventory-transactions-mappings-24.4.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/wms.inv.inventory-transactions-mappings-24.4.0.xlsx`  \n**Data de conversão:** 2025-05-15T14:42:18.562634  \n**Tipo:** .xlsx  \n**[Download original](reference/wms_solutions/mappings/wms.inv.inventory-transactions-mappings-24.4.0.xlsx)**

---

## Sumário



## Resumo automático

Este documento é a especificação de mapeamento entre os dados do WMS e a interface de “Inventory Staged Transactions” do Oracle Cloud SCM (versão 24.4.0). Ele detalha:

1. Campos de cabeçalho e linha  
   - TransactionInterfaceId: concatena group_nbr + seq_nbr  
   - TransactionHeaderId: group_nbr  
   - SourceCode/SourceLineId/SourceHeaderId: valores fixos (‘Cloud WMS’, ‘0’, ‘0’)  
   - TransactionMode: ‘1’ (executa o job após sucesso)  
   - TransactionDate: create_ts  
   - TransferSubinventory, SubinventoryCode, TransactionTypeName: baseados em buckets atuais e anteriores, com regras para issue, receipt ou transfer  
   - TransactionQuantity: usa adj_qty se disponível, senão orig_qty  
   - ItemNumber: substring-before de item_alternate_code até ‘~^~’  
   - OrganizationName: proveniente de campos ref_value_X com código “FCN”  
   - TransactionUOM: ou qty_uom_code ou valor de propriedade de integração (‘Ea’)  
   - ExternalSystemtransactionReference: “group_nbr-seq_nbr”  
   - UseCurrentCost: ‘true’

2. Objeto de lotes (inventoryStagedTransactions-lots)  
   - Não usado se o item não for controlado por lote  
   - LotNbr e LotExpirationDate: extraídos de ref_value_1/2/4/5 conforme ref_code (BAT, EXP)  
   - TransactionQuantity: mesma lógica de adj_qty/orig_qty  
   - Referência à API REST para lotes

3. Objeto de séries (inventoryStagedTransactions-serials)  
   - Para itens controlados por série (serial_nbr presente)  
   - FmSerialNumber e ToSerialNumber: valores de serial_nbr  
   - SerialTransactionTempId: concatena group_nbr + seq_nbr  
   - Referência à API REST para séries

4. Objeto combinado lote-série (inventoryStagedTransactions-lots-lotSerials)  
   - Para itens que são controlados por lote e série simultaneamente  
   - Também referenciado por API REST própria

Além disso, o documento inclui links para a documentação das APIs REST de Inventory Staged Transactions (versões 20a e 22d) e reforça os nomes de campos, defaults e regras condicionais para cada cenário de transação.

## Conteúdo extraído

INV Column: TransactionInterfaceId, WMS Column: group_nbr + seq_nbr, Notes: concat (group_nbr, seq_nbr)
INV Column: TransactionHeaderId, WMS Column: group_nbr, Notes:
INV Column: SourceCode, WMS Column: , Notes: Hard coded to 'Cloud WMS'
INV Column: SourceLineId, WMS Column: , Notes: Hard coded to '0'
INV Column: SourceHeaderId, WMS Column: , Notes: Hard coded to '0'
INV Column: TransferSubinventory, WMS Column: Current Erp Bucket, Notes:
INV Column: TransactionMode, WMS Column: 1, Notes: Hard coded to '1' (Run job - Manage inventory transactions after success)
INV Column: TransactionQuantity, WMS Column: adj_qty/orig_qty, Notes: Used adj_qty, if provided. Default to orig_qty.
INV Column: TransactionDate, WMS Column: create_ts, Notes: Time part is automatically getting
INV Column: SubinventoryCode, WMS Column: Current Erp Bucket/ Prev Erp Bucket, Notes:
INV Column: TransactionTypeName, WMS Column: Miscellaneous issue/Miscellaneous Receipt/Subinventory Transfer, Notes: Prev Erp Bucket != "" and Current Erp Bucket = ""/ Prev Erp Bucket = "" and Current Erp Bucket != ""/ Prev Erp Bucket != "" and Current Erp Bucket != ""
INV Column: ItemNumber, WMS Column: item_alternate_code + '~^~', Notes: substring-before (item_alternate_code, '~^~')
INV Column: OrganizationName, WMS Column: ref_value_3/ref_value_4/ref_value_6/ref_value_10, Notes: Ref Code 3 = "FCN"/Ref Code 4 = "FCN"/Ref Code 6 = "FCN"/Ref Code 10 = "FCN"
INV Column: TransactionUnitOfMeasure, WMS Column: , Notes:
INV Column: TransactionUOM, WMS Column: qty_uom_code, Notes: If integration property "consider_qty_uom_from_property = yes and qty_uom_code='UNITS'" use transaction_unit_of_measure from integration properties(default is 'Ea'), else use qty_uom_code.
INV Column: ExternalSystemtransactionReference, WMS Column:  Group Nbr, "-", Seq Nbr, Notes:
INV Column: UseCurrentCost, WMS Column: , Notes: Hard coded to 'true'
INV Column: inventoryStagedTransactions-lots, WMS Column: [Lot Block], Notes: An object representing the lot details for the staged inventory transaction.

- Only used if the inventory is batch controlled:
  - Value comes from different ref_value_X fields in IHT depending on type.

<https://docs.oracle.com/en/cloud/saas/supply-chain-management/20a/fasrp/api-inventory-staged-transactions-lots.html>

INV Column: inventoryStagedTransactions-serials, WMS Column: [Serial Block], Notes: An object representing the serial number details for the staged inventory transaction. This is for serial number controlled items only.

- Only used if serial_nbr is present in IHT.

<https://docs.oracle.com/en/cloud/saas/supply-chain-management/20a/fasrp/api-inventory-staged-transactions-serials.html>

INV Column: TransactionInterfaceId, WMS Column: group_nbr + seq_nbr, Notes: concat (group_nbr, seq_nbr)
INV Column: LotNbr, WMS Column: ref_value_1/ref_value_2/ref_value_4, Notes: if Ref Code 1 = "BAT"->Ref Value 1, if Ref Code 2 = "BAT"->Ref Value 2
Defaut: ref_value_4
INV Column: LotExpirationDate, WMS Column: ref_value_2/ref_value_3/ref_value_5, Notes: if Ref Code 2 = "EXP"->Ref Value 2, Ref Code 3 = "EXP"->Ref Value 3,
Ref Code 5 = "EXP"-> Ref Value 5
INV Column: TransactionQuantity, WMS Column: adj_qty/orig_qty, Notes: Used 'adj_qty', if provided. Default to 'orig_qty'.
INV Column: SerialTransactionTempId, WMS Column: group_nbr + seq_nbr, Notes: concat (group_nbr, seq_nbr)
INV Column: inventoryStagedTransactions-lots-lotSerials, WMS Column: [Serial Block], Notes: An object representing the serial number details for the staged inventory transaction. This is for an item under both lot and serial number controls.

<https://docs.oracle.com/en/cloud/saas/supply-chain-management/20a/fasrp/api-inventory-staged-transactions-lots-lot-serials.html>

INV Column: TransactionInterfaceId, WMS Column: group_nbr + seq_nbr, Notes: concat (group_nbr, seq_nbr)
INV Column: SourceCode, WMS Column: , Notes: Hard coded to 'Cloud WMS'
INV Column: SourceLineId, WMS Column: , Notes: Hard coded to '0'
INV Column: FmSerialNumber, WMS Column: serial_nbr, Notes: Starting serial number in a range of serial numbers.
INV Column: ToSerialNumber, WMS Column: serial_nbr, Notes: Ending serial number in a range of serial numbers.

REST APIS - Inventory Staged Transactions -
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-inventory-staged-transactions.html>: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
REST APIS - Inventory Staged Transactions -
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-inventory-staged-transactions.html>: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
REST APIS - Inventory Staged Transactions -
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-inventory-staged-transactions.html>: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
REST APIS - Inventory Staged Transactions -
<https://docs.oracle.com/en/cloud/saas/supply-chain-management/22d/fasrp/api-inventory-management-inventory-staged-transactions.html>: , Unnamed: 1: , Unnamed: 2: , Unnamed: 3: , Unnamed: 4:
