# StudyRAG pilot question review

These 20 development questions have been checked against the pinned source by Codex (AI). They have not been accepted by a human reviewer. No retrieval scores have been calculated. See AI_REVIEW.md for corrections and limitations.

Source excerpts: CPython v3.13.0, copyright Python Software Foundation, PSF-2.0. See ATTRIBUTION.md and licenses/CPYTHON-LICENSE.txt. Coordinates refer to pinned RST source lines, not PDF pages.

## pilot-001 | paraphrase

Removing the oldest item from my Python list keeps getting slower as the list grows. What should I use for a FIFO queue, and why?

**Reference answer:** Use collections.deque. Removing from the front of a list shifts other elements; deque supports fast appends and pops at both ends.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked FIFO semantics, shifting cost, deque recommendation, and the explicit irrelevant set passage.

**Grade 2:** [datastructures.rst, lines 172-179](corpus/datastructures.rst). Explains the list performance issue and recommends deque.

```rst
It is also possible to use a list as a queue, where the first element added is
the first element retrieved ("first-in, first-out"); however, lists are not
efficient for this purpose.  While appends and pops from the end of list are
fast, doing inserts or pops from the beginning of a list is slow (because all
of the other elements have to be shifted by one).

To implement a queue, use :class:`collections.deque` which was designed to
have fast appends and pops from both ends.  For example::
```

**Grade 0:** [datastructures.rst, lines 448-455](corpus/datastructures.rst). Sets address uniqueness and membership, not a FIFO queue or its performance.

```rst
Python also includes a data type for *sets*.  A set is an unordered collection
with no duplicate elements.  Basic uses include membership testing and
eliminating duplicate entries.  Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the :func:`set` function can be used to create sets.  Note: to
create an empty set you have to use ``set()``, not ``{}``; the latter creates an
empty dictionary, a data structure that we discuss in the next section.
```

## pilot-002 | exact_term

Why does a function with a default argument L=[] keep values from previous calls, and how do I give calls that omit L a fresh list?

**Reference answer:** Default values are evaluated once. Use a None default and create a new list inside the function when L is None; this gives calls that omit L a fresh list.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Clarified that a fresh list is created for calls which omit the argument; the example does not copy explicitly supplied lists.

**Grade 2:** [controlflow.rst, lines 622-648](corpus/controlflow.rst). Explains shared default state and provides the None-sentinel fix.

```rst
**Important warning:**  The default value is evaluated only once. This makes a
difference when the default is a mutable object such as a list, dictionary, or
instances of most classes.  For example, the following function accumulates the
arguments passed to it on subsequent calls::

   def f(a, L=[]):
       L.append(a)
       return L

   print(f(1))
   print(f(2))
   print(f(3))

This will print ::

   [1]
   [1, 2]
   [1, 2, 3]

If you don't want the default to be shared between subsequent calls, you can
write the function like this instead::

   def f(a, L=None):
       if L is None:
           L = []
       L.append(a)
       return L
```

## pilot-003 | typo

Why did my list become None after I assinged the result of list.sort() back to it?

**Reference answer:** list.sort() modifies the list in place and returns None. Call it without assigning its return value back to the list variable.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Replaced the invalid srot() code with a typo in ordinary prose. The old literal call would raise AttributeError, so its None premise was misleading.

**Grade 2:** [datastructures.rst, lines 122-125](corpus/datastructures.rst). States that methods which only modify the list return None.

```rst
You might have noticed that methods like ``insert``, ``remove`` or ``sort`` that
only modify the list have no return value printed -- they return the default
``None``. [#]_  This is a design principle for all mutable data structures in
Python.
```

## pilot-004 | exact_term

How do I create an empty set, and why does {} not do that?

**Reference answer:** Use set(); {} creates an empty dictionary.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked the empty-set versus empty-dictionary distinction.

**Grade 2:** [datastructures.rst, lines 448-455](corpus/datastructures.rst). Defines sets and distinguishes empty-set and empty-dictionary syntax.

```rst
Python also includes a data type for *sets*.  A set is an unordered collection
with no duplicate elements.  Basic uses include membership testing and
eliminating duplicate entries.  Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the :func:`set` function can be used to create sets.  Note: to
create an empty set you have to use ``set()``, not ``{}``; the latter creates an
empty dictionary, a data structure that we discuss in the next section.
```

## pilot-005 | paraphrase

Can I use a list as a dictionary key? What is different about a tuple containing only strings?

