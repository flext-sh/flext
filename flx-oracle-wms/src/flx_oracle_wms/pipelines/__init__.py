"""Pre-configured pipelines for Oracle WMS integration."""

from flx_oracle_wms.pipelines.inventory_sync import InventorySyncPipeline


__all__ = [
    "InventorySyncPipeline",
]
