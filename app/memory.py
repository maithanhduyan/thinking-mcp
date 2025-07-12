# -*- coding: utf-8 -*-
# app/memory.py
# Knowledge Graph Memory Management Module
"""
Memory là một module quản lý bộ nhớ đồ thị tri thức, cho phép tạo, đọc, cập nhật và xóa các thực thể và quan hệ trong bộ nhớ.


"""

import json
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from app.logger import get_logger
from app.db import get_db_connection

MEMORY_FILE_PATH = os.getenv("MEMORY_FILE_PATH", "../memory.json")

logger = get_logger(__name__)


class Entity:
    """Entity in the knowledge graph"""
    def __init__(self, name: str, entity_type: str, observations: Optional[List[str]] = None):
        self.name = name
        self.entity_type = entity_type
        self.observations = observations or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entityType": self.entity_type,
            "observations": self.observations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        return cls(
            name=data["name"],
            entity_type=data["entityType"],
            observations=data.get("observations", [])
        )


class Relation:
    """Relation between entities in the knowledge graph"""
    def __init__(self, from_entity: str, to_entity: str, relation_type: str):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.relation_type = relation_type
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_entity,
            "to": self.to_entity,
            "relationType": self.relation_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relation':
        return cls(
            from_entity=data["from"],
            to_entity=data["to"],
            relation_type=data["relationType"]
        )


