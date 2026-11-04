# Retrieval comparison

All three methods searched the same frozen 250 chunks for the same 20 development questions. No paid APIs were used. Scores below measure known evidence coverage, not answer accuracy or held-out performance.

| Method | Complete passage at 5 | Complete passage at 10 | Mean passage character coverage at 10 | Median query ms |
|---|---|---|---|---|
| bm25 | 11/16 | 13/16 | 81.4% | 0.34 |
| dense | 13/16 | 15/16 | 91.5% | 10.19 |
| hybrid | 13/16 | 14/16 | 81.5% | 10.54 |

Dense search uses the pinned quantized ONNX export of BAAI/bge-small-en-v1.5. Hybrid search fuses top-50 BM25 and dense candidates using equal-weight RRF with constant 60. No settings were tuned to these results. Dense timings include query encoding; hybrid timings sum its sequential components. Passage encoding and model loading are recorded separately in run.json.

## Per-question known-evidence hits at 10

| Question | BM25 | Dense | Hybrid |
|---|---|---|---|
| pilot-001 | yes | yes | yes |
| pilot-002 | yes | yes | yes |
| pilot-003 | yes | yes | yes |
| pilot-004 | yes | yes | yes |
| pilot-005 | no | yes | no |
| pilot-006 | yes | no | yes |
| pilot-007 | yes | yes | yes |
| pilot-008 | yes | yes | yes |
| pilot-009 | yes | yes | yes |
| pilot-010 | yes | yes | yes |
| pilot-011 | no | yes | yes |
| pilot-012 | no | yes | no |
| pilot-013 | yes | yes | yes |
| pilot-014 | yes | yes | yes |
| pilot-015 | yes | yes | yes |
| pilot-016 | yes | yes | yes |
| pilot-017 | n/a | n/a | n/a |
| pilot-018 | n/a | n/a | n/a |
| pilot-019 | n/a | n/a | n/a |
| pilot-020 | n/a | n/a | n/a |

## Inspect examples

Source excerpts retain Python Software Foundation attribution and PSF-2.0 terms; see evaluation/pilot/ATTRIBUTION.md. Lines refer to original pinned RST.

### pilot-001

Removing the oldest item from my Python list keeps getting slower as the list grows. What should I use for a FIFO queue, and why?

**bm25: py313-datastructures, lines 145-183**

````text
item to the top of the stack, use list.append.  To retrieve an item from the
top of the stack, use list.pop without an explicit index.  For example::

   >>> stack = [3, 4, 5]
   >>> stack.append(6)
   >>> stack.append(7)
   >>> stack
   [3, 4, 5, 6, 7]
   >>> stack.pop()
   7
   >>> stack
   [3, 4, 5, 6]
   >>> stack.pop()
   6
   >>> stack.pop()
   5
   >>> stack
   [3, 4]



Using Lists as Queues


It is also possible to use a list as a queue, where the first element added is
the first element retrieved ("first-in, first-out"); however, lists are not
efficient for this purpose.  While appends and pops from the end of list are
fast, doing i ...
````

**dense: py313-datastructures, lines 145-183**

````text
item to the top of the stack, use list.append.  To retrieve an item from the
top of the stack, use list.pop without an explicit index.  For example::

   >>> stack = [3, 4, 5]
   >>> stack.append(6)
   >>> stack.append(7)
   >>> stack
   [3, 4, 5, 6, 7]
   >>> stack.pop()
   7
   >>> stack
   [3, 4, 5, 6]
   >>> stack.pop()
   6
   >>> stack.pop()
   5
   >>> stack
   [3, 4]



Using Lists as Queues


It is also possible to use a list as a queue, where the first element added is
the first element retrieved ("first-in, first-out"); however, lists are not
efficient for this purpose.  While appends and pops from the end of list are
fast, doing i ...
````

**hybrid: py313-datastructures, lines 145-183**

````text
item to the top of the stack, use list.append.  To retrieve an item from the
top of the stack, use list.pop without an explicit index.  For example::

   >>> stack = [3, 4, 5]
   >>> stack.append(6)
   >>> stack.append(7)
   >>> stack
   [3, 4, 5, 6, 7]
   >>> stack.pop()
   7
   >>> stack
   [3, 4, 5, 6]
   >>> stack.pop()
   6
   >>> stack.pop()
   5
   >>> stack
   [3, 4]



Using Lists as Queues


It is also possible to use a list as a queue, where the first element added is
the first element retrieved ("first-in, first-out"); however, lists are not
efficient for this purpose.  While appends and pops from the end of list are
fast, doing i ...
````

### pilot-002

Why does a function with a default argument L=[] keep values from previous calls, and how do I give calls that omit L a fresh list?

**bm25: py313-controlflow, lines 595-641**

````text
print(reminder)

This function can be called in several ways:

* giving only the mandatory argument:
  ask_ok('Do you really want to quit?')
* giving one of the optional arguments:
  ask_ok('OK to overwrite the file?', 2)
* or even giving all arguments:
  ask_ok('OK to overwrite the file?', 2, 'Come on, only yes or no!')

This example also introduces the in keyword. This tests whether or
not a sequence contains a certain value.

The default values are evaluated at the point of function definition in the
*defining* scope, so that ::

   i = 5

   def f(arg=i):
       print(arg)

   i = 6
   f()

will print 5.

