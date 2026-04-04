"""
High-level analysis: run many simulations and report where two teams are
likely to meet in the 2026 World Cup.
"""

from .data import GROUPS, ROUND_NAMES
from .simulator import simulate_tournament, find_meeting


def _all_teams() -> list[str]:
    return [team for teams in GROUPS.values() for team in teams]


def find_team(name: str) -> str | None:
    """
    Return the canonical team name for *name*, matching case-insensitively.
    Tries exact match first, then substring match.
    """
    needle = name.strip().lower()
    all_teams = _all_teams()

    # Exact match
    for team in all_teams:
        if team.lower() == needle:
            return team

    # Substring: needle inside team name
    for team in all_teams:
        if needle in team.lower():
            return team

    # Substring: team name inside needle (e.g. "ivory coast" -> "Cote d'Ivoire")
    for team in all_teams:
        if team.lower() in needle:
            return team

    return None


def analyze_meeting(team_a_name: str, team_b_name: str, num_simulations: int = 10_000) -> dict:
    """
    Simulate the tournament *num_simulations* times and record where the two
    teams meet.

    Returns a dict with:
        team_a          canonical name of team A
        team_b          canonical name of team B
        num_simulations number of simulations run
        meetings        list of ((match_num, round_name), count) sorted by match_num
        no_meeting      number of simulations where they never met
    """
    team_a = find_team(team_a_name)
    team_b = find_team(team_b_name)

    if not team_a:
        raise ValueError(
            f"Team not found: '{team_a_name}'. "
            f"Run with --list-teams to see all teams."
        )
    if not team_b:
        raise ValueError(
            f"Team not found: '{team_b_name}'. "
            f"Run with --list-teams to see all teams."
        )
    if team_a == team_b:
        raise ValueError(f"Both names resolve to the same team: {team_a}")

    # Aggregate counts by round name (not by individual match number),
    # so that rare 3rd-place routing variants collapse into one entry.
    ROUND_ORDER = ['Round of 32', 'Round of 16', 'Quarterfinal', 'Semifinal', 'Final']
    meeting_counts: dict[str, int] = {}
    no_meeting = 0

    for _ in range(num_simulations):
        results = simulate_tournament()
        match_num = find_meeting(team_a, team_b, results)
        if match_num is not None:
            round_name = ROUND_NAMES.get(match_num, f'Match {match_num}')
            meeting_counts[round_name] = meeting_counts.get(round_name, 0) + 1
        else:
            no_meeting += 1

    # Return sorted in bracket order, omitting rounds with zero occurrences
    sorted_meetings = [
        (rnd, meeting_counts[rnd])
        for rnd in ROUND_ORDER
        if meeting_counts.get(rnd, 0) > 0
    ]

    return {
        'team_a':          team_a,
        'team_b':          team_b,
        'num_simulations': num_simulations,
        'meetings':        sorted_meetings,   # [(round_name, count), ...]
        'no_meeting':      no_meeting,
    }
