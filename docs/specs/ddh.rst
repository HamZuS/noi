.. _noi.specs.ddh:

=============================
Preventing accidental deletes
=============================

.. How to test only this document:

    $ python setup.py test -s tests.SpecsTests.test_ddh
    
    doctest init:

    >>> import lino
    >>> lino.startup('lino_noi.projects.team.settings.doctests')
    >>> from lino.api.doctest import *


Foreign Keys and their `on_delete` setting
==========================================

Here is the output of :meth:`lino.utils.diag.Analyzer.show_foreign_keys` in
Lino Noi:


>>> from lino.utils.diag import analyzer
>>> print(analyzer.show_foreign_keys())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- blogs.Entry :
  - CASCADE : blogs.Tagging.entry
- blogs.EntryType :
  - PROTECT : blogs.Entry.entry_type
- clocking.SessionType :
  - PROTECT : clocking.Session.session_type
- contacts.Company :
  - PROTECT : contacts.Role.company, excerpts.Excerpt.company, system.SiteConfig.site_company, tickets.Project.company
- contacts.CompanyType :
  - PROTECT : contacts.Company.type
- contacts.Partner :
  - CASCADE : contacts.Company.partner_ptr, contacts.Person.partner_ptr
  - PROTECT : clocking.ServiceReport.interesting_for, lists.Member.partner, outbox.Recipient.partner, tickets.Site.partner, topics.Interest.partner, users.User.partner
- contacts.Person :
  - PROTECT : contacts.Role.person, excerpts.Excerpt.contact_person, tickets.Project.contact_person
- contacts.RoleType :
  - PROTECT : contacts.Role.type, excerpts.Excerpt.contact_role, tickets.Project.contact_role
- contenttypes.ContentType :
  - PROTECT : blogs.Entry.owner_type, changes.Change.master_type, changes.Change.object_type, comments.Comment.owner_type, excerpts.Excerpt.owner_type, excerpts.ExcerptType.content_type, gfks.HelpText.content_type, notify.Message.owner_type, outbox.Attachment.owner_type, outbox.Mail.owner_type, uploads.Upload.owner_type
- countries.Country :
  - PROTECT : contacts.Partner.country, countries.Place.country, users.User.country
- countries.Place :
  - PROTECT : contacts.Partner.city, contacts.Partner.region, countries.Place.parent, users.User.city, users.User.region
- deploy.Milestone :
  - PROTECT : deploy.Deployment.milestone, tickets.Ticket.fixed_for, tickets.Ticket.reported_for
- excerpts.Excerpt :
  - SET_NULL : clocking.ServiceReport.printed_by, deploy.Milestone.printed_by
- excerpts.ExcerptType :
  - PROTECT : excerpts.Excerpt.excerpt_type
- faculties.Faculty :
  - PROTECT : clocking.Session.faculty, faculties.Competence.faculty, faculties.Faculty.parent, tickets.Ticket.faculty
- lists.List :
  - PROTECT : lists.Member.list
- lists.ListType :
  - PROTECT : lists.List.list_type
- outbox.Mail :
  - CASCADE : outbox.Attachment.mail, outbox.Recipient.mail
- tickets.Project :
  - PROTECT : excerpts.Excerpt.project, outbox.Mail.project, tickets.Project.parent, tickets.Ticket.project
- tickets.ProjectType :
  - PROTECT : tickets.Project.type
- tickets.Site :
  - PROTECT : deploy.Milestone.site, tickets.Ticket.site, users.User.user_site
- tickets.Ticket :
  - PROTECT : clocking.Session.ticket, deploy.Deployment.ticket, tickets.Link.child, tickets.Link.parent, tickets.Ticket.duplicate_of, votes.Vote.votable
- tickets.TicketType :
  - PROTECT : tickets.Ticket.ticket_type
- topics.Topic :
  - CASCADE : blogs.Tagging.topic
  - PROTECT : faculties.Competence.topic, tickets.Ticket.topic, topics.Interest.topic
- topics.TopicGroup :
  - PROTECT : faculties.Faculty.topic_group, topics.Topic.topic_group
- uploads.UploadType :
  - PROTECT : uploads.Upload.type
- users.User :
  - CASCADE : faculties.Competence.user
  - PROTECT : blogs.Entry.user, changes.Change.user, clocking.ServiceReport.user, clocking.Session.user, comments.Comment.user, dashboard.Widget.user, excerpts.Excerpt.user, notify.Message.user, outbox.Mail.user, tickets.Project.assign_to, tickets.Ticket.reporter, tickets.Ticket.user, tinymce.TextFieldTemplate.user, uploads.Upload.user, users.Authority.authorized, users.Authority.user, votes.Vote.user
