var('N U C V')

delta = (1-N*U)^(-1) * (1-C*V)^(-1)

g0 = delta
g1 = g0 - g0.subs(N=0)
g2 = g1 * N^(-1)
g3 = g1 * C
g4 = (g2 + g3) / 2
g5 = g4.subs(N=N * (2-C)^(-1))
g6 = g5.subs(N=1)
g7 = g6 + g0.subs(N=0)

h0 = delta
h1 = (1-C*V)^(-1) * (2-C) * (2-C-N*U)^(-1)
h2 = h1.subs(N=1)

res = bool(g7 == h2)
print(res)
