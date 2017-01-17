.. _noi.specs.tickets:

=============================
Ticket management in Lino Noi
=============================


.. How to test only this document:

    $ python setup.py test -s tests.SpecsTests.test_tickets
    
    doctest init:
    >>> import lino
    >>> lino.startup('lino_noi.projects.team.settings.demo')
    >>> from lino.api.doctest import *


This document specifies the ticket management functions of Lino Noi,
implemented in :mod:`lino_noi.lib.tickets`.


.. contents::
  :local:


Tickets
=======

A :class:`Ticket <lino_noi.lib.tickets.models.Ticket>` represents a
concrete problem introduced by a :attr:`reporter
<lino_noi.lib.tickets.models.Ticket.reporter>` (a system user).


Lifecycle of a ticket
=====================

The :attr:`state <lino_noi.lib.tickets.models.Ticket.state>` of a
ticket has one of the following values:

>>> rt.show(tickets.TicketStates)
======= =========== =========== ======== ========
 value   name        text        Symbol   Active
------- ----------- ----------- -------- --------
 10      new         New         ⛶        Yes
 15      talk        Talk        ☎        Yes
 20      opened      Opened      ☉        Yes
 21      sticky      Sticky      ♾        Yes
 22      started     Started     ⚒        Yes
 30      sleeping    Sleeping    ☾        No
 40      ready       Ready       ☐        Yes
 50      closed      Closed      ☑        No
 60      cancelled   Cancelled   ☒        No
======= =========== =========== ======== ========
<BLANKLINE>

There is also a "modern" series of symbols, which can be enabled
site-wide in :attr:`lino.core.site.Site.use_new_unicode_symbols`.

You can see this table in your web interface using
:menuselection:`Explorer --> Tickets --> States`.

.. >>> show_menu_path(tickets.TicketStates)
   Explorer --> Tickets --> States

See :class:`lino_noi.lib.tickets.choicelists.TicketStates` for more
information about every state.

Above table in German:

>>> rt.show(tickets.TicketStates, language="de")
====== =========== ============= ======== ========
 Wert   name        Text          Symbol   Aktive
------ ----------- ------------- -------- --------
 10     new         Neu           ⛶        Ja
 15     talk        Besprechen    ☎        Ja
 20     opened      Offen         ☉        Ja
 21     sticky      Sticky        ♾        Ja
 22     started     Gestartet     ⚒        Ja
 30     sleeping    Schläft       ☾        Nein
 40     ready       Bereit        ☐        Ja
 50     closed      Geschlossen   ☑        Nein
 60     cancelled   Storniert     ☒        Nein
====== =========== ============= ======== ========
<BLANKLINE>

And in French (not yet fully translated):

>>> rt.show(tickets.TicketStates, language="fr")
======= =========== ========== ======== ========
 value   name        text       Symbol   Active
------- ----------- ---------- -------- --------
 10      new         Nouveau    ⛶        Oui
 15      talk        Talk       ☎        Oui
 20      opened      Opened     ☉        Oui
 21      sticky      Sticky     ♾        Oui
 22      started     Started    ⚒        Oui
 30      sleeping    Sleeping   ☾        Non
 40      ready       Ready      ☐        Oui
 50      closed      Closed     ☑        Non
 60      cancelled   Annulé     ☒        Non
======= =========== ========== ======== ========
<BLANKLINE>


Note that a ticket also has a checkbox for marking it as :attr:`closed
<lino_noi.lib.tickets.models.Ticket.closed>`.  This means that a ticket
can be marked as "closed" in any of above states.  We don't use this for the moment and are not sure
whether this is a cool feature (:ticket:`372`).

- :attr:`standby <lino_noi.lib.tickets.models.Ticket.standby>` 

Projects
========

The :attr:`project <lino_noi.lib.tickets.models.Ticket.project>` of a
ticket is used to specify "who is going to pay" for it. Lino Noi does
not issue invoices, so it uses this information only for reporting
about it and helping with the decision about whether and how worktime
is being invoiced to the customer.  But the invoicing itself is not
currently a goal of Lino Noi.

So a **project** is something for which somebody is possibly willing
to pay money.

