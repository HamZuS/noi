# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""Extends actions for this plugin"""

from lino.api import dd, rt, _

from lino_noi.lib.clocking.actions import WorkerAction, EndTicketSession, StartTicketSession


class WorkerActionViaVote(WorkerAction):

    def get_workables(self, ar):
        for obj in ar.selected_rows:
            yield obj.votable

class EndTicketSessionViaVote(WorkerActionViaVote, EndTicketSession):
    """End your running session on this ticket via vote.
    """

    def get_action_permission(self, ar, obj, state):
        return super(EndTicketSessionViaVote, self).get_action_permission(
            ar, obj.votable, state)


class StartTicketSessionViaVote(WorkerActionViaVote, StartTicketSession):
    """Start a session on the ticket this vote is attached to"""


    def get_action_permission(self, ar, obj, state):
        return super(StartTicketSessionViaVote, self).get_action_permission(
            ar, obj.votable, state)

