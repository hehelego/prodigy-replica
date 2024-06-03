# suggested edits for the first draft of our slides show

Page 2: the fonts in the screenshot of the knuth-yao dice program is too small.
We may simply scale up the image and ignore the pairing right braces.


Page 3: the title should be "Verifying Equivalence of Probabilistic Programs via **PGF transformer semantics**"

Page 4: change "Content:" to "Contents"

"Probability Program" should be "Probabilistic Programming"


I think title "Background--Introduction to Probability Program" is not a proper summary of what we want to convey in this section.
The contents in this section talks about 3 ideas:

1. The wide use of randomized algorithms and statistical inference give rise to probabilistic programming, which makes working with randomness easy. (the rise of probabilistic programming)
2. There is a trust and reliability issue, that is, how can we know for sure that a the probabilistic behavior of a program is exactly what we want. (the need to verify probabilistic programs)
3. In security-critical settings such as cryptography and cyber-physics systems, one want to fully characterize the behavior of a program, rendering existing techniques insufficient. (the necessity of obtaining full distribution information)

These three ideas give rise to our research problem which is verifying equivalence of probabilistic programs.

Page 6: we shall give more than one application. Suggested ones (besides Monte-Carlo based rendering): build regression models, implementing clustering algorithms, and molecular dynamics simulation.

Page 7: we shall replace the example program with a more realistic one.
I suggest grabbing an example from here: https://hakaru-dev.github.io/examples/
It is not written in pGCL/ReDiP, but perfectly demonstrate what probabilistic programming can do.


Page 12: rename "input 1" and "input 2" to "program to be checked" and "specification program", respectively. (specification is a terminology in program verification, a spec is a formal description of the expected behaviors)

Page 12: replace input 2 program with this one below.

```
nat s;
nat die;

s := 3;
die := unif(1,3);
```

Page 12: "PGF mapping" or PGF transformers is the underlying things. The block should be call a verifier or a checker.

Page 12: The light green color doesn't quite fit with the overall style of this page.
Also the white text are somewhat unclear against a green background.

Page 14: A few things to note:

- A GF is a formal power series.
- A formal power series may not have closed-form (which is the common case unsurprisingly)
- Typo: "Simplifeis" should be "Simplifies"
- Manipulation and operation are synonymous of each other in this context.
- GFs do not enable easier extraction themselves.

Suggested edit:

- encoding sequences with formal power series.
- sequence manipulation is algebraic operations on GFs
- pattern matching with well-known closed-forms.

(also include this table)

| closed-form  | sequence          |
|--------------|-------------------|
| $(1-ax)^b$   | $\binom{b}{n}a^n$ |
| $(1-x)^{-2}$ | $n+1$             |
| $x^k$        | $[n=k]$           |
| $e^{kx}$     | $k^n/n!$          |


Page 17: demonstrating PGFs. To be refined. We will show these stuffs

- $g_X(t) = \mathbb{E}(t^X) = \sum_{0\leq n} \Pr(X=i) t^X$, $g_{X,Y}(s,t) = \mathbb{E}(s^X t^Y)$, and so on.
- $\partial^n/\partial x^n g(1) = \mathbb{E}(X(X-1)\cdots (X-n+1))$ evaluating mean/variance/skewness/kurtosis
- $Z=X+Y$, $\mathbb{E}(t^Z) = \mathbb{E}(t^X t^Y) = \mathbb{E}(t^X) \mathbb{E}(t^Y)$ for independent $X,Y$

Also I want to put an example of "random stopping sum", that is $S=\sum_{i=1}^N X_i$ where Xs are iid with PGF $g_X$ and $N$ is another independent random variable, then $g_S(t) = g_N(g_X(t))$
I will give a proof later.

Page 18: This is still in the "Theory" section.
Also we forget to introduce pGCL to the audience.
I will use probably two images to illustrate the syntax of pGCL.

-----

Page 18: Add this background knowledge line "the PGF transformer semantics is a **denotational semantics** that captures the set of program states with a domain of mathematical objects and program execution with morphisms defined on that domain".