**Important warning:**  The defau ...
````

**dense: py313-controlflow, lines 563-601**

````text
adds a new element at the end of the list.  In this example it is equivalent to
  result = result + [a], but more efficient.



More on Defining Functions

It is also possible to define functions with a variable number of arguments.
There are three forms, which can be combined.



Default Argument Values

The most useful form is to specify a default value for one or more arguments.
This creates a function that can be called with fewer arguments than it is
defined to allow.  For example::

   def ask_ok(prompt, retries=4, reminder='Please try again!'):
       while True:
           reply = input(prompt)
           if reply in {'y', 'ye', 'yes' ...
````

**hybrid: py313-controlflow, lines 595-641**

````text
print(reminder)

This function can be called in several ways:

* giving only the mandatory argument:
  ask_ok('Do you really want to quit?')
* giving one of the optional arguments:
  ask_ok('OK to overwrite the file?', 2)
* or even giving all arguments:
  ask_ok('OK to overwrite the file?', 2, 'Come on, only yes or no!')

This example also introduces the in keyword. This tests whether or
not a sequence contains a certain value.

The default values are evaluated at the point of function definition in the
*defining* scope, so that ::

   i = 5

   def f(arg=i):
       print(arg)

   i = 6
   f()

will print 5.

**Important warning:**  The defau ...
````

### pilot-003

Why did my list become None after I assinged the result of list.sort() back to it?

**bm25: py313-datastructures, lines 116-147**

````text
>>> fruits.sort()
    >>> fruits
    ['apple', 'apple', 'banana', 'banana', 'grape', 'kiwi', 'orange', 'pear']
    >>> fruits.pop()
    'pear'

You might have noticed that methods like insert, remove or sort that
only modify the list have no return value printed -- they return the default
None. [#]_  This is a design principle for all mutable data structures in
Python.

Another thing you might notice is that not all data can be sorted or
compared.  For instance, [None, 'hello', 10] doesn't sort because
integers can't be compared to strings and None can't be compared to
other types.  Also, there are some types that don't have a defined
orderin ...
````

**dense: py313-datastructures, lines 116-147**

````text
>>> fruits.sort()
    >>> fruits
    ['apple', 'apple', 'banana', 'banana', 'grape', 'kiwi', 'orange', 'pear']
    >>> fruits.pop()
    'pear'

You might have noticed that methods like insert, remove or sort that
only modify the list have no return value printed -- they return the default
None. [#]_  This is a design principle for all mutable data structures in
Python.

Another thing you might notice is that not all data can be sorted or
compared.  For instance, [None, 'hello', 10] doesn't sort because
integers can't be compared to strings and None can't be compared to
other types.  Also, there are some types that don't have a defined
orderin ...
````

**hybrid: py313-datastructures, lines 116-147**

````text
>>> fruits.sort()
    >>> fruits
    ['apple', 'apple', 'banana', 'banana', 'grape', 'kiwi', 'orange', 'pear']
    >>> fruits.pop()
    'pear'

You might have noticed that methods like insert, remove or sort that
only modify the list have no return value printed -- they return the default
None. [#]_  This is a design principle for all mutable data structures in
Python.

Another thing you might notice is that not all data can be sorted or
compared.  For instance, [None, 'hello', 10] doesn't sort because
integers can't be compared to strings and None can't be compared to
other types.  Also, there are some types that don't have a defined
orderin ...
````

### pilot-004

How do I create an empty set, and why does {} not do that?

**bm25: py313-datastructures, lines 439-470**

````text
sequence.  Note that multiple assignment is really just a combination of tuple
packing and sequence unpacking.



Sets

Python also includes a data type for *sets*.  A set is an unordered collection
with no duplicate elements.  Basic uses include membership testing and
eliminating duplicate entries.  Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the set function can be used to create sets.  Note: to
create an empty set you have to use set(), not {}; the latter creates an
empty dictionary, a data structure that we discuss in the next section.

Here is a brief d ...
````

**dense: py313-datastructures, lines 439-470**

````text
sequence.  Note that multiple assignment is really just a combination of tuple
packing and sequence unpacking.



Sets

Python also includes a data type for *sets*.  A set is an unordered collection
with no duplicate elements.  Basic uses include membership testing and
eliminating duplicate entries.  Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the set function can be used to create sets.  Note: to
create an empty set you have to use set(), not {}; the latter creates an
empty dictionary, a data structure that we discuss in the next section.

Here is a brief d ...
````

**hybrid: py313-datastructures, lines 439-470**

````text
sequence.  Note that multiple assignment is really just a combination of tuple
packing and sequence unpacking.



Sets

Python also includes a data type for *sets*.  A set is an unordered collection
with no duplicate elements.  Basic uses include membership testing and
eliminating duplicate entries.  Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the set function can be used to create sets.  Note: to
create an empty set you have to use set(), not {}; the latter creates an
empty dictionary, a data structure that we discuss in the next section.

Here is a brief d ...
````

### pilot-005

Can I use a list as a dictionary key? What is different about a tuple containing only strings?

**bm25: py313-datastructures, lines 497-514**

````text
"associative memories" or "associative arrays".  Unlike sequences, which are
indexed by a range of numbers, dictionaries are indexed by *keys*, which can be
any immutable type; strings and numbers can always be keys.  Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains
any mutable object either directly or indirectly, it cannot be used as a key.
You can't use lists as keys, since lists can be modified in place using index
assignments, slice assignments, or methods like list.append and
list.extend.

It is best to think of a dictionary as a set of *key: value* pairs,
with the requirement that the key ...
````

**dense: py313-datastructures, lines 497-514**

````text
"associative memories" or "associative arrays".  Unlike sequences, which are
indexed by a range of numbers, dictionaries are indexed by *keys*, which can be
any immutable type; strings and numbers can always be keys.  Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains
any mutable object either directly or indirectly, it cannot be used as a key.
You can't use lists as keys, since lists can be modified in place using index
assignments, slice assignments, or methods like list.append and
list.extend.

It is best to think of a dictionary as a set of *key: value* pairs,
with the requirement that the key ...
````

**hybrid: py313-datastructures, lines 497-514**

````text
"associative memories" or "associative arrays".  Unlike sequences, which are
indexed by a range of numbers, dictionaries are indexed by *keys*, which can be
any immutable type; strings and numbers can always be keys.  Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains
any mutable object either directly or indirectly, it cannot be used as a key.
You can't use lists as keys, since lists can be modified in place using index
assignments, slice assignments, or methods like list.append and
list.extend.

It is best to think of a dictionary as a set of *key: value* pairs,
with the requirement that the key ...
````

### pilot-006

If processing a file raises an exception, how can I ensure the file gets closed?

**bm25: py313-inputoutput, lines 347-384**

````text
after its suite finishes, even if an exception is raised at some
point.  Using with is also much shorter than writing
equivalent try\ -\ finally blocks::

    >>> with open('workfile', encoding="utf-8") as f:
    ...     read_data = f.read()

    >>> # We can check that the file has been automatically closed.
    >>> f.closed
    True

If you're not using the with keyword, then you should call
f.close() to close the file and immediately free up any system
resources used by it.

   Calling f.write() without using the with keyword or calling
   f.close() **might** result in the arguments
   of f.write() not being completely written to the disk, ...
````

**dense: py313-inputoutput, lines 347-384**

````text
after its suite finishes, even if an exception is raised at some
point.  Using with is also much shorter than writing
equivalent try\ -\ finally blocks::

    >>> with open('workfile', encoding="utf-8") as f:
    ...     read_data = f.read()

    >>> # We can check that the file has been automatically closed.
    >>> f.closed
    True

If you're not using the with keyword, then you should call
f.close() to close the file and immediately free up any system
resources used by it.

   Calling f.write() without using the with keyword or calling
   f.close() **might** result in the arguments
   of f.write() not being completely written to the disk, ...
````

**hybrid: py313-inputoutput, lines 347-384**

````text
after its suite finishes, even if an exception is raised at some
point.  Using with is also much shorter than writing
equivalent try\ -\ finally blocks::

    >>> with open('workfile', encoding="utf-8") as f:
    ...     read_data = f.read()

    >>> # We can check that the file has been automatically closed.
    >>> f.closed
    True

If you're not using the with keyword, then you should call
f.close() to close the file and immediately free up any system
resources used by it.

   Calling f.write() without using the with keyword or calling
   f.close() **might** result in the arguments
   of f.write() not being completely written to the disk, ...
````

### pilot-007

What does adding b to a file mode change, and can I specify encoding in that mode?

**bm25: py313-inputoutput, lines 330-350**

````text
(see open).
Because UTF-8 is the modern de-facto standard, encoding="utf-8" is
recommended unless you know that you need to use a different encoding.
Appending a 'b' to the mode opens the file in binary mode.
Binary mode data is read and written as bytes objects.
You can not specify *encoding* when opening file in binary mode.

In text mode, the default when reading is to convert platform-specific line
endings (\n on Unix, \r\n on Windows) to just \n.  When writing in
text mode, the default is to convert occurrences of \n back to
platform-specific line endings.  This behind-the-scenes modification
to file data is fine for text files, but will ...
````

**dense: py313-inputoutput, lines 330-350**

````text
(see open).
Because UTF-8 is the modern de-facto standard, encoding="utf-8" is
recommended unless you know that you need to use a different encoding.
Appending a 'b' to the mode opens the file in binary mode.
Binary mode data is read and written as bytes objects.
You can not specify *encoding* when opening file in binary mode.

In text mode, the default when reading is to convert platform-specific line
endings (\n on Unix, \r\n on Windows) to just \n.  When writing in
text mode, the default is to convert occurrences of \n back to
platform-specific line endings.  This behind-the-scenes modification
to file data is fine for text files, but will ...
````

**hybrid: py313-inputoutput, lines 330-350**

````text
(see open).
Because UTF-8 is the modern de-facto standard, encoding="utf-8" is
recommended unless you know that you need to use a different encoding.
Appending a 'b' to the mode opens the file in binary mode.
Binary mode data is read and written as bytes objects.
You can not specify *encoding* when opening file in binary mode.

In text mode, the default when reading is to convert platform-specific line
endings (\n on Unix, \r\n on Windows) to just \n.  When writing in
text mode, the default is to convert occurrences of \n back to
platform-specific line endings.  This behind-the-scenes modification
to file data is fine for text files, but will ...
````

### pilot-008

Stdlib JSON to a file and back: which calls do I use, rather than getting a JSON string?

**bm25: py313-inputoutput, lines 486-506**

````text
effort, since the io.TextIOBase.read method only returns strings, which will have to
be passed to a function like int, which takes a string like '123'
and returns its numeric value 123.  When you want to save more complex data
types like nested lists and dictionaries, parsing and serializing by hand
becomes complicated.

Rather than having users constantly writing and debugging code to save
complicated data types to files, Python allows you to use the popular data
interchange format called JSON (JavaScript Object Notation).  The standard module called json can take Python
data hierarchies, and convert them to string representations; this proc ...
````

**dense: py313-inputoutput, lines 503-535**

````text
The JSON format is commonly used by modern applications to allow for data
   exchange.  Many programmers are already familiar with it, which makes
   it a good choice for interoperability.

If you have an object x, you can view its JSON string representation with a
simple line of code::

   >>> import json
   >>> x = [1, 'simple', 'list']
   >>> json.dumps(x)
   '[1, "simple", "list"]'

Another variant of the json.dumps function, called json.dump,
simply serializes the object to a text file.  So if f is a
text file object opened for writing, we can do this::

   json.dump(x, f)

To decode the object again, if f is a binary file or
text file o ...
````

**hybrid: py313-inputoutput, lines 486-506**

````text
effort, since the io.TextIOBase.read method only returns strings, which will have to
be passed to a function like int, which takes a string like '123'
and returns its numeric value 123.  When you want to save more complex data
types like nested lists and dictionaries, parsing and serializing by hand
becomes complicated.

Rather than having users constantly writing and debugging code to save
complicated data types to files, Python allows you to use the popular data
interchange format called JSON (JavaScript Object Notation).  The standard module called json can take Python
data hierarchies, and convert them to string representations; this proc ...
````

### pilot-009

I named my script random.py and now importing random finds my file. How can a local file take priority over the standard library?

**bm25: py313-modules, lines 480-505**

````text
exception is raised.

Contrarily, when using syntax like import item.subitem.subsubitem, each item
except for the last must be a package; the last item can be a module or a
package but can't be a class or function or variable defined in the previous
item.



Importing \* From a Package


Now what happens when the user writes from sound.effects import *?  Ideally,
one would hope that this somehow goes out to the filesystem, finds which
submodules are present in the package, and imports them all.  This could take a
long time and importing sub-modules might have unwanted side-effects that should
only happen when the sub-module is explicitly impo ...
````

**dense: py313-modules, lines 163-198**

````text
executed as the "main" file:


   $ python fibo.py 50
   0 1 1 2 3 5 8 13 21 34

If the module is imported, the code is not run::

   >>> import fibo
   >>>

This is often used either to provide a convenient user interface to a module, or
for testing purposes (running the module as a script executes a test suite).



The Module Search Path


When a module named spam is imported, the interpreter first searches for
a built-in module with that name. These module names are listed in
sys.builtin_module_names. If not found, it then searches for a file
named spam.py in a list of directories given by the variable
sys.path.  sys.path is initialized fr ...
````

**hybrid: py313-modules, lines 163-198**

````text
executed as the "main" file:


   $ python fibo.py 50
   0 1 1 2 3 5 8 13 21 34

If the module is imported, the code is not run::

   >>> import fibo
   >>>

This is often used either to provide a convenient user interface to a module, or
for testing purposes (running the module as a script executes a test suite).



The Module Search Path


When a module named spam is imported, the interpreter first searches for
a built-in module with that name. These module names are listed in
sys.builtin_module_names. If not found, it then searches for a file
named spam.py in a list of directories given by the variable
sys.path.  sys.path is initialized fr ...
````

### pilot-010

CLI + importable module: how do I stop command-line handling from running when the file is imported?

**bm25: py313-modules, lines 129-174**

````text
>>> from fibo import fib as fibonacci
   >>> fibonacci(500)
   0 1 1 2 3 5 8 13 21 34 55 89 144 233 377



   For efficiency reasons, each module is only imported once per interpreter
   session.  Therefore, if you change your modules, you must restart the
   interpreter -- or, if it's just one module you want to test interactively,
   use importlib.reload, e.g. import importlib;
   importlib.reload(modulename).



Executing modules as scripts

When you run a Python module with ::

   python fibo.py <arguments>

the code in the module will be executed, just as if you imported it, but with
the __name__ set to "__main__".  That means that by ad ...
````

**dense: py313-interpreter, lines 30-50**

````text
Typing an end-of-file character (Control-D on Unix, Control-Z on
Windows) at the primary prompt causes the interpreter to exit with a zero exit
status.  If that doesn't work, you can exit the interpreter by typing the
following command: quit().

The interpreter's line-editing features include interactive editing, history
substitution and code completion on systems that support the GNU Readline library.
Perhaps the quickest check to see whether command line editing is supported is
typing Control-P to the first Python prompt you get.  If it beeps, you
have command line editing; see Appendix tut-interacting for an
introduction to the keys.  If n ...
````

**hybrid: py313-modules, lines 129-174**

````text
>>> from fibo import fib as fibonacci
   >>> fibonacci(500)
   0 1 1 2 3 5 8 13 21 34 55 89 144 233 377



   For efficiency reasons, each module is only imported once per interpreter
   session.  Therefore, if you change your modules, you must restart the
   interpreter -- or, if it's just one module you want to test interactively,
   use importlib.reload, e.g. import importlib;
   importlib.reload(modulename).



Executing modules as scripts

When you run a Python module with ::

   python fibo.py <arguments>

the code in the module will be executed, just as if you imported it, but with
the __name__ set to "__main__".  That means that by ad ...
````

### pilot-011

Why does 0.1 + 0.1 + 0.1 fail an equlity check with 0.3, and what comparison helper can I use?

**bm25: py313-inputoutput, lines 347-384**

````text
after its suite finishes, even if an exception is raised at some
point.  Using with is also much shorter than writing
equivalent try\ -\ finally blocks::

    >>> with open('workfile', encoding="utf-8") as f:
    ...     read_data = f.read()

    >>> # We can check that the file has been automatically closed.
    >>> f.closed
    True

If you're not using the with keyword, then you should call
f.close() to close the file and immediately free up any system
resources used by it.

   Calling f.write() without using the with keyword or calling
   f.close() **might** result in the arguments
   of f.write() not being completely written to the disk, ...
````

**dense: py313-floatingpoint, lines 133-160**

````text
>>> math.isclose(0.1 + 0.1 + 0.1, 0.3)
   True

Alternatively, the round function can be used to compare rough
approximations:


   >>> round(math.pi, ndigits=2) == round(22 / 7, ndigits=2)
   True

Binary floating-point arithmetic holds many surprises like this.  The problem
with "0.1" is explained in precise detail below, in the "Representation Error"
section.  See Examples of Floating Point Problems for
a pleasant summary of how binary floating point works and the kinds of
problems commonly encountered in practice.  Also see
The Perils of Floating Point
for a more complete account of other common surprises.

As that says near the end, "the ...
````

**hybrid: py313-datastructures, lines 715-734**

````text
(1, 2, 3)              < (1, 2, 4)
   [1, 2, 3]              < [1, 2, 4]
   'ABC' < 'C' < 'Pascal' < 'Python'
   (1, 2, 3, 4)           < (1, 2, 4)
   (1, 2)                 < (1, 2, -1)
   (1, 2, 3)             == (1.0, 2.0, 3.0)
   (1, 2, ('aa', 'ab'))   < (1, 2, ('abc', 'a'), 4)

Note that comparing objects of different types with < or > is legal
provided that the objects have appropriate comparison methods.  For example,
mixed numeric types are compared according to their numeric value, so 0 equals
0.0, etc.  Otherwise, rather than providing an arbitrary ordering, the
interpreter will raise a TypeError exception.



       chaining, such  ...
````

### pilot-012

Two Python apps need diferent versions of the same package. How do I keep an upgrade for one from breaking the other?

**bm25: py313-venv, lines 110-143**

````text
(tutorial-env) $ python -m pip install novas
  Collecting novas
    Downloading novas-3.1.1.3.tar.gz (136kB)
  Installing collected packages: novas
    Running setup.py install for novas
  Successfully installed novas-3.1.1.3

You can also install a specific version of a package by giving the
package name  followed by == and the version number:


  (tutorial-env) $ python -m pip install requests==2.6.0
  Collecting requests==2.6.0
    Using cached requests-2.6.0-py2.py3-none-any.whl
  Installing collected packages: requests
  Successfully installed requests-2.6.0

If you re-run this command, pip will notice that the requested
version is alrea ...
````

**dense: py313-venv, lines 1-28**

````text
Virtual Environments and Packages

Introduction

Python applications will often use packages and modules that don't
come as part of the standard library.  Applications will sometimes
need a specific version of a library, because the application may
require that a particular bug has been fixed or the application may be
written using an obsolete version of the library's interface.

This means it may not be possible for one Python installation to meet
the requirements of every application.  If application A needs version
1.0 of a particular module but application B needs version 2.0, then
the requirements are in conflict and installing either ve ...
````

**hybrid: py313-venv, lines 110-143**

````text
(tutorial-env) $ python -m pip install novas
  Collecting novas
    Downloading novas-3.1.1.3.tar.gz (136kB)
  Installing collected packages: novas
    Running setup.py install for novas
  Successfully installed novas-3.1.1.3

You can also install a specific version of a package by giving the
package name  followed by == and the version number:


  (tutorial-env) $ python -m pip install requests==2.6.0
  Collecting requests==2.6.0
    Using cached requests-2.6.0-py2.py3-none-any.whl
  Installing collected packages: requests
  Successfully installed requests-2.6.0

If you re-run this command, pip will notice that the requested
version is alrea ...
````

### pilot-013

When does a for-loop else clause execute, and does it run after break?

**bm25: py313-controlflow, lines 228-258**

````text
...
   2 is a prime number
   3 is a prime number
   4 equals 2 * 2
   5 is a prime number
   6 equals 2 * 3
   7 is a prime number
   8 equals 2 * 4
   9 equals 3 * 3

(Yes, this is the correct code.  Look closely: the else clause belongs to
the for loop, **not** the if statement.)

One way to think of the else clause is to imagine it paired with the if
inside the loop.  As the loop executes, it will run a sequence like
if/if/if/else. The if is inside the loop, encountered a number of times. If
the condition is ever true, a break will happen. If the condition is never
true, the else clause outside the loop will execute.

When used with a loo ...
````

**dense: py313-controlflow, lines 205-237**

````text
executing the break, the else clause executes.

In a for loop, the else clause is executed
after the loop finishes its final iteration, that is, if no break occurred.

In a while loop, it's executed after the loop's condition becomes false.

In either kind of loop, the else clause is **not** executed if the
loop was terminated by a break.  Of course, other ways of ending the
loop early, such as a return or a raised exception, will also skip
execution of the else clause.

This is exemplified in the following for loop,
which searches for prime numbers::

   >>> for n in range(2, 10):
   ...     for x in range(2, n):
   ...         if n % x == 0 ...
````

**hybrid: py313-controlflow, lines 205-237**

````text
executing the break, the else clause executes.

In a for loop, the else clause is executed
after the loop finishes its final iteration, that is, if no break occurred.

In a while loop, it's executed after the loop's condition becomes false.

In either kind of loop, the else clause is **not** executed if the
loop was terminated by a break.  Of course, other ways of ending the
loop early, such as a return or a raised exception, will also skip
execution of the else clause.

This is exemplified in the following for loop,
which searches for prime numbers::

   >>> for n in range(2, 10):
   ...     for x in range(2, n):
   ...         if n % x == 0 ...
````

### pilot-014

What tells a for loop to stop when an itterator has no more values, and how do I request its next value manually?

**bm25: py313-classes, lines 785-820**

````text
using a for statement::

   for element in [1, 2, 3]:
       print(element)
   for element in (1, 2, 3):
       print(element)
   for key in {'one':1, 'two':2}:
       print(key)
   for char in "123":
       print(char)
   for line in open("myfile.txt"):
       print(line, end='')

This style of access is clear, concise, and convenient.  The use of iterators
pervades and unifies Python.  Behind the scenes, the for statement
calls iter on the container object.  The function returns an iterator
object that defines the method iterator.__next__ which accesses
elements in the container one at a time.  When there are no more elements,
iterator.__ne ...
````

**dense: py313-classes, lines 811-861**

````text
>>> next(it)
   'a'
   >>> next(it)
   'b'
   >>> next(it)
   'c'
   >>> next(it)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
       next(it)
   StopIteration

Having seen the mechanics behind the iterator protocol, it is easy to add
iterator behavior to your classes.  Define an container.__iter__ method which
returns an object with a iterator.__next__ method.  If the class
defines __next__, then __iter__ can just return self::

   class Reverse:
       """Iterator for looping over a sequence backwards."""
       def __init__(self, data):
           self.data = data
           self.index = len(data)

        ...
````

**hybrid: py313-classes, lines 785-820**

````text
using a for statement::

   for element in [1, 2, 3]:
       print(element)
   for element in (1, 2, 3):
       print(element)
   for key in {'one':1, 'two':2}:
       print(key)
   for char in "123":
       print(char)
   for line in open("myfile.txt"):
       print(line, end='')

This style of access is clear, concise, and convenient.  The use of iterators
pervades and unifies Python.  Behind the scenes, the for statement
calls iter on the container object.  The function returns an iterator
object that defines the method iterator.__next__ which accesses
elements in the container one at a time.  When there are no more elements,
iterator.__ne ...
````

### pilot-015

A function default list retains old items, and a class-level list is shared by instances. Explain each cause and how to make the lists independent.

**bm25: py313-classes, lines 389-423**

````text
are packed into a method object.  When the method object is called
with an argument list, a new argument list is constructed from the instance
object and the argument list, and the function object is called with this new
argument list.



Class and Instance Variables

Generally speaking, instance variables are for data unique to each instance
and class variables are for attributes and methods shared by all instances
of the class::

    class Dog:

        kind = 'canine'         # class variable shared by all instances

        def __init__(self, name):
            self.name = name    # instance variable unique to each instance

    >>> d = D ...
````

**dense: py313-classes, lines 389-423**

````text
are packed into a method object.  When the method object is called
with an argument list, a new argument list is constructed from the instance
object and the argument list, and the function object is called with this new
argument list.



Class and Instance Variables

Generally speaking, instance variables are for data unique to each instance
and class variables are for attributes and methods shared by all instances
of the class::

    class Dog:

        kind = 'canine'         # class variable shared by all instances

        def __init__(self, name):
            self.name = name    # instance variable unique to each instance

    >>> d = D ...
````

**hybrid: py313-classes, lines 389-423**

````text
are packed into a method object.  When the method object is called
with an argument list, a new argument list is constructed from the instance
object and the argument list, and the function object is called with this new
argument list.



Class and Instance Variables

Generally speaking, instance variables are for data unique to each instance
and class variables are for attributes and methods shared by all instances
of the class::

    class Dog:

        kind = 'canine'         # class variable shared by all instances

        def __init__(self, name):
            self.name = name    # instance variable unique to each instance

    >>> d = D ...
````

### pilot-016

Why can ordinary floats surprise me with decimal equality, and which standard-library numeric type is useful when exact decimal representation matters for money?

**bm25: py313-floatingpoint, lines 238-268**

````text
>>> arr = [-0.10430216751806065, -266310978.67179024, 143401161448607.16,
   ...        -143401161400469.7, 266262841.31058735, -0.003244936839808227]
   >>> float(sum(map(Fraction, arr)))   # Exact summation with single rounding
   8.042173697819788e-13
   >>> math.fsum(arr)                   # Single rounding
   8.042173697819788e-13
   >>> sum(arr)                         # Multiple roundings in extended precision
   8.042178034628478e-13
   >>> total = 0.0
   >>> for x in arr:
   ...     total += x                   # Multiple roundings in standard precision
   ...
   >>> total                            # Straight addition has no correct ...
````

**dense: py313-floatingpoint, lines 178-218**

````text
at the NumPy package and many other packages for mathematical and
statistical operations supplied by the SciPy project. See <https://scipy.org>.

Python provides tools that may help on those rare occasions when you really
*do* want to know the exact value of a float.  The
float.as_integer_ratio method expresses the value of a float as a
fraction:


   >>> x = 3.14159
   >>> x.as_integer_ratio()
   (3537115888337719, 1125899906842624)

Since the ratio is exact, it can be used to losslessly recreate the
original value:


    >>> x == 3537115888337719 / 1125899906842624
    True

The float.hex method expresses a float in hexadecimal (base
16), a ...
````

**hybrid: py313-stdlib2, lines 373-406**

````text
>>> from decimal import *
   >>> round(Decimal('0.70') * Decimal('1.05'), 2)
   Decimal('0.74')
   >>> round(.70 * 1.05, 2)
   0.73

The decimal.Decimal result keeps a trailing zero, automatically
inferring four place significance from multiplicands with two place
significance.  Decimal reproduces mathematics as done by hand and avoids
issues that can arise when binary floating point cannot exactly represent
decimal quantities.

Exact representation enables the decimal.Decimal class to perform
modulo calculations and equality tests that are unsuitable for binary floating
point::

   >>> Decimal('1.00') % Decimal('.10')
   Decimal('0.00')
   > ...
````

### pilot-017

How do I use pandas groupby to compute the median salary in each department?

**bm25: py313-classes, lines 726-762**

````text
Notice that code passed to exec() or eval() does not consider the
classname of the invoking class to be the current class; this is similar to the
effect of the global statement, the effect of which is likewise restricted
to code that is byte-compiled together.  The same restriction applies to
getattr(), setattr() and delattr(), as well as when referencing
__dict__ directly.



Odds and Ends

Sometimes it is useful to have a data type similar to the Pascal "record" or C
"struct", bundling together a few named data items. The idiomatic approach
is to use dataclasses for this purpose::

    from dataclasses import dataclass

    @dataclass
    c ...
````

**dense: py313-stdlib, lines 141-181**

````text
floating-point math::

   >>> import math
   >>> math.cos(math.pi / 4)
   0.70710678118654757
   >>> math.log(1024, 2)
   10.0

The random module provides tools for making random selections::

   >>> import random
   >>> random.choice(['apple', 'pear', 'banana'])
   'apple'
   >>> random.sample(range(100), 10)   # sampling without replacement
   [30, 83, 16, 4, 8, 81, 41, 50, 18, 33]
   >>> random.random()    # random float from the interval [0.0, 1.0)
   0.17970987693706186
   >>> random.randrange(6)    # random integer chosen from range(6)
   4

The statistics module calculates basic statistical properties
(the mean, median, variance, etc.) ...
````

**hybrid: py313-stdlib, lines 141-181**

````text
floating-point math::

   >>> import math
   >>> math.cos(math.pi / 4)
   0.70710678118654757
   >>> math.log(1024, 2)
   10.0

The random module provides tools for making random selections::

   >>> import random
   >>> random.choice(['apple', 'pear', 'banana'])
   'apple'
   >>> random.sample(range(100), 10)   # sampling without replacement
   [30, 83, 16, 4, 8, 81, 41, 50, 18, 33]
   >>> random.random()    # random float from the interval [0.0, 1.0)
   0.17970987693706186
   >>> random.randrange(6)    # random integer chosen from range(6)
   4

The statistics module calculates basic statistical properties
(the mean, median, variance, etc.) ...
````

### pilot-018

Which scikit-learn GridSearchCV parameters control cross-validation and parallel execution?

**bm25: py313-errors, lines 508-536**

````text
problem was encountered while processing the lines. Objects which, like files,
provide predefined clean-up actions will indicate this in their documentation.



Raising and Handling Multiple Unrelated Exceptions

There are situations where it is necessary to report several exceptions that
have occurred. This is often the case in concurrency frameworks, when several
tasks may have failed in parallel, but there are also other use cases where
it is desirable to continue execution and collect multiple errors rather than
raise the first exception.

The builtin ExceptionGroup wraps a list of exception instances so
that they can be raised together.  ...
````

**dense: py313-modules, lines 318-332**

````text
'__stderr__', '__stdin__', '__stdout__', '__unraisablehook__',
    '_clear_type_cache', '_current_frames', '_debugmallocstats', '_framework',
    '_getframe', '_git', '_home', '_xoptions', 'abiflags', 'addaudithook',
    'api_version', 'argv', 'audit', 'base_exec_prefix', 'base_prefix',
    'breakpointhook', 'builtin_module_names', 'byteorder', 'call_tracing',
    'callstats', 'copyright', 'displayhook', 'dont_write_bytecode', 'exc_info',
    'excepthook', 'exec_prefix', 'executable', 'exit', 'flags', 'float_info',
    'float_repr_style', 'get_asyncgen_hooks', 'get_coroutine_origin_tracking_depth',
    'getallocatedblocks', 'getdefaultencodin ...
````

**hybrid: py313-stdlib, lines 240-283**

````text
tarfile. ::

   >>> import zlib
   >>> s = b'witch which has which witches wrist watch'
   >>> len(s)
   41
   >>> t = zlib.compress(s)
   >>> len(t)
   37
   >>> zlib.decompress(t)
   b'witch which has which witches wrist watch'
   >>> zlib.crc32(s)
   226805979



Performance Measurement

Some Python users develop a deep interest in knowing the relative performance of
different approaches to the same problem. Python provides a measurement tool
that answers those questions immediately.

For example, it may be tempting to use the tuple packing and unpacking feature
instead of the traditional approach to swapping arguments. The timeit
module q ...
````

### pilot-019

How do I create a PostgreSQL index that speeds up searching a JSONB field?

**bm25: py313-introduction, lines 275-306**

````text
In addition to indexing, *slicing* is also supported.  While indexing is used
to obtain individual characters, *slicing* allows you to obtain a substring::

   >>> word[0:2]  # characters from position 0 (included) to 2 (excluded)
   'Py'
   >>> word[2:5]  # characters from position 2 (included) to 5 (excluded)
   'tho'

Slice indices have useful defaults; an omitted first index defaults to zero, an
omitted second index defaults to the size of the string being sliced. ::

   >>> word[:2]   # character from the beginning to position 2 (excluded)
   'Py'
   >>> word[4:]   # characters from position 4 (included) to the end
   'on'
   >>> word[-2 ...
````

**dense: py313-stdlib2, lines 294-329**

````text
performance trade-offs.

The array module provides an array.array object that is like
a list that stores only homogeneous data and stores it more compactly.  The
following example shows an array of numbers stored as two byte unsigned binary
numbers (typecode "H") rather than the usual 16 bytes per entry for regular
lists of Python int objects::

   >>> from array import array
   >>> a = array('H', [4000, 10, 700, 22222])
   >>> sum(a)
   26932
   >>> a[1:3]
   array('H', [10, 700])

The collections module provides a collections.deque object
that is like a list with faster appends and pops from the left side but slower
lookups in the middle. T ...
````

**hybrid: py313-controlflow, lines 65-108**

````text
>>> for w in words:
   ...     print(w, len(w))
   ...
   cat 3
   window 6
   defenestrate 12

Code that modifies a collection while iterating over that same collection can
be tricky to get right.  Instead, it is usually more straight-forward to loop
over a copy of the collection or to create a new collection::

    # Create a sample collection
    users = {'Hans': 'active', 'Éléonore': 'inactive', '景太郎': 'active'}

    # Strategy:  Iterate over a copy
    for user, status in users.copy().items():
        if status == 'inactive':
            del users[user]

    # Strategy:  Create a new collection
    active_users = {}
    for user, status  ...
````

### pilot-020

Which Qdrant collection settings should I choose for text-embedding-3-small vectors?

**bm25: py313-controlflow, lines 65-108**

````text
>>> for w in words:
   ...     print(w, len(w))
   ...
   cat 3
   window 6
   defenestrate 12

Code that modifies a collection while iterating over that same collection can
be tricky to get right.  Instead, it is usually more straight-forward to loop
over a copy of the collection or to create a new collection::

    # Create a sample collection
    users = {'Hans': 'active', 'Éléonore': 'inactive', '景太郎': 'active'}

    # Strategy:  Iterate over a copy
    for user, status in users.copy().items():
        if status == 'inactive':
            del users[user]

    # Strategy:  Create a new collection
    active_users = {}
    for user, status  ...
````

**dense: py313-stdlib2, lines 30-63**

````text
...     'yellow'], 'blue']]]
   ...
   >>> pprint.pprint(t, width=30)
   [[[['black', 'cyan'],
      'white',
      ['green', 'red']],
     [['magenta', 'yellow'],
      'blue']]]

The textwrap module formats paragraphs of text to fit a given screen
width::

   >>> import textwrap
   >>> doc = """The wrap() method is just like fill() except that it returns
   ... a list of strings instead of one big string with newlines to separate
   ... the wrapped lines."""
   ...
   >>> print(textwrap.fill(doc, width=40))
   The wrap() method is just like fill()
   except that it returns a list of strings
   instead of one big string with newlines
   to s ...
````

**hybrid: py313-classes, lines 908-937**

````text
versatile than full generator definitions and tend to be more memory friendly
than equivalent list comprehensions.

Examples::

   >>> sum(i*i for i in range(10))                 # sum of squares
   285

   >>> xvec = [10, 20, 30]
   >>> yvec = [7, 5, 3]
   >>> sum(x*y for x,y in zip(xvec, yvec))         # dot product
   260

   >>> unique_words = set(word for line in page  for word in line.split())

   >>> valedictorian = max((student.gpa, student.name) for student in graduates)

   >>> data = 'golf'
   >>> list(data[i] for i in range(len(data)-1, -1, -1))
   ['f', 'l', 'o', 'g']




   object.__dict__ which returns the dictionary used to im ...
````

## Limits and next stage

All four unanswerable questions can still retrieve candidates. Neither cosine similarity nor RRF is an answerability guarantee. Seed-passage hits can miss sufficient subpassages or alternative evidence and do not establish multi-part answer completeness. The pooled candidates are saved in pool.jsonl as unjudged; review them before calculating nDCG, MRR or gold recall. Keep separate held-out questions for later generalization checks.
