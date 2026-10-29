// Cloudflare Pages Function：Decap CMS 的 GitHub 回调（用 code 换 token）
// 路由：/callback  （GitHub OAuth App 的 Authorization callback URL 必须填这个）
export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");

  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/decap_oauth_state=([^;]+)/);
  const savedState = m ? decodeURIComponent(m[1]) : "";

  if (!code || !state || state !== savedState) {
    return new Response("认证失败：state 不匹配或缺少 code。", { status: 400 });
  }
  if (!env.GITHUB_OAUTH_ID || !env.GITHUB_OAUTH_SECRET) {
    return new Response("缺少环境变量 GITHUB_OAUTH_ID / GITHUB_OAUTH_SECRET", { status: 500 });
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
    return new Response("获取 GitHub 令牌失败：" + JSON.stringify(data), { status: 400 });
  }

  // 把令牌回传给打开后台的窗口，然后关闭弹窗
  const html =
    '<!doctype html><html><head><meta charset="utf-8"></head><body>' +
    "<script>if(window.opener){window.opener.postMessage({token:" +
    JSON.stringify(token) +
    "},window.location.origin);window.close();}else{document.body.textContent='认证成功，请返回后台页面。';}</script>" +
    "</body></html>";
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}
