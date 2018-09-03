# LTL Model Checking

This project implements LTL model checking on Kripke models.

## Requirements

* python of version 3.5 or above
* pyeda of version 0.28.0 or above

## Running the example

```
python main.py
```

## Running the model checking for resource management protocol

The file proc_model.py runs checks one of the formulas mentioned in the article on the resource management procotol model with any number of processors.

```
python proc_model.py [number of processors] [formula to check index (see below)] <*>
```

### Formulas to check

* 0 - Liveness - AG(EF(~waiting & (shared | owned)) & EF(~waiting & owned))
* 1 - Safety (CTL) - AG(shared | owned | invalid)
* 2 - Safety (LTL) - AG(shared | owned | invalid)
* 3 - Starvation (CTL) - AG((owned & waiting) -> AF(owned & ~waiting))
* 4 - Starvation (LTL) - AG((owned & waiting) -> F(owned & ~waiting))

### Simplifying LTL formulas

When the third argument is * it indicates the formulas need to be simplified to use only the 'next' (X) and 'until' (U) quantifiers.

### examples

```
python proc_model.py 1 0
python proc_model.py 1 1
python proc_model.py 1 2
python proc_model.py 1 2 *
python proc_model.py 1 3
python proc_model.py 1 4
python proc_model.py 1 4 *

python proc_model.py 2 2
python proc_model.py 2 2 *
```