Add this line: "program state $(x,y)$ encoded as PGF $g=\mathbb{E}(s^X t^Y)$"

The re-articulated ReDiP PGF transformer semantics. (This is what I used in the re-implementation)

- `x := n` $g\mapsto g[t/1] s^n$
  $$
  \mathbb{E}(s^X t^Y) \to s^n \mathbb{E}(1^X t^Y) = s^n \mathbb{E}(t^Y) = \mathbb{E}(s^n t^Y)
  $$
- `x := x+n` $g\mapsto g s^n$
  $$
  \mathbb{E}(s^X t^Y) \to s^n \mathbb{E}(s^X t^Y) = \mathbb{E}(s^{X+n} t^Y)
  $$
- `x := x-1` $g\mapsto (g-g[s/0])s^{-1} + g[s/0]$ we have a special case of $X=0$ because 0 is already the smallest natural number.
  $$
  \mathbb{E}(s^X t^Y) \to s^{-1}\mathbb{E}(s^X t^Y) = \mathbb{E}(s^{X-1} t^Y)
  $$
- `x := x+y` $g\mapsto g[t/st]$ 
  $$
  \mathbb{E}(s^X t^Y) \to \mathbb{E}(s^X (st)^Y) = \mathbb{E}(s^{X+Y} t^Y)
  $$
- `x := D` samples from distribution $D$ with PGF $[D](r)$ $g\mapsto g[t/1] \cdot [D](t)$
  $$
  \mathbb{E}(s^X t^Y) \to \mathbb{E}(s^D) \mathbb{E}(1^X t^Y) = \mathbb{E}(s^D t^Y)
  $$
- `x := iid(D,y)` random stopping sum (recall, PGF of random stopping sum) $g\mapsto g[s/1][t/t[D](s)]$
  $$
  \mathbb{E}(s^X t^Y) \to \mathbb{E}(1^X t^Y {([D](s))}^Y) = \sum_{0\leq m} {([D](s))}^m t^m
  $$
- `P;Q` sequential composition, trivial.
- `if(x<n){P}else{Q}` somewhat trivial...

We can talk more about the syntax and semantics: at least I have a few extension coded.

- choice operator: `P [prob] Q`: execute P with probability `prob` otherwise run Q.
- finite loop: `loop(n) P`: essentially `P;P;P ... P` n folds.
- `x := x - n` arbitrary subtraction: `loop(n) {x := x-1}`
- compositional branching condition:
    - `if(p and q){P}else{Q}` is equivalent to `if(p){ if(q){P}else{Q} }else{Q}`
    - `if(p or q){P}else{Q}` is equivalent to `if(p){P}else{ if(q){P}else{Q} }`
    - `if(not p){P}else{Q}` is equivalent to `if(p){Q}else{P}`
- complex comparison:
    - `if(x<=n){P}else{Q}` is equivalent to `if(x<n+1){P}else{Q}`
    - `if(x>n){P}else{Q}` is equivalent to `if(x<=n){Q}else{P}`
    - `if(x>=n){P}else{Q}` is equivalent to `if(x<n){Q}else{P}`
    - `if(x==n){P}else{Q}` is equivalent to `if(x<=n and x>=n){P}else{Q}`
    - `if(x!=n){P}else{Q}` is equivalent to `if(x==n){Q}else{P}`


Page 23 Fixed point induction.

``` while(cond) body;
```

is equivalent to the following infinite expansion

```
if(cond){
    body;
    if(cond){
        body;
        if(cond){
            body;
            ...
             ...
              ...
               ...
        }
    }
}
```

which is characterized by the least fixed point of

```
Q => if(cond){body; Q}
```

We also need an example.

Page 24: This page should talk about the closed form preservation of a ReDiP program. So we essentially have to do induction on the syntax.
Page 25: Linearity is the most important one, please highlight this one and make others dim. We shall give proof of linearity.

-----

Experiments: 


-----

Need to revise the discussion section.

We shall put ideation and support of it on the slides show, not only the digest of ideas.
Work on it later.




