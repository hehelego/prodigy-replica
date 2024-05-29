from probably.pgcl import CheckFail, parse_pgcl, Program
from argparse import ArgumentParser
import time
from impl.semantics import get_map, get_delta, transform


def check(prog1: Program, prog2: Program):
    vars = set(prog1.variables.keys())
    assert vars == set(prog2.variables.keys())
    params = set(prog1.parameters.keys()).union(prog2.parameters.keys())

    vars, params = sorted(vars), sorted(params)
    print(f'detected vars {vars} params {params}')

    xs, us, vmap, pmap = get_map(vars, params)
    delta = get_delta(xs, us)

    print('computing transform for the input program')
    g1 = transform(vmap, pmap, xs, prog1.instructions, delta)
    print(g1.simplify())

    print('computing transform for the spec')
    g2 = transform(vmap, pmap, xs, prog2.instructions, delta)
    print(g2.simplify())

    print('comparing results')
    print((g1 - g2).simplify())
    return (g1 - g2).simplify() == 0


def main():
    parser = ArgumentParser('equiv', 'equiv <p1.pgcl> <p2.pgcl>',
                            'check equivalence of two ReDiP programs')
    parser.add_argument('prog1', help='path to a ReDiP program')
    parser.add_argument('prog2', help='path to a ReDiP program')
    args = parser.parse_args()
    prog1, prog2 = None, None
    with open(args.prog1) as f:
        prog1 = parse_pgcl(f.read())
        if isinstance(prog1, CheckFail):
            print('failed to compile the program:', prog1)
            exit(1)
    with open(args.prog2) as f:
        prog2 = parse_pgcl(f.read())
        if isinstance(prog2, CheckFail):
            print('failed to compile the spec:', prog2)
            exit(1)

    start = time.perf_counter()
    res = check(prog1, prog2)
    duration = time.perf_counter() - start
    print(rf'check result: {res} within {duration} seconds.')


if __name__ == "__main__":
    main()
