"""
ACDIF Core Manifest System
Defines the typed, versioned capability manifests that serve as atomic integration units.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from uuid import UUID, uuid4

import semver
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class CapabilityType(str, Enum):
    """Taxonomy of module capabilities to enable semantic matching."""
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    API_INTEGRATION = "api_integration"
    STORAGE = "storage"
    COMPUTE = "compute"
    MONITORING = "monitoring"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"


class CompatibilityLevel(str, Enum):
    """Semantic version compatibility levels."""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # Backward-compatible features
    PATCH = "patch"  # Bug fixes


class SchemaType(str, Enum):
    """Supported schema types for input/output validation."""
    JSON_SCHEMA = "json_schema"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    OPENAPI = "openapi"


class IOSchema(BaseModel):
    """Input/Output schema definition for capability contracts."""
    model_config = ConfigDict(frozen=True)
    
    schema_type: SchemaType = Field(description="Type of schema definition")
    schema_definition: Dict[str, Any] = Field(description="Schema definition in specified format")
    required: bool = Field(default=True, description="Whether this input/output is required")
    description: Optional[str] = Field(default=None, description="Human-readable description")
    
    @field_validator("schema_definition")
    @classmethod
    def validate_schema_definition(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        """Validate schema definition based on schema type."""
        schema_type = info.data.get("schema_type")
        
        if schema_type == SchemaType.JSON_SCHEMA:
            if not isinstance(v, dict):
                raise ValueError("JSON Schema must be a dictionary")
            if "$schema" not in v:
                v["$schema"] = "http://json-schema.org/draft-07/schema#"
        
        elif schema_type == SchemaType.OPENAPI:
            if "openapi" not in v:
                raise ValueError("OpenAPI schema must specify version")
        
        return v


class CapabilityManifest(BaseModel):
    """
    Core manifest defining a module's capabilities.
    This is the atomic unit of integration in ACDIF.
    """
    model_config = ConfigDict(frozen=True)
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique manifest identifier")
    module_id: str = Field(description="Unique identifier of the owning module")
    module_version: str = Field(description="Semantic version of the module")
    
    # Capability Definition
    name: str = Field(description="Human-readable capability name")
    capability_type: CapabilityType = Field(description="Type of capability")
    version: str = Field(description="Semantic version of this capability")
    
    # Contract
    inputs: Dict[str, IOSchema] = Field(default_factory=dict, description="Input schemas")
    outputs: Dict[str, IOSchema] = Field(default_factory=dict, description="Output schemas")
    dependencies: List[str] = Field(default_factory=list, description="Required dependent capabilities")
    
    # Metadata
    description: Optional[str] = Field(default=None, description="Human