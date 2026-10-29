# -*- coding: utf-8 -*-
"""轻量静态博客生成器：读取 content/posts/*.md，产出 public/ 纯静态站点。"""
import os, re, html, shutil, json
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "content", "posts")
OUT  = os.path.join(BASE, "public")

SITE = {
    "title": "我的笔记",
    "subtitle": "投资 · 生活 · 为人处世 · 工作 · 家庭",
    "desc": "记录思考，留存给家人。",
    "domain": "blog.kaoshang.top",
    "year": "2026",
}

CATS = [("投资", "touzi"), ("生活", "shenghuo"), ("为人处世", "weiren"), ("工作", "gongzuo"), ("家庭", "jiating")]
CAT_NAME = {s: n for n, s in CATS}
CAT_SLUG = {n: s for n, s in CATS}
LINKS = [
    ("港交所披露易", "https://www.hkexnews.hk"),
    ("巨潮资讯", "https://www.cninfo.com.cn"),
    ("上交所", "https://www.sse.com.cn"),
    ("深交所", "https://www.szse.cn"),
]

CSS = r"""
:root{--bg:#FFFFFF;--card:#FFFFFF;--border:#ECECEC;--text:#111111;--text-soft:#333333;--muted:#8A8A8A;--accent:#111111;--accent-light:#F3F3F3;--radius:4px;--font-title:Georgia,"Songti SC","SimSun",serif;--font-body:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;}
/* 仅保留 B 极简墨白单一风格，已移除 A 商务蓝白 / C 温暖纸感 / D 深色杂志 */
*{box-sizing:border-box}
body{margin:0;font-family:var(--font-body);background:var(--bg);color:var(--text);line-height:1.75;-webkit-font-smoothing:antialiased;transition:background .2s,color .2s}
a{color:var(--accent)}
header.top{background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:20}
.top-inner{max-width:1040px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit}
.avatar{width:38px;height:38px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:500}
.brand .bname{font-family:var(--font-title);font-size:17px;margin:0;font-weight:500}
.brand p{font-size:12px;margin:0;color:var(--muted)}
nav.cats{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
nav.cats a{font-size:13px;color:var(--muted);text-decoration:none;padding:5px 10px;border-radius:8px}
nav.cats a:hover,nav.cats a.active{background:var(--accent-light);color:var(--accent)}
/* 风格切换条已移除，仅保留 B 极简墨白 */
.wrap{max-width:1040px;margin:22px auto;padding:0 20px}
.layout{display:flex;gap:18px;align-items:flex-start}
.main{flex:1;min-width:0}
.aside{width:240px;flex:none}
@media(max-width:820px){.layout{flex-direction:column}.aside{width:100%}}
.hero{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px}
.hero h1,.hero h2{margin:0 0 6px;font-size:20px;font-weight:500;font-family:var(--font-title)}
.hero p{margin:0;color:var(--muted);font-size:14px}
.search{margin-top:14px;display:flex;gap:8px}
.search input{flex:1;border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-size:13px;background:var(--card);color:var(--text);font-family:inherit}
.btn{font-size:13px;padding:9px 18px;border-radius:8px;cursor:pointer;border:1px solid var(--accent);background:var(--accent);color:#fff;font-family:inherit}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
.chip{font-size:13px;padding:6px 14px;border:1px solid var(--border);border-radius:20px;background:var(--card);color:var(--muted);text-decoration:none}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.sec-title{font-size:14px;color:var(--muted);margin:18px 0 10px;font-weight:500}
.post{display:block;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 18px;margin-bottom:12px;transition:.15s}
.post:hover{border-color:var(--accent);box-shadow:0 2px 12px rgba(0,0,0,.06)}
.post h3{margin:0 0 6px;font-size:16px;font-weight:500;font-family:var(--font-title)}
.meta{font-size:12px;color:var(--muted);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.badge{font-size:11px;padding:2px 9px;border-radius:6px;background:var(--accent-light);color:var(--accent);text-decoration:none}
.ex{font-size:13px;color:var(--muted);margin:8px 0 0}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.tag{font-size:11px;color:var(--muted);background:var(--bg);border:1px solid var(--border);padding:2px 8px;border-radius:6px}
.adbox{border:1px dashed var(--border);border-radius:var(--radius);padding:26px 16px;text-align:center;color:var(--muted);font-size:12px;background:var(--card);margin-bottom:12px}
.adbox b{display:block;font-size:13px;color:var(--text-soft);font-weight:500;margin-bottom:4px}
.card-side{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:14px}
.card-side h4{margin:0 0 10px;font-size:13px;font-weight:500;color:var(--text)}
.card-side p{font-size:12px;color:var(--muted);margin:0 0 6px}
.card-side a{display:block;font-size:13px;color:var(--accent);text-decoration:none;padding:4px 0}
.card-side a:hover{text-decoration:underline}
.article{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:16px}
.article h1{font-size:25px;margin:0 0 10px;font-weight:500;font-family:var(--font-title);line-height:1.4}
.article h2{font-size:19px;margin:22px 0 8px;font-family:var(--font-title);font-weight:500}
.article h3{font-size:16px;margin:18px 0 6px;font-weight:500}
.article p{font-size:15px;color:var(--text-soft);margin:0 0 14px}
.article a{color:var(--accent)}
.article ul{margin:0 0 14px;padding-left:22px;color:var(--text-soft);font-size:15px}
.article li{margin:4px 0}
.article blockquote{margin:0 0 14px;padding:8px 14px;border-left:3px solid var(--accent);background:var(--accent-light);color:var(--text-soft);font-size:14px}
.article pre{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px;overflow:auto;font-size:13px}
.article code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;background:var(--bg);padding:1px 5px;border-radius:4px}
.article pre code{background:none;padding:0}
.back{font-size:13px;color:var(--accent);text-decoration:none;margin-bottom:14px;display:inline-block}
.foot{border-top:1px solid var(--border);margin-top:30px;background:var(--card)}
.foot-inner{max-width:1040px;margin:0 auto;padding:22px 20px;text-align:center;color:var(--muted);font-size:12px}
.foot-inner p{margin:2px 0}
"""