**Reference answer:** A list cannot be a key because it is mutable. A tuple of strings can be a key; a tuple containing a mutable object cannot.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked list-key and tuple-of-strings claims against the source. This is not a general claim that all immutable Python objects are hashable.

**Grade 2:** [datastructures.rst, lines 495-504](corpus/datastructures.rst). Contrasts mutable lists with permissible immutable tuple keys.

```rst
Another useful data type built into Python is the *dictionary* (see
:ref:`typesmapping`). Dictionaries are sometimes found in other languages as
"associative memories" or "associative arrays".  Unlike sequences, which are
indexed by a range of numbers, dictionaries are indexed by *keys*, which can be
any immutable type; strings and numbers can always be keys.  Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains
any mutable object either directly or indirectly, it cannot be used as a key.
You can't use lists as keys, since lists can be modified in place using index
assignments, slice assignments, or methods like :meth:`~list.append` and
:meth:`~list.extend`.
```

## pilot-006 | paraphrase

If processing a file raises an exception, how can I ensure the file gets closed?

**Reference answer:** Use a with statement around the file operation; it closes the file even if processing raises an exception.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Both file-handling passages independently support closing the file on an exception; either can supply evidence.

**Grade 2:** [inputoutput.rst, lines 345-356](corpus/inputoutput.rst). Shows with and explains closing on exceptions.

```rst
It is good practice to use the :keyword:`with` keyword when dealing
with file objects.  The advantage is that the file is properly closed
after its suite finishes, even if an exception is raised at some
point.  Using :keyword:`!with` is also much shorter than writing
equivalent :keyword:`try`\ -\ :keyword:`finally` blocks::

    >>> with open('workfile', encoding="utf-8") as f:
    ...     read_data = f.read()

    >>> # We can check that the file has been automatically closed.
    >>> f.closed
    True
```

**Grade 2:** [errors.rst, lines 497-509](corpus/errors.rst). Independently describes prompt cleanup even when processing fails.

```rst
The problem with this code is that it leaves the file open for an indeterminate
amount of time after this part of the code has finished executing.
This is not an issue in simple scripts, but can be a problem for larger
applications. The :keyword:`with` statement allows objects like files to be
used in a way that ensures they are always cleaned up promptly and correctly. ::

   with open("myfile.txt") as f:
       for line in f:
           print(line, end="")

After the statement is executed, the file *f* is always closed, even if a
problem was encountered while processing the lines. Objects which, like files,
provide predefined clean-up actions will indicate this in their documentation.
```

## pilot-007 | exact_term

What does adding b to a file mode change, and can I specify encoding in that mode?

**Reference answer:** Binary mode reads and writes bytes, and encoding must not be specified.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked bytes versus text and the explicit restriction on encoding in binary mode.

**Grade 2:** [inputoutput.rst, lines 327-335](corpus/inputoutput.rst). Defines binary mode, bytes, and the encoding restriction.

```rst
Normally, files are opened in :dfn:`text mode`, that means, you read and write
strings from and to the file, which are encoded in a specific *encoding*.
If *encoding* is not specified, the default is platform dependent
(see :func:`open`).
Because UTF-8 is the modern de-facto standard, ``encoding="utf-8"`` is
recommended unless you know that you need to use a different encoding.
Appending a ``'b'`` to the mode opens the file in :dfn:`binary mode`.
Binary mode data is read and written as :class:`bytes` objects.
You can not specify *encoding* when opening file in binary mode.
```

## pilot-008 | shorthand

Stdlib JSON to a file and back: which calls do I use, rather than getting a JSON string?

**Reference answer:** Use json.dump(x, f) with a text file open for writing and json.load(f) with a file open for reading. json.dumps returns a string.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked dump/load file operations versus dumps returning a string.

**Grade 2:** [inputoutput.rst, lines 507-524](corpus/inputoutput.rst). Distinguishes dumps, dump to a text file, and load from a file.

```rst
If you have an object ``x``, you can view its JSON string representation with a
simple line of code::

   >>> import json
   >>> x = [1, 'simple', 'list']
   >>> json.dumps(x)
   '[1, "simple", "list"]'

Another variant of the :func:`~json.dumps` function, called :func:`~json.dump`,
simply serializes the object to a :term:`text file`.  So if ``f`` is a
:term:`text file` object opened for writing, we can do this::

   json.dump(x, f)

To decode the object again, if ``f`` is a :term:`binary file` or
:term:`text file` object which has been opened for reading::

   x = json.load(f)
```

