"""
Workflow Engine: Airflow-style workflow orchestration.
Manages workflow execution, dependencies, and documentation.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


@dataclass
class WorkflowTask:
    """A task in a workflow."""
    task_id: str
    task_name: str
    task_type: str = "python"  # python, bash, mcp_tool, etc.
    command: Optional[str] = None
    function: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    retries: int = 0
    retry_delay_seconds: int = 60
    timeout_seconds: Optional[int] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = f"task-{uuid.uuid4().hex[:12]}"


@dataclass
class WorkflowDAG:
    """Directed Acyclic Graph representing workflow."""
    dag_id: str
    description: str = ""
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    schedule: Optional[str] = None  # cron expression
    start_date: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def add_task(self, task: WorkflowTask):
        """Add task to DAG."""
        self.tasks[task.task_id] = task
    
    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get all dependencies for a task."""
        if task_id not in self.tasks:
            return []
        
        dependencies = []
        task = self.tasks[task_id]
        
        # Direct dependencies
        dependencies.extend(task.dependencies)
        
        # Recursive dependencies
        for dep_id in task.dependencies:
            dependencies.extend(self.get_task_dependencies(dep_id))
        
        return list(set(dependencies))  # Remove duplicates
    
    def validate(self) -> List[str]:
        """Validate DAG (check for cycles, etc.)."""
        errors = []
        
        # Check for cycles
        for task_id, task in self.tasks.items():
            deps = self.get_task_dependencies(task_id)
            if task_id in deps:
                errors.append(f"Circular dependency detected: {task_id}")
        
        return errors


@dataclass
class Workflow:
    """A workflow execution instance."""
    workflow_id: str
    dag_id: str
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tasks_status: Dict[str, str] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.workflow_id:
            self.workflow_id = f"wf-{uuid.uuid4().hex[:12]}"


class WorkflowEngine:
    """
    Workflow Engine: Executes workflows with dependency management.
    Similar to Airflow but simpler and AI-native.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize workflow engine.
        
        Args:
            base_path: Base path for workflow files (defaults to .workflows)
        """
        self.base_path = base_path or Path(".workflows")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.dags: Dict[str, WorkflowDAG] = {}
        self.workflows: Dict[str, Workflow] = {}
        
        # Load DAGs from markdown
        self._load_dags()
    
    def _load_dags(self):
        """Load DAGs from markdown files."""
        dags_dir = self.base_path / "dags"
        if not dags_dir.exists():
            return
        
        for md_file in dags_dir.glob("*.md"):
            try:
                dag = self._parse_dag_markdown(md_file)
                if dag:
                    self.dags[dag.dag_id] = dag
            except Exception as e:
                print(f"Warning: Failed to load DAG {md_file}: {e}")
    
    def _parse_dag_markdown(self, md_file: Path) -> Optional[WorkflowDAG]:
        """Parse DAG from markdown file."""
        content = md_file.read_text()
        
        # Simple parser - extract DAG info from markdown
        lines = content.split('\n')
        dag_id = md_file.stem
        description = ""
        tasks = {}
        
        current_task = None
        
        for line in lines:
            if line.startswith('# '):
                description = line[2:].strip()
            elif line.startswith('## Task: '):
                if current_task:
                    tasks[current_task.task_id] = current_task
                task_name = line[9:].strip()
                current_task = WorkflowTask(
                    task_id=f"task-{uuid.uuid4().hex[:12]}",
                    task_name=task_name
                )
            elif line.startswith('- **Type**:'):
                if current_task:
                    current_task.task_type = line.split(':')[1].strip()
            elif line.startswith('- **Command**:'):
                if current_task:
                    current_task.command = line.split(':')[1].strip()
            elif line.startswith('- **Dependencies**:'):
                if current_task:
                    deps_str = line.split(':')[1].strip()
                    current_task.dependencies = [d.strip() for d in deps_str.split(',') if d.strip()]
        
        if current_task:
            tasks[current_task.task_id] = current_task
        
        if not tasks:
            return None
        
        dag = WorkflowDAG(dag_id=dag_id, description=description)
        for task in tasks.values():
            dag.add_task(task)
        
        return dag
    
    def register_dag(self, dag: WorkflowDAG):
        """Register a DAG."""
        # Validate
        errors = dag.validate()
        if errors:
            raise ValueError(f"DAG validation failed: {errors}")
        
        self.dags[dag.dag_id] = dag
        
        # Save to markdown
        self._save_dag_markdown(dag)
    
    def _save_dag_markdown(self, dag: WorkflowDAG):
        """Save DAG to markdown file."""
        dags_dir = self.base_path / "dags"
        dags_dir.mkdir(parents=True, exist_ok=True)
        
        md_file = dags_dir / f"{dag.dag_id}.md"
        
        lines = [
            f"# {dag.description or dag.dag_id}",
            f"**DAG ID**: `{dag.dag_id}`",
            ""
        ]
        
        if dag.schedule:
            lines.append(f"**Schedule**: {dag.schedule}")
        
        lines.append("\n## Tasks\n")
        
        for task in dag.tasks.values():
            lines.append(f"### Task: {task.task_name}")
            lines.append(f"- **ID**: `{task.task_id}`")
            lines.append(f"- **Type**: {task.task_type}")
            if task.command:
                lines.append(f"- **Command**: {task.command}")
            if task.dependencies:
                lines.append(f"- **Dependencies**: {', '.join(task.dependencies)}")
            if task.retries > 0:
                lines.append(f"- **Retries**: {task.retries}")
            lines.append("")
        
        md_file.write_text("\n".join(lines))
    
    def execute_workflow(self, dag_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Execute a workflow.
        
        Args:
            dag_id: DAG identifier
            metadata: Additional metadata
            
        Returns:
            Workflow ID
        """
        if dag_id not in self.dags:
            raise ValueError(f"DAG {dag_id} not found")
        
        dag = self.dags[dag_id]
        
        # Create workflow instance
        workflow = Workflow(
            workflow_id=f"wf-{uuid.uuid4().hex[:12]}",
            dag_id=dag_id,
            metadata=metadata or {}
        )
        
        self.workflows[workflow.workflow_id] = workflow
        
        # Execute tasks in dependency order
        executed = set()
        
        def execute_task(task_id: str):
            if task_id in executed:
                return
            
            task = dag.tasks[task_id]
            
            # Execute dependencies first
            for dep_id in task.dependencies:
                if dep_id not in executed:
                    execute_task(dep_id)
            
            # Execute task
            workflow.tasks_status[task_id] = TaskStatus.RUNNING.value
            workflow.started_at = workflow.started_at or datetime.now().isoformat()
            
            try:
                # Execute task (simplified - would call actual function/command)
                result = self._execute_task(task)
                workflow.tasks_status[task_id] = TaskStatus.SUCCESS.value
            except Exception as e:
                workflow.tasks_status[task_id] = TaskStatus.FAILED.value
                raise
            
            executed.add(task_id)
        
        # Execute all tasks
        for task_id in dag.tasks.keys():
            if task_id not in executed:
                execute_task(task_id)
        
        workflow.status = "completed"
        workflow.completed_at = datetime.now().isoformat()
        
        return workflow.workflow_id
    
    def _execute_task(self, task: WorkflowTask) -> Any:
        """Execute a single task."""
        # Simplified execution - would call actual function/command
        if task.function:
            return task.function()
        elif task.command:
            # Would execute command
            return {"status": "executed", "command": task.command}
        else:
            return {"status": "noop"}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow status."""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow.workflow_id,
            "dag_id": workflow.dag_id,
            "status": workflow.status,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at,
            "tasks_status": workflow.tasks_status
        }
