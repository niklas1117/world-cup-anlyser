"""
Tournament simulation logic for the 2026 FIFA World Cup.

Group stage:
  - Each group plays a full round-robin (6 matches).
  - Match outcomes are weighted by team strength ratings.
  - Standings determined by points → goal difference → goals for → name.

Knockout stage:
  - No draws; a winner is picked per match using weighted probability.
  - 3rd-place team assignment uses bipartite matching so every R32
    slot that needs a 3rd-place team gets exactly one from an
    acceptable group.
"""

import random
from itertools import combinations

from .data import GROUPS, R32_SLOTS, KNOCKOUT_BRACKET, TEAM_STRENGTH

# ---------------------------------------------------------------------------
# Group-stage helpers
# ---------------------------------------------------------------------------

# Matches needing a 3rd-place team and which groups are acceptable
_THIRD_PLACE_MATCHES = {
    74: set('ABCDF'),
    77: set('CDFGH'),
    79: set('CEFHI'),
    80: set('EHIJK'),
    81: set('BEFIJ'),
    82: set('AEHIJ'),
    85: set('EFGIJ'),
    87: set('DEIJL'),
}


def _win_probability(team_a: str, team_b: str) -> float:
    """Return P(team_a beats team_b) using an ELO-style logistic formula."""
    ra = TEAM_STRENGTH.get(team_a, 1500)
    rb = TEAM_STRENGTH.get(team_b, 1500)
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def _simulate_group_match(team_a: str, team_b: str):
    """
    Simulate one group-stage match.
    Returns (winner, goals_a, goals_b).
    winner is None on a draw.
    """
    p_a = _win_probability(team_a, team_b)
    # Draw probability: higher when teams are evenly matched
    balance = 1.0 - abs(p_a - 0.5) * 2          # 1 when equal, 0 when lopsided
    p_draw = 0.15 + 0.20 * balance               # 0.15 – 0.35

    r = random.random()
    if r < p_draw:
        g = random.randint(0, 3)
        return None, g, g
    elif r < p_draw + (1 - p_draw) * p_a:
        ga = random.randint(1, 4)
        gb = random.randint(0, ga - 1)
        return team_a, ga, gb
    else:
        gb = random.randint(1, 4)
        ga = random.randint(0, gb - 1)
        return team_b, ga, gb


def simulate_group_stage() -> dict:
    """
    Simulate all 12 groups.

    Returns:
        dict: {group_letter: [(team, stats_dict), ...]}  sorted 1st → 4th.
        stats_dict keys: pts, gd, gf
    """
    results = {}
    for group, teams in GROUPS.items():
        standings = {t: {'pts': 0, 'gd': 0, 'gf': 0} for t in teams}
        for team_a, team_b in combinations(teams, 2):
            winner, ga, gb = _simulate_group_match(team_a, team_b)
            standings[team_a]['gd'] += ga - gb
            standings[team_b]['gd'] += gb - ga
            standings[team_a]['gf'] += ga
            standings[team_b]['gf'] += gb
            if winner is None:
                standings[team_a]['pts'] += 1
                standings[team_b]['pts'] += 1
            elif winner == team_a:
                standings[team_a]['pts'] += 3
            else:
                standings[team_b]['pts'] += 3

        sorted_teams = sorted(
            standings.items(),
            key=lambda x: (-x[1]['pts'], -x[1]['gd'], -x[1]['gf'], x[0])
        )
        results[group] = sorted_teams
    return results


# ---------------------------------------------------------------------------
# 3rd-place team assignment
# ---------------------------------------------------------------------------

def _assign_third_place(qualifying: dict) -> dict:
    """
    Assign qualifying 3rd-place teams to R32 slots via backtracking.

    Args:
        qualifying: {group_letter: team_name} for the 8 best 3rd-place teams.

    Returns:
        {match_num: team_name}
    """
    match_list = list(_THIRD_PLACE_MATCHES.keys())

    def backtrack(idx: int, remaining: dict) -> dict | None:
        if idx == len(match_list):
            return {}
        match_num = match_list[idx]
        acceptable = _THIRD_PLACE_MATCHES[match_num]
        for grp in list(remaining):
            if grp in acceptable:
                rest = {k: v for k, v in remaining.items() if k != grp}
                sub = backtrack(idx + 1, rest)
                if sub is not None:
                    return {match_num: remaining[grp], **sub}
        return None

    return backtrack(0, qualifying) or {}


