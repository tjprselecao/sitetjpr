"""build-release2.py → release 2, A e B (e prévias/render), a partir da release 1.

A · com a navegação flutuante (menu lateral).
B · sem menu flutuante; "Voltar ao topo" no fim de cada subseção.

1. 2.2 Termos e declarações · Para candidatos: os três termos davam alerta no download (endereços antigos em http://).
   Passam para os novos documentos do portal (https), cada um em DOCX e em PDF. Os dois formatos têm campos preenchíveis.
   O título continua levando ao DOCX; na mesma linha, "ou em PDF". O nome do termo entra no link do PDF só para leitor de
   tela (<span class="sr">), para o link fazer sentido fora do contexto (WCAG 2.4.4); o texto visível está contido no nome
   acessível (WCAG 2.5.3). "em&nbsp;PDF" para o link não quebrar entre linhas no celular.
   Nenhum elemento vazio: o editor do portal apaga inline vazios ao salvar (visto no Backup 261014).
2. Bolinha dourada dos tutoriais (Abertura e Movimentação): o editor do portal apagou os 10 <em class="sc-pin"></em> vazios
   (Backup 261014), mas conserva <i> vazio (240 deles sobreviveram no mesmo backup, inclusive <i class="sc-car"> nos mesmos
   itens). O pino passa a ser <i>; sem script. Estilo calculado dos 10 pinos conferido no Chrome: idêntico ao do <em>.
3. Decreto Judiciário nº 2.324/2013 e Cartilha de Seleção por Competências: http:// → https:// (os dois respondem 200 direto).
"""
import pathlib
D = pathlib.Path(__file__).parent
R1 = D.parent / 'release1'
P = 'https://www.tjpr.jus.br/documents/d/departamento-administrativo/'
NOVA = ' rel="noopener" target="_blank"'
FIM = '<span aria-hidden="true"> ↗</span><span class="sr"> (abre em nova aba)</span></a>'

# tamanhos conferidos no servidor em 14/10/2026 (content-length ÷ 1024, arredondado, como nos demais documentos da página)
TERMOS = [
    ('http://www.tjpr.jus.br/documents/32415/8529204/TERMO+DE+DESIST%C3%8ANCIA+FORMAL+PELO+CLASSIFICADO/8b06e4b8-0a3a-a4fb-1a48-9764a8558cec',
     'Termo de desistência formal', '(DOCX, 14 KB)',
     'termo-de-desistencia-formal-pelo-classificado', '14 KB', '13 KB'),
    ('http://www.tjpr.jus.br/documents/32415/0/TERMO+DE+OP%C3%87%C3%83O+-+FINAL+DE+LISTA.docx/9d2d0be4-26c1-4489-8bd5-974ca7c92b0f',
     'Termo de opção por constar em final de lista', '(DOCX, 17 KB)',
     'termo-de-opcao-final-de-lista', '15 KB', '46 KB'),
    ('http://www.tjpr.jus.br/documents/32415/0/TERMO+DE+OP%C3%87%C3%83O+-+RECUSA+ADMISS%C3%83O+COMARCA+DIVERSA.docx/82a38de2-908c-66ac-c465-7c3b4b804966',
     'Termo de opção por recusar a admissão em comarca diversa', '(DOCX, 17 KB)',
     'termo-de-opcao-recusa-admissao-comarca-diversa', '15 KB', '14 KB'),
]


def troca(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90])
    return s.replace(a, b)


def termos(s):
    for antigo, nome, fmt_antigo, slug, docx, pdf in TERMOS:
        s = troca(s, f'<a href="{antigo}"{NOVA}>{nome} <span class="fmt">{fmt_antigo}</span>{FIM}',
                     f'<a href="{P}{slug}"{NOVA}>{nome} <span class="fmt">(DOCX, {docx})</span>{FIM}'
                     f' ou <a href="{P}{slug}-1-"{NOVA}><span class="sr">{nome} </span>em&nbsp;PDF <span class="fmt">({pdf})</span>{FIM}')
    for antigo, *_ in TERMOS:
        assert antigo.rsplit('/', 1)[1] not in s
    return s


def pinos(s):
    return troca(s, '<em class="sc-pin"></em>', '<i class="sc-pin"></i>', 10)


HTTPS = ('www.tjpr.jus.br/documents/32415/b3a11bb7-01a3-48db-8042-052b73dce4ab',
         'www.tjpr.jus.br/documents/portlet_file_entry/14681/Cartilha_Selecao_de_Estagiarios_e_Estagiarias_por+Competencias.pdf.pdf/')
def https(s):
    for u in HTTPS:
        s = troca(s, f'"http://{u}', f'"https://{u}')
    assert 'http://www.tjpr.jus.br' not in s
    return s


for pref in ('', 'previa-', 'render-'):
    for v in 'AB':
        s = (R1 / f'{pref}estagiario-release1-{v}.html').read_text(encoding='utf-8')
        s = https(pinos(termos(s)))
        s = troca(s, f' r1 r1-{v.lower()}"', f' r1 r1-{v.lower()} r2 r2-{v.lower()}"')
        s = s.replace(f'estagiario-release1-{v}', f'estagiario-release2-{v}')
        with open(D / f'{pref}estagiario-release2-{v}.html', 'w', encoding='utf-8', newline='\n') as f:
            f.write(s)
print('ok')
