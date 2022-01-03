PEBUG
=====

This is a x86 old-debug-like program.

The main goal of this project is to provide an educational
and introductory interface to assembler, x86 flavor in particular.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   about.md
   requirements.md
   commands.md
   screenshots.md
   modules

API Reference
=============

.. autoclass:: asm8086Machine.Disk
   :members:

.. autoclass:: asm8086Machine.Cpu
   :members:

.. autoclass:: asm8086Machine.Memory
   .. automethod:: peek(page, address)
   .. automethod:: peek(address)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
