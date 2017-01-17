.. _noi.specs.clocking:

==================
Work time tracking
==================

.. How to test only this document:

    $ python setup.py test -s tests.SpecsTests.test_clocking
    
    doctest init:

    >>> from lino import startup
    >>> startup('lino_noi.projects.team.settings.doctests')
    >>> from lino.api.doctest import *


Lino Noi uses both :mod:`lino_noi.lib.tickets` (Ticket management) and
:mod:`lino_noi.lib.clocking` (Development time tracking).

Note that the demo data is on fictive demo date **May 23, 2015**:

>>> dd.today()
datetime.date(2015, 5, 23)


Sessions
========

A :class:`Session <lino_noi.lib.clocking.models.Session>` is when a
user works on a ticket for a given lapse of time.

When end_time is empty, it means that he is still working.

>>> rt.show(clocking.Sessions, limit=15)
... #doctest: -REPORT_UDIFF
================================================= ========= ============ ============ ============ ========== ============ ========= ===========
 Ticket                                            Worker    Start date   Start time   End Date     End Time   Break Time   Summary   Duration
------------------------------------------------- --------- ------------ ------------ ------------ ---------- ------------ --------- -----------
 #2 (Bar is not always baz)                        jean      23/05/2015   09:00:00
 #1 (Föö fails to bar when baz)                    luc       23/05/2015   09:00:00
 #3 (Baz sucks)                                    mathieu   23/05/2015   09:00:00
 #5 (Cannot create Foo)                            jean      22/05/2015   09:00:00     22/05/2015   11:18:00                          2:18
 #4 (Foo and bar don't baz)                        luc       22/05/2015   09:00:00     22/05/2015   12:29:00                          3:29
 #12 (Foo cannot bar)                              mathieu   22/05/2015   09:00:00     22/05/2015   12:53:00                          3:53
 #30 (Ticket 30)                                   mathieu   20/05/2015   09:05:00     20/05/2015   09:17:00                          0:12
 #7 (No Foo after deleting Bar)                    jean      20/05/2015   09:00:00     20/05/2015   10:30:00                          1:30
 #10 (Where can I find a Foo when bazing Bazes?)   luc       20/05/2015   09:00:00     20/05/2015   09:37:00                          0:37
 #21 (Ticket 21)                                   mathieu   20/05/2015   09:00:00     20/05/2015   09:05:00                          0:05
 #11 (Class-based Foos and Bars?)                  jean      19/05/2015   09:00:00     19/05/2015   09:10:00                          0:10
 #13 (Bar cannot foo)                              luc       19/05/2015   09:00:00     19/05/2015   10:02:00                          1:02
 #39 (Ticket 39)                                   mathieu   19/05/2015   09:00:00     19/05/2015   11:18:00                          2:18
 **Total (13 rows)**                                                                                                                  **15:34**
================================================= ========= ============ ============ ============ ========== ============ ========= ===========
<BLANKLINE>


Some sessions are on private tickets:

>>> from django.db.models import Q
>>> rt.show(clocking.Sessions, column_names="ticket user duration ticket__project", filter=Q(ticket__private=True))
... #doctest: -REPORT_UDIFF
============================ ========= ========== =========
 Ticket                       Worker    Duration   Project
---------------------------- --------- ---------- ---------
 #2 (Bar is not always baz)   jean                 téam
 #3 (Baz sucks)               mathieu
 #5 (Cannot create Foo)       jean      2:18
 #39 (Ticket 39)              mathieu   2:18       téam
 **Total (4 rows)**                     **4:36**
============================ ========= ========== =========
<BLANKLINE>


Worked hours
============

This table shows the last seven days, one row per day, with your
working hours.

>>> rt.login('jean').show(clocking.WorkedHours)
... #doctest: -REPORT_UDIFF
======================================= ========== ========== ==========
 Description                             linö       shop       Total
--------------------------------------- ---------- ---------- ----------
 **Sat 23/05/2015** (`#2 <Detail>`__)    0:01                  0:01
 **Fri 22/05/2015** (`#5 <Detail>`__)                          2:18
 **Thu 21/05/2015**                                            0:00
 **Wed 20/05/2015** (`#7 <Detail>`__)               1:30       1:30
 **Tue 19/05/2015** (`#11 <Detail>`__)   0:10                  0:10
 **Mon 18/05/2015**                                            0:00
 **Sun 17/05/2015**                                            0:00
 **Total (7 rows)**                      **0:11**   **1:30**   **3:59**
======================================= ========== ========== ==========
<BLANKLINE>


In the "description" column you see a list of the tickets on which you
worked that day. This is a convenient way to continue some work you
started some days ago.

