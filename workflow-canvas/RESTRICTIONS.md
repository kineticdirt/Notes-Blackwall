# RESTRICTIONS Category

## Overview

The **RESTRICTIONS** category provides blocks for access control, rate limiting, validation, and other security/restriction mechanisms in workflows.

## Blocks

### 1. Rate Limit ⏱️
**Enforce rate limiting on requests**

- **Inputs:**
  - `requests` (number): Maximum number of requests allowed
  - `window` (number): Time window in seconds
  
- **Outputs:**
  - `allowed` (boolean): Whether request is allowed
  - `remaining` (number): Remaining requests in window

**Use Case:** Limit API calls to prevent abuse

### 2. Access Control 🔒
**Check access permissions**

- **Inputs:**
  - `user` (string): User identifier
  - `resource` (string): Resource identifier
  - `permission` (string): Permission type (read, write, etc.)
  
- **Outputs:**
  - `allowed` (boolean): Whether access is allowed
  - `reason` (string): Reason for allow/deny

**Use Case:** Enforce authorization before accessing resources

### 3. Validation ✅
**Validate data against rules**

- **Inputs:**
  - `data: Data to validate
  - `rules` (object): Validation rules (type, required, min, max)
  
- **Outputs:**
  - `valid` (boolean): Whether data is valid
  - `errors` (array): List of validation errors

**Use Case:** Validate input data before processing

### 4. Quota 📊
**Check and enforce quotas**

- **Inputs:**
  - `resource` (string): Resource identifier
  - `amount` (number): Amount to consume
  
- **Outputs:**
  - `within_quota` (boolean): Whether within quota
  - `remaining` (number): Remaining quota

**Use Case:** Track and limit resource usage

### 5. Time Window 🕐
**Restrict execution to time window**

- **Inputs:**
  - `start_time` (string): Start time (HH:MM format)
  - `end_time` (string): End time (HH:MM format)
  
- **Outputs:**
  - `allowed` (boolean): Whether current time is within window
  - `current_time` (string): Current time

**Use Case:** Allow operations only during business hours

### 6. Conditional Restriction 🚫
**Apply restriction based on condition**

- **Inputs:**
  - `condition` (boolean): Condition to evaluate
  - `action` (string): Action type (block/allow)
  
- **Outputs:**
  - `restricted` (boolean): Whether access is restricted
  - `message` (string): Restriction message

**Use Case:** Dynamic restrictions based on runtime conditions

## Usage Examples

### Rate Limiting Workflow
```
HTTP Request → Rate Limit → [If Allowed] → Process → HTTP Response
```

### Access Control Workflow
```
User Input → Access Control → [If Allowed] → Resource Access → Response
```

### Validation Workflow
```
Data Input → Validation → [If Valid] → Transform → Output
```

### Quota Management
```
Resource Request → Quota Check → [If Within Quota] → Execute → Update Quota
```

### Time-Based Restrictions
```
Request → Time Window → [If Allowed] → Process → Response
```

## Integration

Restrictions can be placed anywhere in a workflow to:
- **Protect resources** from unauthorized access
- **Limit usage** to prevent abuse
- **Validate inputs** before processing
- **Enforce policies** based on time, quotas, or conditions

## Configuration

Each restriction block can be configured with:
- Default behaviors
- Custom rules
- Error messages
- Fallback actions

The restrictions category enables secure, controlled workflow execution! 🚫
