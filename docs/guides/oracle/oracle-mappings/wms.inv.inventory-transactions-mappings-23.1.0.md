# wms.inv.inventory-transactions-mappings-23.1.0.xlsx

**Caminho:** `reference/wms_solutions/mappings/wms.inv.inventory-transactions-mappings-23.1.0.xlsx`  \n**Data de conversão:** 2025-05-15T14:42:00.454558  \n**Tipo:** .xlsx  \n**[Download original](reference/wms_solutions/mappings/wms.inv.inventory-transactions-mappings-23.1.0.xlsx)**

---

## Sumário



## Resumo automático

Este documento é um guia de mapeamento entre os dados do WMS e os campos esperados pela API de Inventory Staged Transactions da Oracle Cloud. Em linhas gerais ele:

• Define quais colunas do WMS alimentam cada campo do payload INV, por exemplo  
  – TransactionInterfaceId = concat(group_nbr, seq_nbr)  
  – TransactionHeaderId = group_nbr  
  – SourceCode, SourceLineId, SourceHeaderId são hard-coded (“Cloud WMS”, “0”, “0”)  
  – TransactionMode = “1”  

• Especifica regras de escolha de valores  
  – TransactionQuantity: usa adj_qty se existir, senão orig_qty  
  – TransactionUnitOfMeasure/UOM: pode vir de propriedade de integração ou do campo qty_uom_code  
  – SubinventoryCode e TransactionTypeName: determinadas pela presença ou ausência de bucket atual/ anterior  

• Mapeia demais campos básicos  
  – TransactionDate ← create_ts  
  – ItemNumber ← substring-before(item_alternate_code, ‘~^~’)  
  – OrganizationName ← ref_value_3/4/6/10 quando marcados como “FCN”  
  – ExternalSystemtransactionReference ← group_nbr + “-” + seq_nbr  
  – UseCurrentCost = true  

• Contém seções específicas para controle de lotes, séries e lotes com séries  
  – Lotes: LotNbr e LotExpirationDate vindos de determinados ref_value_X (códigos “BAT”, “EXP”)  
  – Séries: FmSerialNumber e ToSerialNumber = serial_nbr  
  – Para itens com ambos controles detalha objetos JSON conforme a API (lots, serials, lots-lot-serials)  

• Aponta as URLs das APIs REST relevantes (Inventory Staged Transactions) da documentação Oracle SaaS.

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
INV Column: TransactionUnitOfMeasure, WMS Column: , Notes: transaction_unit_of_measure of properties variable
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
