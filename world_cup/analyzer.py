"""
High-level analysis for the 2026 FIFA World Cup.
"""

from .data import GROUPS, ROUND_NAMES
from .simulator import find_earliest_meeting, path_from_match


def _all_teams() -> list[str]:
    return [team for teams in GROUPS.values() for team in teams]


def find_team(name: str) -> str | None:
    """
    Return the canonical team name for *name*, matching case-insensitively.
    Tries exact match first, then substring match.
    """
    needle = name.strip().lower()
    all_teams = _all_teams()

    for team in all_teams:
        if team.lower() == needle:
            return team
    for team in all_teams:
        if needle in team.lower():
            return team
    for team in all_teams:
        if team.lower() in needle:
            return team
    return None


def _find_group(team: str) -> str:
    for group, teams in GROUPS.items():
        if team in teams:
            return group
    raise ValueError(f"Team not in any group: {team}")


def trace_scenarios(team_a_name: str, team_b_name: str) -> dict:
    """
    For every combination of group-stage finishes (1st or 2nd) for two teams,
    trace the bracket to find the first round they would meet.

    Returns:
        {
            team_a:    canonical name,
            team_b:    canonical name,
            group_a:   group letter,
            group_b:   group letter,
            scenarios: [
                {pos_a, pos_b, slot_a, slot_b, match, round},
                ...  # 4 entries, ordered (1,1), (1,2), (2,1), (2,2)
            ]
        }
    """
    team_a = find_team(team_a_name)
    team_b = find_team(team_b_name)

    if not team_a:
        raise ValueError(f"Team not found: '{team_a_name}'")
    if not team_b:
        raise ValueError(f"Team not found: '{team_b_name}'")
    if team_a == team_b:
        raise ValueError(f"Both names resolve to the same team: {team_a}")

    group_a = _find_group(team_a)
    group_b = _find_group(team_b)

    scenarios = []
    for pos_a in (1, 2, 3):
        for pos_b in (1, 2, 3):
            slot_a = f'{pos_a}{group_a}'
            slot_b = f'{pos_b}{group_b}'
            match_num, is_exact, r32_a, r32_b = find_earliest_meeting(slot_a, slot_b)
            round_name = ROUND_NAMES.get(match_num) if match_num else None
            path_a = (
                [(m, ROUND_NAMES.get(m, '')) for m in path_from_match(r32_a)]
                if r32_a else []
            )
            path_b = (
                [(m, ROUND_NAMES.get(m, '')) for m in path_from_match(r32_b)]
                if r32_b else []
            )
            scenarios.append({
                'pos_a':    pos_a,
                'pos_b':    pos_b,
                'slot_a':   slot_a,
                'slot_b':   slot_b,
                'match':    match_num,
                'round':    round_name,
                'is_exact': is_exact,
                'path_a':   path_a,   # [(match_num, round_name), ...]
                'path_b':   path_b,
            })

    return {
        'team_a':    team_a,
        'team_b':    team_b,
        'group_a':   group_a,
        'group_b':   group_b,
        'scenarios': scenarios,
    }
