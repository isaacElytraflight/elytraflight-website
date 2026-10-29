"""o_latex: convert the plain/Unicode math of the original 14 banks into LaTeX inside \\( \\) delimiters.
Used by qlib.Skill (mc/num) so every generator's text is converted at build time; question ids/answers untouched.
Heuristic but deterministic: maximal runs of 'mathy' words that contain at least one strong math marker
(Greek letter, sub/superscript, operator like × · √ = ≈ ∠, function call like H(jω), x_sub) become one \\( ... \\)."""
import re

GREEK = {'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta', 'ε': r'\varepsilon', 'ζ': r'\zeta',
         'θ': r'\theta', 'λ': r'\lambda', 'μ': r'\mu', 'π': r'\pi', 'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\phi',
         'ω': r'\omega', 'Δ': r'\Delta', 'Ω': r'\Omega', 'Σ': r'\Sigma', 'ρ': r'\rho', 'η': r'\eta'}
SUPS = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺', '0123456789-+'))
SUBS = dict(zip('₀₁₂₃₄₅₆₇₈₉ₙₒᵤₜᵢₑᵣₛₗₚₖₐₓ₊₋', '0123456789nouti' 'ersl' 'pkax+-'))
OPS = {'×': r'\times', '·': r'\cdot', '−': '-', '–': '-', '±': r'\pm', '≈': r'\approx', '≫': r'\gg', '≪': r'\ll',
       '≤': r'\le', '≥': r'\ge', '∞': r'\infty', '∫': r'\int', '∑': r'\sum', '∗': r'\ast', '…': r'\ldots',
       '∥': r'\parallel', '→': r'\to', '∠': r'\angle', '°': r'^{\circ}', '½': r'\tfrac{1}{2}', '′': "'", '≠': r'\ne',
       '∝': r'\propto', '✔': r'\checkmark'}
FUNCS = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'arg'}
ROMAN = {'Re', 'Im'}
UNITS = {'dB', 'Hz', 'kHz', 'MHz', 'GHz', 'rad', 'krad', 'Mrad', 's', 'ms', 'ns', 'ps', 'V', 'mV', 'kV', 'A', 'mA', 'nA',
         'W', 'mW', 'F', 'nF', 'pF', 'H', 'mH', 'nH', 'S', 'mS', 'k', 'M', 'G', 'm', 'n', 'p', 'u', 'deg', 'dec', 'decade',
         'RMS', 'rms', 'J', 'K', 'cm', 'mm', 'nm', 'nV', 'uV', 'pA', 'fF', 'MV', 'kW'}
STOP = {'a', 'an', 'at', 'is', 'of', 'to', 'in', 'by', 'or', 'if', 'as', 'be', 'on', 'it', 'so', 'up', 'no', 'we', 'do',
        'A', 'I', 'An', 'At', 'Is', 'Of', 'To', 'In', 'By', 'Or', 'If', 'As', 'On', 'It', 'So', 'No', 'We', 'Do', 'he', 'me'}
STRONG_CH = set(GREEK) - {'Ω'} | set(SUPS) | set(SUBS) | set('_^×·√≈≫≪∠≤≥∞∫∑∗±=∥½≠∝')
MATHY = re.compile(r"^[\w.,+\-−–()\[\]/|{}°%∠µ'′!*^<>" + ''.join(GREEK) + ''.join(SUPS) + ''.join(SUBS) + ''.join(OPS) + r"√=]+$")
FCALL = re.compile(r"^[A-Za-z" + ''.join(GREEK) + r"][A-Za-z0-9_" + ''.join(SUBS) + r"]{0,3}\((?:[^()]|\([^()]*\))*\)")
LEADQ, TRAILP = "'\"“‘", ".,;:?!'\"”’"

def _letters_ok(core):
    for w in re.findall(r"[A-Za-z]+", core):
        if re.fullmatch(r"[a-z]?[A-Z]{1,3}", w): continue
        if len(w) <= 2 or w in FUNCS or w in ROMAN or w in UNITS or (w.isupper() and len(w) <= 3):
            continue
        # sub/superscript words like v_out / x_new are fine
        if re.search(r"_" + w + r"\b", core):
            continue
        return False
    return True

