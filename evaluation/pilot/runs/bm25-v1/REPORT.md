# Keyword baseline development run

This run uses the frozen Python tutorial corpus and 20 AI-reviewed development questions. It makes no API calls. Results describe known source-evidence coverage, not answer accuracy or a held-out benchmark.

- Source documents: 12; searchable chunks: 250.
- Complete known-passage hit at 5: 68.8% of 16 answerable questions.
- Complete known-passage hit at 10: 81.2%.
- Mean known-passage character coverage at 10: 81.4%.
- Local warm retrieval median / p95: 0.169 / 0.223 ms. These exclude ingestion and answer generation.
- Unanswerable questions returning candidates: 4/4. Lexical matches are not evidence that these questions are answerable.

## What these numbers mean

A hit requires the union of retrieved source intervals to cover an entire annotated positive passage, not just touch it. Overlaps are counted once. Any one known passage is sufficient for the hit diagnostic, so this does not establish complete answers for multi-part questions. The separate character-coverage diagnostic averages coverage over annotated passages; some are alternatives and some are complementary. Unlabeled passages remain unjudged. There are no nDCG, MRR, gold recall, or generation scores yet.

## Per-question diagnostics

| Question | Category | Hit at 5 | Hit at 10 | Passage coverage at 10 |
|---|---|---|---|---|
| pilot-001 | paraphrase | yes | yes | 100.0% |
| pilot-002 | exact_term | yes | yes | 100.0% |
| pilot-003 | typo | yes | yes | 100.0% |
| pilot-004 | exact_term | yes | yes | 100.0% |
| pilot-005 | paraphrase | no | no | 79.6% |
| pilot-006 | paraphrase | yes | yes | 100.0% |
| pilot-007 | exact_term | yes | yes | 100.0% |
| pilot-008 | shorthand | yes | yes | 100.0% |
| pilot-009 | paraphrase | no | yes | 100.0% |
| pilot-010 | shorthand | yes | yes | 100.0% |
| pilot-011 | typo | no | no | 0.0% |
| pilot-012 | typo | no | no | 0.0% |
| pilot-013 | exact_term | yes | yes | 100.0% |
| pilot-014 | typo | yes | yes | 100.0% |
| pilot-015 | multi_evidence | yes | yes | 89.6% |
| pilot-016 | multi_evidence | no | yes | 33.3% |
| pilot-017 | unanswerable | n/a | n/a | n/a |
| pilot-018 | unanswerable | n/a | n/a | n/a |
| pilot-019 | unanswerable | n/a | n/a | n/a |
| pilot-020 | unanswerable | n/a | n/a | n/a |

## Inspect the retrieved evidence

Source excerpts below retain the Python Software Foundation attribution and PSF-2.0 license described in run.json and evaluation/pilot/ATTRIBUTION.md. Line numbers refer to the pinned source files, not PDF pages.

### pilot-001

Removing the oldest item from my Python list keeps getting slower as the list grows. What should I use for a FIFO queue, and why?

**Rank 1: py313-datastructures, source lines 145-183** (BM25 17.915)

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

**Rank 2: py313-venv, source lines 48-81** (BM25 16.072)

````text
This will create the tutorial-env directory if it doesn't exist,
and also create directories inside it containing a copy of the Python
interpreter and various supporting files.

A common directory location for a virtual environment is .venv.
This name keeps the directory typically hidden in your shell and thus
out of the way while giving it a name that explains why the directory
exists. It also prevents clashing with .env environment variable
definition files that some tooling supports.

Once you've created a virtual environment, you may activate it.

On Windows, run::

  tutorial-env\Scripts\activate

On Unix or MacOS, run::

  source tutori ...
````

**Rank 3: py313-modules, source lines 480-505** (BM25 13.976)

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

### pilot-002

Why does a function with a default argument L=[] keep values from previous calls, and how do I give calls that omit L a fresh list?

**Rank 1: py313-controlflow, source lines 595-641** (BM25 24.680)

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

**Rank 2: py313-controlflow, source lines 629-670** (BM25 16.847)

````text
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



Keyword Arguments

