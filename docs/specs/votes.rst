================
The votes module
================

.. How to test only this document:

    $ python setup.py test -s tests.SpecsTests.test_votes
    
    doctest init:
    >>> import lino
    >>> lino.startup('lino_noi.projects.team.settings.demo')
    >>> from lino.api.doctest import *


The :mod:`lino_noi.lib.votes` module adds the concept of "votes" to
:ref:`noi`.

A **vote** is when a user has an opinion or interest about a given
ticket (or any other votable).

A **votable**, in :ref:`noi`, is a ticket. But the module is designed
to be reusable in other contexts.


My tasks ("To-Do list")
=======================

Shows your votes having states `assigned` and `done`.

>>> rt.login('luc').user.profile
users.UserTypes.developer:400

>>> rt.login('jean').show(votes.MyTasks)
... #doctest: +REPORT_UDIFF
============================================================================================= =========================================== ==========
 Description                                                                                   Actions                                     Priority
--------------------------------------------------------------------------------------------- ------------------------------------------- ----------
 `#110 (Ticket 93) <Detail>`__ by `mathieu <Detail>`__                                         **Done**                                    0
 `#101 (Ticket 84) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                   **Assigned** → [Watching] [Done] [Cancel]   0
 `#86 (Ticket 69) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                    **Done**                                    0
 `#77 (Ticket 60) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                    **Assigned** → [Watching] [Done] [Cancel]   0
 `#65 (Ticket 48) <Detail>`__ by `mathieu <Detail>`__                                          **Done**                                    0
 `#56 (Ticket 39) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                    **Assigned** → [Watching] [Done] [Cancel]   0
 `#41 (Ticket 24) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                    **Done**                                    0
 `#32 (Ticket 15) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__                    **Assigned** → [Watching] [Done] [Cancel]   0
 `#20 (Ticket 3) <Detail>`__ by `mathieu <Detail>`__                                           **Done**                                    0
 `#11 (Class-based Foos and Bars?) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__   **Assigned** → [Watching] [Done] [Cancel]   0
 `#2 (Bar is not always baz) <Detail>`__ by `mathieu <Detail>`__ for `marc <Detail>`__         **Assigned** → [Watching] [Done] [Cancel]   0
============================================================================================= =========================================== ==========
<BLANKLINE>


>>> rt.login('mathieu').show(votes.MyTasks)
... #doctest: +REPORT_UDIFF
============================================================================= ================================== ==========
 Description                                                                   Actions                            Priority
----------------------------------------------------------------------------- ---------------------------------- ----------
 `#102 (Ticket 85) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__       **Done**                           0
 `#93 (Ticket 76) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__        **Assigned** → [Watching] [Done]   0
 `#57 (Ticket 40) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__        **Done**                           0
 `#48 (Ticket 31) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__        **Assigned** → [Watching] [Done]   0
 `#12 (Foo cannot bar) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__   **Done**                           0
 `#3 (Baz sucks) <Detail>`__ by `luc <Detail>`__ for `marc <Detail>`__         **Assigned** → [Watching] [Done]   0
============================================================================= ================================== ==========
<BLANKLINE>

>>> rt.login('luc').show(votes.MyTasks)
... #doctest: +REPORT_UDIFF
No data to display



>>> rt.login('luc').show(votes.MyOffers)
... #doctest: +REPORT_UDIFF
======================================================================================== =====================================================
 Description                                                                              Actions
---------------------------------------------------------------------------------------- -----------------------------------------------------
 `#100 (Ticket 83) <Detail>`__ by `jean <Detail>`__                                       **Candidate** → [Watching] [Assign] [Done] [Cancel]
 `#55 (Ticket 38) <Detail>`__ by `jean <Detail>`__                                        **Candidate** → [Watching] [Assign] [Done] [Cancel]
 `#10 (Where can I find a Foo when bazing Bazes?) <Detail>`__ by `jean <Detail>`__        **Candidate** → [Watching] [Assign] [Done] [Cancel]
 `#1 (Föö fails to bar when baz) <Detail>`__ by `jean <Detail>`__ for `marc <Detail>`__   **Candidate** → [Watching] [Assign] [Done] [Cancel]
======================================================================================== =====================================================
<BLANKLINE>

Note that Luc is a triager, that's why he has permission to [Assign]
and [Done].

>>> from lino_noi.lib.tickets.roles import Triager
>>> rt.login('luc').user.profile.has_required_roles([Triager])
True

