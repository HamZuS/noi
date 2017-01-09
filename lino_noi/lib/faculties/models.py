# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Database models for :mod:`lino_noi.lib.faculties`.

"""

import logging
# from lino_noi.lib.tickets.models import *

from lino.api import dd, _

# from lino.utils import join_elems
from lino.utils.xmlgen.html import E, join_elems

from django.db import models
from lino.mixins import Hierarchical, Sequenced
from lino.utils.mldbc.mixins import BabelNamed

from lino.modlib.users.mixins import UserAuthored

MAX_WEIGHT = 100


# class Faculty(BabelNamed, Hierarchical, Sequenced, Referrable):
class Faculty(BabelNamed, Hierarchical, Sequenced):
    """A **faculty** is a knowledge or ability which can be required in
    order to work e.g. on some ticket, and which individual users can
    have or not.

    """

    class Meta:
        verbose_name = _("Faculty")
        verbose_name_plural = _("Faculties")
        ordering = ['name']

    affinity = models.IntegerField(
        _("Affinity"), blank=True, default=MAX_WEIGHT,
        help_text=_(
            "How much workers enjoy to get a new ticket "
            "in this faculty."
            "A number between -{0} and +{0}.").format(MAX_WEIGHT))

    # topic_group = dd.ForeignKey(
    #     'topics.TopicGroup', blank=True, null=True,
    #     verbose_name=_("Options category"),
    #     help_text=_("The topic group to use for "
    #                 "specifying additional options."))


dd.update_field(Faculty, 'parent', verbose_name=_("Parent faculty"))


class Competence(UserAuthored, Sequenced):
    """A **competence** is when a given *user* is declared to be competent
    in a given *faculty*.

    .. attribute:: user
    .. attribute:: faculty
    .. attribute:: affinity
    .. attribute:: product

    """
    
    allow_cascaded_delete = "user"

    class Meta:
        verbose_name = _("Competence")
        verbose_name_plural = _("Competences")
        # unique_together = ['user', 'faculty', 'topic']
        unique_together = ['user', 'faculty']

    faculty = dd.ForeignKey('faculties.Faculty')
    affinity = models.IntegerField(
        _("Affinity"), blank=True, default=MAX_WEIGHT,
        help_text=_(
            "How much this user likes to get a new ticket "
            "in this faculty."
            "A number between -{0} and +{0}.").format(MAX_WEIGHT))
    # topic = dd.ForeignKey(
    #     'topics.Topic', blank=True, null=True,
    #     verbose_name=_("Option"),
    #     help_text=_("Some faculties can require additional "
    #                 "options for a competence."))

    # @dd.chooser()
    # def topic_choices(cls, faculty):
    #     Topic = rt.modules.topics.Topic
    #     if not faculty or not faculty.topic_group:
    #         return Topic.objects.none()
    #     return Topic.objects.filter(topic_group=faculty.topic_group)

    def full_clean(self, *args, **kw):
        if self.affinity is None:
            self.affinity = self.faculty.affinity
        # if self.faculty.product_cat:
        #     if not self.product:
        #         raise ValidationError(
        #             "A {0} competence needs a {1} as option")
        super(Competence, self).full_clean(*args, **kw)

    def __unicode__(self):
        return u'%s #%s' % (self._meta.verbose_name, self.pk)


dd.update_field(Competence, 'user', verbose_name=_("User"))

if dd.is_installed('tickets'):
    dd.inject_field(
        'tickets.Ticket', 'faculty',
        dd.ForeignKey("faculties.Faculty", blank=True, null=True))

from .ui import *
