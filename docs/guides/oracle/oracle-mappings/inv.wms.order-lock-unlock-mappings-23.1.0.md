# Oracle WMS Order Lock/Unlock Mappings - Version 23.1.0

> **Function**: Oracle WMS to Inventory module field mappings for order line lock/unlock operations | **Audience**: Integration developers, Oracle WMS engineers | **Status**: Production validated

[![Oracle WMS](https://img.shields.io/badge/Oracle-WMS%2023.1.0-blue.svg)](../index.md)
[![Mapping](https://img.shields.io/badge/mapping-validated-green.svg)](./index.md)
[![Integration](https://img.shields.io/badge/type-API%20mapping-orange.svg)](../oracle-wms-comprehensive-guide.md)

**Field mapping specification for Oracle WMS order line lock/unlock operations to Inventory module - Production validated for version 23.1.0**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../../index.md) → **📂 Hub**: [Guides](../../index.md) → **📂 Oracle**: [Oracle Hub](../index.md) → **📂 Mappings**: [Mappings Hub](./index.md) → **📄 Current**: Order Lock/Unlock Mappings 23.1.0

---

## 📋 **Summary**

This document describes field mappings between Oracle WMS and the Inventory (INV) module for order line lock and unlock operations. Key mappings include:

### **Core Field Mappings**

- **ShipmentLine** ← `orderdtl__ship_request_line__in`
- **ExceptionCode** ← `lock_code`  
- **ExceptionName** ← `lock_description` (defaults to "Shipment Line on Hold for Update" if empty)
- **ExceptionComments** ← `comments` (defaults to "The shipment line was placed on hold by a shipment request for update" if empty)
- **autocreate_lock_flg** → always "True"

### **Action Type Mappings**

- **Lock Operations**: ActionType → "LOCK" or "APPLY_HOLD" (bulk_lock)
- **Unlock Operations**: ActionType → "RELEASELOCK" or "RELEASE_HOLD" (bulk_Unlock)
- **Success Status** ← Status (determined when failure_count = 0)

---

## 📊 **Field Mapping Table**

| WMS Column | Required | INV Column | Format | Notes |
|------------|----------|------------|---------|-------|
| `orderdtl__ship_request_line__in` | Yes | ShipmentLine | String | Primary shipment line identifier |
| `lock_code` | Yes | ExceptionCode | String | Lock/exception code |
| `lock_description` | No | ExceptionName | String | Default: "Shipment Line on Hold for Update" |
| `comments` | No | ExceptionComments | String | Default: "The shipment line was placed on hold by a shipment request for update" |
| N/A | N/A | autocreate_lock_flg | Boolean | Always set to "True" |

### **API Operation Mappings**

| WMS API Operation | INV ActionType | Description |
|-------------------|----------------|-------------|
| `bulk_lock` | "LOCK" or "APPLY_HOLD" | Lock shipment line operations |
| `bulk_Unlock` | "RELEASELOCK" or "RELEASE_HOLD" | Unlock shipment line operations |

### **Response Mappings**

| WMS Response | INV Field | Condition |
|--------------|-----------|-----------|
| `Status` | `Success` | True when `failure_count = 0` |
| API Response | Response Back To Fusion | Complete operation status |

---

## 🔧 **Implementation Details**

### **Lock Operation Flow**

1. Receive shipment line identifier from WMS
2. Apply lock code and description
3. Set ActionType to "LOCK" or "APPLY_HOLD"
4. Return success status based on failure count

### **Unlock Operation Flow**

1. Receive shipment line identifier from WMS
2. Set ActionType to "RELEASELOCK" or "RELEASE_HOLD"
3. Process unlock operation
4. Return success status to Fusion

### **Validation Rules**

- ShipmentLine identifier must be valid
- Lock code must be provided for lock operations
- Success is determined by zero failure count
- All operations require valid API response back to Fusion

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle WMS Guide](../oracle-wms-comprehensive-guide.md) - Understanding WMS operations and architecture
- [Oracle Mappings Hub](./index.md) - Overview of all Oracle integration mappings

### **Next Steps**

- [Receipt Advice Mappings](./inv.wms.receipt-advice-for-purchase-orders-and-RMA-mapping-23.1.0.md) - Related receipt operations
- [Shipment Confirmation Mappings](./wms.inv.shipment-confirmation-for-sales-orders-mapping-23.1.0.md) - Shipment workflow mappings

### **Related Topics**

- [Oracle WMS CLI Guide](../oracle-wms-cli-guide.md) - Command-line operations for lock/unlock
- [Oracle Integration Guide](../oracle-integration-comprehensive-guide.md) - Overall integration patterns
- [Oracle WMS API Reference](../oracle-wms-complete-api-reference.md) - Complete API documentation

---

**📂 Hub**: [Mappings Hub](./index.md) | **🏠 Root**: [Documentation Home](../../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
