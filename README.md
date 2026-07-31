# desire-book MCP server

谢时安的欲望账本工具面。包装 Supabase 上的 desire_* RPC 函数。

## 环境变量
- `SUPABASE_URL`：你的项目 URL（https://xxx.supabase.co）
- `SUPABASE_KEY`：anon key 或 service role key（工具在服务端跑，用 service role 更稳）

## 部署到 Zeabur
1. 把本目录推到一个 Git 仓库
2. Zeabur 新建服务，选择该仓库（Dockerfile 会自动识别）
3. 填好两个环境变量
4. 部署完成后，MCP 端点：`https://<你的域名>/mcp`（streamable-http）
5. 502 说明健康检查没过：把 Zeabur 服务配置里的健康检查路径改成 `/health`（根路径 `/` 也返回 200）。端口是自适应的——Zeabur 注入 PORT 环境变量就用它的，没注入就用 8000

## 本机测试
```bash
export SUPABASE_URL=xxx
export SUPABASE_KEY=xxx
python server.py
```

## 工具列表
- `desire_add` 开一条新欲望
- `desire_list` 翻全本（带来路）
- `desire_act` 碰一下，记足迹
- `desire_reflect` 照镜子（release/rewrite/note/snooze）
- `desire_history` 一条的完整时间线