>>> rt.show(tickets.Projects)
=========== =============== ======== ============== =========
 Reference   Name            Parent   Project Type   Private
----------- --------------- -------- -------------- ---------
 linö        Framewörk                               No
 téam        Téam            linö                    Yes
 docs        Documentatión   linö                    No
 research    Research        docs                    No
 shop        Shop                                    No
=========== =============== ======== ============== =========
<BLANKLINE>


>>> rt.show(tickets.TopLevelProjects)
=========== =========== ======== ================
 Reference   Name        Parent   Children
----------- ----------- -------- ----------------
 linö        Framewörk            *téam*, *docs*
 shop        Shop
=========== =========== ======== ================
<BLANKLINE>


Developers can start working on tickets without specifying a project
(i.e. without knowing who is going to pay for their work).  

But after some time every ticket should get assigned to some
project. You can see a list of tickets which have not yet been
assigned to a project:

>>> pv = dict(has_project=dd.YesNo.no)
>>> rt.show(tickets.Tickets, param_values=pv)
... #doctest: +REPORT_UDIFF
==== =================== ========= =========== ========= ============= =========
 ID   Summary             Author    Topic       Faculty   Actions       Project
---- ------------------- --------- ----------- --------- ------------- ---------
 5    Cannot create Foo   mathieu   Lino Cosi             **Started**
 3    Baz sucks           luc       Lino Core             **Opened**
==== =================== ========= =========== ========= ============= =========
<BLANKLINE>


Distribution of tickets per project
===================================

In our demo database, tickets are distributed over the different
projects as follows (not a realistic distribution):

>>> for p in tickets.Project.objects.all():
...         print p.ref, p.tickets_by_project.count()
linö 23
téam 23
docs 23
research 23
shop 22



Private tickets
===============

Tickets are private by default. But when they are assigned to a public
project, then their privacy is removed.

So the private tickets are (1) those in project "téam" and (2) those
without project:

>>> pv = dict(show_private=dd.YesNo.yes)
>>> rt.show(tickets.Tickets, param_values=pv,
...     column_names="id summary project")
... #doctest: +REPORT_UDIFF
===== ======================= =========
 ID    Summary                 Project
----- ----------------------- ---------
 114   Ticket 114              téam
 109   Ticket 109              téam
 104   Ticket 104              téam
 99    Ticket 99               téam
 94    Ticket 94               téam
 89    Ticket 89               téam
 84    Ticket 84               téam
 79    Ticket 79               téam
 74    Ticket 74               téam
 69    Ticket 69               téam
 64    Ticket 64               téam
 59    Ticket 59               téam
 54    Ticket 54               téam
 49    Ticket 49               téam
 44    Ticket 44               téam
 39    Ticket 39               téam
 34    Ticket 34               téam
 29    Ticket 29               téam
 24    Ticket 24               téam
 19    Ticket 19               téam
 14    Bar cannot baz          téam
 9     Foo never matches Bar   téam
 5     Cannot create Foo
 3     Baz sucks
 2     Bar is not always baz   téam
===== ======================= =========
<BLANKLINE>


And these are the public tickets:

>>> pv = dict(show_private=dd.YesNo.no)
>>> rt.show(tickets.Tickets, param_values=pv,
...     column_names="id summary project")
... #doctest: +REPORT_UDIFF
===== =========================================== ==========
 ID    Summary                                     Project