class KnowledgeGraph:
    """Knowledge graph containing entities and relations"""
    def __init__(self, entities: Optional[List[Entity]] = None, relations: Optional[List[Relation]] = None):
        self.entities = entities or []
        self.relations = relations or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [entity.to_dict() for entity in self.entities],
            "relations": [relation.to_dict() for relation in self.relations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        entities = [Entity.from_dict(e) for e in data.get("entities", [])]
        relations = [Relation.from_dict(r) for r in data.get("relations", [])]
        return cls(entities, relations)


class KnowledgeGraphManager:
    """Manager for knowledge graph operations"""
    
    def __init__(self, memory_file_path: Optional[str] = None):
        # Default memory file path
        if memory_file_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.memory_file_path = os.path.join(current_dir, MEMORY_FILE_PATH)
        else:
            if os.path.isabs(memory_file_path):
                self.memory_file_path = memory_file_path
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.memory_file_path = os.path.join(current_dir, memory_file_path)
        
        logger.info(f"Knowledge graph memory file: {self.memory_file_path}")
    
    async def load_graph(self) -> KnowledgeGraph:
        """Load knowledge graph from file"""
        try:
            if not os.path.exists(self.memory_file_path):
                return KnowledgeGraph()
            
            with open(self.memory_file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return KnowledgeGraph()
                
                lines = content.split("\n")
                entities = []
                relations = []
                
                for line in lines:
                    if line.strip():
                        try:
                            item = json.loads(line)
                            if item.get("type") == "entity":
                                # Remove type field and create entity
                                entity_data = {k: v for k, v in item.items() if k != "type"}
                                entities.append(Entity.from_dict(entity_data))
                            elif item.get("type") == "relation":
                                # Remove type field and create relation
                                relation_data = {k: v for k, v in item.items() if k != "type"}
                                relations.append(Relation.from_dict(relation_data))
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing line in memory file: {line} - {e}")
                            continue
                
                return KnowledgeGraph(entities, relations)
                
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
            return KnowledgeGraph()
    
    async def save_graph(self, graph: KnowledgeGraph) -> None:
        """Save knowledge graph to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            
            lines = []
            
            # Add entities with type field
            for entity in graph.entities:
                entity_data = {"type": "entity", **entity.to_dict()}
                lines.append(json.dumps(entity_data, ensure_ascii=False))
            
            # Add relations with type field
            for relation in graph.relations:
                relation_data = {"type": "relation", **relation.to_dict()}
                lines.append(json.dumps(relation_data, ensure_ascii=False))
            
            with open(self.memory_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            logger.debug(f"Saved knowledge graph with {len(graph.entities)} entities and {len(graph.relations)} relations")
            
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
            raise
    
    async def create_entities(self, entities_data: List[Dict[str, Any]]) -> List[Entity]:
        """Create multiple new entities in the knowledge graph"""
        graph = await self.load_graph()
        existing_names = {entity.name for entity in graph.entities}
        
        new_entities = []
        for entity_data in entities_data:
            entity = Entity.from_dict(entity_data)
            if entity.name not in existing_names:
                new_entities.append(entity)
                graph.entities.append(entity)
                existing_names.add(entity.name)
            else:
                logger.warning(f"Entity '{entity.name}' already exists, skipping")
        
        await self.save_graph(graph)
        logger.info(f"Created {len(new_entities)} new entities")
        return new_entities
    
    async def create_relations(self, relations_data: List[Dict[str, Any]]) -> List[Relation]:
        """Create multiple new relations between entities"""
        graph = await self.load_graph()
        existing_relations = {
            (r.from_entity, r.to_entity, r.relation_type) 
            for r in graph.relations
        }
        
        new_relations = []
        for relation_data in relations_data:
            relation = Relation.from_dict(relation_data)
            relation_key = (relation.from_entity, relation.to_entity, relation.relation_type)
            
            if relation_key not in existing_relations:
                new_relations.append(relation)
                graph.relations.append(relation)
                existing_relations.add(relation_key)
            else:
                logger.warning(f"Relation {relation_key} already exists, skipping")
        
        await self.save_graph(graph)
        logger.info(f"Created {len(new_relations)} new relations")
        return new_relations
    
    async def add_observations(self, observations_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add new observations to existing entities"""
        graph = await self.load_graph()
        results = []
        
        for obs_data in observations_data:
            entity_name = obs_data["entityName"]
            contents = obs_data["contents"]
            
            # Find the entity
            entity = next((e for e in graph.entities if e.name == entity_name), None)
            if not entity:
                raise ValueError(f"Entity with name '{entity_name}' not found")
            
            # Add new observations (filter duplicates)
            new_observations = [content for content in contents if content not in entity.observations]
            entity.observations.extend(new_observations)
            
            results.append({
                "entityName": entity_name,
                "addedObservations": new_observations
            })
        
        await self.save_graph(graph)
        logger.info(f"Added observations to {len(observations_data)} entities")
        return results
    
    async def delete_entities(self, entity_names: List[str]) -> None:
        """Delete multiple entities and their associated relations"""
        graph = await self.load_graph()
        
        # Remove entities
        original_count = len(graph.entities)
        graph.entities = [e for e in graph.entities if e.name not in entity_names]
        deleted_entities = original_count - len(graph.entities)
        
        # Remove relations involving deleted entities
        original_relations = len(graph.relations)
        graph.relations = [
            r for r in graph.relations 
            if r.from_entity not in entity_names and r.to_entity not in entity_names
        ]
        deleted_relations = original_relations - len(graph.relations)
        
        await self.save_graph(graph)
        logger.info(f"Deleted {deleted_entities} entities and {deleted_relations} associated relations")
    
    async def delete_observations(self, deletions_data: List[Dict[str, Any]]) -> None:
        """Delete specific observations from entities"""
        graph = await self.load_graph()
        
        for deletion_data in deletions_data:
            entity_name = deletion_data["entityName"]
            observations_to_delete = deletion_data["observations"]
            
            entity = next((e for e in graph.entities if e.name == entity_name), None)
            if entity:
                entity.observations = [
                    obs for obs in entity.observations 
                    if obs not in observations_to_delete
                ]
            else:
                logger.warning(f"Entity '{entity_name}' not found for observation deletion")
        
        await self.save_graph(graph)
        logger.info(f"Deleted observations from {len(deletions_data)} entities")
    
    async def delete_relations(self, relations_data: List[Dict[str, Any]]) -> None:
        """Delete multiple relations from the knowledge graph"""
        graph = await self.load_graph()
        
        relations_to_delete = {
            (r["from"], r["to"], r["relationType"]) 
            for r in relations_data
        }
        
        original_count = len(graph.relations)
        graph.relations = [
            r for r in graph.relations 
            if (r.from_entity, r.to_entity, r.relation_type) not in relations_to_delete
        ]
        deleted_count = original_count - len(graph.relations)
        
        await self.save_graph(graph)
        logger.info(f"Deleted {deleted_count} relations")
    
    async def read_graph(self) -> KnowledgeGraph:
        """Read the entire knowledge graph"""
        graph = await self.load_graph()
        logger.debug(f"Read graph with {len(graph.entities)} entities and {len(graph.relations)} relations")
        return graph
    
    async def search_nodes(self, query: str) -> KnowledgeGraph:
        """Search for nodes in the knowledge graph based on a query"""
        graph = await self.load_graph()
        query_lower = query.lower()
        
        # Filter entities based on query
        filtered_entities = []
        for entity in graph.entities:
            if (query_lower in entity.name.lower() or 
                query_lower in entity.entity_type.lower() or
                any(query_lower in obs.lower() for obs in entity.observations)):
                filtered_entities.append(entity)
        
        # Get names of filtered entities
        filtered_entity_names = {entity.name for entity in filtered_entities}
        
        # Filter relations to only include those between filtered entities
        filtered_relations = [
            relation for relation in graph.relations
            if (relation.from_entity in filtered_entity_names and 
                relation.to_entity in filtered_entity_names)
        ]
        
        result_graph = KnowledgeGraph(filtered_entities, filtered_relations)
        logger.info(f"Search '{query}' found {len(filtered_entities)} entities and {len(filtered_relations)} relations")
        return result_graph
    
    async def open_nodes(self, names: List[str]) -> KnowledgeGraph:
        """Open specific nodes in the knowledge graph by their names"""
        graph = await self.load_graph()
        names_set = set(names)
        
        # Filter entities by names
        filtered_entities = [
            entity for entity in graph.entities 
            if entity.name in names_set
        ]
        
        # Get names of filtered entities
        filtered_entity_names = {entity.name for entity in filtered_entities}
        
        # Filter relations to only include those between filtered entities
        filtered_relations = [
            relation for relation in graph.relations
            if (relation.from_entity in filtered_entity_names and 
                relation.to_entity in filtered_entity_names)
        ]
        
        result_graph = KnowledgeGraph(filtered_entities, filtered_relations)
        logger.info(f"Opened {len(filtered_entities)} entities and {len(filtered_relations)} relations")
        return result_graph


# Global knowledge graph manager instance
_knowledge_graph_manager = None


def get_knowledge_graph_manager() -> KnowledgeGraphManager:
    """Get the global knowledge graph manager instance"""
    global _knowledge_graph_manager
    if _knowledge_graph_manager is None:
        memory_file_path = MEMORY_FILE_PATH
        _knowledge_graph_manager = KnowledgeGraphManager(memory_file_path)
    return _knowledge_graph_manager


# Convenience functions for external use
async def memory_create_entities(entities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create entities and return their dict representation"""
    manager = get_knowledge_graph_manager()
    new_entities = await manager.create_entities(entities_data)
    return [entity.to_dict() for entity in new_entities]


async def memory_create_relations(relations_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create relations and return their dict representation"""
    manager = get_knowledge_graph_manager()
    new_relations = await manager.create_relations(relations_data)
    return [relation.to_dict() for relation in new_relations]


async def memory_add_observations(observations_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add observations and return results"""
    manager = get_knowledge_graph_manager()
    return await manager.add_observations(observations_data)


async def memory_delete_entities(entity_names: List[str]) -> str:
    """Delete entities and return success message"""
    manager = get_knowledge_graph_manager()
    await manager.delete_entities(entity_names)
    return f"Successfully deleted {len(entity_names)} entities"


async def memory_delete_observations(deletions_data: List[Dict[str, Any]]) -> str:
    """Delete observations and return success message"""
    manager = get_knowledge_graph_manager()
    await manager.delete_observations(deletions_data)
    return f"Successfully deleted observations from {len(deletions_data)} entities"


async def memory_delete_relations(relations_data: List[Dict[str, Any]]) -> str:
    """Delete relations and return success message"""
    manager = get_knowledge_graph_manager()
    await manager.delete_relations(relations_data)
    return f"Successfully deleted {len(relations_data)} relations"


async def memory_read_graph() -> Dict[str, Any]:
    """Read the entire knowledge graph"""
    manager = get_knowledge_graph_manager()
    graph = await manager.read_graph()
    return graph.to_dict()


async def memory_search_nodes(query: str) -> Dict[str, Any]:
    """Search nodes in the knowledge graph"""
    manager = get_knowledge_graph_manager()
    graph = await manager.search_nodes(query)
    return graph.to_dict()


async def memory_open_nodes(names: List[str]) -> Dict[str, Any]:
    """Open specific nodes in the knowledge graph"""
    manager = get_knowledge_graph_manager()
    graph = await manager.open_nodes(names)
    return graph.to_dict()