## pilot-009 | paraphrase

I named my script random.py and now importing random finds my file. How can a local file take priority over the standard library?

**Reference answer:** The script directory is placed at the beginning of sys.path, ahead of the standard-library path, so same-named files can shadow library modules.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Completed the source paragraph and checked local module shadowing; question concerns a Python library module, not a built-in module.

**Grade 2:** [modules.rst, lines 206-211](corpus/modules.rst). Explains script-directory precedence and unintended module replacement in a complete paragraph.

```rst
After initialization, Python programs can modify :data:`sys.path`.  The
directory containing the script being run is placed at the beginning of the
search path, ahead of the standard library path. This means that scripts in that
directory will be loaded instead of modules of the same name in the library
directory. This is an error unless the replacement is intended.  See section
:ref:`tut-standardmodules` for more information.
```

## pilot-010 | shorthand

CLI + importable module: how do I stop command-line handling from running when the file is imported?

**Reference answer:** Put command-line handling under if __name__ == "__main__":. It runs when the module is the main program, not when imported.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked main-guard code and the explanation of imported versus directly executed modules.

**Grade 2:** [modules.rst, lines 149-163](corpus/modules.rst). Shows the main guard and why command-line code does not run on import.

```rst
When you run a Python module with ::

   python fibo.py <arguments>

the code in the module will be executed, just as if you imported it, but with
the ``__name__`` set to ``"__main__"``.  That means that by adding this code at
the end of your module::

   if __name__ == "__main__":
       import sys
       fib(int(sys.argv[1]))

you can make the file usable as a script as well as an importable module,
because the code that parses the command line only runs if the module is
executed as the "main" file:
```

## pilot-011 | typo

Why does 0.1 + 0.1 + 0.1 fail an equlity check with 0.3, and what comparison helper can I use?

**Reference answer:** Binary float representations are inexact; use math.isclose for approximate comparison. Pre-rounding does not fix this example.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Added the direct explanation of binary approximation so the causal part is explicitly supported.

**Grade 2:** [floatingpoint.rst, lines 16-26](corpus/floatingpoint.rst). Directly explains binary floating-point representation and approximation of decimal fractions.

```rst
Floating-point numbers are represented in computer hardware as base 2 (binary)
fractions.  For example, the **decimal** fraction ``0.625``
has value 6/10 + 2/100 + 5/1000, and in the same way the **binary** fraction ``0.101``
has value 1/2 + 0/4 + 1/8. These two fractions have identical values, the only
real difference being that the first is written in base 10 fractional notation,
and the second in base 2.

Unfortunately, most decimal fractions cannot be represented exactly as binary
fractions.  A consequence is that, in general, the decimal floating-point
numbers you enter are only approximated by the binary floating-point numbers
actually stored in the machine.
```

**Grade 2:** [floatingpoint.rst, lines 114-137](corpus/floatingpoint.rst). Shows failed equality and the successful math.isclose comparison.

```rst
One illusion may beget another.  For example, since 0.1 is not exactly 1/10,
summing three values of 0.1 may not yield exactly 0.3, either:

.. doctest::

   >>> 0.1 + 0.1 + 0.1 == 0.3
   False

Also, since the 0.1 cannot get any closer to the exact value of 1/10 and
0.3 cannot get any closer to the exact value of 3/10, then pre-rounding with
:func:`round` function cannot help:

.. doctest::

   >>> round(0.1, 1) + round(0.1, 1) + round(0.1, 1) == round(0.3, 1)
   False

Though the numbers cannot be made closer to their intended exact values,
the :func:`math.isclose` function can be useful for comparing inexact values:

.. doctest::

   >>> math.isclose(0.1 + 0.1 + 0.1, 0.3)
   True
```

## pilot-012 | typo

Two Python apps need diferent versions of the same package. How do I keep an upgrade for one from breaking the other?

**Reference answer:** Give the applications separate virtual environments so each can use its own installed package versions.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked conflicting package requirements and per-application environment isolation. Removed a leading blank line from the evidence.

**Grade 2:** [venv.rst, lines 17-32](corpus/venv.rst). States the package-version conflict and its virtual-environment solution.

