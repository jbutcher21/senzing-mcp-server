"""Wrapper for Senzing SDK to provide async interface and initialization."""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Optional

# Import Senzing SDK modules
# Note: Senzing environment must be initialized before running this module
# (e.g., by sourcing setupEnv or equivalent initialization script)
try:
    from senzing import (
        SzEngine,
        SzEngineFlags,
        SzError,
        SzNotFoundError,
    )
    from senzing_core import SzAbstractFactoryCore
except ImportError as e:
    raise ImportError(
        f"Failed to import Senzing SDK: {e}\n"
        "Please ensure the Senzing environment is properly initialized.\n"
        "This typically requires sourcing the Senzing setupEnv script before running."
    ) from e


class SenzingSDKWrapper:
    """Async wrapper for Senzing SDK."""

    def __init__(self):
        self.factory: Optional[SzAbstractFactoryCore] = None
        self.engine: Optional[SzEngine] = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._initialized = False

    async def initialize(self):
        """Initialize Senzing SDK from environment variables."""
        if self._initialized:
            return

        # Get configuration from environment
        engine_config = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
        if not engine_config:
            raise ValueError(
                "SENZING_ENGINE_CONFIGURATION_JSON environment variable not set"
            )

        module_name = os.getenv("SENZING_MODULE_NAME", "senzing-mcp")
        instance_name = os.getenv("SENZING_INSTANCE_NAME", "senzing-mcp-server")
        verbose_logging = int(os.getenv("SENZING_LOG_LEVEL", "0"))

        # Initialize in thread pool to avoid blocking
        await asyncio.get_event_loop().run_in_executor(
            self.executor, self._sync_initialize, engine_config, module_name, instance_name, verbose_logging
        )

        self._initialized = True

    def _sync_initialize(self, engine_config: str, module_name: str, instance_name: str, verbose_logging: int):
        """Synchronous initialization of Senzing SDK."""
        try:
            # Create factory with settings
            # The factory automatically initializes all components
            self.factory = SzAbstractFactoryCore(
                instance_name=instance_name,
                settings=engine_config,
                verbose_logging=verbose_logging
            )

            # Create engine component (already initialized through factory)
            self.engine = self.factory.create_engine()

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Senzing SDK: {str(e)}")

    async def _run_async(self, func, *args, **kwargs):
        """Run a synchronous SDK function asynchronously."""
        if not self._initialized:
            raise RuntimeError("SDK not initialized. Call initialize() first.")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, partial(func, *args, **kwargs)
        )

    # Entity Operations

    async def get_entity_by_record_id(self, data_source: str, record_id: str, flags: int = None) -> str:
        """Get entity details by data source and record ID (same flags as sz_explorer)."""
        try:
            # Use the same comprehensive flags as get_entity_by_entity_id
            if flags is None:
                flags = (
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_UNMAPPED_DATA
                )

            result = await self._run_async(
                self.engine.get_entity_by_record_id, data_source, record_id, flags
            )
            return result
        except SzNotFoundError:
            return json.dumps({"error": "Record not found", "data_source": data_source, "record_id": record_id})
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def get_entity_by_entity_id(self, entity_id: int, flags: int = None) -> str:
        """Get entity details by entity ID with comprehensive information (same flags as sz_explorer)."""
        try:
            # Use the exact same flags as sz_explorer's get command
            if flags is None:
                flags = (
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_UNMAPPED_DATA
                )

            result = await self._run_async(
                self.engine.get_entity_by_entity_id, entity_id, flags
            )
            return result
        except SzNotFoundError:
            return json.dumps({"error": "Entity not found", "entity_id": entity_id})
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def search_by_attributes(self, attributes: str, flags: int = None) -> str:
        """Search for entities by attributes with comprehensive search information (same flags as sz_explorer).

        If fewer than 11 entities are found, automatically performs a second search with full feature details.
        """
        try:
            # Use the exact same flags as sz_explorer's search command
            if flags is None:
                base_flags = (
                    SzEngineFlags.SZ_SEARCH_INCLUDE_ALL_ENTITIES |
                    SzEngineFlags.SZ_INCLUDE_FEATURE_SCORES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA |
                    SzEngineFlags.SZ_INCLUDE_MATCH_KEY_DETAILS |
                    SzEngineFlags.SZ_SEARCH_INCLUDE_STATS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
                )
                flags = base_flags

            # First search with base flags
            result = await self._run_async(
                self.engine.search_by_attributes, attributes, flags
            )

            # Parse result to check entity count
            result_data = json.loads(result)
            entity_count = len(result_data.get("RESOLVED_ENTITIES", []))

            # If fewer than 11 entities, redo search with full feature details
            if entity_count < 11 and entity_count > 0:
                enhanced_flags = flags | SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_FEATURES | SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_FEATURES
                result = await self._run_async(
                    self.engine.search_by_attributes, attributes, enhanced_flags
                )

            return result
        except SzError as e:
            return json.dumps({"error": str(e)})

    # Relationship Operations

    async def find_path_by_entity_id(
        self, start_entity_id: int, end_entity_id: int, max_degrees: int, flags: int = 0
    ) -> str:
        """Find relationship path between two entities."""
        try:
            result = await self._run_async(
                self.engine.find_path_by_entity_id,
                start_entity_id,
                end_entity_id,
                max_degrees,
                flags,
            )
            return result
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def find_network_by_entity_id(
        self, entity_list: str, max_degrees: int, build_out_degrees: int, max_entities: int, flags: int = 0
    ) -> str:
        """Find network of related entities."""
        try:
            result = await self._run_async(
                self.engine.find_network_by_entity_id,
                entity_list,
                max_degrees,
                build_out_degrees,
                max_entities,
                flags,
            )
            return result
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def why_entities(
        self, entity_id_1: int, entity_id_2: int, flags: int = None
    ) -> str:
        """Explain why two entities are related (same flags as sz_explorer)."""
        try:
            # Use the exact same flags as sz_explorer's why command (why_not)
            if flags is None:
                flags = (
                    SzEngineFlags.SZ_ENTITY_DEFAULT_FLAGS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_INTERNAL_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_FEATURE_STATS |
                    SzEngineFlags.SZ_INCLUDE_FEATURE_SCORES |
                    SzEngineFlags.SZ_INCLUDE_MATCH_KEY_DETAILS
                )

            result = await self._run_async(
                self.engine.why_entities, entity_id_1, entity_id_2, flags
            )
            return result
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def how_entity_by_entity_id(self, entity_id: int, flags: int = None) -> str:
        """Explain how an entity was resolved (same flags as sz_explorer)."""
        try:
            # Use the exact same flags as sz_explorer's how command (get_how_data)
            if flags is None:
                flags = (
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_INTERNAL_FEATURES |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_FEATURE_STATS |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA |
                    SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_FEATURES |
                    SzEngineFlags.SZ_INCLUDE_MATCH_KEY_DETAILS
                )

            result = await self._run_async(
                self.engine.how_entity_by_entity_id, entity_id, flags
            )
            return result
        except SzError as e:
            return json.dumps({"error": str(e)})

    async def cleanup(self):
        """Clean up resources."""
        if self._initialized:
            await self._run_async(self._sync_cleanup)
            self.executor.shutdown(wait=True)

    def _sync_cleanup(self):
        """Synchronous cleanup of Senzing SDK."""
        if self.factory:
            self.factory.destroy()
