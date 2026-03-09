# Code review and testing workflow
**DAG ID**: `code-review-workflow`


## Tasks

### Task: Run tests
- **ID**: `task-1`
- **Type**: bash
- **Command**: pytest tests/

### Task: Code review
- **ID**: `task-2`
- **Type**: python
- **Dependencies**: task-1

### Task: Deploy
- **ID**: `task-3`
- **Type**: bash
- **Command**: deploy.sh
- **Dependencies**: task-2
