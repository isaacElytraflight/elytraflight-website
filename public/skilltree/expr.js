/* Safe arithmetic for symbolic questions. No eval.
   Same language as skilltree/expr.py: variables plus pi and e;
   sqrt abs exp ln log sin cos tan; ^ and ** are right-associative power;
   2x and 2(x+1) mean multiplication. log is the natural log. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SkillExpr = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const FUNCS = {
    sqrt: Math.sqrt,
    abs: Math.abs,
    exp: Math.exp,
    ln: Math.log,
    log: Math.log,
    sin: Math.sin,
    cos: Math.cos,
    tan: Math.tan
  };
  const CONSTS = { pi: Math.PI, e: Math.E };
  const MAX_LEN = 200;

  function ExprError(message) {
    this.name = 'ExprError';
    this.message = message;
  }
  ExprError.prototype = Object.create(Error.prototype);

  function tokenize(src, bound) {
    // e and E are not variables. 2e-3 is always a number. If a caller binds
    // one of those names anyway, that letter is not an exponent, so 2e+1
    // is 2*e+1 rather than 20.
    const boundNames = bound || new Set();
    const toks = [];
    let i = 0;
    const n = src.length;
    while (i < n) {
      const c = src[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '×' || c === '·') { toks.push(['*', null]); i++; continue; }
      if (c === '\u2212') { toks.push(['-', null]); i++; continue; }
      if (c === '*' && src[i + 1] === '*') { toks.push(['^', null]); i += 2; continue; }
      if ('+-*/^()'.includes(c)) { toks.push([c, null]); i++; continue; }
      if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1] || ''))) {
        const start = i;
        if (src[i] === '.') {
          i++;
          while (i < n && /[0-9]/.test(src[i])) i++;
        } else {
          while (i < n && /[0-9]/.test(src[i])) i++;
          if (src[i] === '.') {
            i++;
            while (i < n && /[0-9]/.test(src[i])) i++;
          }
        }
        if ((src[i] === 'e' || src[i] === 'E') && !boundNames.has(src[i])) {
          let k = i + 1;
          if (src[k] === '+' || src[k] === '-') k++;
          if (/[0-9]/.test(src[k] || '')) {
            while (k < n && /[0-9]/.test(src[k])) k++;
            i = k;
          }
        }
        const value = Number(src.slice(start, i));
        if (!Number.isFinite(value)) throw new ExprError('bad number');
        toks.push(['num', value]);
        continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        const start = i;
        i++;
        while (i < n && /[A-Za-z0-9_]/.test(src[i])) i++;
        toks.push(['name', src.slice(start, i)]);
        continue;
      }
      throw new ExprError('unexpected character ' + c);
    }
    return toks;
  }

  function Parser(toks) {
    this.toks = toks;
    this.i = 0;
  }
  Parser.prototype.peek = function () {
    return this.i < this.toks.length ? this.toks[this.i] : null;
  };
  Parser.prototype.eat = function () {
    const tok = this.peek();
    if (!tok) throw new ExprError('expression ended early');
    this.i++;
    return tok;
  };
  Parser.prototype.parse = function () {
    const node = this.expr();
    if (this.peek()) throw new ExprError('unexpected ' + this.peek()[0]);
    return node;
  };
  Parser.prototype.expr = function () {
    let node = this.term();
    while (this.peek() && (this.peek()[0] === '+' || this.peek()[0] === '-')) {
      const op = this.eat()[0];
      node = ['bin', op, node, this.term()];
    }
    return node;
  };
  Parser.prototype.term = function () {
    let node = this.unary();
    for (;;) {
      const nxt = this.peek();
      if (nxt && (nxt[0] === '*' || nxt[0] === '/')) {
        const op = this.eat()[0];
        node = ['bin', op, node, this.unary()];
      } else if (nxt && (nxt[0] === 'num' || nxt[0] === 'name' || nxt[0] === '(')) {
        node = ['bin', '*', node, this.unary()];
      } else break;
    }
    return node;
  };
  Parser.prototype.unary = function () {
    const nxt = this.peek();
    if (nxt && nxt[0] === '+') { this.eat(); return this.unary(); }
    if (nxt && nxt[0] === '-') { this.eat(); return ['neg', this.unary()]; }
    return this.power();
  };
  Parser.prototype.power = function () {
    let node = this.primary();
    if (this.peek() && this.peek()[0] === '^') {
      this.eat();
      node = ['bin', '^', node, this.unary()];
    }
    return node;
  };
  Parser.prototype.primary = function () {
    const nxt = this.peek();
    if (!nxt) throw new ExprError('expression ended early');
    if (nxt[0] === 'num') { this.eat(); return ['num', nxt[1]]; }
    if (nxt[0] === 'name') {
      const name = this.eat()[1];
      if (this.peek() && this.peek()[0] === '(' && Object.prototype.hasOwnProperty.call(FUNCS, name)) {
        this.eat();
        const arg = this.expr();
        if (!this.peek() || this.peek()[0] !== ')') throw new ExprError('expected )');
        this.eat();
        return ['call', name, arg];
      }
      return ['var', name];
    }
    if (nxt[0] === '(') {
      this.eat();
      const node = this.expr();
      if (!this.peek() || this.peek()[0] !== ')') throw new ExprError('expected )');
      this.eat();
      return node;
    }
    throw new ExprError('unexpected ' + nxt[0]);
  };

  function freeNames(ast, out) {
    out = out || new Set();
    const kind = ast[0];
    if (kind === 'var') out.add(ast[1]);
    else if (kind === 'neg' || kind === 'call') freeNames(ast[ast.length - 1], out);
    else if (kind === 'bin') { freeNames(ast[2], out); freeNames(ast[3], out); }
    return out;
  }

  function parse(src, variables) {
    if (typeof src !== 'string') throw new ExprError('expression must be text');
    const text = src.trim();
    if (!text) throw new ExprError('enter an expression');
    if (text.length > MAX_LEN) throw new ExprError('expression is too long');
    if (text.includes('\\') || text.includes('$')) throw new ExprError('use plain names, not TeX');
    const allowed = new Set(variables);
    const reserved = [...allowed].filter(name => Object.prototype.hasOwnProperty.call(FUNCS, name)).sort();
    if (reserved.length) throw new ExprError('function name used as a variable: ' + reserved.join(', '));
    if (allowed.has('e') || allowed.has('E')) throw new ExprError('e and E are reserved for the constant e and for scientific notation');
    const ast = new Parser(tokenize(text, allowed)).parse();
    const unknown = [...freeNames(ast)].filter(name => !allowed.has(name) && !Object.prototype.hasOwnProperty.call(CONSTS, name)).sort();
    if (unknown.length) throw new ExprError('unknown name ' + unknown.join(', '));
    return ast;
  }

  function evalNode(ast, env) {
    const kind = ast[0];
    if (kind === 'num') return ast[1];
    if (kind === 'var') {
      if (Object.prototype.hasOwnProperty.call(env, ast[1])) return env[ast[1]];
      if (Object.prototype.hasOwnProperty.call(CONSTS, ast[1])) return CONSTS[ast[1]];
      throw new ExprError('unknown name ' + ast[1]);
    }
    if (kind === 'neg') return -evalNode(ast[1], env);
    if (kind === 'call') return FUNCS[ast[1]](evalNode(ast[2], env));
    if (kind === 'bin') {
      const left = evalNode(ast[2], env);
      const right = evalNode(ast[3], env);
      if (ast[1] === '+') return left + right;
      if (ast[1] === '-') return left - right;
      if (ast[1] === '*') return left * right;
      if (ast[1] === '/') {
        if (right === 0) throw new Error('div0');
        return left / right;
      }
      if (ast[1] === '^') return Math.pow(left, right);
    }
    throw new ExprError('bad expression');
  }

  function evaluate(ast, env) {
    try {
      const value = evalNode(ast, env);
      return Number.isFinite(value) ? value : null;
    } catch (e) {
      return null;
    }
  }

  function grade(question, text, rng) {
    const random = rng || Math.random;
    const names = question.variables.map(v => v.name);
    let key;
    try { key = parse(question.answer, names); }
    catch (e) { return { ok: false, invalid: false }; }
    let guess;
    try { guess = parse(text == null ? '' : String(text), names); }
    catch (e) { return { ok: false, invalid: true, message: e.message }; }
    const samples = 6;
    const tol = question.tolerance != null ? question.tolerance : 1e-3;
    let hits = 0;
    let tries = 0;
    while (hits < samples && tries < samples * 8) {
      tries++;
      const env = {};
      for (const v of question.variables) env[v.name] = v.min + random() * (v.max - v.min);
      const a = evaluate(key, env);
      const b = evaluate(guess, env);
      if (a == null || b == null) continue;
      const scale = Math.max(Math.abs(a), Math.abs(b), 1e-9);
      if (Math.abs(a - b) > tol * scale * (1 + 1e-9)) return { ok: false, invalid: false };
      hits++;
    }
    return { ok: hits >= samples, invalid: false };
  }

  return { parse, evaluate, grade, tokenize, freeNames, ExprError, FUNCS: Object.keys(FUNCS), CONSTS: Object.keys(CONSTS) };
});
