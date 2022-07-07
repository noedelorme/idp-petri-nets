# Interdisciplinary project about Petri nets
This is an Python implementation of algorithms for efficient generation and check of separators for continuous Petri nets. This algorithms are based on <a id="1" href="#">[1]</a> and <a id="2" href="https://doi.org/10.3233/FI-2015-1168">[2]</a>.

## Installation
You need first to unstall <a href="https://github.com/Z3Prover/z3">Z3</a>, which is a theorem prover from Microsoft Research. You can use Pip with the following command.
```bash
pip install z3-solver
```

To execute the program, just use the following command.
```bash
python main.py
```

## References
<a id="1" href="#">[1]</a> 
Michael Blondin & Javier Esparza. Separators in Continuous Petri Nets. (2022)

<a id="2" href="https://doi.org/10.3233/FI-2015-1168">[2]</a> 
Estibaliz Fraca & Serge Haddad. Complexity Analysis of Continuous Petri Nets. (2015)