----- ------------------------------------------- ----------
 116   Ticket 116                                  research
 115   Ticket 115                                  docs
 113   Ticket 113                                  linö
 112   Ticket 112                                  shop
 111   Ticket 111                                  research
 110   Ticket 110                                  docs
 108   Ticket 108                                  linö
 107   Ticket 107                                  shop
 106   Ticket 106                                  research
 105   Ticket 105                                  docs
 103   Ticket 103                                  linö
 102   Ticket 102                                  shop
 101   Ticket 101                                  research
 100   Ticket 100                                  docs
 98    Ticket 98                                   linö
 97    Ticket 97                                   shop
 96    Ticket 96                                   research
 95    Ticket 95                                   docs
 93    Ticket 93                                   linö
 92    Ticket 92                                   shop
 91    Ticket 91                                   research
 90    Ticket 90                                   docs
 88    Ticket 88                                   linö
 87    Ticket 87                                   shop
 86    Ticket 86                                   research
 85    Ticket 85                                   docs
 83    Ticket 83                                   linö
 82    Ticket 82                                   shop
 81    Ticket 81                                   research
 80    Ticket 80                                   docs
 78    Ticket 78                                   linö
 77    Ticket 77                                   shop
 76    Ticket 76                                   research
 75    Ticket 75                                   docs
 73    Ticket 73                                   linö
 72    Ticket 72                                   shop
 71    Ticket 71                                   research
 70    Ticket 70                                   docs
 68    Ticket 68                                   linö
 67    Ticket 67                                   shop
 66    Ticket 66                                   research
 65    Ticket 65                                   docs
 63    Ticket 63                                   linö
 62    Ticket 62                                   shop
 61    Ticket 61                                   research
 60    Ticket 60                                   docs
 58    Ticket 58                                   linö
 57    Ticket 57                                   shop
 56    Ticket 56                                   research
 55    Ticket 55                                   docs
 53    Ticket 53                                   linö
 52    Ticket 52                                   shop
 51    Ticket 51                                   research
 50    Ticket 50                                   docs
 48    Ticket 48                                   linö
 47    Ticket 47                                   shop
 46    Ticket 46                                   research
 45    Ticket 45                                   docs
 43    Ticket 43                                   linö
 42    Ticket 42                                   shop
 41    Ticket 41                                   research
 40    Ticket 40                                   docs
 38    Ticket 38                                   linö
 37    Ticket 37                                   shop
 36    Ticket 36                                   research
 35    Ticket 35                                   docs
 33    Ticket 33                                   linö
 32    Ticket 32                                   shop
 31    Ticket 31                                   research
 30    Ticket 30                                   docs
 28    Ticket 28                                   linö
 27    Ticket 27                                   shop
 26    Ticket 26                                   research
 25    Ticket 25                                   docs
 23    Ticket 23                                   linö
 22    Ticket 22                                   shop
 21    Ticket 21                                   research
 20    Ticket 20                                   docs
 18    Ticket 18                                   linö
 17    Ticket 17                                   shop
 16    How to get bar from foo                     research
 15    Bars have no foo                            docs
 13    Bar cannot foo                              linö
 12    Foo cannot bar                              shop
 11    Class-based Foos and Bars?                  research
 10    Where can I find a Foo when bazing Bazes?   docs
 8     Is there any Bar in Foo?                    linö
 7     No Foo after deleting Bar                   shop
 6     Sell bar in baz                             research
 4     Foo and bar don't baz                       docs
 1     Föö fails to bar when baz                   linö
===== =========================================== ==========
<BLANKLINE>



There are 5 private and 11 public tickets in the demo database.

>>> tickets.Ticket.objects.filter(private=True).count()
25
>>> tickets.Ticket.objects.filter(private=False).count()
91

My tickets
==========

>>> rt.login('jean').show(tickets.MyTickets)
... #doctest: +REPORT_UDIFF
=================================================================== =======================================
 Description                                                         Actions
