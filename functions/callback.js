// Cloudflare Pages Function：Decap CMS 的 GitHub 回调（用 code 换 token）
// 路由：/callback  （GitHub OAuth App 的 Authorization callback URL 必须填这个）
// 关键：Decap/Netlify CMS 的握手协议——
//   1) popup 先向主窗口 postMessage('authorizing:github')
//   2) 主窗口应答后，popup 把 'authorization:github:success:{token,provider}' 发回
export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");

  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/decap_oauth_state=([^;]+)/);
  const savedState = m ? decodeURIComponent(m[1]) : "";

  if (!code || !state || state !== savedState) {
    return renderHandshake("error", "认证失败：state 不匹配或缺少 code。");
  }
  if (!env.GITHUB_OAUTH_ID || !env.GITHUB_OAUTH_SECRET) {
    return renderHandshake("error", "缺少环境变量 GITHUB_OAUTH_ID / GITHUB_OAUTH_SECRET");
  }

  const origin = url.origin;
  const resp = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      client_id: env.GITHUB_OAUTH_ID,
      client_secret: env.GITHUB_OAUTH_SECRET,
      code: code,
      redirect_uri: origin + "/callback",
    }),
  });
  const data = await resp.json();
  const token = data.access_token;
  if (!token) {
    return renderHandshake("error", "获取 GitHub 令牌失败：" + JSON.stringify(data));
  }

  return renderHandshake("success", token);
}

function renderHandshake(kind, payload) {
  const content =
    kind === "success"
      ? JSON.stringify({ token: payload, provider: "github" })
      : JSON.stringify({ error: String(payload) });
  const message = JSON.stringify(`authorization:github:${kind}:${content}`);
  const html =
    '<!doctype html><html><head><meta charset="utf-8"></head><body>' +
    "<script>(function(){" +
    "function receiveMessage(e){if(window.opener){window.opener.postMessage(" +
    message +
    ",e.origin);}}" +
    "window.addEventListener('message',receiveMessage,false);" +
    "if(window.opener){window.opener.postMessage('authorizing:github','*');}" +
    "})();</script>" +
    "</body></html>";
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}
