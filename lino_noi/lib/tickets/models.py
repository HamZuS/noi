# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""This module adds models for Projects, Tickets & Co.

A **Project** is something into which somebody (the `partner`) invests
time, energy and money.  The partner can be either external or the
runner of the site.  Projects form a tree: each Project can have a
`parent` (another Project for which it is a sub-project).

Projects are handled by their *name* while Tickets are handled by
their *number*.

.. rubric:: Change notifications

The ticket :attr:`reporter <Ticket.reporter>` and the
:attr:`assigned_to <Ticket.assigned_to>` worker get automatically
notified about any change.  This is similar to what happens in
:mod:`lino_xl.lib.stars.models`, except that the reporter and the
assignee don't need to star a ticket in order to get notified.

"""

from __future__ import unicode_literals

import six
from builtins import str

from importlib import import_module
import inspect
    
from django.conf import settings
from django.db import models
from django.db.models import Q

from atelier.sphinxconf.base import srcref

from lino import mixins
from lino.api import dd, rt, _, pgettext

from lino.utils.xmlgen.html import E

from lino_xl.lib.cal.mixins import daterange_text
from lino_xl.lib.contacts.mixins import ContactRelated
from lino.modlib.users.mixins import UserAuthored, Assignable
from lino.modlib.comments.mixins import RFC
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_noi.lib.votes.mixins import Votable
from lino_noi.lib.clocking.mixins import Workable
from lino.utils import join_elems

from .choicelists import TicketEvents, TicketStates, LinkTypes
from .roles import Triager


class TimeInvestment(dd.Model):
    """Model mixin for things which represent a time investment.  This
    currently just defines a group of three fields:

    .. attribute:: closed

        Whether this investment is closed, i.e. certain things should
        not change anymore.

    .. attribute:: private

        Whether this investment is private, i.e. should not be
        publicly visible anywhere.
        
        The default value is True.  Tickets on public projects cannot
        be private, but tickets on private projects may be manually
        set to public.

    .. attribute:: planned_time

        The time (in hours) we plan to work on this project or ticket.

    """
    class Meta:
        abstract = True

    closed = models.BooleanField(_("Closed"), default=False)
    private = models.BooleanField(_("Private"), default=True)

    planned_time = models.TimeField(
        _("Planned time"),
        blank=True, null=True)

    # invested_time = models.TimeField(
    #     _("Invested time"), blank=True, null=True, editable=False)


class ProjectType(mixins.BabelNamed):
    """The type of a :class:`Project`."""

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Project Type")
        verbose_name_plural = _('Project Types')


class TicketType(mixins.BabelNamed):
    """The type of a :class:`Ticket`."""

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Ticket type")
        verbose_name_plural = _('Ticket types')


#~ class Repository(UserAuthored):
    #~ class Meta:
        #~ verbose_name = _("Repository")
        #~ verbose_name_plural = _('Repositories')


@dd.python_2_unicode_compatible
class Project(mixins.DatePeriod, TimeInvestment,
              mixins.Hierarchical, mixins.Referrable,
              ContactRelated):
    """A **project** is something on which several users work together.

    .. attribute:: name

    .. attribute:: parent

    .. attribute:: assign_to

        The user to whom new tickets will be assigned.
        See :attr:`Ticket.assigned_to`.

    """
    class Meta:
        app_label = 'tickets'
        verbose_name = _("Project")
        verbose_name_plural = _('Projects')

    name = models.CharField(_("Name"), max_length=200)
    # parent = models.ForeignKey(
    #     'self', blank=True, null=True, verbose_name=_("Parent"))
    assign_to = dd.ForeignKey(
        settings.SITE.user_model,
        verbose_name=_("Assign tickets to"),
        blank=True, null=True,
        help_text=_("The user to whom new tickets will be assigned."))
    type = dd.ForeignKey('tickets.ProjectType', blank=True, null=True)
    description = dd.RichTextField(_("Description"), blank=True)
    srcref_url_template = models.CharField(blank=True, max_length=200)
    changeset_url_template = models.CharField(blank=True, max_length=200)
    # root = models.ForeignKey(
    #     'self', blank=True, null=True, verbose_name=_("Root"))

    def __str__(self):
        return self.ref or self.name

    @dd.displayfield(_("Activity overview"))
    def activity_overview(self, ar):
        if ar is None:
            return ''
        TicketsByProject = rt.modules.tickets.TicketsByProject
        elems = []
        for tst in (TicketStates.objects()):
            pv = dict(state=tst)
            sar = ar.spawn(
                TicketsByProject, master_instance=self, param_values=pv)
            num = sar.get_total_count()
            if num > 0:
                elems += [
                    "{0}: ".format(tst.text),
                    sar.ar2button(label=str(num))]
        return E.p(*elems)


    # def save(self, *args, **kwargs):
    #     root = self.parent
    #     while root is not None:
    #         if root.parent is None:
    #             break
    #         else:
    #             root = root.parent
    #     self.root = root
    #     super(Project, self).save(*args, **kwargs)


@dd.python_2_unicode_compatible
class Site(dd.Model):
    class Meta:
        app_label = 'tickets'
        verbose_name = pgettext("Ticketing", "Site")
        verbose_name_plural = pgettext("Ticketing", "Sites")

    partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)
    # responsible_user = dd.ForeignKey(
    #     'users.User', verbose_name=_("Responsible"),
    #     blank=True, null=True)
    name = models.CharField(_("Designation"), max_length=200)
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    def __str__(self):
        return self.name


@dd.python_2_unicode_compatible
class Link(dd.Model):

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Dependency")
        verbose_name_plural = _("Dependencies")

    type = LinkTypes.field(
        default=LinkTypes.requires.as_callable)
    parent = dd.ForeignKey(
        'tickets.Ticket',
        verbose_name=_("Parent"),
        related_name='tickets_children')
    child = dd.ForeignKey(
        'tickets.Ticket',
        blank=True, null=True,
        verbose_name=_("Child"),
        related_name='tickets_parents')

    @dd.displayfield(_("Type"))
    def type_as_parent(self, ar):
        # print('20140204 type_as_parent', self.type)
        return self.type.as_parent()

    @dd.displayfield(_("Type"))
    def type_as_child(self, ar):
        # print('20140204 type_as_child', self.type)
        return self.type.as_child()

    def __str__(self):
        if self.type is None:
            return "Link object"  # super(Link, self).__unicode__()
        return _("%(child)s is %(what)s") % dict(
            child=str(self.child),
            what=self.type_of_parent_text())

    def type_of_parent_text(self):
        return _("%(type)s of %(parent)s") % dict(
            parent=self.parent,
            type=self.type.as_child())


# class CloseTicket(dd.Action):
#     #label = _("Close ticket")
#     label = "\u2611"
#     help_text = _("Mark this ticket as closed.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is not None or obj.closed is not None:
#             return False
#         return super(CloseTicket, self).get_action_permission(ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         now = datetime.datetime.now()
#         for obj in ar.selected_rows:
#             obj.closed = now
#             obj.save()
#             ar.set_response(refresh=True)


# class StandbyTicket(dd.Action):
#     #label = _("Standby mode")
#     label = "\u2a37"
#     label = "\u2609"
#     help_text = _("Put this ticket into standby mode.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is not None or obj.closed is not None:
#             return False
#         return super(StandbyTicket, self).get_action_permission(
#             ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         now = datetime.datetime.now()
#         for obj in ar.selected_rows:
#             obj.standby = now
#             obj.save()
#             ar.set_response(refresh=True)


# class ActivateTicket(dd.Action):
#     # label = _("Activate")
#     label = "☀"  # "\u2600"
#     help_text = _("Reactivate this ticket from standby mode or closed state.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is None and obj.closed is None:
#             return False
#         return super(ActivateTicket, self).get_action_permission(
#             ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         for obj in ar.selected_rows:
#             obj.standby = False
#             obj.closed = False
#             obj.save()
#             ar.set_response(refresh=True)


class SpawnTicket(dd.Action):
    # label = _("Spawn new ticket")
    # label = "\u2611" "☑"
    # label = "⚇"  # "\u2687"
    show_in_workflow = False
    show_in_bbar = False

    def __init__(self, label, link_type):
        self.label = label
        self.link_type = link_type
        self.help_text = _(
            "Spawn a new child ticket {0} this one.").format(
            link_type.as_child())
        super(SpawnTicket, self).__init__()

    def run_from_ui(self, ar, **kw):
        p = ar.selected_rows[0]
        c = rt.modules.tickets.Ticket(
            reporter=ar.get_user(),
            summary=_("New ticket {0} #{1}".format(
                self.link_type.as_child(), p.id)))
        for k in ('project', 'private'):
            setattr(c, k, getattr(p, k))
        c.full_clean()
        c.save()
        d = rt.modules.tickets.Link(
            parent=p, child=c,
            type=self.link_type)
        d.full_clean()
        d.save()
        ar.success(
            _("New ticket {0} has been spawned as child of {1}.").format(
                c, p))
        ar.goto_instance(c)


@dd.python_2_unicode_compatible
class Ticket(UserAuthored, mixins.CreatedModified,
             TimeInvestment, RFC, Votable, Workable):
    """A **Ticket** is a concrete question or problem formulated by a
    :attr:`reporter` (a user).
    
    A Ticket is always related to one and only one Project.  It may be
    related to other tickets which may belong to other projects.


    .. attribute:: user

        The user who entered this ticket and is responsible for
        managing it.

    .. attribute:: reporter

        The user who is asking for help.

    .. attribute:: assigned_to

        No longer used. The user who is working on this ticket.

        If this field is empty and :attr:`project` is not empty, then
        default value is taken from :attr:`Project.assign_to`.

    .. attribute:: state

        The state of this ticket. See :class:`TicketStates
        <lino_noi.lib.tickets.choicelists.TicketStates>`

    .. attribute:: waiting_for

        What to do next. An unformatted one-line text which describes
        what this ticket is waiting for.

    .. attribute:: upgrade_notes

        A formatted text field meant for writing instructions for the
        hoster's site administrator when doing an upgrade where this
        ticket is being deployed.

    .. attribute:: description

        A complete and concise description of the ticket. This should
        describe in more detail what this ticket is about. If the
        ticket has evolved during time, it should reflect the latest
        version.

        The description can contain memo commands (see :doc:`/specs/memo`).

    .. attribute:: duplicate_of

        A pointer to the ticket which is the cause of this ticket.

        A ticket with a non-empty :attr:`duplicate_of` field can be
        called a "duplicate".  The number of a duplicate is
        theoretically higher than the number of the ticket it
        duplicates.

        The :attr:`state` of a duplicate does not automatically become
        that of the duplicated ticket.  Each ticket continues to have
        its own state. Example: Some long time ago, with Mathieu, we
        agreed that ticket #100 can go to *Sleeping*. Now Aurélie
        reported the same problem again as #904. This means that we
        should talk about it. And even before talking with her, I'd
        like to have a look at the code in order to estimate whether
        it is difficult or not, so I set the state of #904 to ToDo.

        Wouldn't it be preferrable to replace the :attr:`duplicate_of
        field by a :class:`LinkType
        <lino_noi.lib.tickets.choicelists.LinkTypes>` called
        "Duplicated/Duplicated by"?  No. We had this before and
        preferred the field, because a field is at least one click
        less, and because we *want* users to define a clear hiearchy
        with a clear root ticket. You can have a group of tickets
        which are all direct or indirect duplicates of this "root of
        all other problems".

    .. attribute:: deadline

        Specify that the ticket must be done for a given date.

        TODO: Triagers should have a table of tickets having this
        field non-empty and are still in an active state.

    .. attribute:: priority

        How urgent this ticket is. This should be a value between 0
        and 100.

    .. attribute:: rating

        How the reporter rates this ticket.

    """

    quick_search_fields = "summary description"

    workflow_state_field = 'state'
    # author_field_name = 'reporter'

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Ticket")
        verbose_name_plural = _('Tickets')
        abstract = dd.is_abstract_model(__name__, 'Ticket')

    project = dd.ForeignKey(
        'tickets.Project', blank=True, null=True,
        related_name="tickets_by_project")
    site = dd.ForeignKey('tickets.Site', blank=True, null=True)
    topic = dd.ForeignKey('topics.Topic', blank=True, null=True)
    nickname = models.CharField(_("Nickname"), max_length=50, blank=True)
    summary = models.CharField(
        pgettext("Ticket", "Summary"), max_length=200,
        blank=True,
        help_text=_("Short summary of the problem."))
    description = dd.RichTextField(_("Description"), blank=True)
    upgrade_notes = dd.RichTextField(_("Upgrade notes"), blank=True)
    ticket_type = dd.ForeignKey('tickets.TicketType', blank=True, null=True)
    duplicate_of = models.ForeignKey(
        'self', blank=True, null=True, verbose_name=_("Duplicate of"))

    reported_for = dd.ForeignKey(
        'deploy.Milestone',
        related_name='tickets_reported',
        verbose_name='Reported for',
        blank=True, null=True,
        help_text=_("Milestone for which this ticket has been reported."))
    fixed_for = dd.ForeignKey(  # no longer used since 20150814
        'deploy.Milestone',
        related_name='tickets_fixed',
        verbose_name='Fixed for',
        blank=True, null=True,
        help_text=_("The milestone for which this ticket has been fixed."))
    # assigned_to = dd.ForeignKey(
    #     settings.SITE.user_model,
    #     verbose_name=_("Assigned to"),
    #     related_name="assigned_tickets",
    #     blank=True, null=True,
    #     help_text=_("The user who works on this ticket."))

    reporter = dd.ForeignKey(
        settings.SITE.user_model,
        verbose_name=_("Reporter"),
        related_name="reported_tickets")
    state = TicketStates.field(default=TicketStates.as_callable('new'))
    # rating = Ratings.field(blank=True)
    waiting_for = models.CharField(
        _("Waiting for"), max_length=200, blank=True)

    deadline = models.DateField(
        verbose_name=_("Deadline"),
        blank=True, null=True)

    priority = models.SmallIntegerField(_("Priority"), default=100)

    # deprecated fields:
    feedback = models.BooleanField(
        _("Feedback"), default=False)
    standby = models.BooleanField(_("Standby"), default=False)

    spawn_triggered = SpawnTicket(
        _("Spawn triggered ticket"),
        LinkTypes.triggers)
    # spawn_triggered = SpawnTicket("⚇", LinkTypes.triggers)  # "\u2687"
    # spawn_ticket = SpawnTicket("", LinkTypes.requires)  # "\u2687"

    # def get_rfc_description(self, ar):
    #     return ar.parse_memo(self.description)

    def on_create(self, ar):
        # print "20150523a on_create", self.reporter_id
        # print "20150523a on_create", self.reporter_id
        me = ar.get_user()
        if me is not None:
            if self.reporter_id is None:
                self.reporter = me
            # if self.assigned_to_id is None:
            #     if me.profile.has_required_roles([Triager]):
            #         self.assigned_to = me
        if self.reporter_id and self.reporter.user_site:
            self.site = self.reporter.user_site
        super(Ticket, self).on_create(ar)

    def full_clean(self):
        """If :attr:`project` is not set and if the ticket has a
        :attr:`reporter`, use that reporter's :attr:`current_project`
        as default value.

        """
        if self.id and self.duplicate_of_id == self.id:
            self.duplicate_of = None
        # print "20150523b on_create", self.reporter
        super(Ticket, self).full_clean()
        me = self.reporter
        if False:
            if me and not self.project and me.current_project:
                self.project = me.current_project
        if self.project:
            # if not self.assigned_to and self.project.assign_to:
            #     self.assigned_to = self.project.assign_to
            if not self.project.private:
                self.private = False

    def disabled_fields(self, ar):
        rv = super(Ticket, self).disabled_fields(ar)
        if self.project and not self.project.private:
            rv.add('private')
        if not ar.get_user().profile.has_required_roles([Triager]):
            rv.add('assigned_to')
            rv.add('reporter')            
        return rv

    # def get_choices_text(self, request, actor, field):
    #     return "{0} ({1})".format(self, self.summary)

    def __str__(self):
        if self.nickname:
            return "#{0} ({1})".format(self.id, self.nickname)
        return "#{0} ({1})".format(self.id, self.summary)

    @dd.chooser()
    def reported_for_choices(cls, site):
        if not site:
            return []
        # return site.milestones_by_site.filter(reached__isnull=False)
        return site.milestones_by_site.all()

    @dd.chooser()
    def fixed_for_choices(cls, site):
        if not site:
            return []
        return site.milestones_by_site.all()

    def get_overview(self, ar):
        return E.span(
            ar.obj2html(self), _(" by "),
            ar.obj2html(self.reporter))

    @dd.displayfield(_("Description"))
    def overview(self, ar):
        if ar is None:
            return ''
        return self.get_overview(ar)
        
        # return ar.obj2html(self, "#{0}".self.id)
        # return ar.obj2html(self)
        # return E.span(ar.obj2html(self), ' ', self.summary)

    # def get_notify_message(self, ar, cw):
    #     return E.tostring(E.p(
    #         _("{user} worked on [ticket {t}]").format(
    #             user=ar.get_user(), t=self.id)))

    def get_vote_rater(self):
        return self.reporter
       
    def is_workable_for(self, user):
        if self.standby or self.closed:
            return False
        if not self.state.active and not user.profile.has_required_roles(
                [Triager]):
            return False
        return True
        
# dd.update_field(Ticket, 'user', verbose_name=_("Reporter"))


dd.inject_field(
    'users.User', 'user_site',
    dd.ForeignKey(
        'tickets.Site', # verbose_name=_("Site"),
        blank=True, null=True, related_name="users_by_site",
        help_text=_("")))


@dd.receiver(dd.post_ui_build)
def setup_memo_commands(sender=None, **kwargs):
    """See :doc:`/specs/memo`."""
    def ticket2html(parser, s):
        ar = parser.context['ar']
        # dd.logger.info("20161019 %s", ar.renderer)
        pk = int(s)
        obj = sender.site.models.tickets.Ticket.objects.get(pk=pk)
        text = "#{0}".format(obj.id)
        e = ar.obj2html(obj, text, title=obj.summary)
        return E.tostring(e)
        # url = rnd.get_detail_url(obj)
        # title = obj.summary
        # return '<a href="{0}" title="{2}">{1}</a>'.format(url, text, title)

    sender.memo_parser.register_command('ticket', ticket2html)


    def py2html(parser, s):
        args = s.split(None, 1)
        if len(args) == 1:
            txt = s
        else:
            s = args[0]
            txt = args[1]
        parts = s.split('.')
        obj = import_module(parts[0])
        for p in parts[1:]:
            try:
                obj = getattr(obj, p)
            except AttributeError:
                break
        mod = inspect.getmodule(obj)
        url = srcref(mod)
        # fn = inspect.getsourcefile(obj)
        if url:
            # lines = inspect.getsourcelines(s)
            return '<a href="{0}" target="_blank">{1}</a>'.format(url, txt)
        return "<pre>{}</pre>".format(s)
    sender.memo_parser.register_command('py', py2html)


    # rnd = sender.site.plugins.extjs.renderer
    
    # def f(s):
    #     pk = int(s)
    #     obj = sender.modules.tickets.Ticket.objects.get(pk=pk)
    #     url = rnd.get_detail_url(obj)
    #     text = "#{0}".format(obj.id)
    #     title = obj.summary
    #     return '<a href="{0}" title="{2}">{1}</a>'.format(url, text, title)

    # rnd.memo_parser.register_command('ticket', f)


from .ui import *
