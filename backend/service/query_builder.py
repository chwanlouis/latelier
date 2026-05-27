import logging
from enum import Enum
from typing import Any, Dict, List, Optional
from model.neo4j.enum import NodeTypeName, RelationTypeName

logger = logging.getLogger(__name__)

class Neo4jNativeQuery:
    def __init__(self):
        self._statements: List[str] = []
        self._params: Dict[str, Any] = {}
        self._param_counter = 0

    def _generate_param_key(self, key: str) -> str:
        """Dynamically generate a unique Cypher parameter key to avoid conflicts with duplicate property names or WHERE conditions."""
        self._param_counter += 1
        # Remove dots from variable paths (e.g., f.food_group becomes f_food_group_1)
        clean_key = key.replace(".", "_")
        return f"{clean_key}_{self._param_counter}"

    def _format_attributes(self, attributes: Dict[str, Any], var_name: str) -> str:
        """Convert dictionary attributes to Cypher's {key: $param_key} format and store them in the parameter pool."""
        if not attributes:
            return ""
        pairs = []
        for k, v in attributes.items():
            param_key = self._generate_param_key(k)
            self._params[param_key] = v
            pairs.append(f"{k}: ${param_key}")
        return f" {{{', '.join(pairs)}}}"

    def match_node(self, var_name: str, label: Enum, attributes: Optional[Dict[str, Any]] = None) -> "Neo4jNativeQuery":
        """Construct a MATCH node fragment: MATCH (f:Food {id: $id_1})"""
        attr_string = self._format_attributes(attributes or {}, var_name)
        self._statements.append(f"MATCH ({var_name}:{label.value}{attr_string})")
        return self

    def optional_match_relation(
        self,
        source_var: str,
        rel_var: str,
        rel_type: Enum,
        target_var: str,
        target_label: Enum,
        target_attributes: Optional[Dict[str, Any]] = None
    ) -> "Neo4jNativeQuery":
        """Construct an OPTIONAL MATCH relationship fragment."""
        target_attr_string = self._format_attributes(target_attributes or {}, target_var)
        statement = (
            f"OPTIONAL MATCH ({source_var})-"
            f"[{rel_var}:{rel_type.value}]->"
            f"({target_var}:{target_label.value}{target_attr_string})"
        )
        self._statements.append(statement)
        return self

    def where(self, condition_dict: Dict[str, Any]) -> "Neo4jNativeQuery":
        """
        Construct a WHERE condition filter fragment, supporting properties with node variable names.
        Example: query_builder.where({"f.food_group": "Spices", "c.name": "Allicin"})
        Output: WHERE f.food_group = $f_food_group_1 AND c.name = $c_name_2
        """
        if not condition_dict:
            return self

        where_clauses = []
        for field_path, value in condition_dict.items():
            param_key = self._generate_param_key(field_path)
            self._params[param_key] = value
            where_clauses.append(f"{field_path} = ${param_key}")

        statement = f"WHERE { ' AND '.join(where_clauses) }"
        self._statements.append(statement)
        return self

    def return_vars(self, *vars_to_return: str, collect_map: Optional[Dict[str, str]] = None) -> "Neo4jNativeQuery":
        """Construct a RETURN fragment, supporting advanced collect aliasing."""
        return_parts = list(vars_to_return)
        if collect_map:
            map_pairs = [f"{k}: {v}" for k, v in collect_map.items()]
            pairs_str = ", ".join(map_pairs)
            return_parts.append(f"collect({{{pairs_str}}}) AS compound_packs")

        self._statements.append(f"RETURN {', '.join(return_parts)}")
        return self

    def limit_count(self, number: int) -> "Neo4jNativeQuery":
        """
        Construct a LIMIT clause.
        Example: query_builder.limit_count(10)
        Output: LIMIT $limit_1
        """
        param_key = self._generate_param_key("limit")
        self._params[param_key] = number

        self._statements.append(f"LIMIT ${param_key}")
        return self

    def get_string_query(self) -> str:
        """Compile and return the final concatenated Cypher query string."""
        return "\n".join(self._statements)

    @property
    def parameters(self) -> Dict[str, Any]:
        """Retrieve the safely extracted Cypher parameter dictionary."""
        return self._params


if __name__ == "__main__":
    _id = 8
    query_builder = Neo4jNativeQuery()
    query_builder.match_node(
        var_name="f",
        label=NodeTypeName.Food,
        attributes={"id": _id}
    )
    query_builder.optional_match_relation(
        source_var="f",
        rel_var="r",
        rel_type=RelationTypeName.CONTAINS_COMPOUND,
        target_var="c",
        target_label=NodeTypeName.Compound
    )
    query_builder.where({
        "f.food_group": "Herbs and Spices",
        "c.state": "solid"
    })
    query_builder.return_vars("f", collect_map={"compound": "c", "rel": "r"})
    query_builder.limit_count(10)
    query = query_builder.get_string_query()
    params = query_builder.parameters

    print("--- 產出的 Cypher 字串 ---")
    print(query)
    print("\n--- 抽離的安全參數字典 ---")
    print(params)