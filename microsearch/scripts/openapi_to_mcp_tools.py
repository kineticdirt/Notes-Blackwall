#!/usr/bin/env python3
"""
Convert OpenAPI 3.x (JSON or YAML) to an MCP-style tools array (name, description, inputSchema).

Usage:
  python3 openapi_to_mcp_tools.py path/to/openapi.json -o tools_catalog.json

Optional: pip install pyyaml for .yaml/.yml inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def _load_spec(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            print("Install PyYAML for YAML specs: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
        return yaml.safe_load(raw)
    return json.loads(raw)


def _ref_name(ref: str) -> str | None:
    m = re.match(r"#/components/schemas/(.+)", ref.strip())
    return m.group(1) if m else None


def _resolve_schema(spec: dict, schema: dict | None) -> dict:
    if not schema:
        return {"type": "object", "properties": {}}
    if "$ref" in schema:
        name = _ref_name(schema["$ref"])
        comps = spec.get("components", {}).get("schemas", {})
        if name and name in comps:
            return _resolve_schema(spec, comps[name])
    return schema


def _param_to_property(spec: dict, param: dict) -> tuple[str, dict, bool]:
    name = param.get("name", "arg")
    required = param.get("required", False)
    schema = param.get("schema") or {"type": "string"}
    schema = _resolve_schema(spec, schema)
    prop = {
        "type": schema.get("type", "string"),
        "description": (param.get("description") or "")[:500],
    }
    if "enum" in schema:
        prop["enum"] = schema["enum"]
    return name, prop, bool(required)


def _body_schema(spec: dict, op: dict) -> tuple[dict, list[str]]:
    rb = op.get("requestBody", {})
    if not rb:
        return {}, []
    content = rb.get("content") or {}
    for ct in ("application/json", "application/*+json", "multipart/form-data"):
        if ct in content:
            s = content[ct].get("schema")
            resolved = _resolve_schema(spec, s or {})
            if resolved.get("type") == "object":
                props = resolved.get("properties") or {}
                req = list(resolved.get("required") or [])
                return props, req
            return {"payload": resolved}, (["payload"] if rb.get("required") else [])
    return {}, []


def _tool_name(method: str, path: str, op: dict) -> str:
    oid = op.get("operationId")
    if oid:
        return re.sub(r"[^a-zA-Z0-9_]", "_", oid).strip("_")
    # camelCase from path + method
    seg = [method.lower()] + [s for s in path.split("/") if s and not s.startswith("{")]
    parts = re.split(r"[^a-zA-Z0-9]+", "_".join(seg))
    camel = "".join(p[:1].upper() + p[1:].lower() for p in parts if p)
    return camel or f"{method.upper()}{abs(hash(path)) % 10000}"


def openapi_to_tools(spec: dict) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    paths = spec.get("paths") or {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            if method not in path_item:
                continue
            op = path_item[method]
            if not isinstance(op, dict):
                continue
            name = _tool_name(method, path, op)
            desc = (op.get("summary") or op.get("description") or f"{method.upper()} {path}")[:2000]
            properties: dict[str, Any] = {}
            required: list[str] = []

            for param in op.get("parameters") or []:
                if not isinstance(param, dict):
                    continue
                if param.get("in") not in ("query", "path", "header"):
                    continue
                pname, prop, req = _param_to_property(spec, param)
                properties[pname] = prop
                if req:
                    required.append(pname)

            body_props, body_req = _body_schema(spec, op)
            for k, v in body_props.items():
                if isinstance(v, dict):
                    properties[k] = {
                        "type": v.get("type", "string"),
                        "description": (v.get("description") or "")[:500],
                    }
                    if "enum" in v:
                        properties[k]["enum"] = v["enum"]
            for k in body_req:
                if k not in required:
                    required.append(k)

            tools.append(
                {
                    "name": name,
                    "description": desc,
                    "inputSchema": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                    "_meta": {"method": method.upper(), "path": path},
                }
            )
    return tools


def spec_sha256(spec: dict) -> str:
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAPI 3.x → MCP tools JSON array")
    parser.add_argument("openapi", type=Path, help="Path to openapi.json or .yaml")
    parser.add_argument("-o", "--output", type=Path, help="Write tools JSON array")
    parser.add_argument("--strip-meta", action="store_true", help="Omit _meta from output")
    args = parser.parse_args()

    spec = _load_spec(args.openapi)
    tools = openapi_to_tools(spec)
    out_tools = []
    for t in tools:
        row = {k: v for k, v in t.items() if k != "_meta" or not args.strip_meta}
        out_tools.append(row)

    payload = json.dumps(out_tools, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {len(out_tools)} tools to {args.output}", file=sys.stderr)
    else:
        print(payload)

    print(
        json.dumps(
            {
                "num_operations": len(out_tools),
                "openapi_sha256": spec_sha256(spec),
            },
            indent=2,
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
