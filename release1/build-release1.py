"""build-release1.py → release 1, A e B, a partir da v51 com as alterações de texto de v51/estagiario-novo-C-update.html.

A · com a navegação flutuante (menu lateral).
B · sem menu flutuante; "Voltar ao topo" no fim de cada subseção.

1. Texto do C-update: as diferenças entre v51 B e o C-update são extraídas aqui mesmo e aplicadas às seis bases da v51
   (A, B, prévias e render). Cada trecho precisa existir uma única vez em cada base.
2. Ajustes combinados na revisão do C-update:
   - certidões pelo Mensageiro: "as certidões devem ser apresentadas" (o parágrafo fala de "essas certidões");
   - casamento: "se o estado civil mudar durante o processo admissional, toda a documentação deve ser atualizada";
   - "Departamento de Gestão de Recursos Humanos" → "Secretaria de Gestão de Pessoas" em todos os lugares;
   - menu lateral (A): "Remanejamento e permuta", como o novo título do 3.2.
3. Endereços definitivos (ENDERECOS abaixo): documentos do 3.2 e imagens. Enquanto um endereço estiver vazio, fica o marcador
   provisório e o aviso no HTML.
4. Nova arte do Balcão: texto alternativo novo e recorte do celular na ilustração.
5. Limpeza: saem os comentários de desenvolvimento do HTML (cartões desativados, notas de versão) e os comentários do CSS;
   ficam só os avisos úteis para publicar e manter (valores da bolsa; imagens ainda sem endereço).
6. Editor do portal (sem JavaScript): os passos da 1.1 deixam de ter altura fixa enquanto o script não roda, para não vazarem
   por cima das seções seguintes.
7. Problemas vistos no ar: valores da bolsa em lista (o editor desmonta <div> dentro de <dl>); lista de documentos,
   busca do topo e perfis escondidos sem script; "Quem resolve?" vira links para o canal sem script.
8. Cartões "Quem pode concorrer" e "Carga horária" sem a frase do curso a distância e a dos períodos de avaliação.
9. Sem o link "Pular para o conteúdo" próprio: o portal já tem o dele.
"""
import re, pathlib, difflib
D = pathlib.Path(__file__).parent
V51 = D.parent / 'v51'

# ---------------------------------------------------------------- endereços definitivos
# Imagens: documentos do portal (JPG, mesmas artes da pasta assets), sem o ?version=…&t=… (só força novo download; sem ele o portal
# entrega a versão mais recente). O código no fim do caminho é o identificador do arquivo e não muda se o título for editado.
ENDERECOS = {
    '#LINK-PROVISORIO-oficio-remanejamento': 'https://www.tjpr.jus.br/documents/d/departamento-administrativo/estagio-oficio-de-remanejamento',
    '#LINK-PROVISORIO-oficio-permuta': 'https://www.tjpr.jus.br/documents/d/departamento-administrativo/estagio-oficio-de-permuta',
    '#LINK-PROVISORIO-nepotismo': 'https://www.tjpr.jus.br/documents/d/departamento-administrativo/estagio-declaracao-de-nepotismo-permuta-e-remanejamento',
    '../assets/1-seletivo_3072x512.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/1-seletivo_3072x512.jpg/fa6b753c-d703-c17a-70f7-1455fbd04c78',
    '../assets/2-admissao_3072x512.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/2-admissao_3072x512.jpg/65635a85-2caa-394f-1e9b-78289aa25e6c',
    '../assets/3-estagio_3072x512.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/3-estagio_3072x512.jpg/eda8a704-195b-7de2-bbe7-b83b4287174f',
    '../assets/4-residencia_3072x512.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/4-residencia_3072x512.jpg/b1822ad6-9811-97c9-a6ac-9a8370763281',
    '../assets/5-balcao_3072x512.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/5-balcao_3072x512.jpg/47905bd2-1cae-4204-cc96-d2463e1cf8aa',
    '../assets/6-cartilha_1086x1448.webp': 'https://www.tjpr.jus.br/documents/14681/4190397/6-cartilha_1086x1448.jpg/5a5eeb34-64c2-a2d2-0863-0c5144b23da8',
}


def troca(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90])
    return s.replace(a, b)