Functions can also be called using keyword arguments
of the form kwarg=value.  For instance, the following function::

   def parrot(voltage, state='a stiff', action='voom', type='Norwegian Blue'):
       print("-- This parrot wouldn't", action, end=' ')
       print("if you put", voltage, "volts through it. ...
````

**Rank 3: py313-controlflow, source lines 563-601** (BM25 14.345)

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

### pilot-003

Why did my list become None after I assinged the result of list.sort() back to it?

**Rank 1: py313-datastructures, source lines 116-147** (BM25 13.164)

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

**Rank 2: py313-controlflow, source lines 520-550** (BM25 11.137)

````text
0 1 1 2 3 5 8 13 21 34 55 89

Coming from other languages, you might object that fib is not a function but
a procedure since it doesn't return a value.  In fact, even functions without a
return statement do return a value, albeit a rather boring one.  This
value is called None (it's a built-in name).  Writing the value None is
normally suppressed by the interpreter if it would be the only value written.
You can see it if you really want to using print::

   >>> fib(0)
   >>> print(fib(0))
   None

It is simple to write a function that returns a list of the numbers of the
Fibonacci series, instead of printing it::

   >>> def fib2(n):  # retur ...
````

**Rank 3: py313-controlflow, source lines 545-569** (BM25 10.999)

````text
>>> f100 = fib2(100)    # call it
   >>> f100                # write the result
   [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

This example, as usual, demonstrates some new Python features:

* The return statement returns with a value from a function.
  return without an expression argument returns None. Falling off
  the end of a function also returns None.

* The statement result.append(a) calls a *method* of the list object
  result.  A method is a function that 'belongs' to an object and is named
  obj.methodname, where obj is some object (this may be an expression),
  and methodname is the name of a method that is defined by the object's  ...
````

### pilot-004

How do I create an empty set, and why does {} not do that?

**Rank 1: py313-datastructures, source lines 439-470** (BM25 14.735)

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

**Rank 2: py313-datastructures, source lines 614-661** (BM25 10.645)

````text
>>> basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']
   >>> for i in sorted(basket):
   ...     print(i)
   ...
   apple
   apple
   banana
   orange
   orange
   pear

Using set on a sequence eliminates duplicate elements. The use of
sorted in combination with set over a sequence is an idiomatic
way to loop over unique elements of the sequence in sorted order. ::

   >>> basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']
   >>> for f in sorted(set(basket)):
   ...     print(f)
   ...
   apple
   banana
   orange
   pear

It is sometimes tempting to change a list while you are looping over it;
however, it is of ...
````

**Rank 3: py313-classes, source lines 56-79** (BM25 9.982)

````text
Python Scopes and Namespaces

Before introducing classes, I first have to tell you something about Python's
scope rules.  Class definitions play some neat tricks with namespaces, and you
need to know how scopes and namespaces work to fully understand what's going on.
Incidentally, knowledge about this subject is useful for any advanced Python
programmer.

Let's begin with some definitions.

A *namespace* is a mapping from names to objects.  Most namespaces are currently
implemented as Python dictionaries, but that's normally not noticeable in any
way (except for performance), and it may change in the future.  Examples of
namespaces are: the s ...
````

### pilot-005

Can I use a list as a dictionary key? What is different about a tuple containing only strings?

**Rank 1: py313-datastructures, source lines 497-514** (BM25 22.217)

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

**Rank 2: py313-datastructures, source lines 513-549** (BM25 14.712)

````text
extracting the value given the key.  It is also possible to delete a key:value
pair with del. If you store using a key that is already in use, the old
value associated with that key is forgotten.  It is an error to extract a value
using a non-existent key.

Performing list(d) on a dictionary returns a list of all the keys
used in the dictionary, in insertion order (if you want it sorted, just use
sorted(d) instead). To check whether a single key is in the
dictionary, use the in keyword.

Here is a small example using a dictionary::

   >>> tel = {'jack': 4098, 'sape': 4139}
   >>> tel['guido'] = 4127
   >>> tel
   {'jack': 4098, 'sape': 4139, ...
````

**Rank 3: py313-classes, source lines 56-79** (BM25 13.516)

````text
Python Scopes and Namespaces

Before introducing classes, I first have to tell you something about Python's
scope rules.  Class definitions play some neat tricks with namespaces, and you
need to know how scopes and namespaces work to fully understand what's going on.
Incidentally, knowledge about this subject is useful for any advanced Python
programmer.

Let's begin with some definitions.

A *namespace* is a mapping from names to objects.  Most namespaces are currently
implemented as Python dictionaries, but that's normally not noticeable in any
way (except for performance), and it may change in the future.  Examples of
namespaces are: the s ...
````

### pilot-006

If processing a file raises an exception, how can I ensure the file gets closed?

**Rank 1: py313-inputoutput, source lines 347-384** (BM25 14.881)

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

**Rank 2: py313-errors, source lines 482-513** (BM25 11.049)

````text
Predefined Clean-up Actions

Some objects define standard clean-up actions to be undertaken when the object
is no longer needed, regardless of whether or not the operation using the object
succeeded or failed. Look at the following example, which tries to open a file
and print its contents to the screen. ::

   for line in open("myfile.txt"):
       print(line, end="")

The problem with this code is that it leaves the file open for an indeterminate
amount of time after this part of the code has finished executing.
This is not an issue in simple scripts, but can be a problem for larger
applications. The with statement allows objects like files ...
````

**Rank 3: py313-classes, source lines 785-820** (BM25 10.542)

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

### pilot-007

What does adding b to a file mode change, and can I specify encoding in that mode?

**Rank 1: py313-inputoutput, source lines 330-350** (BM25 19.097)

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

**Rank 2: py313-inputoutput, source lines 431-461** (BM25 16.774)

````text
the number of characters written. ::

   >>> f.write('This is a test\n')
   15

Other types of objects need to be converted -- either to a string (in text mode)
or a bytes object (in binary mode) -- before writing them::

   >>> value = ('the answer', 42)
   >>> s = str(value)  # convert the tuple to string
   >>> f.write(s)
   18

f.tell() returns an integer giving the file object's current position in the file
represented as number of bytes from the beginning of the file when in binary mode and
an opaque number when in text mode.

To change the file object's position, use f.seek(offset, whence).  The position is computed
from adding *offset ...
````

**Rank 3: py313-inputoutput, source lines 306-332** (BM25 14.838)

````text
two positional arguments and one keyword argument:
open(filename, mode, encoding=None)

::

   >>> f = open('workfile', 'w', encoding="utf-8")


   >>> print(f)
   <open file 'workfile', mode 'w' at 80a0960>

The first argument is a string containing the filename.  The second argument is
another string containing a few characters describing the way in which the file
will be used.  *mode* can be 'r' when the file will only be read, 'w'
for only writing (an existing file with the same name will be erased), and
'a' opens the file for appending; any data written to the file is
automatically added to the end.  'r+' opens the file for both reading  ...
````

### pilot-008

Stdlib JSON to a file and back: which calls do I use, rather than getting a JSON string?

**Rank 1: py313-inputoutput, source lines 486-506** (BM25 18.337)

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

**Rank 2: py313-inputoutput, source lines 503-535** (BM25 16.488)

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

**Rank 3: py313-controlflow, source lines 913-947** (BM25 11.306)

````text
Arbitrary Argument Lists

   single: * (asterisk); in function calls

Finally, the least frequently used option is to specify that a function can be
called with an arbitrary number of arguments.  These arguments will be wrapped
up in a tuple (see tut-tuples).  Before the variable number of arguments,
zero or more normal arguments may occur. ::

   def write_multiple_items(file, separator, *args):
       file.write(separator.join(args))


Normally, these *variadic* arguments will be last in the list of formal
parameters, because they scoop up all remaining input arguments that are
passed to the function. Any formal parameters which occur after ...
````

### pilot-009

I named my script random.py and now importing random finds my file. How can a local file take priority over the standard library?

**Rank 1: py313-modules, source lines 480-505** (BM25 20.353)

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

**Rank 2: py313-stdlib, source lines 35-79** (BM25 14.505)

````text
>>> help(os)
   <returns an extensive manual page created from the module's docstrings>

For daily file and directory management tasks, the shutil module provides
a higher level interface that is easier to use::

   >>> import shutil
   >>> shutil.copyfile('data.db', 'archive.db')
   'archive.db'
   >>> shutil.move('/build/executables', 'installdir')
   'installdir'



File Wildcards

The glob module provides a function for making file lists from directory
wildcard searches::

   >>> import glob
   >>> glob.glob('*.py')
   ['primes.py', 'random.py', 'quote.py']



Command Line Arguments

Common utility scripts often need to process command li ...
````

**Rank 3: py313-modules, source lines 504-528** (BM25 14.438)

````text
list of module names that should be imported when from package import * is
encountered.  It is up to the package author to keep this list up-to-date when a
new version of the package is released.  Package authors may also decide not to
support it, if they don't see a use for importing \* from their package.  For
example, the file sound/effects/__init__.py could contain the following
code::

   __all__ = ["echo", "surround", "reverse"]

This would mean that from sound.effects import * would import the three
named submodules of the sound.effects package.

Be aware that submodules might become shadowed by locally defined names. For
example, if y ...
````

### pilot-010

CLI + importable module: how do I stop command-line handling from running when the file is imported?

**Rank 1: py313-modules, source lines 129-174** (BM25 19.034)

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

**Rank 2: py313-stdlib, source lines 35-79** (BM25 15.089)

````text
>>> help(os)
   <returns an extensive manual page created from the module's docstrings>

For daily file and directory management tasks, the shutil module provides
a higher level interface that is easier to use::

   >>> import shutil
   >>> shutil.copyfile('data.db', 'archive.db')
   'archive.db'
   >>> shutil.move('/build/executables', 'installdir')
   'installdir'



File Wildcards

The glob module provides a function for making file lists from directory
wildcard searches::

   >>> import glob
   >>> glob.glob('*.py')
   ['primes.py', 'random.py', 'quote.py']



Command Line Arguments

Common utility scripts often need to process command li ...
````

**Rank 3: py313-interpreter, source lines 48-75** (BM25 14.542)

````text
when called with a file name argument or with a file as standard input, it reads
and executes a *script* from that file.

A second way of starting the interpreter is python -c command [arg] ...,
which executes the statement(s) in *command*, analogous to the shell's
-c option.  Since Python statements often contain spaces or other
characters that are special to the shell, it is usually advised to quote
*command* in its entirety.

Some Python modules are also useful as scripts.  These can be invoked using
python -m module [arg] ..., which executes the source file for *module* as
if you had spelled out its full name on the command line.

When a  ...
````

### pilot-011

Why does 0.1 + 0.1 + 0.1 fail an equlity check with 0.3, and what comparison helper can I use?

**Rank 1: py313-inputoutput, source lines 347-384** (BM25 14.323)

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

**Rank 2: py313-datastructures, source lines 579-622** (BM25 13.164)

````text
be retrieved at the same time using the enumerate function. ::

   >>> for i, v in enumerate(['tic', 'tac', 'toe']):
   ...     print(i, v)
   ...
   0 tic
   1 tac
   2 toe

To loop over two or more sequences at the same time, the entries can be paired
with the zip function. ::

   >>> questions = ['name', 'quest', 'favorite color']
   >>> answers = ['lancelot', 'the holy grail', 'blue']
   >>> for q, a in zip(questions, answers):
   ...     print('What is your {0}?  It is {1}.'.format(q, a))
   ...
   What is your name?  It is lancelot.
   What is your quest?  It is the holy grail.
   What is your favorite color?  It is blue.

To loop over  ...
````

**Rank 3: py313-modules, source lines 236-264** (BM25 11.259)

````text
from the command line.  Second, it does not check the cache if there is no
source module.  To support a non-source (compiled only) distribution, the
compiled module must be in the source directory, and there must not be a source
module.

Some tips for experts:

* You can use the -O or -OO switches on the Python command
  to reduce the size of a compiled module.  The -O switch removes assert
  statements, the -OO switch removes both assert statements and __doc__
  strings.  Since some programs may rely on having these available, you should
  only use this option if you know what you're doing.  "Optimized" modules have
  an opt- tag and are usu ...
````

### pilot-012

Two Python apps need diferent versions of the same package. How do I keep an upgrade for one from breaking the other?

**Rank 1: py313-venv, source lines 110-143** (BM25 14.963)

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

**Rank 2: py313-floatingpoint, source lines 133-160** (BM25 13.650)

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

**Rank 3: py313-floatingpoint, source lines 178-218** (BM25 13.566)

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

### pilot-013

When does a for-loop else clause execute, and does it run after break?

**Rank 1: py313-controlflow, source lines 228-258** (BM25 32.290)

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

**Rank 2: py313-controlflow, source lines 205-237** (BM25 24.640)

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

**Rank 3: py313-errors, source lines 397-422** (BM25 21.147)

````text
Traceback (most recent call last):
     File "<stdin>", line 2, in <module>
       raise KeyboardInterrupt
   KeyboardInterrupt

If a finally clause is present, the finally
clause will execute as the last task before the try
statement completes. The finally clause runs whether or
not the try statement produces an exception. The following
points discuss more complex cases when an exception occurs:

* If an exception occurs during execution of the try
  clause, the exception may be handled by an except
  clause. If the exception is not handled by an except
  clause, the exception is re-raised after the finally
  clause has been executed.

* An  ...
````

### pilot-014

What tells a for loop to stop when an itterator has no more values, and how do I request its next value manually?

**Rank 1: py313-classes, source lines 785-820** (BM25 20.097)

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

**Rank 2: py313-controlflow, source lines 686-712** (BM25 14.741)

````text
parrot function), and their order is not important.  This also includes
non-optional arguments (e.g. parrot(voltage=1000) is valid too).
No argument may receive a value more than once.
Here's an example that fails due to this restriction::

   >>> def function(a):
   ...     pass
   ...
   >>> function(0, a=0)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   TypeError: function() got multiple values for argument 'a'

When a final formal parameter of the form **name is present, it receives a
dictionary (see typesmapping) containing all keyword arguments except for
those corresponding to a formal parameter.  Thi ...
````

**Rank 3: py313-floatingpoint, source lines 26-58** (BM25 14.699)

````text
actually stored in the machine.

The problem is easier to understand at first in base 10.  Consider the fraction
1/3.  You can approximate that as a base 10 fraction::

   0.3

or, better, ::

   0.33

or, better, ::

   0.333

and so on.  No matter how many digits you're willing to write down, the result
will never be exactly 1/3, but will be an increasingly better approximation of
1/3.

In the same way, no matter how many base 2 digits you're willing to use, the
decimal value 0.1 cannot be represented exactly as a base 2 fraction.  In base
2, 1/10 is the infinitely repeating fraction ::

   0.000110011001100110011001100110011001100110011001 ...
````

### pilot-015

A function default list retains old items, and a class-level list is shared by instances. Explain each cause and how to make the lists independent.

**Rank 1: py313-classes, source lines 389-423** (BM25 24.405)

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

**Rank 2: py313-classes, source lines 420-460** (BM25 19.449)

````text
'Buddy'

As discussed in tut-object, shared data can have possibly surprising
effects with involving mutable objects such as lists and dictionaries.
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
   ...
````

**Rank 3: py313-introduction, source lines 367-407** (BM25 16.303)

````text
operations supported by such types.

   string-methods
      Strings support a large number of methods for
      basic transformations and searching.

   f-strings
      String literals that have embedded expressions.

   formatstrings
      Information about string formatting with str.format.

   old-string-formatting
      The old formatting operations invoked when strings are
      the left operand of the % operator are described in more detail here.



Lists

Python knows a number of *compound* data types, used to group together other
values.  The most versatile is the *list*, which can be written as a list of
comma-separated values (item ...
````

### pilot-016

Why can ordinary floats surprise me with decimal equality, and which standard-library numeric type is useful when exact decimal representation matters for money?

**Rank 1: py313-floatingpoint, source lines 238-268** (BM25 21.255)

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

**Rank 2: py313-stdlib2, source lines 373-406** (BM25 20.034)

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

**Rank 3: py313-floatingpoint, source lines 267-302** (BM25 17.932)

````text
decimal fractions cannot be represented exactly as binary (base 2) fractions.
This is the chief reason why Python (or Perl, C, C++, Java, Fortran, and many
others) often won't display the exact decimal number you expect.

Why is that?  1/10 is not exactly representable as a binary fraction.  Since at
least 2000, almost all machines use IEEE 754 binary floating-point arithmetic,
and almost all platforms map Python floats to IEEE 754 binary64 "double
precision" values.  IEEE 754 binary64 values contain 53 bits of precision, so
on input the computer strives to convert 0.1 to the closest fraction it can of
the form *J*/2**\ *N* where *J* is an in ...
````

### pilot-017

How do I use pandas groupby to compute the median salary in each department?

**Rank 1: py313-classes, source lines 726-762** (BM25 8.310)

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

**Rank 2: py313-classes, source lines 143-167** (BM25 7.563)

````text
time, so don't rely on dynamic name resolution!  (In fact, local variables are
already determined statically.)

A special quirk of Python is that -- if no global or nonlocal
statement is in effect -- assignments to names always go into the innermost scope.
Assignments do not copy data --- they just bind names to objects.  The same is true
for deletions: the statement del x removes the binding of x from the
namespace referenced by the local scope.  In fact, all operations that introduce
new names use the local scope: in particular, import statements and
function definitions bind the module or function name in the local scope.

The global state ...
````

**Rank 3: py313-inputoutput, source lines 28-58** (BM25 7.555)

````text
characters that can refer to variables or literal values.

  ::

     >>> year = 2016
     >>> event = 'Referendum'
     >>> f'Results of the {year} {event}'
     'Results of the 2016 Referendum'

* The str.format method of strings requires more manual
  effort.  You'll still use { and } to mark where a variable
  will be substituted and can provide detailed formatting directives,
  but you'll also need to provide the information to be formatted. In the following code
  block there are two examples of how to format variables:


  ::

     >>> yes_votes = 42_572_654
     >>> total_votes = 85_705_149
     >>> percentage = yes_votes / total_vote ...
````

### pilot-018

Which scikit-learn GridSearchCV parameters control cross-validation and parallel execution?

**Rank 1: py313-errors, source lines 508-536** (BM25 9.277)

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

**Rank 2: py313-errors, source lines 81-111** (BM25 8.499)

````text
Handling Exceptions

It is possible to write programs that handle selected exceptions. Look at the
following example, which asks the user for input until a valid integer has been
entered, but allows the user to interrupt the program (using Control-C or
whatever the operating system supports); note that a user-generated interruption
is signalled by raising the KeyboardInterrupt exception. ::

   >>> while True:
   ...     try:
   ...         x = int(input("Please enter a number: "))
   ...         break
   ...     except ValueError:
   ...         print("Oops!  That was no valid number.  Try again...")
   ...

The try statement works as follow ...
````

**Rank 3: py313-errors, source lines 30-64** (BM25 7.717)

````text
(':') is missing before it.  File name and line number are printed so you
know where to look in case the input came from a script.



Exceptions

Even if a statement or expression is syntactically correct, it may cause an
error when an attempt is made to execute it. Errors detected during execution
are called *exceptions* and are not unconditionally fatal: you will soon learn
how to handle them in Python programs.  Most exceptions are not handled by
programs, however, and result in error messages as shown here::

   >>> 10 * (1/0)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
       10 * (1/0)
   ZeroDivisionE ...
````

### pilot-019

How do I create a PostgreSQL index that speeds up searching a JSONB field?

**Rank 1: py313-introduction, source lines 275-306** (BM25 10.490)

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

**Rank 2: py313-inputoutput, source lines 106-137** (BM25 10.358)

````text
Formatted String Literals

Formatted string literals (also called f-strings for
short) let you include the value of Python expressions inside a string by
prefixing the string with f or F and writing expressions as
{expression}.

An optional format specifier can follow the expression. This allows greater
control over how the value is formatted. The following example rounds pi to
three places after the decimal::

   >>> import math
   >>> print(f'The value of pi is approximately {math.pi:.3f}.')
   The value of pi is approximately 3.142.

Passing an integer after the ':' will cause that field to be a minimum
number of characters wide.  This is  ...
````

**Rank 3: py313-controlflow, source lines 65-108** (BM25 9.097)

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

**Rank 1: py313-controlflow, source lines 65-108** (BM25 10.762)

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

**Rank 2: py313-controlflow, source lines 993-1028** (BM25 9.231)

````text
>>> f = make_incrementor(42)
   >>> f(0)
   42
   >>> f(1)
   43

The above example uses a lambda expression to return a function.  Another use
is to pass a small function as an argument::

   >>> pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
   >>> pairs.sort(key=lambda pair: pair[1])
   >>> pairs
   [(4, 'four'), (1, 'one'), (3, 'three'), (2, 'two')]



Documentation Strings

   single: docstrings
   single: documentation strings
   single: strings, documentation

Here are some conventions about the content and formatting of documentation
strings.

The first line should always be a short, concise summary of the object's
purpos ...
````

**Rank 3: py313-datastructures, source lines 296-334** (BM25 8.699)

````text
...     [5, 6, 7, 8],
   ...     [9, 10, 11, 12],
   ... ]

The following list comprehension will transpose rows and columns::

   >>> [[row[i] for row in matrix] for i in range(4)]
   [[1, 5, 9], [2, 6, 10], [3, 7, 11], [4, 8, 12]]

As we saw in the previous section, the inner list comprehension is evaluated in
the context of the for that follows it, so this example is
equivalent to::

   >>> transposed = []
   >>> for i in range(4):
   ...     transposed.append([row[i] for row in matrix])
   ...
   >>> transposed
   [[1, 5, 9], [2, 6, 10], [3, 7, 11], [4, 8, 12]]

which, in turn, is the same as::

   >>> transposed = []
   >>> for i in rang ...
````

## Next checks

Inspect failures and partial-coverage cases before changing retrieval settings. Some misses can reflect chunk boundaries or alternative evidence rather than irrelevant retrieval. Add judged alternatives from the candidate pool; keep a record of label changes and rerun against the new label hash. Freeze a shared chunk configuration for later dense/hybrid comparisons. Add a genuine held-out set before claiming generalization.
