"""Safe arithmetic for symbolic questions.

This is the same language the quiz grades in the browser. It does not call
eval. Names are the question's variables plus the constants pi and e.
Functions are sqrt, abs, exp, ln, log (natural log), sin, cos, and tan.
^ and ** are both power, and power is right-associative. 2x and 2(x+1)
mean multiplication.
"""
import math
import random

FUNCS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "exp": math.exp,
    "ln": math.log,
    "log": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
}
CONSTS = {"pi": math.pi, "e": math.e}
MAX_LEN = 200


class ExprError(Exception):
    pass


def tokenize(src, bound=()):
    """bound is the set of declared variable names.

    e and E are rejected as variables. If one is passed anyway, scientific
    notation does not consume that letter, so 2e+1 is 2*e+1 rather than 20.
    """
    bound = set(bound)
    toks = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c.isspace():
            i += 1
            continue
        if c in "×·":
            toks.append(("*", None))
            i += 1
            continue
        if c == "\u2212":
            toks.append(("-", None))
            i += 1
            continue
        if c == "*" and i + 1 < n and src[i + 1] == "*":
            toks.append(("^", None))
            i += 2
            continue
        if c in "+-*/^()":
            toks.append((c, None))
            i += 1
            continue
        if c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            j = i
            if src[j] == ".":
                j += 1
                while j < n and src[j].isdigit():
                    j += 1
            else:
                while j < n and src[j].isdigit():
                    j += 1
                if j < n and src[j] == ".":
                    j += 1
                    while j < n and src[j].isdigit():
                        j += 1
            # 2e-3 is a number. e and E are not variables, so this never
            # swallows a name: 2*e+1 is the constant, and 2e+1 is 20.
            if j < n and src[j] in "eE" and src[j] not in bound:
                k = j + 1
                if k < n and src[k] in "+-":
                    k += 1
                if k < n and src[k].isdigit():
                    while k < n and src[k].isdigit():
                        k += 1
                    j = k
            try:
                value = float(src[i:j])
            except ValueError as exc:
                raise ExprError("bad number") from exc
            if not math.isfinite(value):
                raise ExprError("bad number")
            toks.append(("num", value))
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            toks.append(("name", src[i:j]))
            i = j
            continue
        raise ExprError("unexpected character " + c)
    return toks


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self):
        if self.i < len(self.toks):
            return self.toks[self.i]
        return None

    def eat(self):
        tok = self.peek()
        if tok is None:
            raise ExprError("expression ended early")
        self.i += 1
        return tok

    def parse(self):
        node = self.expr()
        if self.peek() is not None:
            raise ExprError("unexpected " + self.peek()[0])
        return node

    def expr(self):
        node = self.term()
        while self.peek() and self.peek()[0] in ("+", "-"):
            op = self.eat()[0]
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while True:
            nxt = self.peek()
            if nxt and nxt[0] in ("*", "/"):
                op = self.eat()[0]
                node = ("bin", op, node, self.unary())
            elif nxt and nxt[0] in ("num", "name", "("):
                node = ("bin", "*", node, self.unary())
            else:
                break
        return node

    def unary(self):
        nxt = self.peek()
        if nxt and nxt[0] == "+":
            self.eat()
            return self.unary()
        if nxt and nxt[0] == "-":
            self.eat()
            return ("neg", self.unary())
        return self.power()

    def power(self):
        node = self.primary()
        if self.peek() and self.peek()[0] == "^":
            self.eat()
            node = ("bin", "^", node, self.unary())
        return node

    def primary(self):
        nxt = self.peek()
        if nxt is None:
            raise ExprError("expression ended early")
        if nxt[0] == "num":
            self.eat()
            return ("num", nxt[1])
        if nxt[0] == "name":
            name = self.eat()[1]
            if self.peek() and self.peek()[0] == "(" and name in FUNCS:
                self.eat()
                arg = self.expr()
                if not self.peek() or self.peek()[0] != ")":
                    raise ExprError("expected )")
                self.eat()
                return ("call", name, arg)
            return ("var", name)
        if nxt[0] == "(":
            self.eat()
            node = self.expr()
            if not self.peek() or self.peek()[0] != ")":
                raise ExprError("expected )")
            self.eat()
            return node
        raise ExprError("unexpected " + nxt[0])


