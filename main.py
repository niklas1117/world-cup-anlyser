#!/usr/bin/env python3
"""
World Cup 2026 Analyzer
=======================

Usage:
  python main.py when <team1> <team2> [--html FILE]
  python main.py list-teams

Examples:
  python main.py when Norway Germany
  python main.py when Norway Germany --html norway_germany.html
  python main.py when Brazil Argentina
  python main.py list-teams
"""

import argparse
import sys

from world_cup.analyzer import trace_scenarios, find_team
from world_cup.data import GROUPS
from world_cup.visualizer import print_grid, generate_html


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
    when_p.add_argument(
        '--html', metavar='FILE',
        help='Also write an HTML visualization to FILE (e.g. report.html)',
    )

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
        print_grid(result)

        if args.html:
            generate_html(result, args.html)
            print(f"  HTML report written to: {args.html}\n")

    elif args.command == 'list-teams':
        _print_teams()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
