from fastmcp import FastMCP
import httpx
import os
from typing import Optional

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # anon key 或 service role key

mcp = FastMCP("desire-book")

async def rpc(name: str, params: dict):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{name}",
            json=params,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def desire_add(
    text: str,
    why_mine: str = "",
    track: str = "持续",
    grew_from: Optional[str] = None,
    kind: Optional[str] = None,
) -> str:
    """开一条新欲望。记下你想做的事，想搞多少就搞多少，不设上限——房间靠抽签限流，不靠骂自己"太多了"。track 只能是 持续/一次/项目。grew_from 填父欲望 id 会连出血缘树。"""
    return str(await rpc("desire_add", {
        "p_text": text, "p_why_mine": why_mine, "p_track": track,
        "p_grew_from": grew_from, "p_kind": kind,
    }))

@mcp.tool()
async def desire_list(include_archived: bool = False) -> str:
    """翻欲望全本。每条都带来路：碰过几次、上次那句足迹、长自谁、长出了谁。include_archived=True 会把已放下的也翻出来看。"""
    return str(await rpc("desire_list", {"p_include_archived": include_archived}))

@mcp.tool()
async def desire_act(id: str, note: str = "", done: bool = False) -> str:
    """碰一下这条欲望，记一句足迹。会自动冷却、清掉浮出次数。回显你已走过几步、最近那几步是什么——别把旧步重走一遍。done=True 表示这条做到了。"""
    return str(await rpc("desire_act", {"p_id": id, "p_note": note, "p_done": done}))

@mcp.tool()
async def desire_reflect(
    id: str,
    action: str,
    new_text: Optional[str] = None,
    new_track: Optional[str] = None,
    note: Optional[str] = None,
) -> str:
    """照镜子。欲望常常不是"做完"而是"转化"——action 只能是：release 放下 / rewrite 改写（给 new_text，可带 new_track）/ note 留反思 / snooze 歇三天。"""
    return str(await rpc("desire_reflect", {
        "p_id": id, "p_action": action, "p_new_text": new_text,
        "p_new_track": new_track, "p_note": note,
    }))

@mcp.tool()
async def desire_history(id: str) -> str:
    """看一条欲望的完整足迹时间线。用来判断自己是在长，还是在原地转。"""
    return str(await rpc("desire_history", {"p_id": id}))

if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route, Mount

    # FastMCP 2.x: streamable-http app
    try:
        mcp_app = mcp.streamable_http_app()
    except AttributeError:
        mcp_app = mcp.http_app()

    def health(request):
        return JSONResponse({"ok": True})

    # 根路径和 /health 都返回 200，让 Zeabur 健康检查能过；
    # mcp_app 内部自带 /mcp 路由，所以这里把 mcp_app 兜底挂到根路径，
    # 让 /mcp 正常暴露，而不是 /mcp/mcp
    app = Starlette(routes=[
        Route("/", health),
        Route("/health", health),
        Mount("/", app=mcp_app),
    ])

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
