from typing import Any, Optional, Self
from neomodel import (
    AsyncStructuredRel, AsyncStructuredNode, StringProperty, IntegerProperty, DateTimeProperty
)
from neo4j.graph import Relationship as Neo4jRelationship
from neo4j.graph import Node as Neo4jNode
from module.core.tools.log import logger


class BaseCompositionRel(AsyncStructuredRel):
    source_type = StringProperty(default="UNKNOWN")
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()

    @classmethod
    def from_neo4j_relation(cls, rel: Any) -> Optional[Self]:
        if rel is None:
            return None
        if isinstance(rel, Neo4jRelationship):
            properties = rel._properties
        elif isinstance(rel, dict):
            properties = rel
        else:
            logger.error(f"Unable to convert from unsupported type {type(rel)} to relationship model {cls.__name__}")
            raise TypeError(f"Expected neo4j.graph.Relationship or dict, but received {type(rel)}")
        return cls.inflate(properties)


class StructuredNodeBaseClass(AsyncStructuredNode):
    __abstract_node__ = True
    source_type = StringProperty(default="UNKNOWN")
    creator_id = IntegerProperty()
    updater_id = IntegerProperty()
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()

    @classmethod
    def from_neo4j_node(cls, node: Any) -> Optional[Self]:
        if node is None:
            return None
        if isinstance(node, Neo4jNode):
            return cls.inflate(node)
        elif isinstance(node, dict):
            properties = {k: v for k, v in node.items() if not k.startswith('_')}
            instance = cls(**properties)
            return instance
        else:
            logger.error(f"Unable to convert from type {type(node)} to OGM model {cls.__name__}")
            raise TypeError(f"Expected neo4j.graph.Node or dict, but received {type(node)}")