JS = r"""
document.addEventListener('DOMContentLoaded',function(){
  var s=document.getElementById('search');
  if(s){s.addEventListener('input',function(){var q=s.value.trim().toLowerCase();document.querySelectorAll('#home-list .post').forEach(function(el){var txt=(el.getAttribute('data-search')||'').toLowerCase();el.style.display=(!q||txt.indexOf(q)>-1)?'':'none';});});}
});
"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="minimal">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<link rel="stylesheet" href="{{ROOT}}static/style.css">
</head>
<body>
{{HEADER}}
<div class="wrap">{{CONTENT}}</div>
{{FOOTER}}
<script src="{{ROOT}}static/blog.js"></script>
</body>
</html>"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md_to_html(md):
    lines = md.splitlines()
    out, para, code = [], [], []
    in_code = False
    i = 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code, in_code = [], False
            else:
                flush()
                in_code = True
            i += 1
            continue
        if in_code:
            code.append(line)
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush()
            lv = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lv, inline(m.group(2)), lv))
            i += 1
            continue
        if s.startswith(">"):
            flush()
            out.append("<blockquote>" + inline(s[1:].strip()) + "</blockquote>")
            i += 1
            continue
        if re.match(r"^[-*]\s+", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append("<li>" + inline(re.sub(r"^[-*]\s+", "", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        para.append(s)
        i += 1
    flush()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
    return "\n".join(out)


def parse_post(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    meta, body = {}, raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2]
    slug = os.path.splitext(os.path.basename(path))[0]
    raw_tags = meta.get("tags", "")
    if isinstance(raw_tags, list):
        tags = [str(t).strip() for t in raw_tags if str(t).strip()]
    else:
        tags = [t.strip() for t in re.split(r"[,，]", str(raw_tags)) if t.strip()]
    excerpt = meta.get("excerpt", "").strip()
    if not excerpt:
        plain = re.sub(r"[#>*`\[\]()]", "", body).strip()
        excerpt = plain[:78] + ("…" if len(plain) > 78 else "")
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "category": meta.get("category", ""),
        "tags": tags,
        "date": meta.get("date", ""),
        "excerpt": excerpt,
        "body": body.strip(),
    }


def header(root, active_slug=""):
    items = '<a href="%sindex.html"%s>首页</a>' % (root, ' class="active"' if active_slug == "" else "")
    for name, slug in CATS:
        cls = ' class="active"' if slug == active_slug else ""
        items += '<a href="%sc/%s/index.html"%s>%s</a>' % (root, slug, cls, name)
    return (
        '<header class="top"><div class="top-inner">'
        '<a class="brand" href="%sindex.html"><div class="avatar">记</div>'
        '<div><div class="bname">%s</div><p>%s</p></div></a>'
        '<nav class="cats">%s</nav></div></header>'
        % (root, SITE["title"], SITE["subtitle"], items)
    )


def aside(root):
    about = '<div class="card-side"><h4>关于我</h4><p>%s</p></div>' % "一名 SRM 解决方案顾问，业余做点价值投资。这里记录想留给孩子和家人的思考。"
    ad = '<div class="adbox" style="padding:34px 16px;"><b>广告位（预留）</b>300 × 250</div>'
    links = '<div class="card-side"><h4>友情链接</h4>' + "".join(
        '<a href="%s" target="_blank" rel="noopener">%s</a>' % (u, t) for t, u in LINKS
    ) + "</div>"
    return "<aside class=\"aside\">%s%s%s</aside>" % (about, ad, links)


def footer():
    return (
        '<footer class="foot"><div class="foot-inner">'
        '<p>© %s %s · %s</p><p class="foot-sub">记录思考，留存给家人 · 纯静态站点</p>'
        "</div></footer>" % (SITE["year"], SITE["title"], SITE["domain"])
    )


def page(title, root, content, active_slug=""):
    out = PAGE
    out = out.replace("{{TITLE}}", title)
    out = out.replace("{{DESC}}", SITE["desc"])
    out = out.replace("{{ROOT}}", root)
    out = out.replace("{{HEADER}}", header(root, active_slug))
    out = out.replace("{{FOOTER}}", footer())
    out = out.replace("{{CONTENT}}", content)
    return out


def post_card(p, root):
    search = " ".join([p["title"], p["excerpt"], p["category"], " ".join(p["tags"])]).lower()
    tags = "".join('<span class="tag">#%s</span>' % t for t in p["tags"])
    return (
        '<a class="post" href="%sp/%s/index.html" data-search="%s">'
        '<h3>%s</h3>'
        '<div class="meta"><span class="badge">%s</span><span>%s</span><span>约 %d 分钟</span></div>'
        '<div class="ex">%s</div><div class="tags">%s</div></a>'
        % (root, p["slug"], html.escape(search), html.escape(p["title"]), p["category"], p["date"],
           max(1, len(p["body"]) // 400), html.escape(p["excerpt"]), tags)
    )


def build():
    posts = []
    for fn in sorted(os.listdir(SRC)):
        if fn.endswith(".md"):
            posts.append(parse_post(os.path.join(SRC, fn)))
    posts.sort(key=lambda p: p["date"], reverse=True)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "static"), exist_ok=True)
    with open(os.path.join(OUT, "static", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(OUT, "static", "blog.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    # 复制 static 源目录里的其它文件（如 Decap 后台上传的图片 uploads）
    SRC_STATIC = os.path.join(BASE, "static")
    if os.path.isdir(SRC_STATIC):
        for root, _, files in os.walk(SRC_STATIC):
            for fn in files:
                rel = os.path.relpath(os.path.join(root, fn), SRC_STATIC)
                dst = os.path.join(OUT, "static", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, fn), dst)
    # 复制 admin 后台页面到 public/admin（Decap CMS）
    SRC_ADMIN = os.path.join(BASE, "admin")
    if os.path.isdir(SRC_ADMIN):
        for root, _, files in os.walk(SRC_ADMIN):
            for fn in files:
                rel = os.path.relpath(os.path.join(root, fn), SRC_ADMIN)
                dst = os.path.join(OUT, "admin", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, fn), dst)

    chips = "".join('<a class="chip" href="c/%s/index.html">%s</a>' % (slug, name) for name, slug in CATS)
    hero = (
        '<div class="hero"><h2>记录思考，留存给家人</h2><p>%s</p>'
        '<div class="search"><input id="search" placeholder="搜索文章标题、标签…"></div></div>' % SITE["desc"]
    )
    home_main = (
        '<div class="hero"><h1>记录思考，留存给家人</h1><p>%s</p>'
        '<div class="search"><input id="search" placeholder="搜索文章标题、标签…"></div></div>'
        '<div class="chips">%s</div>'
        '<div class="adbox"><b>广告位（预留 · 首页横幅）</b>728 × 90</div>'
        '<div class="sec-title">最新文章</div><div id="home-list">%s</div>'
        % (SITE["desc"], chips, "".join(post_card(p, "") for p in posts))
    )
    home = '<div class="layout"><div class="main">%s</div>%s</div>' % (home_main, aside(""))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("%s · %s" % (SITE["title"], SITE["subtitle"]), "", home, ""))

    for name, slug in CATS:
        sub = [p for p in posts if p["category"] == name]
        content = (
            '<div class="layout"><div class="main">'
            '<div class="sec-title">%s · 共 %d 篇</div><div>%s</div></div>%s</div>'
            % (name, len(sub), "".join(post_card(p, "../../") for p in sub), aside("../../"))
        )
        d = os.path.join(OUT, "c", slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page("%s · %s" % (name, SITE["title"]), "../../", content, slug))

    for p in posts:
        tags = "".join('<span class="tag">#%s</span>' % t for t in p["tags"])
        article = (
            '<div class="article"><h1>%s</h1>'
            '<div class="meta"><a class="badge" href="../../c/%s/index.html">%s</a><span>%s</span><span>约 %d 分钟</span></div>'
            '%s<div class="tags">%s</div></div>'
            % (html.escape(p["title"]), CAT_SLUG.get(p["category"], ""), p["category"], p["date"],
               max(1, len(p["body"]) // 400), md_to_html(p["body"]), tags)
        )
        content = (
            '<div class="layout"><div class="main">'
            '<a class="back" href="../../index.html">← 返回</a>%s'
            '<div class="adbox" style="padding:30px 16px;"><b>广告位（预留 · 文末）</b>文章底部横幅</div>'
            '</div>%s</div>' % (article, aside("../../"))
        )
        d = os.path.join(OUT, "p", p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page("%s · %s" % (p["title"], SITE["title"]), "../../", content, CAT_SLUG.get(p["category"], "")))

    base = "https://" + SITE["domain"]
    urls = [base + "/", base + "/index.html"]
    for name, slug in CATS:
        urls.append("%s/c/%s/" % (base, slug))
    for p in posts:
        urls.append("%s/p/%s/" % (base, p["slug"]))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>%s</loc></url>" % u)
    sm.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % base)

    print("构建完成：%d 篇文章" % len(posts))
    for p in posts:
        print("  - [%s] %s" % (p["category"], p["title"]))


if __name__ == "__main__":
    build()
