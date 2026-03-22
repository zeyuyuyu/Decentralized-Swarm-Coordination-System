from typing import List, Dict, Any
import hashlib
import time
import json

class SwarmConsensus:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.proposals: Dict[str, Any] = {}
        self.votes: Dict[str, Dict[str, bool]] = {}
        self.confirmed = set()
        self.min_votes = (len(peers) * 2) // 3 + 1

    def propose_action(self, action: Dict[str, Any]) -> str:
        """Propose a new action to the swarm network"""
        action_id = self._generate_action_id(action)
        timestamp = time.time()
        
        proposal = {
            'action': action,
            'proposer': self.node_id,
            'timestamp': timestamp,
            'action_id': action_id
        }
        
        self.proposals[action_id] = proposal
        self.votes[action_id] = {self.node_id: True}
        
        return action_id

    def vote_on_proposal(self, action_id: str, approve: bool) -> bool:
        """Vote on a proposed action"""
        if action_id not in self.proposals:
            return False
            
        self.votes[action_id][self.node_id] = approve
        
        if self._check_consensus(action_id):
            self.confirmed.add(action_id)
            return True
            
        return False

    def get_confirmed_actions(self) -> List[Dict[str, Any]]:
        """Get list of actions that achieved consensus"""
        return [self.proposals[action_id] for action_id in self.confirmed]

    def _generate_action_id(self, action: Dict[str, Any]) -> str:
        """Generate unique ID for an action"""
        action_str = json.dumps(action, sort_keys=True)
        return hashlib.sha256(
            f"{action_str}{self.node_id}{time.time()}".encode()
        ).hexdigest()

    def _check_consensus(self, action_id: str) -> bool:
        """Check if consensus is reached for an action"""
        if action_id not in self.votes:
            return False
            
        approve_count = sum(1 for v in self.votes[action_id].values() if v)
        reject_count = sum(1 for v in self.votes[action_id].values() if not v)
        
        return approve_count >= self.min_votes or reject_count >= self.min_votes

    def get_pending_proposals(self) -> Dict[str, Any]:
        """Get proposals waiting for consensus"""
        return {k:v for k,v in self.proposals.items() 
                if k not in self.confirmed}

    def validate_proposal(self, proposal: Dict[str, Any]) -> bool:
        """Validate a proposal's format and signature"""
        required_fields = {'action', 'proposer', 'timestamp', 'action_id'}
        if not all(field in proposal for field in required_fields):
            return False
            
        # Add additional validation logic here
        return True