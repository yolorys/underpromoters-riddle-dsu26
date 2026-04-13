#!/usr/bin/env python
# coding: utf-8

import os, shutil
from argparse import Action, ArgumentTypeError
from pathlib import Path

global STOCKFISH_PATH
STOCKFISH_PATH = Path(os.environ.get('STOCKFISH_PATH', shutil.which('stockfish')))
global ANALYSIS_TIME_LIMIT
ANALYSIS_TIME_LIMIT = 0.1

class SetStockfish(Action):
    def __call__(self, parser, namespace, values, option_string):
        if values.exists():
            STOCKFISH_PATH = values
        else:
            raise ArgumentTypeError("Stockfish path must exist and be executable")

class SetAnalysisTimeLimit(Action):
    def __call__(self, parser, namespace, values, option_string):
        ANALYSIS_TIME_LIMIT = values

def add_arguments(parser):
    parser.add_argument('--stockfish',
                        metavar='PATH',
                        help='Path to stockfish engine (taken from environment STOCKFISH_PATH or autodetected: "%(default)s")',
                        default=STOCKFISH_PATH,
                        type=Path,
                        action=SetStockfish)

    parser.add_argument('--time-limit',
                        metavar='SECS',
                        help='Time limit for analysis (default: "%(default)s")',
                        type=float,
                        default=0.1,
                        action=SetAnalysisTimeLimit)

def add_input_output_args(parser, input_default, output_default):
    parser.add_argument('input',
                    help='Input file (default: "%(default)s")',
                    nargs='?',
                    type=Path,
                    default=input_default)
    parser.add_argument('output',
                        help='Output file (default: "%(default)s")',
                        nargs='?',
                        type=Path,
                        default=output_default)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    add_arguments(parser)

    parser.parse_args()
    print(f"stockfish_path: {STOCKFISH_PATH}")
