import numpy as np
from collections import defaultdict

class WorkflowAnalyzer:
    def __init__(self, swarm_nodes):
        self.swarm_nodes = swarm_nodes
        self.workflow_metrics = defaultdict(list)

    def analyze_workflow(self):
        for node in self.swarm_nodes:
            for task in node.tasks:
                self.workflow_metrics[task].append({
                    'node_id': node.id,
                    'completion_time': task.completion_time,
                    'energy_consumption': task.energy_consumption
                })

        self.optimize_workflow()

    def optimize_workflow(self):
        for task, metrics in self.workflow_metrics.items():
            avg_completion_time = np.mean([m['completion_time'] for m in metrics])
            avg_energy_consumption = np.mean([m['energy_consumption'] for m in metrics])

            # Reassign tasks to nodes with lower completion time and energy consumption
            self.reassign_tasks(task, avg_completion_time, avg_energy_consumption)

    def reassign_tasks(self, task, avg_completion_time, avg_energy_consumption):
        best_node = None
        best_completion_time = float('inf')
        best_energy_consumption = float('inf')

        for node in self.swarm_nodes:
            if node.can_execute(task):
                completion_time = node.estimate_task_completion_time(task)
                energy_consumption = node.estimate_task_energy_consumption(task)

                if completion_time < best_completion_time and energy_consumption < best_energy_consumption:
                    best_node = node
                    best_completion_time = completion_time
                    best_energy_consumption = energy_consumption

        if best_node:
            best_node.assign_task(task)
