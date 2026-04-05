"""
Visualizations for the World Cup 2026 analyzer.

print_grid()     – ANSI-colored 3×3 scenario grid for the terminal.
generate_html()  – self-contained HTML page with scenario table + bracket
                   path diagrams for every scenario.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_ORDINALS = {1: '1st', 2: '2nd', 3: '3rd'}

# ANSI foreground colors by round
_ANSI_COLOR = {
    'Round of 32':  '\033[92m',   # bright green
    'Round of 16':  '\033[32m',   # green
    'Quarterfinal': '\033[93m',   # bright yellow
    'Semifinal':    '\033[33m',   # orange
    'Final':        '\033[91m',   # bright red
}
_ANSI_RESET = '\033[0m'
_ANSI_DIM   = '\033[2m'

# Short labels for round names
_SHORT = {
    'Round of 32':  'R32',
    'Round of 16':  'R16',
    'Quarterfinal': 'QF',
    'Semifinal':    'SF',
    'Final':        'Final',
}

# HTML CSS class by round
_CSS = {
    'Round of 32':  'r32',
    'Round of 16':  'r16',
    'Quarterfinal': 'qf',
    'Semifinal':    'sf',
    'Final':        'final',
}


# ---------------------------------------------------------------------------
# Terminal: colored 3×3 grid
# ---------------------------------------------------------------------------

def print_grid(result: dict) -> None:
    """Print a Unicode-box + ANSI-colored 3×3 scenario grid."""
    team_a    = result['team_a']
    team_b    = result['team_b']
    group_a   = result['group_a']
    group_b   = result['group_b']
    scenarios = result['scenarios']

    grid = {(s['pos_a'], s['pos_b']): s for s in scenarios}

    COL_W = 16   # visible width of each data cell
    HDR_W = 13   # visible width of the row-header cell

    def visible_text(s: dict) -> str:
        if not s['round']:
            return '—'
        return s['round'] + ('' if s['is_exact'] else ' *')

    def colored_cell(s: dict) -> str:
        text    = visible_text(s)
        padded  = text.center(COL_W)
        color   = _ANSI_COLOR.get(s['round'] or '', '')
        dim     = _ANSI_DIM if not s['is_exact'] else ''
        return f"{dim}{color}{padded}{_ANSI_RESET}"

    total_w = HDR_W + 2 + 1 + 3 * (COL_W + 2 + 1)

    # Header
    print(f"\n{'═' * total_w}")
    print(f"  {team_a} (Group {group_a})  vs  {team_b} (Group {group_b})")
    print(f"{'═' * total_w}")

    # Top border
    print(f"┌{'─'*(HDR_W+2)}┬{'─'*(COL_W+2)}┬{'─'*(COL_W+2)}┬{'─'*(COL_W+2)}┐")

    # Column-header row
    hdrs = [f"{team_b} {_ORDINALS[p]}".center(COL_W) for p in (1, 2, 3)]
    print(f"│{' '*(HDR_W+2)}│ {hdrs[0]} │ {hdrs[1]} │ {hdrs[2]} │")

    # Separator
    print(f"├{'─'*(HDR_W+2)}┼{'─'*(COL_W+2)}┼{'─'*(COL_W+2)}┼{'─'*(COL_W+2)}┤")

    # Data rows
    for pos_a in (1, 2, 3):
        row_hdr = f" {team_a} {_ORDINALS[pos_a]}".ljust(HDR_W + 2)
        cells   = [f" {colored_cell(grid[(pos_a, pos_b)])} " for pos_b in (1, 2, 3)]
        print(f"│{row_hdr}│{'│'.join(cells)}│")

    # Bottom border
    print(f"└{'─'*(HDR_W+2)}┴{'─'*(COL_W+2)}┴{'─'*(COL_W+2)}┴{'─'*(COL_W+2)}┘")

    # Legend
    legend = '  '.join(
        f"{_ANSI_COLOR.get(r,'')}{_SHORT[r]}{_ANSI_RESET}"
        for r in ('Round of 32', 'Round of 16', 'Quarterfinal', 'Semifinal', 'Final')
    )
    print(f"\n  {legend}")
    if any(not s['is_exact'] for s in scenarios):
        print(f"  * earliest possible — depends on 3rd-place bracket draw")
    print()


# ---------------------------------------------------------------------------
# HTML generator
# ---------------------------------------------------------------------------

def generate_html(result: dict, output_path: str) -> None:
    """
    Write a self-contained HTML file visualising all 9 meeting scenarios.

    Each scenario shows a bracket-path diagram: two horizontal pill-and-arrow
    chains (one per team) aligned by round, with the meeting match highlighted.
    """
    team_a  = result['team_a']
    team_b  = result['team_b']
    group_a = result['group_a']
    group_b = result['group_b']

    html = _build_html(result)
    Path(output_path).write_text(html, encoding='utf-8')


# -- HTML colour palette --
_HEX = {
    'Round of 32':  ('#0f4c0f', '#6bff6b'),
    'Round of 16':  ('#0a3d0a', '#4ecb4e'),
    'Quarterfinal': ('#3d3a00', '#f5e642'),
    'Semifinal':    ('#3d2000', '#ff9f38'),
    'Final':        ('#3d0000', '#ff5555'),
}
_MEET_BG   = '#2a1a4e'
_MEET_BORD = '#c084fc'


def _round_style(round_name: str) -> str:
    bg, fg = _HEX.get(round_name, ('#222', '#ccc'))
    return f"background:{bg};color:{fg}"


def _path_diagram_html(s: dict, team_a: str, team_b: str) -> str:
    """Render the bracket-path diagram for one scenario as HTML."""
    meeting = s['match']
    path_a  = s['path_a']   # [(match_num, round_name), ...]
    path_b  = s['path_b']

    def node(match_num: int, round_name: str, is_meeting: bool, team: str) -> str:
        short  = _SHORT.get(round_name, round_name)
        label  = f"M{match_num}<br><small>{short}</small>"
        if is_meeting:
            style = f"background:{_MEET_BG};border:2px solid {_MEET_BORD};color:#e8d5ff"
            star  = '<span class="star">★</span>'
            return f'<div class="node meeting" style="{style}">{star}{label}</div>'
        else:
            style = _round_style(round_name)
            cls   = f'node {_CSS.get(round_name, "")}'
            return f'<div class="{cls}" style="{style}">{label}</div>'

    def path_row(path: list, team_name: str, color: str) -> str:
        nodes_html = ''
        for i, (m, rnd) in enumerate(path):
            if i:
                nodes_html += '<div class="arrow">›</div>'
            nodes_html += node(m, rnd, m == meeting, team_name)
        return (
            f'<div class="path-row">'
            f'<span class="team-label" style="color:{color}">{team_name}</span>'
            f'<div class="path-nodes">{nodes_html}</div>'
            f'</div>'
        )

    # Team flag colors (approximate)
    color_a = '#cc0000'   # red  (team A — Norway side)
    color_b = '#ffcc00'   # gold (team B — Germany side)

    rows = (
        path_row(path_a, team_a, color_a)
        + path_row(path_b, team_b, color_b)
    )

    meet_text = ''
    if meeting:
        rnd = s['round']
        exact = '' if s['is_exact'] else ' (earliest possible)'
        meet_text = (
            f'<div class="meet-note">'
            f'★ They meet in Match {meeting} — {rnd}{exact}'
            f'</div>'
        )

    return f'<div class="path-diagram">{rows}{meet_text}</div>'


def _build_html(result: dict) -> str:
    team_a    = result['team_a']
    team_b    = result['team_b']
    group_a   = result['group_a']
    group_b   = result['group_b']
    scenarios = result['scenarios']

    grid = {(s['pos_a'], s['pos_b']): s for s in scenarios}

    # ── Scenario grid ──────────────────────────────────────────────────────
    col_headers = ''.join(
        f'<th>{team_b}<br>{_ORDINALS[p]}</th>' for p in (1, 2, 3)
    )
    grid_rows = ''
    for pos_a in (1, 2, 3):
        cells = ''
        for pos_b in (1, 2, 3):
            s     = grid[(pos_a, pos_b)]
            rnd   = s['round'] or '—'
            exact = '' if s['is_exact'] else ' <sup>*</sup>'
            css   = _CSS.get(rnd, '')
            bg, fg = _HEX.get(rnd, ('#1a1a2e', '#aaa'))
            style = f'background:{bg};color:{fg}'
            cells += f'<td class="{css}" style="{style}">{rnd}{exact}</td>'
        grid_rows += f'<tr><th>{team_a}<br>{_ORDINALS[pos_a]}</th>{cells}</tr>'

    # ── Bracket-path cards ────────────────────────────────────────────────
    cards = ''
    for s in scenarios:
        pos_a, pos_b = s['pos_a'], s['pos_b']
        rnd  = s['round'] or '—'
        mark = '' if s['is_exact'] else ' *'
        bg, fg = _HEX.get(s['round'] or '', ('#1a1a2e', '#888'))
        header_style = f'background:{bg};color:{fg}'
        title = (
            f'{team_a} {_ORDINALS[pos_a]} + {team_b} {_ORDINALS[pos_b]}'
            f'<span class="pill" style="{header_style}">{rnd}{mark}</span>'
        )
        diagram = _path_diagram_html(s, team_a, team_b)
        cards += f'<div class="card"><h3>{title}</h3>{diagram}</div>'

    has_inexact = any(not s['is_exact'] for s in scenarios)
    footnote = (
        '<p class="footnote">* Earliest possible meeting — '
        'the actual round depends on which 8 of 12 third-place teams qualify '
        'and how they are seeded into the bracket.</p>'
        if has_inexact else ''
    )

    css = '''
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: #0a0e1a;
      color: #dde;
      padding: 2rem;
      line-height: 1.5;
    }
    h1 { font-size: 1.8rem; color: #fff; margin-bottom: .25rem; }
    h2 { font-size: 1rem; color: #889; margin-bottom: 2rem; font-weight: 400; }
    h3 { font-size: 1rem; color: #ccc; margin-bottom: 1rem;
         display: flex; align-items: center; gap: .75rem; }
    section { margin-bottom: 3rem; }
    section > h2 { font-size: 1.1rem; color: #aac; font-weight: 600;
                   margin-bottom: 1rem; border-bottom: 1px solid #223;
                   padding-bottom: .5rem; }

    /* Scenario grid */
    table { border-collapse: collapse; }
    th, td {
      padding: .6rem 1.1rem;
      border: 1px solid #223;
      text-align: center;
      font-size: .9rem;
    }
    th { background: #131828; color: #aac; font-weight: 500; }
    td { transition: filter .2s; }
    td:hover { filter: brightness(1.3); }

    /* Bracket-path cards */
    .card {
      background: #111827;
      border: 1px solid #223;
      border-radius: 10px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.25rem;
    }
    .pill {
      display: inline-block;
      padding: .15rem .6rem;
      border-radius: 999px;
      font-size: .8rem;
      font-weight: 600;
    }
    .path-diagram { display: flex; flex-direction: column; gap: .6rem; }
    .path-row {
      display: flex;
      align-items: center;
      gap: .4rem;
    }
    .team-label {
      width: 7rem;
      flex-shrink: 0;
      font-size: .82rem;
      font-weight: 600;
      text-align: right;
      padding-right: .75rem;
    }
    .path-nodes { display: flex; align-items: center; gap: .3rem; flex-wrap: wrap; }
    .node {
      width: 68px;
      min-height: 48px;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: .78rem;
      font-weight: 600;
      text-align: center;
      flex-shrink: 0;
      border: 1px solid transparent;
      line-height: 1.3;
    }
    .node small { font-weight: 400; font-size: .7rem; opacity: .8; }
    .node.meeting { box-shadow: 0 0 12px rgba(192,132,252,.4); }
    .star { font-size: .9rem; display: block; }
    .arrow {
      font-size: 1.2rem;
      color: #445;
      flex-shrink: 0;
      user-select: none;
    }
    .meet-note {
      margin-top: .5rem;
      padding: .4rem .8rem;
      background: #1a0f2e;
      border-left: 3px solid #c084fc;
      border-radius: 4px;
      font-size: .82rem;
      color: #c084fc;
    }
    .footnote {
      font-size: .82rem;
      color: #667;
      margin-top: 1rem;
      font-style: italic;
    }
    '''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{team_a} vs {team_b} — World Cup 2026</title>
<style>{css}</style>
</head>
<body>
<h1>{team_a} vs {team_b}</h1>
<h2>2026 FIFA World Cup — When do they meet?</h2>

<section>
  <h2>Scenario matrix</h2>
  <table>
    <thead><tr><th></th>{col_headers}</tr></thead>
    <tbody>{grid_rows}</tbody>
  </table>
  {footnote}
</section>

<section>
  <h2>Bracket paths by scenario</h2>
  {cards}
</section>
</body>
</html>'''
