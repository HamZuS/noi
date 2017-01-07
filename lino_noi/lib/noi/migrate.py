# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""This is a real-world example of how the application developer
can provide automatic data migrations for :ref:`dpy`.

This module is used because a :ref:`noi` Site has
:attr:`migration_class <lino.core.site.Site.migration_class>` set to
``"lino_noi.lib.migrate.Migrator"``.

"""

from django.conf import settings
from lino.api import dd, rt
from lino.utils.dpy import Migrator, override


def noop(*args):
    return None


class Migrator(Migrator):
    "The standard migrator for :ref:`noi`."

    def migrate_from_0_0_1(self, globals_dict):
        """
        - Convert products to topics.
        - Interest.product becomes Interest.topic
        - Interest.site.partner becomes Interest.partner and if the site has
          no partner, create one.
        - Rename Faculty.product_cat to topic_group
        - Rename Competence.product to Competence.topic
           
        """

        bv2kw = globals_dict['bv2kw']
        products_Product = rt.models.topics.Topic
        products_ProductCat = rt.models.topics.TopicGroup
        faculties_Competence = rt.models.faculties.Competence
        faculties_Faculty = rt.models.faculties.Faculty
        tickets_Site = rt.models.tickets.Site
        tickets_Interest = rt.models.topics.Interest
        tickets_Ticket = rt.models.tickets.Ticket
        Partner = dd.resolve_model(dd.plugins.topics.partner_model)

        @override(globals_dict)
        def create_tickets_site(id, partner_id, name, remark):
            kw = dict()
            kw.update(id=id)
            kw.update(partner_id=partner_id)
            kw.update(name=name)
            kw.update(remark=remark)
            return tickets_Site(**kw)

        @override(globals_dict)
        def create_tickets_interest(id, product_id, site_id):
            kw = dict()
            kw.update(id=id)
            kw.update(topic_id=product_id)
            try:
                partner = Partner.objects.get(id=site_id)
            except Partner.DoesNotExist:
                partner = Partner(id=site_id, name=str(site_id))
                partner.save()
            kw.update(partner=partner)
            return tickets_Interest(**kw)

        @override(globals_dict)
        def create_products_productcat(id, name, description):
            kw = dict()
            kw.update(id=id)
            if name is not None: kw.update(bv2kw('name', name))
            kw.update(description=description)
            return products_ProductCat(**kw)

        @override(globals_dict)
        def create_products_product(id, ref, name, description, cat_id):
            kw = dict()
            kw.update(id=id)
            kw.update(ref=ref)
            if name is not None: kw.update(bv2kw('name', name))
            if description is not None: kw.update(bv2kw('description', description))
            kw.update(topic_group_id=cat_id)
            return products_Product(**kw)

        @override(globals_dict)
        def create_tickets_ticket(id, modified, created, closed, private, planned_time, project_id, site_id, product_id,
                                  nickname, summary, description, upgrade_notes, ticket_type_id, duplicate_of_id,
                                  reported_for_id, fixed_for_id, assigned_to_id, reporter_id, state, waiting_for,
                                  deadline, priority, feedback, standby, faculty_id):
            if state: state = settings.SITE.modules.tickets.TicketStates.get_by_value(state)
            kw = dict()
            kw.update(id=id)
            kw.update(modified=modified)
            kw.update(created=created)
            kw.update(closed=closed)
            kw.update(private=private)
            kw.update(planned_time=planned_time)
            kw.update(project_id=project_id)
            kw.update(site_id=site_id)
            kw.update(topic_id=product_id)
            kw.update(nickname=nickname)
            kw.update(summary=summary)
            kw.update(description=description)
            kw.update(upgrade_notes=upgrade_notes)
            kw.update(ticket_type_id=ticket_type_id)
            kw.update(duplicate_of_id=duplicate_of_id)
            kw.update(reported_for_id=reported_for_id)
            kw.update(fixed_for_id=fixed_for_id)
            kw.update(assigned_to_id=assigned_to_id)
            kw.update(reporter_id=reporter_id)
            kw.update(state=state)
            kw.update(waiting_for=waiting_for)
            kw.update(deadline=deadline)
            kw.update(priority=priority)
            kw.update(feedback=feedback)
            kw.update(standby=standby)
            kw.update(faculty_id=faculty_id)
            return tickets_Ticket(**kw)

        @override(globals_dict)
        def create_faculties_competence(id, seqno, user_id, faculty_id, affinity, product_id):
            kw = dict()
            kw.update(id=id)
            kw.update(seqno=seqno)
            kw.update(user_id=user_id)
            kw.update(faculty_id=faculty_id)
            kw.update(affinity=affinity)
            kw.update(topic_id=product_id)
            return faculties_Competence(**kw)

        @override(globals_dict)
        def create_faculties_faculty(id, ref, parent_id, name, affinity, product_cat_id):
            kw = dict()
            kw.update(id=id)
            kw.update(ref=ref)
            kw.update(parent_id=parent_id)
            if name is not None: kw.update(bv2kw('name', name))
            kw.update(affinity=affinity)
            kw.update(topic_group_id=product_cat_id)
            return faculties_Faculty(**kw)

        return '0.0.2'

    def migrate_from_0_0_2(self, globals_dict):

        bv2kw = globals_dict['bv2kw']
        faculties_Faculty = rt.models.faculties.Faculty
        tickets_Site = rt.models.tickets.Site

        @override(globals_dict)
        def create_faculties_faculty(id, ref, seqno, parent_id, name, affinity, product_cat_id):
            kw = dict()
            kw.update(id=id)
            # kw.update(ref=ref)
            kw.update(seqno=seqno)
            kw.update(parent_id=parent_id)
            if name is not None: kw.update(bv2kw('name', name))
            kw.update(affinity=affinity)
            # kw.update(product_cat_id=product_cat_id)
            return faculties_Faculty(**kw)

        @override(globals_dict)
        def create_tickets_site(id, partner_id, name, remark):
            kw = dict()
            kw.update(id=id)
            # kw.update(partner_id=partner_id)
            kw.update(name=name)
            kw.update(remark=remark)
            return tickets_Site(**kw)

        return '0.0.3'

    def migrate_from_1_0_1(self, globals_dict):
        """Move Deployment and Milestone from 'tickets' to new plugin
        'deploy'.

        """
        if settings.SITE.is_installed('deploy'):
            globals_dict.update(
                tickets_Deployment=rt.models.deploy.Deployment)
            globals_dict.update(
                tickets_Milestone=rt.models.deploy.Milestone)
        else:
            globals_dict.update(create_tickets_deployment=noop)
            globals_dict.update(create_tickets_milestone=noop)
        return '1.0.2'

    def migrate_from_1_0_2(self, globals_dict):
        """
        - convert stars.Star to votes.Vote
        
        """
        from django.utils import timezone
        # bv2kw = globals_dict['bv2kw']
        new_content_type_id = globals_dict['new_content_type_id']
        # cal_EventType = resolve_model("cal.EventType")
        # users_User = resolve_model("users.User")
        votes_Vote = rt.models.votes.Vote
        tickets_Ticket = rt.models.tickets.Ticket

        @override(globals_dict)
        def create_stars_star(id, user_id, owner_type_id, owner_id, nickname):
            # owner_type_id = new_content_type_id(owner_type_id)
            kw = dict()
            kw.update(id=id)
            kw.update(user_id=user_id)
            # kw.update(owner_type_id=owner_type_id)
            kw.update(created=timezone.now())
            kw.update(votable_id=owner_id)
            kw.update(nickname=nickname)
            return votes_Vote(**kw)

        # @override(globals_dict)
        # def create_tickets_ticket(id, modified, created, assigned_to_id, closed, private, planned_time, project_id, site_id, topic_id, nickname, summary, description, upgrade_notes,
        #     ticket_type_id, duplicate_of_id, reporter_id, state, rating, waiting_for, deadline,
        #     priority, feedback, standby, faculty_id):
        #     if state: state = settings.SITE.modules.tickets.TicketStates.get_by_value(state)
        #     if rating: rating = settings.SITE.modules.tickets.Ratings.get_by_value(rating)
        #     kw = dict()
        #     kw.update(id=id)
        #     kw.update(modified=modified)
        #     kw.update(created=created)
        #     # kw.update(assigned_to_id=assigned_to_id)
        #     kw.update(closed=closed)
        #     kw.update(private=private)
        #     kw.update(planned_time=planned_time)
        #     kw.update(project_id=project_id)
        #     kw.update(site_id=site_id)
        #     kw.update(topic_id=topic_id)
        #     kw.update(nickname=nickname)
        #     kw.update(summary=summary)
        #     kw.update(description=description)
        #     kw.update(upgrade_notes=upgrade_notes)
        #     kw.update(ticket_type_id=ticket_type_id)
        #     kw.update(duplicate_of_id=duplicate_of_id)
        #     kw.update(reporter_id=reporter_id)
        #     kw.update(state=state)
        #     # kw.update(rating=rating)
        #     kw.update(waiting_for=waiting_for)
        #     kw.update(deadline=deadline)
        #     kw.update(priority=priority)
        #     kw.update(feedback=feedback)
        #     kw.update(standby=standby)
        #     kw.update(faculty_id=faculty_id)
        #     return tickets_Ticket(**kw)

        return '2016.12.0'

    def unused_migrate_from_2016_12_0(self, globals_dict):
        """
        - convert Ticket.assigned_to to votes
        
        """
        votes_Vote = rt.models.votes.Vote
        tickets_Ticket = rt.models.tickets.Ticket

        @override(globals_dict)
        def create_tickets_ticket(id, modified, created, assigned_to_id, closed, private, planned_time, project_id,
                                  site_id, topic_id, nickname, summary, description, upgrade_notes, ticket_type_id,
                                  duplicate_of_id, reported_for_id, fixed_for_id, reporter_id, state, waiting_for,
                                  deadline, priority, feedback, standby, faculty_id):
            if state: state = settings.SITE.modules.tickets.TicketStates.get_by_value(state)
            kw = dict()
            kw.update(id=id)
            kw.update(modified=modified)
            kw.update(created=created)
            # kw.update(assigned_to_id=assigned_to_id)
            kw.update(closed=closed)
            kw.update(private=private)
            kw.update(planned_time=planned_time)
            kw.update(project_id=project_id)
            kw.update(site_id=site_id)
            kw.update(topic_id=topic_id)
            kw.update(nickname=nickname)
            kw.update(summary=summary)
            kw.update(description=description)
            kw.update(upgrade_notes=upgrade_notes)
            kw.update(ticket_type_id=ticket_type_id)
            kw.update(duplicate_of_id=duplicate_of_id)
            kw.update(reported_for_id=reported_for_id)
            kw.update(fixed_for_id=fixed_for_id)
            kw.update(reporter_id=reporter_id)
            kw.update(state=state)
            kw.update(waiting_for=waiting_for)
            kw.update(deadline=deadline)
            kw.update(priority=priority)
            kw.update(feedback=feedback)
            kw.update(standby=standby)
            kw.update(faculty_id=faculty_id)
            ticket = tickets_Ticket(**kw)
            if not assigned_to_id:
                return ticket
            vote = votes_Vote(
                votable=ticket, user_id=assigned_to_id, created=created,
                state=settings.SITE.models.votes.VoteStates.assigned)
            return (ticket, vote)

        return '2016.12.1'
