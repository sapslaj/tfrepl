#!/usr/bin/env python3
from copy import copy, deepcopy
import tempfile
import os

import sys
import pygments
from pygments.lexers import TerraformLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import PromptSession, print_formatted_text
from pygments.formatters import TerminalFormatter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


def run(dir):
    os.system(f"terraform -chdir={dir} init")
    os.system(f"terraform -chdir={dir} plan")


def fmt(dir):
    os.system(f"terraform -chdir={dir} fmt")


def touch_repl_file(dir, filename):
    os.system(f"touch {dir}/{filename}")


def read_repl_file(dir, filename):
    lines = []
    with open(f"{dir}/{filename}", "r") as file:
        lines = file.readlines()
    return [line.rstrip("\n") for line in lines]


def write_repl_file(dir, filename, lines):
    with open(f"{dir}/{filename}", "w") as file:
        file.write("\n".join(lines))


def lines_reducer(lines, block_level, direct_output, new_line):
    lines = deepcopy(lines)
    block_level = copy(block_level)
    direct_output = copy(direct_output)
    if new_line.startswith("="):
        direct_output = True
        lines.append('output "output" {')
        block_level = 1
        lines.append(f"  value {new_line}")
    elif new_line.startswith("local "):
        lines.append("locals {")
        block_level = 1
        lines.append(new_line.removeprefix("local "))
    else:
        lines.append(new_line)
    for character in new_line:
        if character in ("{", "[", "("):
            block_level += 1
        elif character in ("}", "]", ")"):
            block_level -= 1
    if direct_output and new_line == "" and block_level == 1:
        lines.append("}")
        block_level = 0
        direct_output = False
    return lines, block_level, direct_output


def desugar(input_lines, lines=None, block_level=None, direct_output=None):
    lines = deepcopy(lines) if lines is not None else []
    block_level = copy(block_level) if block_level is not None else 0
    direct_output = copy(direct_output) if direct_output is not None else False
    for line in input_lines:
        lines, block_level, direct_output = lines_reducer(lines, block_level, direct_output, line.rstrip("\n"))
    # big chung hack
    if len(lines) > 2 and lines[-2] == 'output "output" {' and line[-1] != "}" and block_level == 1 and direct_output:
        lines.append("}")
    return lines


def print_lines(lines, style):
    input_file = "\n".join(lines)
    tokens = pygments.lex(input_file, lexer=TerraformLexer())
    print_formatted_text(PygmentsTokens(tokens), style=style)


def repl(session, dir):
    style = style_from_pygments_cls(get_style_by_name(os.environ.get("TFREPL_COLOR_SCHEME", "default")))
    reset = True
    lines = []
    block_level = 0
    direct_output = False
    while True:
        if reset:
            lines = []
            block_level = 0
            direct_output = False
        reset = False
        prompt = "... " if block_level > 0 else "> "
        line = session.prompt(
            f"{len(lines) + 1} {prompt}",
            lexer=PygmentsLexer(TerraformLexer),
            style=TerminalFormatter(style=style).style,
            include_default_pygments_style=False,
            auto_suggest=AutoSuggestFromHistory(),
        )
        lines, block_level, direct_output = lines_reducer(lines, block_level, direct_output, line)
        if line == "" and block_level == 0:
            write_repl_file(dir, "repl.tf", lines)
            fmt(dir)
            lines = read_repl_file(dir, "repl.tf")
            print_lines(lines, style)
            run(dir)
            reset = True
        elif line in ("print", "print()", ":p"):
            lines.pop()
            print_lines(lines, style)
        elif line in ("ls", ":ls"):
            lines.pop()
            os.system(f"ls -lah {dir}")
        elif line in ("edit", "edit()", ":e", ":edit"):
            lines.pop()
            editor = os.environ.get("TFREPL_EDITOR", os.environ.get("EDITOR", "vi"))
            if lines:
                write_repl_file(dir, "repl.tf", lines)
            else:
                touch_repl_file(dir, "repl.tf")
            os.system(f"{editor} {dir}/repl.tf")
            edited_lines = desugar(read_repl_file(dir, "repl.tf"))
            write_repl_file(dir, "repl.tf", edited_lines)
            fmt(dir)
            lines = read_repl_file(dir, "repl.tf")
            print_lines(lines, style)
            run(dir)
            reset = True
        elif line in ("exit", "exit()", "quit", "quit()", ":q", ":quit"):
            sys.exit(0)
        elif line in ("init", "init()", ":init"):
            os.system(f"terraform -chdir={dir} init")
            reset = True
        elif line in ("plan", "plan()", ":plan"):
            os.system(f"terraform -chdir={dir} plan")
            reset = True
        elif line in ("apply", "apply()", ":apply"):
            os.system(f"terraform -chdir={dir} apply")
            reset = True


def main():
    tfrepl_config_root = os.path.expanduser("~/.tfrepl")
    os.system(f"mkdir -p {tfrepl_config_root}")
    session = PromptSession(history=FileHistory(f"{tfrepl_config_root}/history"))
    with tempfile.TemporaryDirectory() as tempdir:
        skeldir = f"{tfrepl_config_root}/skel"
        if os.path.isdir(skeldir):
            print(f"Copying skeleton from {skeldir}")
            os.system(f"cp -r '{skeldir}/' '{tempdir}/'")
        print(f"Starting REPL in {tempdir}")
        repl(session, tempdir)


if __name__ == "__main__":
    main()
