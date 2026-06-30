#!/usr/bin/env python3
"""Genera portal/hub.html: centro de mando único que enlaza TODAS las pantallas de los
3 sitios (portal de diseño + panel TailAdmin + panel Spike) sin fusionarlos.
Escanea el disco -> catálogo categorizado -> hub.html autocontenido (cardeep, con buscador)."""
import glob, os, json, html
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # portal/
def stems(pattern, base):
    out=[]
    for p in sorted(glob.glob(os.path.join(ROOT, pattern))):
        out.append((os.path.splitext(os.path.basename(p))[0], os.path.relpath(p, ROOT).replace("\\","/")))
    return out
def pretty(s):
    s=s.replace("-"," ").replace("_"," ").strip()
    return s[:1].upper()+s[1:] if s else s

# ---- Sitio 1: portal de diseño cardeep ----
DESIGN={"index":"Landing","marketplace":"Marketplace","analitica":"Analítica","dashboard":"Resumen",
 "dealers":"Dealers","dossier":"Dossier 3D","finanzas":"Finanzas","garaje":"Garaje 360°",
 "inteligencia":"Inteligencia","plano":"Plano 3D","arbitrage":"Arbitrage"}
design=[{"cat":"Pantallas","items":[{"label":DESIGN[s],"href":h} for s,h in stems("*.html","") if s in DESIGN]}]

# ---- Sitio 2: TailAdmin PRO (app/*.html) ----
TA_LABEL={"index":"eCommerce","analytics":"Analytics","marketing":"Marketing","crm":"CRM","stocks":"Stocks",
 "saas":"SaaS","logistics":"Logistics","sales":"Sales","finance":"Finanzas","ai":"AI Assistant",
 "ai-settings":"AI · Ajustes","code-generator":"Generador de código","image-generator":"Generador de imágenes",
 "integrations":"Integraciones","api-keys":"API Keys","chat":"Chat","inbox":"Inbox","inbox-details":"Inbox · detalle",
 "calendar":"Calendario","file-manager":"Gestor de archivos","invoices":"Facturas","create-invoice":"Crear factura",
 "single-invoice":"Factura","products-list":"Productos","add-product":"Añadir producto","billing":"Facturación",
 "transactions":"Transacciones","profile":"Perfil","signin":"Entrar","signup":"Registro","reset-password":"Recuperar"}
def ta_cat(s):
    if s in {"index","analytics","marketing","crm","stocks","saas","logistics","sales","finance"}: return "Dashboards"
    if s in {"ai","ai-settings","code-generator","image-generator","integrations","api-keys"}: return "IA"
    if s in {"products-list","add-product","billing","invoices","create-invoice","single-invoice","transactions"}: return "E-commerce"
    if s in {"chat","inbox","inbox-details","calendar","file-manager","task-list","task-kanban","email"}: return "Apps"
    if "chart" in s: return "Gráficas"
    if "table" in s: return "Tablas"
    if "form" in s: return "Formularios"
    if "layout" in s: return "Layouts"
    if s in {"signin","signup","reset-password","two-step-verification"}: return "Acceso"
    if s in {"404","500","503","coming-soon","maintenance","success","blank","faq","pricing-tables","profile","maps"}: return "Páginas"
    return "Componentes UI"
def build(items_stems, cat_fn, label_map):
    groups={}
    for s,h in items_stems:
        c=cat_fn(s); groups.setdefault(c,[]).append({"label":label_map.get(s,pretty(s)),"href":h})
    order=["Dashboards","IA","E-commerce","Apps","Gráficas","Tablas","Formularios","Componentes UI","Layouts","Páginas","Acceso","Blog","Iconos","Otros"]
    return [{"cat":c,"items":sorted(groups[c],key=lambda x:x["label"])} for c in order if c in groups]
tailadmin=build(stems("app/*.html",""), ta_cat, TA_LABEL)

