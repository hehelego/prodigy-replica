from probably.pgcl import CheckFail, compiler
from probably.pgcl.ast import Expr, BernoulliExpr, Binop, BinopExpr, Unop, UnopExpr, DUniformExpr, GeometricExpr, PoissonExpr, IidSampleExpr, VarExpr, NatLitExpr, RealLitExpr, Var, Instr, SkipInstr, WhileInstr, IfInstr, AsgnInstr, ChoiceInstr, LoopInstr
# from probably.pgcl.ast import TickInstr, ObserveInstr, ProbabilityQueryInstr, ExpectationInstr, PlotInstr, PrintInstr, OptimizationQuery
import sympy
from typing import Callable, Iterable, Any

SExpr = Any
TransFunc = Callable[[Instr, SExpr], SExpr]


def get_map(
    vars: Iterable[Var],
    params: Iterable[Var],
) -> tuple[list[SExpr], list[SExpr], dict[Var, int], dict[Var, SExpr]]:
    '''
    (vars, params) -> (X, U, variable map, parameter map)
    X: E(t^X) the indeterminate t of PGF
    U: (1-XU)^(-1) for constructing the dirac delta SOP
    P: parameters

    parameters does not get involved in the dirac delta,
    but are simply undetermined parameter variables
    '''
    vmap = dict((v, i) for (i, v) in enumerate(vars))
    dim = len(vmap)
    xu = sympy.symbols(f'x:{dim} u:{dim}')
    xs, us = xu[:dim], xu[dim:]

    pmap = dict((v, sympy.symbols(f'p{i}')) for (i, v) in enumerate(params))
    return xs, us, vmap, pmap


def get_delta(xs: list[SExpr], us: list[SExpr]) -> SExpr:
    f = sympy.Integer(1)
    for (x, u) in zip(xs, us):
        f *= (1 - x * u)
    return f**(-1)


t = sympy.symbols('t')


def bernoulli_pgf(p) -> SExpr:
    return sympy.Integer(1) - p + p * t


def unif_pgf(l, r) -> SExpr:
    # unif(l,r) = l + unif(0, r-l)
    one = sympy.Integer(1)
    n = r - l + one
    return t**l / n * (one - t**n) / (one - t)


def geom_pgf(p) -> SExpr:
    return (sympy.Integer(1) - p) / (sympy.Integer(1) - p * t)


def pois_pgf(s) -> SExpr:
    return sympy.exp(s * (t - sympy.Integer(1)))


def eval_expr(expr: Expr, pmap: dict[Var, SExpr]) -> SExpr:
    if isinstance(expr, RealLitExpr):
        p = expr.to_fraction()
        return sympy.Rational(p.numerator, p.denominator)
    elif isinstance(expr, NatLitExpr):
        return sympy.Integer(expr.value)
    elif isinstance(expr, BinopExpr):
        op, l, r = expr.operator, expr.lhs, expr.rhs
        l, r = eval_expr(l, pmap), eval_expr(r, pmap)
        match op:
            case Binop.PLUS:
                return l + r
            case Binop.MINUS:
                return l - r
            case Binop.TIMES:
                return l * r
            case Binop.DIVIDE:
                return l / r
            case Binop.POWER:
                return l**r
    elif isinstance(expr, VarExpr):
        return pmap[expr.var]
    raise NotImplementedError(rf'cannot evaluate: {expr}')


def get_pgf(
    dexpr: BernoulliExpr | DUniformExpr | GeometricExpr | PoissonExpr,
    pmap: dict[Var, SExpr],
) -> SExpr:
    if isinstance(dexpr, BernoulliExpr):
        prob = eval_expr(dexpr.param, pmap)
        return bernoulli_pgf(prob).simplify()
    elif isinstance(dexpr, DUniformExpr):
        l, r = eval_expr(dexpr.start, pmap), eval_expr(dexpr.end, pmap)
        return unif_pgf(l, r).simplify()
    elif isinstance(dexpr, GeometricExpr):
        prob = eval_expr(dexpr.param, pmap)
        return geom_pgf(prob).simplify()
    else:
        rate = eval_expr(dexpr.param, pmap)
        return pois_pgf(rate).simplify()


