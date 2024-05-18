# course project: automated verification of probabilistic program

Especially on correctness of implementation of MCMC sampling algorithm

The research work of Prof. Joost-Pieter Katoen at RWTH Aachen

- theoretica foundation: Generating Functions for Probabilistic Programs
- application scope: exact verification/inference/synthesis for probabilistic programs
- papers:
  - Does a Program Yield the Right Distribution? Verifying Probabilistic Programs via Generating Functions·
  - Exact Probabilistic Inference Using Generating Functions
  - Exact Bayesian Inference for Loopy Probabilistic Programs
  - A Deductive Verification Infrastructure for Probabilistic Programs (no, no GF)


The course project:

1. study the underlying program logic
   - syntax and semantics of probabilistic program
   - generating function semantics
   - Bayesian reasoning and program logic
2. a small DSL incorporating PGF computation using sagemath.
   - programming language
   - specification language
   - verification condition generation
   - constraint solving using sagemath or sympy
3. case study of a practical MCMC program:
   - detect introduced bugs
   - prove correct program

## feedback on proposal

Very interesting problem, and studying recent research is a good starting point.
In the milestone, try to formulate a concrete problem, including:
- What are the probabilistic programs you want to verify,
- What are the properties?
- What approaches are you going to take? Perhaps give a brief survey from the referred paper.


## note on paper reading

Supported programs

- discrete probabilistic programs
- potentially unbounded looping
- over an infinite state space

Behavior specs

- standard distributions (geometric, uniform, etc.)
- finite convolutions of those distributions.

Solved problem: determine whether a program yields exactly the desired distribution _under all possible inputs_.

**remark** they are probably trying to find certain canonical form.
Kozen's transformer semantics.

- The denotational semantics of a program is a distribution transformer: takes a PGF and spits out another PGF.
- The program and the spec are encoded as PGF transformers.
- Whether it is the case: $\forall g . prog(g) = spec(g)$. Extensional equality.
- Second order PGF (SOP)
- Restricted programming language (guard is rectangular): so that they admit closed-form PGF.

**doubt** wow... Huge restriction. Without linear/affine guards, some common programs of practical value will not be encodable.  
**response to doubt** not exactly. At least affine operators are expressible. See appendix of the journal version 2205.01449.

### limitations of previous methods


Existing techniques mostly concern with approximations.
That is verifying or inferring _upper/lower bounds on various quantities_.

- assertion-violation probabilities.
- pre-expectations and moments.
- expected running time
- concentrations

They can only provide a digest of the probability distribution of the program.

In what scenario are these digests insufficient?

- Safety critical and security critical applications.
    - cryptography. Warning side-channel leak is ahead.

### second order PGF

The formal power series (FPS): 

$$
\sum_{\sigma\in\mathbb{N}^k} f(\sigma) \mathbf{X}^\sigma
$$

- $f(\sigma)$ is the coefficient, and
- $\mathbf{X}^\sigma = \prod_{j=1}^k X_j^{\sigma(j)}$

The probability generating functions are FPS such that (with joint PMF coefficient)

$$
1 = \sum_{\sigma\in\mathbb{N}^k} f(\sigma)
\qquad
\forall \sigma\in\mathbb{N}^k . 0 \leq f(\sigma)
$$

Second order PGFs: from $\mathbb{N}^k\to\mathbb{R}$ to $\mathbb{N}^l\to (\mathbb{R}[[U]])$
Used to encode linear functions $PGF\to PGF$.

To encode a function $f: R[[U]] \to R[[X]]$, use the following formal power series (joint PMF)

$$
\sum_{\tau\in\mathbb{N}^l} f(\tau) \mathbb{U}^{\tau}
\qquad
f(\tau) \in R[[X]]
$$

First order PGFs can be encoded in this way, simply let $\mathbf{X} = \langle \rangle$ i.e. the empty sequence.

To apply a transform $T: SOP\to SOP$

$$
\sum_{\tau\in\mathbb{N}^l} T(f(\tau)) \mathbb{U}^{\tau}
$$

### linear SOP transformer equivalence check

- linearity, just check equality on point mass PMF is sufficient
- The generalized Dirac SOP input: $\prod_i {(1-X_i U_i)}^{-1} = \sum_{\sigma} (0+X^\sigma )U^\sigma$ all point mass PGF is encoded.

### the pGCL and ReDiP language

### overview of their approach

1. To tackle the program equivalence problem, they defined the PGF transformer semantics.
2. They showed that (at least for loop-free programs) the PGF transformers of ReDiP programs are linear.
3. They developed techniques for solving this problem.

- deciding equivalence of two linear PGF transforms.
- deciding equality for all point-mass PGF inputs.
- deciding equivalence of two linear SOP transformers.
- deciding equality on the generalized Dirac SOP.

The PGF semantics of ReDiP programs can be generalized to SOP semantics, which also preserves closed form (at least for loop-free programs)

## question

### question 1: do we really need the exact distribution

Is that really the case?
Some approximations are really good.

Say that we use the following digest:

$$
E(X),
E(X^2),
E(X^3),
E(X^4),
$$

I think bias will be revealed, probably. Think. $E({(X+d)}^k)$.

We probably cannot distinguish two distributions of the same family whose parameters vary a little bit.
But we will not confuse different kinds of distributions.


### question 2: what if we are interested in only a subset of valid inputs

We don't necessarily need the "equivalent on arbitrary inputs".
Perhaps we just want $f(x) = g(x)$ for all $x\in S$.

Say that we are doing some optimization, and we know that at this point,
the value of the parameters falls in a specific domain $D$.
We may want to verify that _for all inputs in the domain D, the two programs give equivalent output_.

While this is possible for a flexible programming language and a specification language.
The restrictions of ReDiP makes it impossible some times.


```haskell
restrict :: (a -> Bool) -> (a -> b) -> (a -> Maybe b)
restrict cond prog input = if cond input
                           then Just (prog input)
                           else Nothing
```

We can just verify equivalence `restrict domain f == restrict domain g`,
if the language allow encoding sufficiently complex conditions.
However, that is not the case of ReDiP, which imposes a rather strict constraint on guards.




## milestone

Very interesting problem, and studying recent research is a good starting point.

In the milestone, try to formulate a concrete problem, including:
- What are the probabilistic programs you want to verify, 
- What are the properties?
- What approaches are you going to take? Perhaps give a brief survey from the referred paper.