# ---- Sitio 3: Spike PRO (app/spike/main/*.html) ----
SP_LABEL={"index":"Dashboard","index2":"Dashboard 2"}
def sp_cat(s):
    if s in {"index","index2"}: return "Dashboards"
    if s.startswith("app-"): return "Apps"
    if s.startswith("eco-"): return "E-commerce"
    if s.startswith("chart-"): return "Gráficas"
    if s.startswith("form-"): return "Formularios"
    if s.startswith("table-"): return "Tablas"
    if s.startswith("ui-"): return "Componentes UI"
    if s.startswith("authentication-"): return "Acceso"
    if s.startswith("blog-"): return "Blog"
    if s.startswith("icon-"): return "Iconos"
    if s.startswith("page-"): return "Páginas"
    return "Páginas"
def sp_label(s):
    if s in SP_LABEL: return SP_LABEL[s]
    for pre in ("app-","eco-","chart-","chart-apex-","form-","table-","ui-","authentication-","blog-","icon-","page-"):
        if s.startswith(pre): return pretty(s[len(pre):])
    return pretty(s)
sp_stems=stems("app/spike/main/*.html","")
spg={}
for s,h in sp_stems: spg.setdefault(sp_cat(s),[]).append({"label":sp_label(s),"href":h})
order=["Dashboards","Apps","E-commerce","Gráficas","Tablas","Formularios","Componentes UI","Blog","Iconos","Páginas","Acceso"]
spike=[{"cat":c,"items":sorted(spg[c],key=lambda x:x["label"])} for c in order if c in spg]

SITES=[
 {"id":"portal","name":"Portal cardeep","desc":"El sitio de diseño (landing, marketplace, paneles del producto).","index":"index.html","groups":design},
 {"id":"tailadmin","name":"Panel · TailAdmin","desc":"Suite admin completa: dashboards, apps, e-commerce, IA, charts, tablas, UI.","index":"app/index.html","groups":tailadmin},
 {"id":"spike","name":"Panel · Spike","desc":"Suite admin Spike: dashboards, apps, eco-shop, blog, charts, componentes.","index":"app/spike/main/index2.html","groups":spike},
]
total=sum(len(i["items"]) for st in SITES for i in st["groups"])

def chips(items):
    return "".join('<a class="chip" target="_blank" rel="noopener" data-l="%s" href="%s">%s</a>'
        %(html.escape(it["label"].lower()), html.escape(it["href"]), html.escape(it["label"])) for it in items)
def section(st):
    g="".join('<div class="grp"><div class="grp-h">%s <span class="grp-n">%d</span></div><div class="chips">%s</div></div>'
        %(html.escape(gr["cat"]), len(gr["items"]), chips(gr["items"])) for gr in st["groups"])
    cnt=sum(len(gr["items"]) for gr in st["groups"])
    return ('<section class="site" data-site="%s"><div class="site-h"><div><h2>%s</h2><p>%s</p></div>'
        '<a class="open" target="_blank" rel="noopener" href="%s">Abrir sitio ↗</a></div>'
        '<div class="site-c mono">%d pantallas</div>%s</section>'
        %(st["id"], html.escape(st["name"]), html.escape(st["desc"]), html.escape(st["index"]), cnt, g))

