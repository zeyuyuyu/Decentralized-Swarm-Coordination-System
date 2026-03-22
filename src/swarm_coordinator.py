import asyncio
import random
import hashlib

class SwarmCoordinator:
    def __init__(self, nodes):
        self.nodes = nodes
        self.consensus_state = {}

    async def coordinate_swarm(self):
        while True:
            await self.reach_consensus()
            await self.execute_coordinated_tasks()
            await asyncio.sleep(10)

    async def reach_consensus(self):
        for node in self.nodes:
            self.consensus_state[node] = await self.propose_and_vote(node)

        majority_decision = self.get_majority_decision()
        self.broadcast_decision(majority_decision)

    async def propose_and_vote(self, node):
        proposal = await node.propose_task()
        votes = await asyncio.gather(*[node.vote(proposal) for node in self.nodes])
        return sum(votes) >= len(self.nodes) // 2 + 1

    def get_majority_decision(self):
        return max(self.consensus_state, key=self.consensus_state.get)

    def broadcast_decision(self, decision):
        for node in self.nodes:
            node.execute_task(decision)