.. 
    Find the users who worked on more than one project:
    >>> for u in users.User.objects.all():
    ...     qs = tickets.Project.objects.filter(tickets_by_project__sessions_by_ticket__user=u).distinct()
    ...     if qs.count() > 1:
    ...         print u.username, "worked on", [o for o in qs]
    jean worked on [Project #2 ('t\xe9am'), Project #5 ('shop'), Project #4 ('research')]
    luc worked on [Project #1 ('lin\xf6'), Project #3 ('docs')]
    mathieu worked on [Project #5 ('shop'), Project #4 ('research'), Project #3 ('docs'), Project #2 ('t\xe9am')]

Render this table to HTML in order to reproduce :ticket:`523`:

>>> url = "/api/clocking/WorkedHours?"
>>> url += "_dc=1442341081053&cw=430&cw=83&cw=83&cw=83&cw=83&cw=83&cw=83&ch=&ch=&ch=&ch=&ch=&ch=&ch=&ci=description&ci=vc0&ci=vc1&ci=vc2&ci=vc3&ci=vc4&ci=vc5&name=0&pv=16.05.2015&pv=23.05.2015&pv=7&an=show_as_html&sr="
>>> res = test_client.get(url, REMOTE_USER="jean")
>>> json.loads(res.content)
{u'open_url': u'/bs3/clocking/WorkedHours?limit=15', u'success': True}


The html version of this table table has only 5 rows (4 data rows and
the total row) because valueless rows are not included by default:

>>> ar = rt.login('jean')
>>> u = ar.get_user()
>>> ar = clocking.WorkedHours.request(user=u)
>>> ar = ar.spawn(clocking.WorkedHours)
>>> lst = list(ar)
>>> len(lst)
7
>>> e = ar.table2xhtml()
>>> len(e.findall('./tbody/tr'))
5




Service Report
==============

A service report (:class:`clocking.ServiceReport
<lino_noi.lib.clocking.ui.ServiceReport>`) is a document which reports
about the hours invested during a given date range.  It can be
addressed to a recipient (a user) and in that case will consider only
the tickets for which this user has specified interest.

It currently contains two tables:

- a list of tickets, with invested time (i.e. the sum of durations
  of all sessions that lie in the given data range)
- a list of projects, with invested time and list of the tickets that
  are assigned to this project.

This report is useful for developers like me because it serves as a
base for writing invoices.


>>> obj = clocking.ServiceReport.objects.get(pk=1)
>>> obj.printed_by.build_method
<BuildMethods.weasy2html:weasy2html>


>>> obj.interesting_for
Partner #100 ('welket')

>>> rt.show(clocking.TicketsByReport, obj)
... #doctest: -REPORT_UDIFF
==== ============================================================================================== ======== ===========
 ID   Description                                                                                    State    Time
---- ---------------------------------------------------------------------------------------------- -------- -----------
 1    Föö fails to bar when baz. Site: welket. Author: jean. Project: linö. Topic: Lino Cosi         New      0:00
 4    Foo and bar don't baz. Author: jean. Project: docs. Topic: Lino Welfare                        Sticky   3:29
 7    No Foo after deleting Bar. Site: welket. Author: mathieu. Project: shop. Topic: Lino Core      Ready    1:30
 11   Class-based Foos and Bars?. Site: pypi. Author: mathieu. Project: research. Topic: Lino Core   Talk     0:10
 12   Foo cannot bar. Author: luc. Project: shop. Topic: Lino Welfare                                Opened   3:53
 13   Bar cannot foo. Site: welket. Author: jean. Project: linö. Topic: Lino Cosi                    Sticky   1:02
 21   Ticket 21. Site: welsch. Author: luc. Project: research. Topic: Lino Cosi                      Opened   0:05
                                                                                                              **10:09**
==== ============================================================================================== ======== ===========
<BLANKLINE>


The :class:`ProjectsByReport
<lino_noi.projects.team.lib.clocking.ui.ProjectsByReport>`
table lists all projects and the time invested.

>>> rt.show(clocking.ProjectsByReport, obj)
==================== =============== ======== ==================================== =========== ============
 Reference            Name            Parent   Tickets                              Time        Total time
-------------------- --------------- -------- ------------------------------------ ----------- ------------
 docs                 Documentatión   linö     `#4 <Detail>`__                      3:29        3:44
 linö                 Framewörk                `#13 <Detail>`__                     1:02        4:46
 research             Research        docs     `#21 <Detail>`__, `#11 <Detail>`__   0:15        0:15
 shop                 Shop                     `#12 <Detail>`__, `#7 <Detail>`__    5:23        5:23
 **Total (4 rows)**                                                                 **10:09**
==================== =============== ======== ==================================== =========== ============
<BLANKLINE>


Note our tree structure (which is currently not very visible)::

  - linö
    - docs
      - research
    - téam
  - shop


The `Total time` column in this table is the `Time` invested for this
project and the sum of times invested in all of its children.

The `Total time` for "linö" in above table is **12:09**, which is the
sum of **3:29** (direct time of linö) + **6:28** (time of docs) +
**2:12** (time of research).
