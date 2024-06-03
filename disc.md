
### limitation 1: do we really need full distribution information

The authors of the PRODIGY paper argues that techniques for evaluating probability of events and moments of variables are sometimes insufficient since they let-go tiny perturbations which may leave vulnerabilities undetected.
The argument is not examplified by concrete examples nor supportted by quantitative calculations, which puts its validity in doubt.

For example, consider two probabilistic programs that output $X_1$ and $X_2$ respectively.
We can symbolically evaluate and compare $D(X_1) - D(X_2)$ with $0$ to check whether $X_1$ and $X_2$ have the same distribution.

$$
D(X) = (\mathbb{E}(X^k); \Pr(X>\mathbb{E}X/k)) \quad k=1,2,3\ldots 10
$$

We deem that such method is good enough even in security critical scenarios.

One future research may compare the suitability of PGF based techniques and statistics based technique in the verification of real-world programs.

### extension 1: what if we are interested in only a subset of valid inputs

The Leibniz equivalence (indistinguishable for arbitrary input $f=g$ iff $\forall x. f(x)=g(x)$).
We Often just need to check $\forall x \in S . f(x) = g(x)$.

One of such scenario is that in a performance critical program, we may be able to apply certain optimization whose correctness can only be proved in a certain context.
Say that in one branch, we know that the program state $x$ satisfies $P(x)$. We may want to check $\forall x . P(x) \to (f(x)=g(x))$.

In a flexible programming language, such equivalence checking can be formulated readily:

```haskell
-- input: x
-- prog: a program that handles input x such that P(x) is true
-- cond: the P(x) predicate
restrict :: (a -> Bool) -> (a -> b) -> (a -> Maybe b)
restrict cond prog input = if cond input
                           then Just (prog input)
                           else Nothing

-- check equivalence: (restrict p f) (restrict p g)
```

However, ReDiP imposes rather strict constraints on guards, making some predicate not expressible.

How can we lift the rectangular constraint is a valuable future research direction.

### extension 2: incorporating real-valued variable using CF/MGF

PGF is essentially the Z transform of the joint PMF.
To enable support for continuous random variables, one may try replacing PGFs with CFs, which are Laplace transform of the joint PDF.

However, introducing Laplance transform may break the closed-form preservation property of ReDiP programs (that is, a rational PGF get transformed into another rational PGF),
potentially making equivalence checking undecidable.

Future works may explore effective and efficient way to add support for continuous random variables.

### extension 3: checking equivalence of reactive programs

Cryptographic systems and automated driving systems are often open-ended reactive system, meaning that they never halt (or terminate).

PRODIGY, however, can only tackle UAST programs, so it is incapable of verifying reactive systems.
For example, PRODIGY will not able to check the equivalence of the following two programs:

Program 1

```
OnInputSymbol(() => {
    alpha1, alpha2 = iid(std_normal, 2)
    x[n] = input();
    output(alpha1 * (x[n-1] - mu) + alpha2 * (x[n-2] - mu)^2);
    mu = (mu * n + x[n]) / (n + 1);
    n += 1;
})
```

Program 2

```
OnInputSymbol(() => {
    alpha1, alpha2 = iid(std_normal, 2)
    output(alpha1 * (x[n-1] - mu) + alpha2 * (x[n-2]^2 - 2*x[n]*mu + mu^2));
    x[n] = input();
    n += 1
    mu = (mu * (n-1) + x[n]) / n
})
```


It remains to be explored how to formulate the PGF transformer semantics for reactive systems.

### Certifying equivalence of ReDiP programs:
As the experiments suggests, verifying ReDiP programs can be computationally, rendering this technique unsuitable for IoT devices, which typically are not equipped with high performance processors. One possible work around is to trade space with time.
(1) make program verifier generate a machine-checkable proof instead of simply the true/false answer
(2) ship the probabilistic program and the proof together to edge devices
(3) only run proof validation on the low-power device.
This approach is called certification and proof-carrying-code in the program verification community.
 
In the future, we may try to develop proof-generating ReDiP verifier and proof checkers.