```rst
This means it may not be possible for one Python installation to meet
the requirements of every application.  If application A needs version
1.0 of a particular module but application B needs version 2.0, then
the requirements are in conflict and installing either version 1.0 or 2.0
will leave one application unable to run.

The solution for this problem is to create a :term:`virtual environment`, a
self-contained directory tree that contains a Python installation for a
particular version of Python, plus a number of additional packages.

Different applications can then use different virtual environments.
To resolve the earlier example of conflicting requirements,
application A can have its own virtual environment with version 1.0
installed while application B has another virtual environment with version 2.0.
If application B requires a library be upgraded to version 3.0, this will
not affect application A's environment.
```

## pilot-013 | exact_term

When does a for-loop else clause execute, and does it run after break?

**Reference answer:** It executes on normal exhaustion without break; break skips it. Return or a raised exception also skips it.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked normal exhaustion, break, return, and exception cases.

**Grade 2:** [controlflow.rst, lines 203-215](corpus/controlflow.rst). Explains normal completion versus early exits for loop else.

```rst
In a :keyword:`!for` or :keyword:`!while` loop the :keyword:`!break` statement
may be paired with an :keyword:`!else` clause.  If the loop finishes without
executing the :keyword:`!break`, the :keyword:`!else` clause executes.

In a :keyword:`for` loop, the :keyword:`!else` clause is executed
after the loop finishes its final iteration, that is, if no break occurred.

In a :keyword:`while` loop, it's executed after the loop's condition becomes false.

In either kind of loop, the :keyword:`!else` clause is **not** executed if the
loop was terminated by a :keyword:`break`.  Of course, other ways of ending the
loop early, such as a :keyword:`return` or a raised exception, will also skip
execution of the :keyword:`else` clause.
```

## pilot-014 | typo

What tells a for loop to stop when an itterator has no more values, and how do I request its next value manually?

**Reference answer:** The iterator raises StopIteration from __next__; call next(iterator) to request the next element.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Extended the excerpt to include the complete opening sentence; checked next and StopIteration.

**Grade 2:** [classes.rst, lines 798-805](corpus/classes.rst). Connects the iterator protocol, next, and StopIteration, including the full opening sentence.

```rst
This style of access is clear, concise, and convenient.  The use of iterators
pervades and unifies Python.  Behind the scenes, the :keyword:`for` statement
calls :func:`iter` on the container object.  The function returns an iterator
object that defines the method :meth:`~iterator.__next__` which accesses
elements in the container one at a time.  When there are no more elements,
:meth:`~iterator.__next__` raises a :exc:`StopIteration` exception which tells the
:keyword:`!for` loop to terminate.  You can call the :meth:`~iterator.__next__` method
using the :func:`next` built-in function; this example shows how it all works::
```

## pilot-015 | multi_evidence

A function default list retains old items, and a class-level list is shared by instances. Explain each cause and how to make the lists independent.

**Reference answer:** The function default is evaluated once: use None and allocate a list inside the function for omitted arguments. A class-level list is shared: allocate a list as an instance attribute inside __init__ for each instance.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked both causes and both fixes; clarified omitted function argument and instance-specific attributes.

**Grade 2:** [controlflow.rst, lines 622-648](corpus/controlflow.rst). Supports the function-default cause and fix.

```rst
**Important warning:**  The default value is evaluated only once. This makes a
difference when the default is a mutable object such as a list, dictionary, or
instances of most classes.  For example, the following function accumulates the
arguments passed to it on subsequent calls::

   def f(a, L=[]):
       L.append(a)
       return L

   print(f(1))
   print(f(2))
   print(f(3))

This will print ::

   [1]
   [1, 2]
   [1, 2, 3]

If you don't want the default to be shared between subsequent calls, you can
write the function like this instead::

   def f(a, L=None):
       if L is None:
           L = []
       L.append(a)
       return L
```

**Grade 2:** [classes.rst, lines 422-454](corpus/classes.rst). Supports the shared class-list cause and per-instance fix.

```rst
As discussed in :ref:`tut-object`, shared data can have possibly surprising
effects with involving :term:`mutable` objects such as lists and dictionaries.
For example, the *tricks* list in the following code should not be used as a
class variable because just a single list would be shared by all *Dog*
instances::

    class Dog:

        tricks = []             # mistaken use of a class variable

        def __init__(self, name):
            self.name = name

        def add_trick(self, trick):
            self.tricks.append(trick)

    >>> d = Dog('Fido')
    >>> e = Dog('Buddy')
    >>> d.add_trick('roll over')
    >>> e.add_trick('play dead')
    >>> d.tricks                # unexpectedly shared by all dogs
    ['roll over', 'play dead']

Correct design of the class should use an instance variable instead::

    class Dog:

        def __init__(self, name):
            self.name = name
            self.tricks = []    # creates a new empty list for each dog

        def add_trick(self, trick):
            self.tricks.append(trick)
```