# ---------------------------------------------------------------- 1. alterações do C-update
def alteracoes():
    """Pares (antes, depois) com contexto suficiente para serem únicos, a partir de v51 B × C-update."""
    a = (V51 / 'estagiario-novo-v51-B.html').read_text(encoding='utf-8').splitlines()
    b = (V51 / 'estagiario-novo-C-update.html').read_text(encoding='utf-8').splitlines()
    pares = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        assert op == 'replace' and i2 - i1 == j2 - j1, (op, i1, i2, j1, j2)
        for x, y in zip(a[i1:i2], b[j1:j2]):
            for o, p1, p2, q1, q2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
                if o == 'equal':
                    continue
                pares.append((x, p1, p2, y[q1:q2]))
    # junta trechos próximos da mesma linha e acrescenta contexto até o trecho ficar único nas bases
    blocos = []
    for x, p1, p2, novo in pares:
        if blocos and blocos[-1][0] is x and p1 - blocos[-1][2] < 80:
            bx, bp1, bp2, partes = blocos[-1]
            blocos[-1] = (bx, bp1, p2, partes + [(p1, p2, novo)])
        else:
            blocos.append((x, p1, p2, [(p1, p2, novo)]))
    bases = [(V51 / f'{p}estagiario-novo-v51-{v}.html').read_text(encoding='utf-8') for p in ('', 'previa-', 'render-') for v in 'AB']
    saida = []
    for x, p1, p2, partes in blocos:
        for m in range(30, 400, 10):
            ini, fim = max(0, p1 - m), min(len(x), p2 + m)
            antes = x[ini:fim]
            if all(base.count(antes) == 1 for base in bases):
                break
        else:
            raise AssertionError(x[p1 - 60:p2 + 60])
        depois, pos = '', ini
        for q1, q2, novo in partes:
            depois += x[pos:q1] + novo; pos = q2
        depois += x[pos:fim]
        saida.append((antes, depois))
    return saida


# ---------------------------------------------------------------- 2. ajustes da revisão
def revisao(s):
    s = troca(s, 'o documento deve ser apresentado na tarefa do Hércules durante a etapa da admissão.',
                 'as certidões devem ser apresentadas na tarefa do Hércules durante a etapa da admissão.')
    s = troca(s, 'Por isso, se houver mudança no percurso do processo admissional, toda a documentação deve ser atualizada de acordo.',
                 'Por isso, se o estado civil mudar durante o processo admissional, toda a documentação deve ser atualizada.')
    s = troca(s, 'ao Departamento de Gestão de Recursos Humanos', 'à Secretaria de Gestão de Pessoas', 3)
    s = troca(s, 'do Departamento de Gestão de Recursos Humanos', 'da Secretaria de Gestão de Pessoas', 2)
    assert 'Departamento de Gestão de Recursos Humanos' not in s
    if 'class="snav' in s:
        s = troca(s, '<span class="lb">Remanejamento ou permuta</span>', '<span class="lb">Remanejamento e permuta</span>')
    return s


# ---------------------------------------------------------------- 3. endereços
def enderecos(s):
    for prov, url in ENDERECOS.items():
        if not url:
            continue
        n = s.count(f'"{prov}"')
        assert n >= 1, prov
        s = s.replace(f'"{prov}"', f'"{url}"')
        if prov.startswith('../assets/'):        # o aviso "troque o src" deixa de ser necessário
            nome = prov.split('/')[-1]
            s, k = re.subn(r'<!-- (?:IMAGEM DE CAPA|CAPA DA CARTILHA) · ao publicar, troque o src pelo endereço online da imagem ' + re.escape(nome) + r' -->\n?', '', s)
            assert k == 1, (nome, k)
    return s


# formato e tamanho dos documentos do 3.2 (eMAG 3.8), conferidos no servidor em 01/10/2026, como nos demais documentos da página
FORMATOS = {'Ofício de Remanejamento': '(PDF, 102 KB)', 'Ofício de Permuta': '(PDF, 43 KB)', 'Declaração de Nepotismo': '(PDF, 389 KB)'}
def formatos(s):
    for nome, fmt in FORMATOS.items():
        s = troca(s, f'{nome}<span aria-hidden="true"> ↗</span><span class="sr"> (abre em nova aba)</span></a>',
                     f'{nome} <span class="fmt">{fmt}</span><span aria-hidden="true"> ↗</span><span class="sr"> (abre em nova aba)</span></a>')
    return s


# ---------------------------------------------------------------- 3b. nova arte do Balcão (assets/5-balcao, 01/10/2026)
# A arte não tem mais o título "Balcão Virtual": o texto alternativo descreve só a cena. A ilustração fica no centro-direita,
# então no celular (capa recortada em 3:1) o recorte acompanha a ilustração, em vez de mostrar o fundo da esquerda.
ALT_BALCAO_V49 = ('Balcão Virtual: atendimento via Microsoft Teams. Ilustração: uma pessoa conversa por videochamada, no notebook, '
                  'com uma atendente de fone de ouvido.')
