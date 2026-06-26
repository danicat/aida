import os
from a2ui.schema.catalog import CatalogConfig, FileSystemCatalogProvider

def get_aida_catalog_config() -> CatalogConfig:
    schema_path = os.path.join(os.path.dirname(__file__), "aida_catalog_schema.json")
    examples_path = os.path.join(os.path.dirname(__file__), "examples", "*.json")
    return CatalogConfig(
        name="aida_custom",
        provider=FileSystemCatalogProvider(schema_path),
        examples_path=examples_path
    )
