from probably.pgcl.ast import Expr, BernoulliExpr, Binop, BinopExpr, Unop, UnopExpr, DUniformExpr, GeometricExpr, PoissonExpr, IidSampleExpr, VarExpr, BoolLitExpr, NatLitExpr, RealLitExpr, Var, Instr, SkipInstr, WhileInstr, IfInstr, AsgnInstr, ChoiceInstr, LoopInstr
from typing import Callable, Iterable, Any
import numpy

rng = numpy.random.default_rng()

SExpr = Any


def eval_expr(expr: Expr, map: dict[Var, SExpr]) -> SExpr:
    eval = lambda e: eval_expr(e, map)
    if isinstance(expr, RealLitExpr):
        p = expr.to_fraction()
        return p.numerator / p.denominator
    elif isinstance(expr, NatLitExpr):
        return expr.value
    elif isinstance(expr, BoolLitExpr):
        return expr.value
    elif isinstance(expr, VarExpr):
        return map[expr.var]
    elif isinstance(expr, UnopExpr):
        op = expr.operator
        x = eval(expr.expr)
        match op:
            case Unop.NEG:
                return not bool(x)
            case Unop.IVERSON:
                return int(bool(x))
    elif isinstance(expr, BinopExpr):
        op, l, r = expr.operator, expr.lhs, expr.rhs
        l, r = eval(l), eval(r)
        match op:
        # part 1
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
            # part 2
            case Binop.EQ:
                return l == r
            case Binop.LT:
                return l < r
            case Binop.LEQ:
                return l <= r
            case Binop.GT:
                return l > r
            case Binop.GEQ:
                return l >= r
            # part 3
            case Binop.OR:
                return bool(l) or bool(r)
            case Binop.AND:
                return bool(l) and bool(r)
        raise NotImplementedError(rf'unsupported binary operator: {op}')
    elif isinstance(expr, IidSampleExpr):
        n = int(eval(expr.variable))
        dist = expr.sampling_dist
        return sum(eval(dist) for _ in range(n))
    elif isinstance(expr,
                    (BernoulliExpr, DUniformExpr, GeometricExpr, PoissonExpr)):
        if isinstance(expr, BernoulliExpr):
            p = eval(expr.param)
            return rng.binomial(1, p)
        elif isinstance(expr, DUniformExpr):
            l, r = int(eval(expr.start)), int(eval(expr.end))
            return rng.choice(range(l, r + 1))
        elif isinstance(expr, GeometricExpr):
            p = eval(expr.param)
            return rng.geometric(p)
        else:
            p = eval(expr.param)
            return rng.poisson(p)

    raise NotImplementedError(rf'cannot evaluate: {expr}')


def run(map: dict[Var, SExpr], prog: list[Instr]):

    def general(inst: Instr):
        funcs = [
            (SkipInstr, run_skip),
            (AsgnInstr, run_asgn),
            (WhileInstr, run_while),
            (IfInstr, run_if),
            (ChoiceInstr, run_choice),
            (LoopInstr, run_loop),
            # (TickInstr, None),
            # (ObserveInstr, None),
            # (ProbabilityQueryInstr, None),
            # (ExpectationInstr, None),
            # (PlotInstr, None),
            # (PrintInstr, None),
            # (OptimizationQuery, None),
        ]
        for (instrType, run_func) in funcs:
            if isinstance(inst, instrType):
                assert run_func is not None
                run_func(inst)

    def seq(instrs: list[Instr]):
        for instr in instrs:
            general(instr)

    def run_skip(_: SkipInstr):
        return

    def run_asgn(inst: AsgnInstr):
        dest, expr = inst.lhs, inst.rhs
        map[dest] = eval_expr(expr, map)

    def run_if(inst: IfInstr):
        cond, br1, br0 = inst.cond, inst.true, inst.false
        if eval_expr(cond, map):
            seq(br1)
        else:
            seq(br0)

    def run_while(inst: WhileInstr):
        while eval_expr(inst.cond, map):
            seq(inst.body)

    def run_choice(inst: ChoiceInstr):
        p = eval_expr(inst.prob, map)
        br = rng.choice((0,1), p=(p, 1 - p))
        seq(inst.lhs if br == 0 else inst.rhs)

    def run_loop(inst: LoopInstr):
        for _ in range(inst.iterations.value):
            seq(inst.body)

    seq(prog)