ALT_BALCAO = 'Ilustração: uma pessoa acena para quatro colegas numa videochamada, no notebook.'
def balcao(s):
    s = troca(s, f'<img class="banner" src="{ENDERECOS["../assets/5-balcao_3072x512.webp"]}" alt="{ALT_BALCAO_V49}"',
                 f'<img class="banner banner-dir" src="{ENDERECOS["../assets/5-balcao_3072x512.webp"]}" alt="{ALT_BALCAO}"')
    k = s.index('</style>', s.index('id="tjpr-estagio-conteudo"'))
    css = '\n@container est (max-width: 760px){ #tjpr-estagio-conteudo.v44 .cover>img.banner.banner-dir{object-position:70% center} }\n'
    return s[:k] + css + s[k:]


# ---------------------------------------------------------------- 3c. editor do portal, sem JavaScript
# Sem o script (editor WYSIWYG do portal, ou script removido), os 10 passos da 1.1 aparecem todos de uma vez; cada um tinha
# height:100% da coluna, e a pilha vazava ~28 mil px por cima das seções seguintes. A classe bx-js só existe com o script rodando.
def semjs(s):
    k = s.index('</style>', s.index('id="tjpr-estagio-conteudo"'))
    css = '#tjpr-estagio-conteudo:not(.bx-js) .etC-p{height:auto;overflow:visible}\n'
    return s[:k] + css + s[k:]


# ---------------------------------------------------------------- 3d. problemas vistos no ar (01/10/2026)
# a) Valores da bolsa: o editor do portal (CKEditor) só aceita <dt>/<dd> diretamente dentro de <dl>; ao achar <div> ali,
#    fecha a <dl> e solta os pares para fora dela, e o quadro perde a grade. Vira lista (<ul>/<li>) com dois <span>.
# b) Lista de documentos, "Quem resolve?", busca do topo e perfis dependem de script. Sem script, ficam escondidos (lista,
#    busca, perfis) ou viram links para o canal (Quem resolve); a classe vt-js só entra quando o script da vitrine termina.
# c) Faixa de acentos das buscas escrita em \u, sem caracteres combinantes soltos no código.
def bolsa_li(m):
    t = m.group(0)
    for a, b in (('<dl class="bolsa-g">', '<ul class="bolsa-g">'), ('</dl>', '</ul>'), ('<div class="at">', '<li class="at">'),
                 ('<div>', '<li>'), ('</div>', '</li>'), ('<dt>', '<span class="bo-k">'), ('</dt>', '</span>'),
                 ('<dd>', '<span class="bo-v">'), ('</dd>', '</span>')):
        t = t.replace(a, b)
    return t
def aovivo(s):
    s, n = re.subn(r'<dl class="bolsa-g">.*?</dl>', bolsa_li, s, flags=re.S)
    assert n == 2, n
    i = s.index('<style'); j = s.index('</style>', i)
    css = s[i:j]
    for a, b in (('.bolsa-g>div', '.bolsa-g>li'), ('.bolsa-g dt', '.bolsa-g .bo-k'), ('.bolsa-g dd', '.bolsa-g .bo-v'),
                 ('.bolsa-g .at dd', '.bolsa-g .at .bo-v'), ('.qr-c button', '.qr-c [data-src]')):
        css = css.replace(a, b)
    assert 'bolsa-g dt' not in css and 'bolsa-g dd' not in css and '.qr-c button' not in css
    css += ('#tjpr-estagio-conteudo .bolsa-g{padding:0;list-style:none}\n'
            '#tjpr-estagio-conteudo .bolsa-g :is(.bo-k,.bo-v){display:block}\n'
            '#tjpr-estagio-conteudo .qr-c [data-src]{text-decoration:none}\n'
            '#tjpr-estagio-conteudo:not(.vt-js) :is(.dk,.hsearch,.qr-out){display:none}\n'
            '#tjpr-estagio-conteudo:not(.vt-js) .qr{grid-template-columns:1fr}\n'
            '#tjpr-estagio-conteudo:not(.bx-js) #tjpr-estagio-perfis{display:none}\n')
    s = s[:i] + css + s[j:]
    s, n = re.subn(r'<button type="button" aria-pressed="false" (data-src="[^"]*" data-go="([^"]*)"[^>]*)>(.*?)</button>',
                   r'<a href="#\2" \1>\3</a>', s)
    assert n == 10, n
    s = troca(s, "$$('.qr-c button',qr).forEach(function(b){b.addEventListener('click',function(){",
                 "$$('.qr-c [data-src]',qr).forEach(function(b){b.setAttribute('role','button');b.setAttribute('aria-pressed','false');"
                 "b.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault();b.click();}});"
                 "b.addEventListener('click',function(e){e.preventDefault();")
    s = troca(s, "$$('.qr-c button',qr).forEach(function(x)", "$$('.qr-c [data-src]',qr).forEach(function(x)")
    s = troca(s, "$$('.qr-c button').forEach(function(b)", "$$('.qr-c [data-src]').forEach(function(b)")
    s = troca(s, "a.hasAttribute('data-tab'))return;", "a.hasAttribute('data-tab')||a.hasAttribute('data-src'))return;")
    s = troca(s, "R.addEventListener('click',function(){setTimeout(sincroniza,0)});sincroniza();",
                 "R.addEventListener('click',function(){setTimeout(sincroniza,0)});sincroniza();\nR.classList.add('vt-js');")
    s = troca(s, '/[̀-ͯ]/g', r'/[̀-ͯ]/g', 2)
    # d) O portal apaga o trecho "innerHTML=" dos scripts publicados (visto em 01/10/2026: "pal.innerHTML='…'" virou "pal.'…'",
    #    erro de sintaxe que derrubava o script da vitrine inteiro). As atribuições passam por htm(), com insertAdjacentHTML.
    def sem_inner(m):
        js = m.group(2)
        if '.innerHTML=' not in js:
            return m.group(0)
        js, k = re.subn(r'\b([a-z]+)\.innerHTML=([^;]*);', r'htm(\1,\2);', js)
        js = js.replace('(function(){', "(function(){\nfunction htm(e,h){e.textContent='';e.insertAdjacentHTML('beforeend',h);}", 1)
        return m.group(1) + js + m.group(3)
    s = re.sub(r'(<script>)(.*?)(</script>)', sem_inner, s, flags=re.S)
    assert 'innerHTML' not in s
    return s