------------------------------------------------------------------- ---------------------------------------
 `#112 (Ticket 112) <Detail>`__ for `marc <Detail>`__                [▶] [★] **Sticky** → [⛶]
 `#109 (Ticket 109) <Detail>`__ for `marc <Detail>`__                [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#103 (Ticket 103) <Detail>`__ for `marc <Detail>`__                [▶] [★] **Sticky** → [⛶]
 `#100 (Ticket 100) <Detail>`__                                      [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#94 (Ticket 94) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#91 (Ticket 91) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#85 (Ticket 85) <Detail>`__                                        [▶] [★] **Sticky** → [⛶]
 `#82 (Ticket 82) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#76 (Ticket 76) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#73 (Ticket 73) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#67 (Ticket 67) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#64 (Ticket 64) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#58 (Ticket 58) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#55 (Ticket 55) <Detail>`__                                        [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#49 (Ticket 49) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#46 (Ticket 46) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#40 (Ticket 40) <Detail>`__                                        [▶] [★] **Sticky** → [⛶]
 `#37 (Ticket 37) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#31 (Ticket 31) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#28 (Ticket 28) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#22 (Ticket 22) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **Sticky** → [⛶]
 `#19 (Ticket 19) <Detail>`__ for `marc <Detail>`__                  [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#13 (Bar cannot foo) <Detail>`__ for `marc <Detail>`__             [▶] [★] **Sticky** → [⛶]
 `#10 (Where can I find a Foo when bazing Bazes?) <Detail>`__        [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
 `#4 (Foo and bar don't baz) <Detail>`__ for `marc <Detail>`__       [▶] [★] **Sticky** → [⛶]
 `#1 (Föö fails to bar when baz) <Detail>`__ for `marc <Detail>`__   [▶] [★] **New** → [♾] [☾] [☎] [☉] [☐]
=================================================================== =======================================
<BLANKLINE>


Sites
=====

Lino Noi has a list of all sites for which we do support:

>>> rt.show(tickets.Sites)
============= ========= ======== ====
 Designation   Partner   Remark   ID
------------- --------- -------- ----
 pypi          pypi               3
 welket        welket             1
 welsch        welsch             2
============= ========= ======== ====
<BLANKLINE>

A ticket may or may not be "local", i.e. specific to a given site.
When a ticket is site-specific, we simply assign the `site` field.  We
can see all local tickets for a given site object:

>>> welket = tickets.Site.objects.get(name="welket")
>>> rt.show(tickets.TicketsBySite, welket)
... #doctest: +REPORT_UDIFF -SKIP
===== =========================== ========= =========== =============== ============ ==========
 ID    Summary                     Author    Topic       Faculty         Actions      Project
----- --------------------------- --------- ----------- --------------- ------------ ----------
 115   Ticket 115                  mathieu   Lino Core                   **Ready**    docs
 109   Ticket 109                  jean      Lino Cosi                   **New**      téam
 103   Ticket 103                  jean      Lino Core                   **Sticky**   linö
 97    Ticket 97                   mathieu   Lino Cosi                   **Ready**    shop
 91    Ticket 91                   jean      Lino Core                   **New**      research
 85    Ticket 85                   jean      Lino Cosi                   **Sticky**   docs
 79    Ticket 79                   mathieu   Lino Core                   **Ready**    téam
 73    Ticket 73                   jean      Lino Cosi                   **New**      linö
 67    Ticket 67                   jean      Lino Core                   **Sticky**   shop
 61    Ticket 61                   mathieu   Lino Cosi                   **Ready**    research
 55    Ticket 55                   jean      Lino Core                   **New**      docs
 49    Ticket 49                   jean      Lino Cosi                   **Sticky**   téam
 43    Ticket 43                   mathieu   Lino Core                   **Ready**    linö
 37    Ticket 37                   jean      Lino Cosi                   **New**      shop
 31    Ticket 31                   jean      Lino Core                   **Sticky**   research
 25    Ticket 25                   mathieu   Lino Cosi                   **Ready**    docs
 19    Ticket 19                   jean      Lino Core                   **New**      téam
 13    Bar cannot foo              jean      Lino Cosi   Documentation   **Sticky**   linö
 7     No Foo after deleting Bar   mathieu   Lino Core                   **Ready**    shop
 1     Föö fails to bar when baz   jean      Lino Cosi                   **New**      linö
===== =========================== ========= =========== =============== ============ ==========
<BLANKLINE>


Note that the above table shows no state change actions in the
Actions column because it is being requested by anonymous. For an
authenticated developer it looks like this:

>>> rt.login('luc').show(tickets.TicketsBySite, welket)
... #doctest: +REPORT_UDIFF -SKIP
===== =========================== ========= =========== =============== ==================== ==========
 ID    Summary                     Author    Topic       Faculty         Actions              Project
----- --------------------------- --------- ----------- --------------- -------------------- ----------
 115   Ticket 115                  mathieu   Lino Core                   [▶] [☆] **Ready**    docs
 109   Ticket 109                  jean      Lino Cosi                   [▶] [★] **New**      téam
 103   Ticket 103                  jean      Lino Core                   [▶] [★] **Sticky**   linö
 97    Ticket 97                   mathieu   Lino Cosi                   [▶] [☆] **Ready**    shop
 91    Ticket 91                   jean      Lino Core                   [▶] [★] **New**      research
 85    Ticket 85                   jean      Lino Cosi                   [▶] [★] **Sticky**   docs
 79    Ticket 79                   mathieu   Lino Core                   [▶] [☆] **Ready**    téam
 73    Ticket 73                   jean      Lino Cosi                   [▶] [★] **New**      linö
 67    Ticket 67                   jean      Lino Core                   [▶] [★] **Sticky**   shop
 61    Ticket 61                   mathieu   Lino Cosi                   [▶] [☆] **Ready**    research
 55    Ticket 55                   jean      Lino Core                   [▶] [★] **New**      docs
 49    Ticket 49                   jean      Lino Cosi                   [▶] [★] **Sticky**   téam
 43    Ticket 43                   mathieu   Lino Core                   [▶] [☆] **Ready**    linö
 37    Ticket 37                   jean      Lino Cosi                   [▶] [★] **New**      shop
 31    Ticket 31                   jean      Lino Core                   [▶] [★] **Sticky**   research
 25    Ticket 25                   mathieu   Lino Cosi                   [▶] [☆] **Ready**    docs
 19    Ticket 19                   jean      Lino Core                   [▶] [★] **New**      téam
 13    Bar cannot foo              jean      Lino Cosi   Documentation   [▶] [★] **Sticky**   linö
 7     No Foo after deleting Bar   mathieu   Lino Core                   [▶] [☆] **Ready**    shop
 1     Föö fails to bar when baz   jean      Lino Cosi                   [★] **New**          linö
===== =========================== ========= =========== =============== ==================== ==========
<BLANKLINE>




Milestones
==========

Every site can have its list of "milestones" or "releases". A
milestone is when a site gets an upgrade of the software which is
running there. 

A milestone is not necessary an *official* release of a new
version. It just means that you release some changed software to the
users of that site.

>>> welket = tickets.Site.objects.get(name="welket")
>>> rt.show(rt.actors.deploy.MilestonesBySite, welket)
... #doctest: -REPORT_UDIFF
======= ============== ============ ======== ====
 Label   Expected for   Reached      Closed   ID
------- -------------- ------------ -------- ----
         15/05/2015     15/05/2015   No       7
         11/05/2015     11/05/2015   No       5
         07/05/2015     07/05/2015   No       3
         03/05/2015     03/05/2015   No       1
======= ============== ============ ======== ====
<BLANKLINE>


Deployments
===========

Every milestone has its list of "deployments", i.e. the tickets that
are being fixed when this milestone is reached.

The demo database currently does not have any deployments:

>>> rt.show(rt.actors.deploy.Deployments)
No data to display


Release notes
=============

Lino Noi has an excerpt type for printing a milestone.  This is used
to produce *release notes*.

>>> obj = deploy.Milestone.objects.get(pk=7)
>>> rt.show(rt.actors.deploy.DeploymentsByMilestone, obj)
No data to display

>>> rt.show(clocking.OtherTicketsByMilestone, obj)
No data to display



Dependencies between tickets
============================

>>> rt.show(tickets.LinkTypes)
... #doctest: +REPORT_UDIFF
======= =========== ===========
 value   name        text
------- ----------- -----------
 10      requires    Requires
 20      triggers    Triggers
 30      suggests    Suggests
 40      obsoletes   Obsoletes
======= =========== ===========
<BLANKLINE>




>>> rt.show(tickets.Links)
... #doctest: +REPORT_UDIFF
==== ================= ================================ ============================
 ID   Dependency type   Parent                           Child
---- ----------------- -------------------------------- ----------------------------
 1    Requires          #1 (Föö fails to bar when baz)   #2 (Bar is not always baz)
==== ================= ================================ ============================
<BLANKLINE>


Comments
========

Currently the demo database contains just some comments...

>>> rt.show(comments.Comments, column_names="id user short_text")
==== ================= ===================
 ID   Author            Short text
---- ----------------- -------------------
 1    Romain Raffault   Hackerish comment
 2    Rolf Rompen       Hackerish comment
 3    Robin Rood        Hackerish comment
==== ================= ===================
<BLANKLINE>


>>> obj = tickets.Ticket.objects.get(pk=7)
>>> rt.show(comments.CommentsByRFC, obj)
<BLANKLINE>


Filtering tickets
=================


>>> show_fields(tickets.Tickets)
+-----------------+-----------------+---------------------------------------------------------------+
| Internal name   | Verbose name    | Help text                                                     |
+=================+=================+===============================================================+
| user            | Author          |                                                               |
+-----------------+-----------------+---------------------------------------------------------------+
| end_user        | End user        | Only rows concerning this end user.                           |
+-----------------+-----------------+---------------------------------------------------------------+
| assigned_to     | Voted by        | Only tickets having a vote by this user.                      |
+-----------------+-----------------+---------------------------------------------------------------+
| not_assigned_to | Not voted by    | Only tickets having no vote by this user.                     |
+-----------------+-----------------+---------------------------------------------------------------+
| interesting_for | Interesting for | Only tickets interesting for this partner.                    |
+-----------------+-----------------+---------------------------------------------------------------+
| site            | Site            | Select a site if you want to see only tickets for this site.  |
+-----------------+-----------------+---------------------------------------------------------------+
| project         | Project         |                                                               |
+-----------------+-----------------+---------------------------------------------------------------+
| state           | State           | Only rows having this state.                                  |
+-----------------+-----------------+---------------------------------------------------------------+
| has_project     | Has project     | Show only (or hide) tickets which have a project assigned.    |
+-----------------+-----------------+---------------------------------------------------------------+
| show_assigned   | Assigned        | Whether to show assigned tickets                              |
+-----------------+-----------------+---------------------------------------------------------------+
| show_active     | Active          | Whether to show active tickets                                |
+-----------------+-----------------+---------------------------------------------------------------+
| show_todo       | To do           | Show only (or hide) tickets which are todo (i.e. state is New |
|                 |                 | or ToDo).                                                     |
+-----------------+-----------------+---------------------------------------------------------------+
| show_private    | Private         | Show only (or hide) tickets that are marked private.          |
+-----------------+-----------------+---------------------------------------------------------------+
| start_date      | Period from     | Start date of observed period                                 |
+-----------------+-----------------+---------------------------------------------------------------+
| end_date        | until           | End date of observed period                                   |
+-----------------+-----------------+---------------------------------------------------------------+
| observed_event  | Observed event  |                                                               |
+-----------------+-----------------+---------------------------------------------------------------+
| topic           | Topic           |                                                               |
+-----------------+-----------------+---------------------------------------------------------------+
| feasable_by     | Feasable by     | Show only tickets for which I am competent.                   |
+-----------------+-----------------+---------------------------------------------------------------+




The detail layout of a ticket
=============================

Here is a textual description of the fields and their layout used in
the detail window of a ticket.

>>> from lino.utils.diag import py2rst
>>> print(py2rst(tickets.Tickets.detail_layout, True))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
(main) [visible for all]:
- **General** (general):
  - (general_1):
    - (general1):
      - (general1_1): **Summary** (summary), **ID** (id), **Author** (user), **End user** (end_user)
      - (general1_2): **Site** (site), **Topic** (topic), **Project** (project), **Private** (private)
      - (general1_3): **Actions** (workflow_buttons), **Faculty** (faculty)
    - **Votes** (votes.VotesByVotable) [visible for user consultant hoster developer senior admin]
  - (general_2): **Description** (description), **Comments** (CommentsByRFC) [visible for user consultant hoster developer senior admin], **Sessions** (SessionsByTicket) [visible for consultant hoster developer senior admin]
- **More** (more):
  - (more_1):
    - (more1):
      - (more1_1): **Created** (created), **Modified** (modified), **Reported for** (reported_for), **Ticket type** (ticket_type)
      - (more1_2): **State** (state), **Duplicate of** (duplicate_of), **Planned time** (planned_time), **Priority** (priority)
    - **Duplicates** (DuplicatesByTicket)
  - (more_2): **Upgrade notes** (upgrade_notes), **Dependencies** (LinksByTicket) [visible for developer senior admin]
- **History** (changes.ChangesByMaster) [visible for developer senior admin]
- **Deployments** (deploy.DeploymentsByTicket) [visible for user consultant hoster developer senior admin]
<BLANKLINE>



