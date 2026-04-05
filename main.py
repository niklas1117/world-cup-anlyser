#!/usr/bin/env python3
"""
World Cup 2026 Analyzer
=======================

Usage:
  python main.py when <team1> <team2>
  python main.py list-teams

Examples:
  python main.py when Norway Germany
  python main.py when Brazil Argentina
  python main.py list-teams
"""

import argparse
import sys

from world_cup.analyzer import trace_scenarios, find_team
from world_cup.data import GROUPS


def _ordinal(n: int) -> str:
    return {1: '1st', 2: '2nd', 3: '3rd'}[n]


def _print_scenarios(result: dict) -> None:
    team_a  = result['team_a']
    team_b  = result['team_b']
    group_a = result['group_a']
    group_b = result['group_b']

    has_inexact = any(not s['is_exact'] for s in result['scenarios'])

    print(f"\n{'═' * 60}")
    print(f"  {team_a} (Group {group_a})  vs  {team_b} (Group {group_b})")
    print(f"{'═' * 60}")
    print(f"  {'Scenario':<38}  {'Meeting'}")
    print(f"  {'-' * 38}  {'-' * 18}")

    for s in result['scenarios']:
        scenario = (
            f"{team_a} {_ordinal(s['pos_a'])}, "
            f"{team_b} {_ordinal(s['pos_b'])}"
        )
        if s['round'] is None:
            meeting = '—'
        elif s['is_exact']:
            meeting = s['round']
        else:
            meeting = s['round'] + ' *'
        print(f"  {scenario:<38}  {meeting}")

    if has_inexact:
        print(f"\n  * earliest possible — depends on 3rd-place bracket draw")
        print(f"    (only the best 8 of 12 third-place teams qualify)")

    print()


def _print_teams() -> None:
    print("\n2026 FIFA World Cup – Teams by Group\n")
    for group in sorted(GROUPS):
        print(f"  Group {group}: {', '.join(GROUPS[group])}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='World Cup 2026 Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest='command')

    when_p = subparsers.add_parser('when', help='Find when two teams could meet')
    when_p.add_argument('team1', help='First team')
    when_p.add_argument('team2', help='Second team')

    subparsers.add_parser('list-teams', help='List all teams and their groups')

    args = parser.parse_args()

    if args.command == 'when':
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

        result = trace_scenarios(args.team1, args.team2)
        _print_scenarios(result)

    elif args.command == 'list-teams':
        _print_teams()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
