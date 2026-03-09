# Worktree Orchestration v2.0.0 - Radical Architecture

## Vision: Event-Driven Competitive AI Framework

A **radical reimagining** of worktree orchestration that embraces:
- **Event-driven architecture** with reactive streams
- **JSON-RPC over Unix domain sockets** for IPC
- **Plugin-based extensibility** with hot-reloading
- **Directory-based isolation** (no git dependency)
- **Competitive rounds** with real-time scoring
- **WebSocket dashboard** for live monitoring

---

## Core Principles

### 1. Event-Driven Everything
- **Event Bus**: Central pub/sub system using RxJS observables
- **Reactive Streams**: All state changes flow through event streams
- **Decoupled Components**: Services communicate only via events
- **Backpressure Handling**: Built-in flow control for high-throughput scenarios

### 2. JSON-RPC Over Unix Sockets
- **Zero Network Overhead**: Local IPC via Unix domain sockets
- **Type-Safe RPC**: Auto-generated TypeScript types from JSON-RPC schemas
- **Request/Response + Notifications**: Full JSON-RPC 2.0 support
- **Connection Pooling**: Efficient socket reuse

### 3. Plugin Architecture
- **Hot-Reloadable**: Plugins can be updated without restart
- **Isolated Execution**: Each plugin runs in its own context
- **Event Hooks**: Plugins subscribe to events and emit new ones
- **Dependency Injection**: Plugins receive services via DI container

### 4. Directory-Based Isolation
- **Workspace Isolation**: Each "worktree" is a directory with its own environment
- **Snapshot System**: Capture state at any point
- **Copy-on-Write**: Efficient disk usage
- **Cleanup Policies**: Automatic garbage collection

### 5. Competitive Rounds
- **Round-Based Execution**: Multiple agents compete in rounds
- **Scoring System**: Pluggable scoring functions
- **Time Limits**: Per-round and per-action timeouts
- **Leaderboard**: Real-time ranking updates

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard (Port 4000)                │
│              WebSocket + HTTP REST API                  │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket + HTTP
┌────────────────────▼────────────────────────────────────┐
│              Orchestrator Core                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Event Bus   │  │ Round Engine │  │ Plugin Mgr   │ │
│  │  (RxJS)      │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC over Unix Socket
┌────────────────────▼────────────────────────────────────┐
│            JSON-RPC Server (Unix Socket)                │
│         /tmp/worktree-orch-v2.sock                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Workspace Manager                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Isolation   │  │  Snapshot    │  │  Cleanup     │ │
│  │  Manager     │  │  Manager     │  │  Manager     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Plugin Runtime                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Plugin A    │  │  Plugin B    │  │  Plugin C    │ │
│  │  (Isolated)  │  │  (Isolated)  │  │  (Isolated)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Event Bus (`core/event-bus.ts`)
- **RxJS Subject-based**: Multicast event streams
- **Type-safe events**: TypeScript discriminated unions
- **Middleware support**: Transform/filter events
- **Replay buffer**: Last N events cached for new subscribers

### 2. Round Engine (`core/round-engine.ts`)
- **Round lifecycle**: Init → Execute → Score → Complete
- **Agent registry**: Track competing agents
- **Action queue**: Per-agent action queues
- **Timeout management**: Per-round and per-action timeouts

### 3. JSON-RPC Server (`rpc/server.ts`)
- **Unix socket listener**: `/tmp/worktree-orch-v2.sock`
- **Request router**: Route methods to handlers
- **Error handling**: Standard JSON-RPC error codes
- **Batch support**: Multiple requests in one call

### 4. Workspace Manager (`workspace/manager.ts`)
- **Directory creation**: Isolated workspace directories
- **Environment setup**: Per-workspace env vars
- **Snapshot/restore**: Capture and restore state
- **Cleanup**: Remove old/unused workspaces

### 5. Plugin Manager (`plugins/manager.ts`)
- **Plugin loader**: Dynamic require/import
- **Hot reload**: Watch files and reload plugins
- **Dependency graph**: Resolve plugin dependencies
- **Sandboxing**: Isolated execution contexts

### 6. Dashboard (`dashboard/server.ts`)
- **Express server**: HTTP REST API
- **WebSocket server**: Real-time updates via Socket.IO
- **React frontend**: Modern UI (separate package)
- **Metrics aggregation**: Collect and display metrics

---

## Data Flow Example: Competitive Round

```
1. User starts round via JSON-RPC:
   → rpc.handleStartRound({ agents: ["agent1", "agent2"], task: "..." })
   
2. Round Engine emits: RoundStartedEvent
   → eventBus.emit({ type: "round.started", roundId: "r1", ... })
   
3. Plugins subscribe and react:
   → pluginA.on("round.started", () => { /* prepare workspace */ })
   → pluginB.on("round.started", () => { /* initialize agent */ })
   
4. Workspace Manager creates isolated directories:
   → workspace.create({ id: "r1-agent1", base: "/workspaces" })
   → workspace.create({ id: "r1-agent2", base: "/workspaces" })
   
5. Agents execute actions (via plugins):
   → plugin.agent.execute({ action: "write_file", ... })
   → eventBus.emit({ type: "action.executed", ... })
   
6. Scoring happens:
   → scorer.evaluate({ roundId: "r1", results: [...] })
   → eventBus.emit({ type: "round.scored", scores: {...} })
   
7. Dashboard receives updates via WebSocket:
   → socket.emit("round.update", { roundId: "r1", status: "completed" })
   
8. Round completes:
   → eventBus.emit({ type: "round.completed", roundId: "r1" })
   → workspace.cleanup({ roundId: "r1" })
```

---

## File Structure