## pilot-016 | multi_evidence

Why can ordinary floats surprise me with decimal equality, and which standard-library numeric type is useful when exact decimal representation matters for money?

**Reference answer:** Many decimal fractions are only approximate in binary floats. The decimal module provides Decimal for decimal arithmetic and applications requiring exact decimal representation, subject to its precision and rounding settings.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Added explicit binary-representation evidence alongside the equality example and Decimal use cases.

**Grade 2:** [floatingpoint.rst, lines 16-26](corpus/floatingpoint.rst). Explains why decimal fractions may have only approximate binary representations.

```rst
Floating-point numbers are represented in computer hardware as base 2 (binary)
fractions.  For example, the **decimal** fraction ``0.625``
has value 6/10 + 2/100 + 5/1000, and in the same way the **binary** fraction ``0.101``
has value 1/2 + 0/4 + 1/8. These two fractions have identical values, the only
real difference being that the first is written in base 10 fractional notation,
and the second in base 2.

Unfortunately, most decimal fractions cannot be represented exactly as binary
fractions.  A consequence is that, in general, the decimal floating-point
numbers you enter are only approximated by the binary floating-point numbers
actually stored in the machine.
```

**Grade 2:** [floatingpoint.rst, lines 114-129](corpus/floatingpoint.rst). Shows decimal equality surprises for binary floats.

```rst
One illusion may beget another.  For example, since 0.1 is not exactly 1/10,
summing three values of 0.1 may not yield exactly 0.3, either:

.. doctest::

   >>> 0.1 + 0.1 + 0.1 == 0.3
   False

Also, since the 0.1 cannot get any closer to the exact value of 1/10 and
0.3 cannot get any closer to the exact value of 3/10, then pre-rounding with
:func:`round` function cannot help:

.. doctest::

   >>> round(0.1, 1) + round(0.1, 1) + round(0.1, 1) == round(0.3, 1)
   False
```

**Grade 2:** [stdlib2.rst, lines 358-368](corpus/stdlib2.rst). Identifies Decimal and financial/exact-decimal use cases.

```rst
The :mod:`decimal` module offers a :class:`~decimal.Decimal` datatype for
decimal floating-point arithmetic.  Compared to the built-in :class:`float`
implementation of binary floating point, the class is especially helpful for

* financial applications and other uses which require exact decimal
  representation,
* control over precision,
* control over rounding to meet legal or regulatory requirements,
* tracking of significant decimal places, or
* applications where the user expects the results to match calculations done by
  hand.
```

## pilot-017 | unanswerable

How do I use pandas groupby to compute the median salary in each department?

**Reference answer:** The supplied documents do not contain enough information to answer this question.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked absence of pandas/groupby/DataFrame and reviewed list, dictionary, statistics, and file-handling sections; none specifies the pandas API requested.

**Absence rationale:** Pandas DataFrame/groupby usage is not covered in this frozen tutorial corpus.

## pilot-018 | unanswerable

Which scikit-learn GridSearchCV parameters control cross-validation and parallel execution?

**Reference answer:** The supplied documents do not contain enough information to answer this question.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked absence of scikit-learn/GridSearchCV and reviewed function arguments and standard-library chapters; none provides the requested tuning API.

**Absence rationale:** Scikit-learn and GridSearchCV are outside this corpus.

## pilot-019 | unanswerable

How do I create a PostgreSQL index that speeds up searching a JSONB field?

**Reference answer:** The supplied documents do not contain enough information to answer this question.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked absence of PostgreSQL/JSONB and reviewed JSON serialization; file serialization does not answer database-index configuration.

**Absence rationale:** PostgreSQL indexing and JSONB are not covered; Python JSON serialization is not evidence for a database index.

## pilot-020 | unanswerable

Which Qdrant collection settings should I choose for text-embedding-3-small vectors?

**Reference answer:** The supplied documents do not contain enough information to answer this question.

**Status:** AI-reviewed; human acceptance optional and not yet recorded.

**Review note:** Checked absence of Qdrant/model identifier and reviewed numeric types and package management; none specifies vector collection settings.

**Absence rationale:** Qdrant collection configuration and this embedding model are not covered.

