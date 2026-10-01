"""teste-release1.py ARQ → testes de acessibilidade que o axe não faz:
1. "Aumentar a fonte" do portal (font-size 120 % no contêiner da página): o texto acompanha?
2. Reflow (WCAG 1.4.10): em 320 px de largura, algo passa da tela?
3. Espaçamento de texto (WCAG 1.4.12): com as medidas do critério, algum texto some cortado?"""
import sys, subprocess, pathlib, re, html, json, platform
CH = ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' if platform.system() == 'Darwin'
      else r'C:\Program Files\Google\Chrome\Application\chrome.exe')
D = pathlib.Path(__file__).parent

def roda(arq, js, w=1280, iframe=None):
    fonte = (D / arq).read_text(encoding='utf-8')
    f = D / '_t-f.html'
    if iframe:   # a página vai num iframe da largura pedida; o resultado volta por postMessage
        f.write_text(fonte + '<script>addEventListener("load",function(){setTimeout(function(){' + js +
                     'parent.postMessage(JSON.stringify(r),"*")},700)})</script>', encoding='utf-8')
        p = D / '_t-p.html'
        p.write_text(f'<body style="margin:0"><iframe src="{f.name}" style="width:{iframe}px;height:900px;border:0"></iframe>'
                     '<script>addEventListener("message",function(e){document.body.setAttribute("data-r",e.data)})</script></body>', encoding='utf-8')
        url = p.as_uri()
    else:
        f.write_text(fonte + '<script>addEventListener("load",function(){setTimeout(function(){' + js +
                     'setTimeout(function(){document.body.setAttribute("data-r",JSON.stringify(r))},400)},700)})</script>', encoding='utf-8')
        url = f.as_uri()
    out = subprocess.run([CH, '--headless=new', '--disable-gpu', f'--window-size={w},1000', '--virtual-time-budget=8000', '--dump-dom', url],
                         capture_output=True, text=True, encoding='utf-8').stdout
    for x in (D / '_t-f.html', D / '_t-p.html'):
        if x.exists(): x.unlink()
    m = re.search(r'data-r="([^"]*)"', out)
    return json.loads(html.unescape(m.group(1))) if m else None

ARQ = sys.argv[1]
AMOSTRA = ('var R=document.getElementById("tjpr-estagio-conteudo");'
           'var q=function(s){var e=R.querySelector(s);return e?parseFloat(getComputedStyle(e).fontSize):0};'
           'var S=["#tjpr-estagio-programa .about1 p",".hero2 h2",".sbh h4",".ddq>summary b",".bolsa-g .bo-v",".faq summary span"];')
r = roda(ARQ, AMOSTRA + 'var a=S.map(q);R.parentElement.style.fontSize="120%";'
         'setTimeout(function(){window.r={antes:a,depois:S.map(q),z:R.style.getPropertyValue("--z")};r=window.r},300);var r=null;'
         .replace('var r=null;', '') )
print('1. fonte 120 %:', r)

r = roda(ARQ, 'document.querySelectorAll("#tjpr-estagio-conteudo details").forEach(function(d){d.open=true});'
              'var W=document.documentElement.clientWidth,fora=[];'
              'document.querySelectorAll("#tjpr-estagio-conteudo *").forEach(function(e){var b=e.getBoundingClientRect();'
              'if(b.width&&b.right>W+1&&!e.closest("[aria-hidden=true],.sc,svg")){var ov=getComputedStyle(e.parentElement).overflowX;'
              'fora.push((e.className&&e.className.baseVal===undefined?e.className:e.tagName)+" "+Math.round(b.right-W)+"px"+(ov!=="visible"?" (rola: "+ov+")":""))}});'
              'var r={largura:W,rolagem_horizontal:document.documentElement.scrollWidth>W,fora:fora.slice(0,15),total:fora.length};', iframe=320)
print('2. 320 px:', r)

r = roda(ARQ, 'var st=document.createElement("style");st.textContent="#tjpr-estagio-conteudo *{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}#tjpr-estagio-conteudo p{margin-bottom:2em!important}";'
              'document.head.appendChild(st);document.querySelectorAll("#tjpr-estagio-conteudo details").forEach(function(d){d.open=true});'
              'var cort=[];document.querySelectorAll("#tjpr-estagio-conteudo *").forEach(function(e){var s=getComputedStyle(e);'
              'if(!e.getClientRects().length||e.closest("[aria-hidden=true],.sr,.snav")||(e.offsetWidth<=1&&e.offsetHeight<=1))return;'
              'if((s.overflow==="hidden"||s.overflowY==="hidden")&&e.scrollHeight>e.clientHeight+2&&e.textContent.trim())cort.push((e.className||e.tagName)+": "+e.textContent.trim().slice(0,40))});'
              'var r={cortados:cort.slice(0,15),total:cort.length};')
print('3. espaçamento de texto:', r)
