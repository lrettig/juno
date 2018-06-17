"""
Juno

A clean pywebassembly wrapper which exposes host functions. Implements the EEI specified at
https://github.com/ewasm/design.

Lane Rettig <lanerettig@gmail.com>
"""


def has_wasm_preamble(code):
    return len(code) >= 8 and code[0:8] == b'\x00asm\x01\x00\x00\x00'


def juno_execute(state, msg, tx_context, code):
    if not has_wasm_preamble(code):
        raise Exception("Invalid code")
