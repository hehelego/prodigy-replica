from probably.pgcl import CheckFail, compiler
from argparse import ArgumentParser
import time
from copy import deepcopy
from impl.simulation import run


def main():
    parser = ArgumentParser('simulate', 'simulate [-n times] <prog.pgcl> {args}',
                            'run simulation of a ReDiP programs many times')
    parser.add_argument('-n', default=100)
    parser.add_argument('prog', help='path to ReDiP program')
    parser.add_argument('args', help='stringified diction of var/param map')
    args = parser.parse_args()

    print(args)
    n = int(args.n)
    path = str(args.prog)
    map = eval(args.args)

    prog = None
    with open(path) as f:
        prog = compiler.compile_pgcl(f.read())
        if isinstance(prog, CheckFail):
            print('failed to compile the program:', prog)
            exit(1)

    start = time.perf_counter()
    for _ in range(n):
        m = deepcopy(map)
        run(m, prog.instructions)
        print(m)
    duration = time.perf_counter() - start
    print(rf'simulation {n} runs takes {duration} seconds.')


if __name__ == "__main__":
    main()