```
worktree-orchestration-v2/
├── package.json
├── tsconfig.json
├── .eslintrc.js
├── jest.config.js
├── benchmark.config.js
│
├── src/
│   ├── index.ts                    # Main entry point
│   │
│   ├── core/
│   │   ├── event-bus.ts            # RxJS-based event bus
│   │   ├── round-engine.ts         # Round orchestration
│   │   ├── types.ts                # Core TypeScript types
│   │   └── errors.ts               # Error classes
│   │
│   ├── rpc/
│   │   ├── server.ts               # JSON-RPC server (Unix socket)
│   │   ├── client.ts               # JSON-RPC client
│   │   ├── methods.ts              # RPC method handlers
│   │   ├── schemas.ts              # JSON-RPC schemas
│   │   └── types.ts                # Auto-generated RPC types
│   │
│   ├── workspace/
│   │   ├── manager.ts              # Workspace lifecycle
│   │   ├── isolation.ts            # Directory isolation
│   │   ├── snapshot.ts             # Snapshot/restore
│   │   └── cleanup.ts              # Cleanup policies
│   │
│   ├── plugins/
│   │   ├── manager.ts              # Plugin loader/manager
│   │   ├── runtime.ts              # Plugin execution context
│   │   ├── registry.ts             # Plugin registry
│   │   └── types.ts                # Plugin interface
│   │
│   ├── dashboard/
│   │   ├── server.ts                # Express + Socket.IO server
│   │   ├── api/
│   │   │   ├── rounds.ts           # Round endpoints
│   │   │   ├── agents.ts           # Agent endpoints
│   │   │   └── metrics.ts          # Metrics endpoints
│   │   └── websocket.ts            # WebSocket handlers
│   │
│   ├── scoring/
│   │   ├── engine.ts                # Scoring engine
│   │   ├── strategies.ts           # Scoring strategies
│   │   └── types.ts                # Score types
│   │
│   └── utils/
│       ├── logger.ts                # Structured logging
│       ├── config.ts                # Configuration loader
│       └── validation.ts            # Schema validation
│
├── plugins/
│   ├── example-plugin/
│   │   ├── index.ts
│   │   ├── package.json
│   │   └── README.md
│   └── README.md
│
├── tests/
│   ├── unit/
│   │   ├── core/
│   │   ├── rpc/
│   │   ├── workspace/
│   │   └── plugins/
│   ├── integration/
│   │   ├── round-flow.test.ts
│   │   └── rpc-server.test.ts
│   ├── property/
│   │   └── event-bus.test.ts       # fast-check property tests
│   └── fixtures/
│       └── workspaces/
│
├── benchmarks/
│   ├── event-bus.bench.ts
│   ├── rpc-server.bench.ts
│   └── round-engine.bench.ts
│
├── docs/
│   ├── API.md                      # JSON-RPC API reference
│   ├── PLUGINS.md                  # Plugin development guide
│   └── DEPLOYMENT.md               # Deployment guide
│
└── scripts/
    ├── generate-rpc-types.ts       # Generate RPC types from schemas
    └── setup-dev.sh                # Development setup
```

---

## Technology Stack

- **Runtime**: Node.js 20+ (ESM)
- **Language**: TypeScript 5.3+
- **Event System**: RxJS 7+
- **RPC**: Custom JSON-RPC over Unix sockets
- **HTTP**: Express.js
- **WebSocket**: Socket.IO
- **Testing**: Jest + fast-check
- **Benchmarking**: benchmark.js
- **Logging**: pino (structured logging)
- **Validation**: zod (runtime type validation)

---

## MVP Scope (v1.0.0)

### ✅ Implemented
- [x] Event bus with RxJS
- [x] JSON-RPC server over Unix socket
- [x] Basic round engine (single round, 2 agents)
- [x] Workspace manager (directory creation/cleanup)
- [x] Plugin system (load/unload plugins)
- [x] Dashboard server (HTTP + WebSocket)
- [x] Basic scoring (time-based + correctness)

### 🔨 Stubbed (v1.1.0+)
- [ ] Snapshot/restore system (stub: always creates fresh)
- [ ] Advanced scoring strategies (stub: simple time+correctness)
- [ ] Plugin hot-reloading (stub: requires restart)
- [ ] Workspace copy-on-write (stub: full copies)
- [ ] Multi-round tournaments (stub: single rounds only)
- [ ] Advanced cleanup policies (stub: delete after round)
- [ ] Metrics aggregation (stub: basic counters)
- [ ] Plugin dependency resolution (stub: load order)

---

## Extensibility Points

1. **Custom Scoring**: Implement `ScoringStrategy` interface
2. **Custom Plugins**: Implement `Plugin` interface
3. **Custom Events**: Extend event type union
4. **Custom RPC Methods**: Add handlers to `rpc/methods.ts`
5. **Custom Workspace Backends**: Implement `WorkspaceBackend` interface

---

## Performance Targets

- **Event throughput**: >100K events/sec
- **RPC latency**: <1ms (p99)
- **Round startup**: <100ms
- **Workspace creation**: <50ms
- **Plugin load**: <200ms

---

## Security Considerations

- **Unix socket permissions**: 0600 (owner read/write only)
- **Plugin sandboxing**: Isolated Node.js contexts
- **Workspace isolation**: chroot-like directory isolation
- **Input validation**: Zod schemas for all inputs
- **Rate limiting**: Per-agent action rate limits

---

## Next Steps

1. **Phase 1**: Core event bus + RPC server
2. **Phase 2**: Round engine + workspace manager
3. **Phase 3**: Plugin system + dashboard
4. **Phase 4**: Testing + benchmarking
5. **Phase 5**: Documentation + examples