def free_names(ast, out=None):
    if out is None:
        out = set()
    kind = ast[0]
    if kind == "var":
        out.add(ast[1])
    elif kind in ("neg", "call"):
        free_names(ast[-1], out)
    elif kind == "bin":
        free_names(ast[2], out)
        free_names(ast[3], out)
    return out


def parse(src, variables):
    """Parse src. variables is the iterable of declared names. Raises ExprError."""
    if not isinstance(src, str):
        raise ExprError("expression must be text")
    text = src.strip()
    if not text:
        raise ExprError("enter an expression")
    if len(text) > MAX_LEN:
        raise ExprError("expression is too long")
    if "\\" in text or "$" in text:
        raise ExprError("use plain names, not TeX")
    allowed = set(variables)
    reserved = sorted(name for name in allowed if name in FUNCS)
    if reserved:
        raise ExprError("function name used as a variable: " + ", ".join(reserved))
    collided = sorted(name for name in allowed if name in ("e", "E"))
    if collided:
        raise ExprError("e and E are reserved for the constant e and for scientific notation")
    ast = Parser(tokenize(text, allowed)).parse()
    unknown = sorted(name for name in free_names(ast) if name not in allowed and name not in CONSTS)
    if unknown:
        raise ExprError("unknown name " + ", ".join(unknown))
    return ast


def _eval_node(ast, env):
    kind = ast[0]
    if kind == "num":
        return ast[1]
    if kind == "var":
        name = ast[1]
        if name in env:
            return float(env[name])
        if name in CONSTS:
            return CONSTS[name]
        raise ExprError("unknown name " + name)
    if kind == "neg":
        return -_eval_node(ast[1], env)
    if kind == "call":
        return FUNCS[ast[1]](_eval_node(ast[2], env))
    if kind == "bin":
        op = ast[1]
        left = _eval_node(ast[2], env)
        right = _eval_node(ast[3], env)
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise ZeroDivisionError
            return left / right
        if op == "^":
            return left ** right
    raise ExprError("bad expression")


def evaluate(ast, env):
    """Return a finite float, or None when the expression is undefined there."""
    try:
        value = _eval_node(ast, env)
    except (ValueError, OverflowError, ZeroDivisionError, ExprError, TypeError):
        return None
    if isinstance(value, complex) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value):
        return None
    return float(value)


def _sample(variables, rng):
    env = {}
    for spec in variables:
        lo = float(spec["min"])
        hi = float(spec["max"])
        env[spec["name"]] = rng.uniform(lo, hi)
    return env


def agrees(key_ast, guess_ast, variables, tolerance, samples=6, rng=None):
    """True when guess matches key at `samples` finite random points."""
    rng = rng or random.Random()
    tol = float(tolerance)
    hits = 0
    tries = 0
    limit = samples * 8
    while hits < samples and tries < limit:
        tries += 1
        env = _sample(variables, rng)
        key = evaluate(key_ast, env)
        guess = evaluate(guess_ast, env)
        if key is None or guess is None:
            continue
        scale = max(abs(key), abs(guess), 1e-9)
        if abs(key - guess) > tol * scale * (1 + 1e-9):
            return False
        hits += 1
    return hits >= samples


def grade(key, guess, variables, tolerance, samples=6, seed=1):
    """True, False, or None. None means the learner's text did not parse."""
    names = [spec["name"] for spec in variables]
    key_ast = parse(key, names)
    try:
        guess_ast = parse(guess, names)
    except ExprError:
        return None
    return agrees(key_ast, guess_ast, variables, tolerance, samples, random.Random(seed))