# ---------------------------------------------------------------- 3e. cartões de "O que é o estágio" mais curtos (01/10/2026)
# Os detalhes continuam nas respostas ligadas a cada cartão (FAQ 02 e "Jornada, horário e teletrabalho").
def curtos(s):
    s = troca(s, ' Curso a distância vale se a instituição for credenciada na <abbr title="Secretaria de Estado da Educação">SEED</abbr> ou no <abbr title="Ministério da Educação">MEC</abbr>.</p>', '</p>')
    s = troca(s, ' Nos períodos de avaliação, a jornada cai pelo menos à metade.</p>', '</p>')
    return s


# ---------------------------------------------------------------- 3f. sem o "Pular para o conteúdo" próprio (01/10/2026)
# O portal já tem o seu ("Pular para o Conteúdo principal", accesskey 1); o nosso aparecia por cima do cabeçalho do portal.
def sem_skip(s):
    s = troca(s, '<a class="skip" href="#tjpr-estagio-inscricoes">Pular para o conteúdo</a>\n', '')
    s = re.sub(r'#tjpr-estagio-conteudo \.skip(:focus)?\{[^}]*\}\n', '', s)
    s = troca(s, ':is(.cmd-trigger,.cl,.qr,.dk,.skip)', ':is(.cmd-trigger,.cl,.qr,.dk)')
    assert 'skip' not in s
    return s


# ---------------------------------------------------------------- 4. limpeza
FICAM = ('BOLSA-AUXÍLIO', 'Mesmos valores do quadro', 'IMAGEM DE CAPA', 'CAPA DA CARTILHA')
def limpeza(s):
    i = s.index('id="tjpr-estagio-conteudo"')
    def html(m):
        return m.group(0) if m.group(1).strip().startswith(FICAM) else ''
    corpo = re.sub(r'<!--(.*?)-->\n?', html, s[i:], flags=re.S)
    s = s[:i] + corpo
    s = re.sub(r'(<style[^>]*>)(.*?)(</style>)', lambda m: m.group(1) + re.sub(r'\n{3,}', '\n\n', re.sub(r'/\*.*?\*/\n?', '', m.group(2), flags=re.S)) + m.group(3), s, flags=re.S)
    return s


# ---------------------------------------------------------------- montagem
ALT = alteracoes()
print(len(ALT), 'alterações do C-update')
for pref in ('', 'previa-', 'render-'):
    for v in 'AB':
        s = (V51 / f'{pref}estagiario-novo-v51-{v}.html').read_text(encoding='utf-8')
        for antes, depois in ALT:
            s = troca(s, antes, depois)
        s = limpeza(sem_skip(curtos(aovivo(semjs(balcao(formatos(enderecos(revisao(s)))))))))
        s = troca(s, f' v51 v51-{v.lower()}"', f' v51 v51-{v.lower()} r1 r1-{v.lower()}"')
        s = s.replace(f'estagiario-novo-v51-{v}', f'estagiario-release1-{v}')
        (D / f'{pref}estagiario-release1-{v}.html').write_text(s, encoding='utf-8', newline='\n')
faltam = [k for k, u in ENDERECOS.items() if not u]
print('ok' + (f' · ainda sem endereço: {len(faltam)}' if faltam else ''))
