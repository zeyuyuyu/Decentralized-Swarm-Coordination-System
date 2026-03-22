import asyncio
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum
import logging

class NodeStatus(Enum):
    ACTIVE = 'active'
    FAILING = 'failing'
    OFFLINE = 'offline'

@dataclass
class SwarmNode:
    id: str
    status: NodeStatus
    load: float
    last_heartbeat: float
    tasks: Set[str]

class SwarmCoordinator:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.task_assignments: Dict[str, str] = {}
        self.load_threshold = 0.8
        self.heartbeat_timeout = 30.0
        logging.basicConfig(level=logging.INFO)

    async def register_node(self, node_id: str) -> None:
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            status=NodeStatus.ACTIVE,
            load=0.0,
            last_heartbeat=asyncio.get_event_loop().time(),
            tasks=set()
        )
        logging.info(f'Node {node_id} registered')

    async def heartbeat(self, node_id: str, load: float) -> None:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.last_heartbeat = asyncio.get_event_loop().time()
            node.load = load
            
            if load > self.load_threshold:
                await self.rebalance_tasks(node_id)

    async def rebalance_tasks(self, overloaded_node_id: str) -> None:
        overloaded = self.nodes[overloaded_node_id]
        candidates = [
            n for n in self.nodes.values()
            if n.status == NodeStatus.ACTIVE and n.load < self.load_threshold
        ]
        
        if not candidates:
            logging.warning(f'No available nodes for rebalancing {overloaded_node_id}')
            return

        tasks_to_move = sorted(
            overloaded.tasks,
            key=lambda t: self.task_assignments.get(t, 0)
        )[:len(candidates)]

        for task, target in zip(tasks_to_move, candidates):
            await self.reassign_task(task, overloaded_node_id, target.id)

    async def reassign_task(self, task_id: str, from_node: str, to_node: str) -> None:
        if from_node in self.nodes and to_node in self.nodes:
            self.nodes[from_node].tasks.remove(task_id)
            self.nodes[to_node].tasks.add(task_id)
            self.task_assignments[task_id] = to_node
            logging.info(f'Task {task_id} moved from {from_node} to {to_node}')

    async def monitor_health(self) -> None:
        while True:
            current_time = asyncio.get_event_loop().time()
            for node_id, node in self.nodes.items():
                if (current_time - node.last_heartbeat) > self.heartbeat_timeout:
                    if node.status == NodeStatus.ACTIVE:
                        node.status = NodeStatus.FAILING
                        await self.handle_node_failure(node_id)

            await asyncio.sleep(5)

    async def handle_node_failure(self, node_id: str) -> None:
        failing_node = self.nodes[node_id]
        logging.warning(f'Node {node_id} failing, redistributing {len(failing_node.tasks)} tasks')

        active_nodes = [
            n for n in self.nodes.values()
            if n.id != node_id and n.status == NodeStatus.ACTIVE
        ]

        if not active_nodes:
            logging.error('No active nodes available for task redistribution')
            return

        for task in failing_node.tasks.copy():
            target = min(active_nodes, key=lambda n: len(n.tasks))
            await self.reassign_task(task, node_id, target.id)

        failing_node.status = NodeStatus.OFFLINE

    def get_cluster_status(self) -> Dict:
        return {
            'nodes': len(self.nodes),
            'active_nodes': sum(1 for n in self.nodes.values() if n.status == NodeStatus.ACTIVE),
            'total_tasks': sum(len(n.tasks) for n in self.nodes.values()),
            'average_load': sum(n.load for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        }