def _strong(core):
    if any(c in STRONG_CH for c in core): return True
    if any(w in FUNCS for w in re.findall(r"[A-Za-z]+", core)): return True
    if FCALL.match(core): return True
    if re.search(r"[A-Za-z0-9)]/[A-Za-z(√]", core): return True
    if re.fullmatch(r"[A-Za-z]", core) is None and re.search(r"\d[eE]\^", core): return True
    return False

def _word_kind(w):
    core = w.strip(LEADQ).rstrip(TRAILP)
    if not core or core in STOP or core.lstrip('([') in STOP: return None
    if not MATHY.match(core) or not _letters_ok(core): return None
    if re.fullmatch(r"[A-Za-z]{3,}", core) and core not in FUNCS | ROMAN | UNITS and not re.fullmatch(r"[a-z]?[A-Z]{1,3}", core): return None
    return 'S' if _strong(core) else 'W'

def _balanced_inner(s, i):
    """s[i] == '(' -> index of matching ')' (or len-1)"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '(': d += 1
        elif s[j] == ')':
            d -= 1
            if d == 0: return j
    return len(s) - 1

def _tex(s):
    """convert one math run (plain/Unicode) to LaTeX (no delimiters)"""
    out = []
    i = 0
    def emit(t):
        if out and re.search(r"\\[A-Za-z]+$", out[-1]) and re.match(r"[A-Za-z0-9]", t): out.append(' ')
        out.append(t)
    while i < len(s):
        c = s[i]
        if c in SUPS:
            j = i
            while j < len(s) and s[j] in SUPS: j += 1
            emit('^{' + ''.join(SUPS[x] for x in s[i:j]) + '}'); i = j; continue
        if c in SUBS:
            j = i
            while j < len(s) and s[j] in SUBS: j += 1
            sub = ''.join(SUBS[x] for x in s[i:j])
            emit('_{' + (r'\mathrm{%s}' % sub if len(sub) > 1 and sub.isalpha() else sub) + '}'); i = j; continue
        if c == '_':
            m = re.match(r"_([A-Z]+[0-9]*(?![a-z])|[A-Z]?[a-z0-9]+|" + '|'.join(GREEK) + ")", s[i:])
            if m:
                sub = m.group(1)
                if sub in GREEK: sub = GREEK[sub]
                elif len(sub) > 1 and sub.isalpha(): sub = r'\mathrm{%s}' % sub
                emit('_{' + sub + '}'); i += len(m.group(0)); continue
            emit(r'\_'); i += 1; continue
        if c == '^':
            if i + 1 < len(s) and s[i + 1] == '(':
                j = _balanced_inner(s, i + 1)
                emit('^{' + _tex(s[i + 2:j]) + '}'); i = j + 1; continue
            m = re.match(r"\^([-−]?[A-Za-z0-9.]+)", s[i:])
            if m: emit('^{' + _tex(m.group(1)) + '}'); i += len(m.group(0)); continue
            if i + 1 < len(s) and s[i + 1] != ' ': emit('^{' + _tex(s[i + 1]) + '}'); i += 2; continue
            emit(r'\hat{}'); i += 1; continue
        if c == '√':
            if i + 1 < len(s) and s[i + 1] == '(':
                j = _balanced_inner(s, i + 1)
                emit(r'\sqrt{' + _tex(s[i + 2:j]) + '}'); i = j + 1; continue
            m = re.match(r"√([A-Za-z0-9." + ''.join(GREEK) + r"]+)", s[i:])
            if m: emit(r'\sqrt{' + _tex(m.group(1)) + '}'); i += len(m.group(0)); continue
            emit(r'\surd'); i += 1; continue
        if c == 'µ':
            m = re.match(r"µ([A-Za-z]*)", s[i:])
            emit(r'\mu' + (r'\mathrm{%s}' % m.group(1) if m.group(1) else '')); i += len(m.group(0)); continue
        if c in GREEK: emit(GREEK[c]); i += 1; continue
        if c in OPS: emit(OPS[c]); i += 1; continue
        if c.isalpha() and c.isascii():
            m = re.match(r"[A-Za-z]+", s[i:]); w = m.group(0)
            prev = s[:i].rstrip()
            after_num = bool(re.search(r"[\d)°]\s+$", s[:i])) or bool(re.search(r"\d$", s[:i]) and w in UNITS and len(w) > 1)
            after_unit = bool(re.search(r"(\\mathrm\{[^}]*\}|\\Omega)/$", ''.join(out))) or bool(re.search(r"(\\mathrm\{[^}]*\})/\\sqrt\{$", ''.join(out)))
            if w in FUNCS and w != 'arg': emit('\\' + w)
            elif w in ROMAN or w == 'arg': emit(r'\mathrm{%s}' % w)
            elif (after_num or after_unit) and w in UNITS: emit(r'\mathrm{%s}' % w)
            elif len(w) >= 3 and not (w.isupper() and len(w) <= 3) and not re.fullmatch(r"[a-z][A-Z]{1,3}", w): emit(r'\mathrm{%s}' % w)
            elif w in ('dB', 'Hz'): emit(r'\mathrm{%s}' % w)
            else: emit(w)
            i += len(w); continue
        if c == ' ':
            j = i
            while j < len(s) and s[j] == ' ': j += 1
            a, b = s[:i], s[j:]
            if re.search(r"\\(sin|cos|tan|log|ln|exp)$", ''.join(out)):
                emit(' '); i = j; continue
            if re.search(r"[\w)\]°" + ''.join(SUPS) + ''.join(SUBS) + "]$", a) and re.match(r"[\w(µ" + ''.join(GREEK) + "]", b) \
                    and not re.match(r"(and|or)\b", b):
                emit(r'\ ')
            i = j; continue
        if c in '{}': emit('\\' + c); i += 1; continue
        if c == '%': emit(r'\%'); i += 1; continue
        if c == ',' and re.match(r",\d{3}(?!\d)", s[i:]) and re.search(r"\d$", s[:i]): emit('{,}'); i += 1; continue
        emit(c); i += 1
    return ''.join(out)

def _convert_plain(text):
    # tokens: words and the whitespace between them (newlines kept)
    parts = re.split(r"( +|\n)", text)
    words = [(p, _word_kind(p) if p.strip() and p != '\n' else None) for p in parts]
    out = []
    i = 0
    n = len(words)
    while i < n:
        p, k = words[i]
        if k is None:
            out.append(p); i += 1; continue
        # extend a run over words of kind S/W separated by single spaces
        j = i; last = i; has_s = False
        while j < n:
            pj, kj = words[j]
            if kj is not None:
                last = j; has_s |= kj == 'S'; j += 1
                if re.search(r"[.,;:?!]['\")\]]*$", pj) and not re.search(r"\d\.$", pj.rstrip(")'\"]")) : break
                if j < n and words[j][0].strip() == '' and words[j][0] != '\n' and j + 1 < n and words[j + 1][1] is not None:
                    j += 1; continue
                break
            break
        seg_words = [w for w, kk in words[i:last + 1]]
        # trim weak edge words that are lone single letters/numbers-without-strong (keep run tight)
        if not has_s:
            out.append(''.join(seg_words)); i = last + 1; continue
        run = ''.join(seg_words)
        pre = ''
        while run and run[0] in LEADQ: pre += run[0]; run = run[1:]
        suf = ''
        while True:
            changed = False
            while run and run[-1] in TRAILP: suf = run[-1] + suf; run = run[:-1]; changed = True
            if run.endswith(')') and run.count(')') > run.count('('): suf = ')' + suf; run = run[:-1]; changed = True
            if run.endswith(']') and run.count(']') > run.count('['): suf = ']' + suf; run = run[:-1]; changed = True
            if not changed: break
        while run.startswith('(') and run.count('(') > run.count(')'): pre += '('; run = run[1:]
        while run.startswith('[') and run.count('[') > run.count(']'): pre += '['; run = run[1:]
        # trailing weak unit-less fragments are fine; wrap
        if run:
            out.append(pre + r'\(' + _tex(run) + r'\)' + suf)
        else:
            out.append(pre + suf)
        i = last + 1
    return ''.join(out)

def latexify(text):
    if not isinstance(text, str) or not text: return text
    # leave existing math alone
    pieces = re.split(r"(\\\(.*?\\\)|\\\[.*?\\\])", text, flags=re.S)
    return ''.join(p if p.startswith(('\\(', '\\[')) else _convert_plain(p) for p in pieces)

if __name__ == '__main__':
    import sys
    for t in sys.argv[1:]: print(latexify(t))
