// Cloudflare Pages Function：Decap CMS 的 GitHub 登录入口
// 路由：/auth  （由 Decap 后台的 auth_endpoint 调用）
// 需要的 Cloudflare Pages 环境变量（Secrets）：GITHUB_OAUTH_ID、GITHUB_OAUTH_SECRET
export async function onRequestGet({ request, env }) {
  if (!env.GITHUB_OAUTH_ID) {
    return new Response("缺少环境变量 GITHUB_OAUTH_ID", { status: 500 });
  }
  const url = new URL(request.url);
  const origin = url.origin;
  const state = crypto.randomUUID();
  const authorizeUrl =
    "https://github.com/login/oauth/authorize?" +
    new URLSearchParams({
      client_id: env.GITHUB_OAUTH_ID,
      redirect_uri: origin + "/callback",
      scope: "repo",
      state: state,
      allow_signup: "false",
    }).toString();
  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizeUrl,
      "Set-Cookie":
        "decap_oauth_state=" + state + "; Path=/; HttpOnly; SameSite=Lax; Max-Age=600",
    },
  });
}
