#!/usr/bin/env python3
"""
=========================================================
Kade2Psych
---------------------------------------------------------
Converts Kade/Taro Engine modcharts into
Psych Engine 1.0.4 compatible Lua scripts.

Author: ChatGPT + Angeliu Gamer
=========================================================
"""

import os
import sys

from src.lexer import Lexer
from src.parser import Parser
from src.generator import Generator
from src.ast import *
from src.rules import RuleEngine


VERSION = "0.1.0"


def print_header():

    print("=" * 60)
    print(" Kade2Psych")
    print(" Kade/Taro -> Psych Engine Converter")
    print(f" Version {VERSION}")
    print("=" * 60)
    print()


def ask_file():

    while True:

        path = input("Lua file to convert: ").strip('"')

        if os.path.isfile(path):
            return path

        print("File not found.\n")


def build_output_name(path):

    folder = os.path.dirname(path)

    name = os.path.basename(path)

    if "." in name:
        name = name[:name.rfind(".")]

    return os.path.join(folder, name + "_psych.lua")


def main():

    print_header()

    if len(sys.argv) >= 2:

        source = sys.argv[1]

        if not os.path.isfile(source):
            print("File not found.")
            return

    else:

        source = ask_file()

    print()

    print("Reading source...")

    with open(source, "r", encoding="utf8") as f:
        text = f.read()

    print("Lexing...")

    lexer = Lexer(text)

    tokens = lexer.lex()

    print(f"  {len(tokens)} tokens.")

    print("Parsing...")

    parser = Parser(tokens)

    tree = parser.parse()

    print("Generating Psych Lua...")

    generator = Generator()

    output = generator.generate(tree)

    output_name = build_output_name(source)

    with open(output_name, "w", encoding="utf8") as f:
        f.write(output)

    print()

    print("Done!")

    print(output_name)


if __name__ == "__main__":
    main()