# ---------------------------------------------------------------------------
# Knockout-stage simulation
# ---------------------------------------------------------------------------

def _simulate_knockout_match(team_a: str, team_b: str) -> str:
    """Pick a winner; no draws in the knockout rounds."""
    return team_a if random.random() < _win_probability(team_a, team_b) else team_b


# ---------------------------------------------------------------------------
# Full tournament
# ---------------------------------------------------------------------------

def simulate_tournament() -> dict:
    """
    Simulate the complete 2026 World Cup.

    Returns:
        dict: {match_num: {'team1': str, 'team2': str, 'winner': str}}
        Covers all knockout matches from R32 (73-88) through the Final (104).
    """
    # --- Group stage ---
    group_results = simulate_group_stage()

    # Build position → team lookup  (e.g. '1A', '2B')
    pos_to_team: dict[str, str] = {}
    for group, standings in group_results.items():
        for rank, (team, _) in enumerate(standings, start=1):
            pos_to_team[f'{rank}{group}'] = team

    # Best 8 third-place teams
    third_place_all = [
        (grp, team, stats)
        for grp, standings in group_results.items()
        for team, stats in [standings[2]]
    ]
    third_place_all.sort(key=lambda x: (-x[2]['pts'], -x[2]['gd'], -x[2]['gf'], x[1]))
    qualifying_thirds = {grp: team for grp, team, _ in third_place_all[:8]}
    third_assignments = _assign_third_place(qualifying_thirds)  # {match_num: team}

    match_results: dict[int, dict] = {}

    # --- Round of 32 ---
    for match_num, (slot1, slot2) in R32_SLOTS.items():
        team1 = pos_to_team.get(slot1)
        if slot2.startswith('3'):
            team2 = third_assignments.get(match_num)
        else:
            team2 = pos_to_team.get(slot2)

        if team1 and team2:
            winner = _simulate_knockout_match(team1, team2)
            match_results[match_num] = {'team1': team1, 'team2': team2, 'winner': winner}

    # --- R16 through Final (in bracket order) ---
    for match_num, (src1, src2) in KNOCKOUT_BRACKET.items():
        if match_num <= 88:
            continue  # R32 already handled above
        m1 = match_results.get(src1)
        m2 = match_results.get(src2)
        if m1 and m2:
            team1 = m1['winner']
            team2 = m2['winner']
            winner = _simulate_knockout_match(team1, team2)
            match_results[match_num] = {'team1': team1, 'team2': team2, 'winner': winner}

    return match_results


def find_meeting(team_a: str, team_b: str, match_results: dict) -> int | None:
    """
    Return the match number where team_a and team_b meet, or None if they never do.
    """
    for match_num in sorted(match_results):
        m = match_results[match_num]
        if {m['team1'], m['team2']} == {team_a, team_b}:
            return match_num
    return None


# ---------------------------------------------------------------------------
# Deterministic bracket-path tracing
# ---------------------------------------------------------------------------

def get_bracket_path(slot: str) -> list[int]:
    """
    Return the ordered list of match numbers a given slot passes through,
    from R32 all the way to the Final.

    slot examples: '1E' (Group E winner), '2I' (Group I runner-up)
    """
    r32_match = None
    for match_num, (s1, s2) in R32_SLOTS.items():
        if s1 == slot or s2 == slot:
            r32_match = match_num
            break

    if r32_match is None:
        return []

    path = [r32_match]
    current = r32_match
    for match_num, (src1, src2) in KNOCKOUT_BRACKET.items():
        if src1 == current or src2 == current:
            path.append(match_num)
            current = match_num

    return path


def find_first_common_match(slot_a: str, slot_b: str) -> int | None:
    """
    Return the earliest match number where the bracket paths of slot_a and
    slot_b first converge (i.e. the round they would meet if both advance).
    """
    path_a = get_bracket_path(slot_a)
    path_b = get_bracket_path(slot_b)
    if not path_a or not path_b:
        return None

    set_a = set(path_a)
    for match in path_b:
        if match in set_a:
            return match
    return None
