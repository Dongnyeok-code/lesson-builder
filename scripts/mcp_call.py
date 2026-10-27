#!/usr/bin/env python3
"""MCP 서버(npx 패키지)를 직접 불러 도구를 실행하는 도우미.
MCP가 클라이언트에 등록되어 있지 않은 환경(cowork, 스크립트)에서도 같은 데이터를 쓰기 위함.

사용법:
  python3 mcp_call.py <패키지> --list
  python3 mcp_call.py <패키지> <도구이름> '<JSON 인자>'
예:
  python3 mcp_call.py korean-elementary-learning-map-mcp get_standard '{"code":"6실02-07"}'
  python3 mcp_call.py korea-learning-map-mcp get_topic '{"code":"6실02-07"}'
"""
import json, subprocess, sys


def rpc(proc, msg):
    proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n"); proc.stdin.flush()
    if "id" not in msg:
        return None
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("MCP 서버 응답 없음")
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("id") == msg["id"]:
            return r


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    pkg, tool = sys.argv[1], sys.argv[2]
    args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    p = subprocess.Popen(["npx", "-y", pkg], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    try:
        rpc(p, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "lesson-builder", "version": "1"}}})
        rpc(p, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        if tool == "--list":
            r = rpc(p, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            for t in r["result"]["tools"]:
                props = list((t.get("inputSchema") or {}).get("properties", {}).keys())
                print(f'- {t["name"]}({", ".join(props)}): {t.get("description", "")[:90]}')
            return
        r = rpc(p, {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}})
        if "error" in r:
            print(json.dumps(r["error"], ensure_ascii=False, indent=1)); sys.exit(1)
        for c in r["result"].get("content", []):
            if c.get("type") == "text":
                print(c["text"])
    finally:
        p.terminate()


if __name__ == "__main__":
    main()
