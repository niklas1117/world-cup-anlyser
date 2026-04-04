#!/usr/bin/env python3
"""
World Cup 2026 Analyzer
=======================

Usage:
  python main.py when <team1> <team2> [--simulations N]
  python main.py list-teams

Examples:
  python main.py when Norway Germany
  python main.py when "Cote d'Ivoire" Brazil --simulations 5000
  python main.py list-teams
"""

import argparse
import sys

from world_cup.analyzer import analyze_meeting, find_team
from world_cup.data import GROUPS


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _bar(pct: float, width: int = 30) -> str:
    filled = round(pct / 100 * width)
    return '█' * filled + '░' * (width - filled)


def _print_results(result: dict) -> None:
    team_a = result['team_a']
    team_b = result['team_b']
    n = result['num_simulations']
    meetings = result['meetings']
    no_meeting = result['no_meeting']

    print(f"\n{'═' * 58}")
    print(f"  {team_a}  vs  {team_b}")
    print(f"  Based on {n:,} simulations of the 2026 FIFA World Cup")
    print(f"{'═' * 58}\n")

    if not meetings:
        print(f"  In {n:,} simulations these teams never met.\n")
        return

    best_round, best_count = max(meetings, key=lambda x: x[1])

    print(f"  {'Round':<22}  {'Probability':>11}  {'Likelihood'}")
    print(f"  {'-' * 22}  {'-' * 11}  {'-' * 30}")

    for round_name, count in meetings:
        pct = count / n * 100
        marker = ' ◀ most likely' if round_name == best_round else ''
        print(f"  {round_name:<22}  {pct:>10.1f}%  {_bar(pct)}{marker}")

    pct_no = no_meeting / n * 100
    print(f"  {'No meeting':<22}  {pct_no:>10.1f}%  {_bar(pct_no)}")

    print(f"\n  Most likely encounter: {best_round}  ({best_count / n * 100:.1f}%)\n")


def _print_teams() -> None:
    print("\n2026 FIFA World Cup – Teams by Group\n")
    for group in sorted(GROUPS):
        teams = GROUPS[group]
        print(f"  Group {group}: {', '.join(teams)}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='World Cup 2026 Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest='command')

    # --- when ---
    when_p = subparsers.add_parser(
        'when',
        help='Find when two teams are likely to meet',
    )
    when_p.add_argument('team1', help='First team')
    when_p.add_argument('team2', help='Second team')
    when_p.add_argument(
        '--simulations', '-n',
        type=int,
        default=10_000,
        metavar='N',
        help='Number of Monte Carlo simulations (default: 10 000)',
    )

    # --- list-teams ---
    subparsers.add_parser('list-teams', help='List all teams and their groups')

    args = parser.parse_args()

    if args.command == 'when':
        # Validate early so we give a nice error before running simulations
        resolved_a = find_team(args.team1)
        resolved_b = find_team(args.team2)
        if not resolved_a:
            print(f"\nError: team not found – '{args.team1}'")
            print("Run  python main.py list-teams  to see all team names.\n")
            sys.exit(1)
        if not resolved_b:
            print(f"\nError: team not found – '{args.team2}'")
            print("Run  python main.py list-teams  to see all team names.\n")
            sys.exit(1)
        if resolved_a == resolved_b:
            print(f"\nError: both names resolve to the same team ({resolved_a}).\n")
            sys.exit(1)

        print(f"\nRunning {args.simulations:,} simulations …", end='', flush=True)
        result = analyze_meeting(args.team1, args.team2, args.simulations)
        print(" done.")
        _print_results(result)

    elif args.command == 'list-teams':
        _print_teams()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