HTML=f'''<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>cardeep · centro de mando</title>
<link rel="icon" href="assets/cd-icon.png">
<link href="https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#EEF1F5;--panel:#FFF;--panel2:#F4F6F9;--ink:#13161B;--ink2:rgba(19,22,27,.6);--ink3:rgba(19,22,27,.42);
--line:rgba(20,28,40,.1);--mint:#1AA567;--mint2:#E4F3EB;--mintInk:#0B7C49;--navy:#13366B;--navy2:#1B4A8F;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:'General Sans','Segoe UI',system-ui,sans-serif;letter-spacing:-.005em;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}.mono{{font-family:'JetBrains Mono',monospace}}
.wrap{{max-width:1180px;margin:0 auto;padding:30px 24px 80px}}
.hero{{position:relative;overflow:hidden;border-radius:22px;padding:34px 34px 30px;color:#EAF2FF;background:radial-gradient(120% 160% at 88% -30%,var(--navy2),var(--navy) 62%);margin-bottom:26px}}
.hero::after{{content:"";position:absolute;right:-30px;top:-50px;width:240px;height:240px;border-radius:50%;background:radial-gradient(circle,rgba(70,214,160,.5),transparent 65%)}}
.brand{{display:flex;align-items:center;gap:11px;position:relative}}
.brand b{{font-size:21px;font-weight:700;letter-spacing:-.03em}}
.hero h1{{position:relative;margin:16px 0 6px;font-size:clamp(24px,3vw,34px);font-weight:600;letter-spacing:-.03em}}
.hero p{{position:relative;margin:0;color:rgba(234,242,255,.72);font-size:15px;max-width:560px}}
.search{{position:relative;margin-top:20px;display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:13px;padding:0 14px;max-width:480px}}
.search input{{flex:1;background:none;border:0;outline:none;color:#fff;font-size:15px;padding:13px 0;font-family:inherit}}
.search input::placeholder{{color:rgba(234,242,255,.6)}}
.stat{{position:relative;margin-top:14px;font-size:12.5px;color:rgba(234,242,255,.85)}}
.site{{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px 22px 8px;margin-bottom:18px;box-shadow:0 1px 3px rgba(20,28,40,.04)}}
.site-h{{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}}
.site-h h2{{margin:0;font-size:19px;font-weight:600;letter-spacing:-.02em}}
.site-h p{{margin:4px 0 0;font-size:13.5px;color:var(--ink2);max-width:560px}}
.open{{flex-shrink:0;font-size:13px;font-weight:600;color:var(--mintInk);background:var(--mint2);padding:9px 14px;border-radius:10px}}
.open:hover{{background:#d6ecdf}}
.site-c{{font-size:11px;color:var(--ink3);margin:10px 0 14px}}
.grp{{padding:12px 0;border-top:1px solid var(--line)}}
.grp-h{{font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:10px}}
.grp-n{{color:var(--mint);margin-left:4px}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chip{{font-size:13px;font-weight:500;color:var(--ink);background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:8px 13px;transition:background .15s,border-color .15s,transform .12s}}
.chip:hover{{background:var(--mint2);border-color:var(--mint);color:var(--mintInk);transform:translateY(-1px)}}
.empty{{display:none}}
footer{{margin-top:24px;font-size:12px;color:var(--ink3);text-align:center}}
.nohit{{display:none;padding:30px;text-align:center;color:var(--ink3)}}
</style></head>
<body>
<div class="wrap">
  <div class="hero">
    <div class="brand"><svg width="30" height="30" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10.6" stroke="#46D6A0" stroke-width="1.5"/><circle cx="12" cy="12" r="6.4" stroke="#46D6A0" stroke-width="1.5"/><circle cx="12" cy="12" r="2.6" fill="#46D6A0"/></svg><b>cardeep</b></div>
    <h1>Centro de mando</h1>
    <p>Todos los paneles y pantallas de cardeep, accesibles desde un solo sitio. Cada panel se abre intacto en su pestaña.</p>
    <div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(234,242,255,.7)" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg><input id="q" placeholder="Buscar pantalla… (chat, factura, crm, gráfica…)" autocomplete="off"></div>
    <div class="stat mono">{len(SITES)} sitios · {total} pantallas</div>
  </div>
  <div id="nohit" class="nohit">Sin resultados para “<span id="qe"></span>”.</div>
  {''.join(section(s) for s in SITES)}
  <footer class="mono">cardeep · centro de mando — generado por _build/gen_hub.py</footer>
</div>
<script>
const q=document.getElementById('q'),nohit=document.getElementById('nohit'),qe=document.getElementById('qe');
q.addEventListener('input',()=>{{
  const t=q.value.toLowerCase().trim(); let any=false;
  document.querySelectorAll('.site').forEach(site=>{{
    let sv=false;
    site.querySelectorAll('.grp').forEach(g=>{{
      let gv=false;
      g.querySelectorAll('.chip').forEach(c=>{{const m=!t||c.dataset.l.includes(t);c.style.display=m?'':'none';if(m)gv=true;}});
      g.classList.toggle('empty',!gv); if(gv)sv=true;
    }});
    site.style.display=sv?'':'none'; if(sv)any=true;
  }});
  nohit.style.display=any?'none':'block'; qe.textContent=q.value;
}});
</script>
</body></html>'''
open(os.path.join(ROOT,"hub.html"),"w",encoding="utf-8").write(HTML)
print("hub.html generado ·",total,"pantallas ·",len(SITES),"sitios")
for s in SITES: print("  -",s["name"],sum(len(g["items"]) for g in s["groups"]),"pantallas,",len(s["groups"]),"categorías")
