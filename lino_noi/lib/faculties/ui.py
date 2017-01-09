# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)
from __future__ import unicode_literals

from django.db import models

from lino.api import dd, rt, _
from lino.modlib.users.mixins import My
from lino.modlib.users.desktop import Users
from lino_noi.lib.tickets.roles import Triager

class Faculties(dd.Table):
    model = 'faculties.Faculty'
    # order_by = ["ref", "name"]
    detail_layout = """
    id name
    parent affinity
    FacultiesByParent CompetencesByFaculty
    """
    insert_layout = """
    name
    parent
    """


class AllFaculties(Faculties):
    label = _("Faculties (all)")
    required_roles = dd.required(dd.SiteStaff)
    column_names = 'name affinity parent *'
    order_by = ["name"]


class TopLevelFaculties(Faculties):
    label = _("Faculties (tree)")
    required_roles = dd.required(dd.SiteStaff)
    order_by = ["name"]
    column_names = 'name id children_summary parent *'
    filter = models.Q(parent__isnull=True)
    variable_row_height = True


class FacultiesByParent(Faculties):
    label = _("Child faculties")
    master_key = 'parent'
    column_names = 'seqno name affinity *'
    order_by = ["seqno"]
    # order_by = ["parent", "seqno"]
    # order_by = ["name"]
    

class Competences(dd.Table):
    required_roles = dd.required(dd.SiteStaff)
    # required_roles = dd.required(SocialStaff)
    model = 'faculties.Competence'
    column_names = 'id user faculty affinity *'
    order_by = ["id"]


class CompetencesByUser(Competences):
    required_roles = dd.required()
    master_key = 'user'
    column_names = 'seqno faculty affinity *'
    order_by = ["seqno"]


class CompetencesByFaculty(Competences):
    master_key = 'faculty'
    column_names = 'user affinity *'
    order_by = ["user"]


class MyCompetences(My, CompetencesByUser):
    pass

if dd.is_installed('tickets'):
    class AssignableWorkersByTicket(Users):
        # model = 'users.User'
        use_as_default_table = False
        # model = 'faculties.Competence'
        master = 'tickets.Ticket'
        column_names = 'username #faculties_competence_set_by_user__affinity *'
        label = _("Assignable workers")
        required_roles = dd.login_required(Triager)

        @classmethod
        def get_request_queryset(self, ar):
            ticket = ar.master_instance
            if ticket is None:
                return rt.models.users.User.objects.none()

            # rt.models.faculties.Competence.objects.filter(
            #     faculty=ticket.faculty)
            qs = rt.models.users.User.objects.all()
            # qs = super(
            #     AssignableWorkersByTicket, self).get_request_queryset(ar)

            if ticket.topic:
                qs = qs.filter(
                    faculties_competence_set_by_user__topic=ticket.topic)
            if ticket.faculty:
                # faculties = ticket.faculty.whole_clan()
                faculties = ticket.faculty.get_parental_line()
                qs = qs.filter(
                    faculties_competence_set_by_user__faculty__in=faculties)
            qs = qs.order_by('faculties_competence_set_by_user__affinity')
            return qs