def pgf_leq(g: SExpr, x: sympy.Symbol, n: int) -> SExpr:
    return sum(g.taylor_term(i, x) for i in range(n + 1)).simplify()


def transform(
    vmap: dict[Var, int],
    pmap: dict[Var, int],
    xs: list[SExpr],
    prog: list[Instr],
    g: SExpr,
) -> SExpr:

    def general(inst: Instr, g: SExpr) -> SExpr:
        funcs = [
            (SkipInstr, skip_trans),
            (AsgnInstr, asgn_trans),
            (WhileInstr, while_trans),
            (IfInstr, if_trans),
            (ChoiceInstr, choice_trans),
            (LoopInstr, loop_trans),
            # (TickInstr, None),
            # (ObserveInstr, None),
            # (ProbabilityQueryInstr, None),
            # (ExpectationInstr, None),
            # (PlotInstr, None),
            # (PrintInstr, None),
            # (OptimizationQuery, None),
        ]
        for (instrType, trans) in funcs:
            if isinstance(inst, instrType):
                assert trans is not None
                g = trans(inst, g)
        return g.simplify()

    def seq(instrs: list[Instr], g: SExpr) -> SExpr:
        for instr in instrs:
            g = general(instr, g).simplify()
        return g

    def skip_trans(_: SkipInstr, g: SExpr) -> SExpr:
        return g

    def asgn_trans(inst: AsgnInstr, g: SExpr) -> SExpr:
        '''
        we currently only handle these cases:
        x := (const)
        x := sample-distribution
        x := iid
        x := x + (const)
        x := x - (const)
        x := x + (var)
        '''
        dest, expr = inst.lhs, inst.rhs
        x = xs[vmap[dest]]

        if isinstance(expr, NatLitExpr):
            n = expr.value
            g = g.limit(x, 1) * x**n
        elif isinstance(expr, (
                BernoulliExpr,
                DUniformExpr,
                GeometricExpr,
                PoissonExpr,
        )):
            pgf = get_pgf(expr, pmap)
            g = g.limit(x, 1) * pgf.subs(t, x)
        elif isinstance(expr, IidSampleExpr):
            dist = expr.sampling_dist
            y = xs[vmap[expr.variable.var]]
            assert isinstance(dist, (
                BernoulliExpr,
                DUniformExpr,
                GeometricExpr,
                PoissonExpr,
            ))
            pgf = get_pgf(dist, pmap).subs(t, x)
            g = g.limit(x, 1).subs(y, y * pgf)
        elif isinstance(expr, BinopExpr):
            op = expr.operator
            assert isinstance(expr.lhs, VarExpr) and expr.lhs.var == dest
            if isinstance(expr.rhs, NatLitExpr):
                assert op == Binop.PLUS or op == Binop.MINUS
                if op == Binop.PLUS:
                    # E(t^X) => E(t^(X+1)) = E(t^X * t) = t E(t^X)
                    g = g * x**expr.rhs.value
                else:
                    for _ in range(expr.rhs.value):
                        # E(t^X) => E(t^(X-1)) = E(t^X)/t
                        # except for the constant term (X=0)
                        g = g.limit(x, 0) + (g - g.limit(x, 0)) / x
            elif isinstance(expr.rhs, VarExpr):
                assert op == Binop.PLUS or op == Binop.MINUS
                y = xs[vmap[expr.rhs.var]]
                if op == Binop.PLUS:
                    # E(t^X s^Y) => E(t^(X+Y) s^Y) = E(t^X s^Y t^Y) = E(t^X (st)^Y)
                    g = g.subs(y, x * y)
                else:
                    # E(t^X s^Y) => E(t^(X-Y) s^Y) = E(t^X s^(-Y) t^Y) = E(t^X (t/s)^Y)
                    g = g.subs(y, y / x)
            else:
                raise NotImplementedError(
                    f'unsupported assignment RHS: {expr}')
        else:
            raise NotImplementedError(f'unsupported assignment RHS: {expr}')
        return g.simplify()

    def if_trans(inst: IfInstr, g: SExpr) -> SExpr:
        # NOTE: only partial support for ReDiP syntax
        cond, br1, br0 = inst.cond, inst.true, inst.false
        if isinstance(cond, BinopExpr):
            op = cond.operator
            if op == Binop.AND:
                # if(p and q) P else Q <=> if(p) {if(q) P else Q} else Q
                inner = [IfInstr(cond.rhs, br1, br0)]
                g = if_trans(IfInstr(cond.lhs, inner, br0), g)
            elif op == Binop.OR:
                # if(p or q) P else Q <=> if(p) P else {if(q) P else Q}
                inner = [IfInstr(cond.rhs, br1, br0)]
                g = if_trans(IfInstr(cond.lhs, br1, inner), g)
            else:
                rev_op = {
                    Binop.LEQ: Binop.GEQ,
                    Binop.LT: Binop.GT,
                    Binop.GEQ: Binop.LEQ,
                    Binop.GT: Binop.LT,
                    Binop.EQ: Binop.EQ
                }
                assert op in rev_op
                if isinstance(cond.lhs, VarExpr) and isinstance(
                        cond.rhs, NatLitExpr):
                    x = xs[vmap[cond.lhs.var]]
                    n = cond.rhs.value
                    match op:
                        case Binop.LEQ:  # true: leq, false: gt
                            h = pgf_leq(g, x, n)
                            g = seq(br1, h) + seq(br0, g - h)
                        case Binop.LT:  # true: lt, false: geq
                            h = pgf_leq(g, x, n - 1)
                            g = seq(br1, h) + seq(br0, g - h)
                        case Binop.GEQ:  # true: geq, false: lt
                            h = pgf_leq(g, x, n - 1)
                            g = seq(br1, g - h) + seq(br0, h)
                        case Binop.GT:  # true: gt, false: leq
                            h = pgf_leq(g, x, n)
                            g = seq(br1, g - h) + seq(br0, h)
                        case Binop.EQ:  # true: eq, false: neq
                            h = g.taylor_term(n, x)
                            g = seq(br1, h) + seq(br0, g - h)
                elif isinstance(cond.rhs, VarExpr) and isinstance(
                        cond.lhs, NatLitExpr):
                    swapped_cond = BinopExpr(rev_op[op], cond.rhs, cond.lhs)
                    swapped = IfInstr(swapped_cond, br0, br1)
                    g = if_trans(swapped, g)
                else:
                    raise NotImplementedError(
                        rf'unsupported if condition: {cond}')
        elif isinstance(cond, UnopExpr):
            # if (not phi) P else Q <=> if (phi) Q else P
            assert cond.operator == Unop.NEG
            g = if_trans(IfInstr(cond, br0, br1), g)
        else:
            raise NotImplementedError(rf'unsupported if condition: {cond}')
        return g.simplify()

    def while_trans(inst: WhileInstr, g: SExpr) -> SExpr:
        inv_file = input('invariant program:').strip()
        inv_prog = None
        with open(inv_file) as f:
            inv_prog = compiler.compile_pgcl(f.read())
            if isinstance(inv_prog, CheckFail):
                raise ValueError('failed to compile the invariant program:')
        body = inst.body + inv_prog.instructions
        unfolded_prog = IfInstr(inst.cond, body, [])
        return if_trans(unfolded_prog, g)

    def choice_trans(inst: ChoiceInstr, g: SExpr) -> SExpr:
        p = eval_expr(inst.prob, pmap)
        g_on = p * seq(inst.lhs, g)
        g_off = (sympy.Integer(1) - p) * seq(inst.rhs, g)
        return (g_on + g_off).simplify()

    def loop_trans(inst: LoopInstr, g: SExpr) -> SExpr:
        for _ in range(inst.iterations.value):
            g = seq(inst.body, g).simplify()
        return g

    return seq(prog, g)
