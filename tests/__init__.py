"""
Examples how to run these tests::

  $ python setup.py test
  $ python setup.py test -s tests.DocsTests
  $ python setup.py test -s tests.DocsTests.test_debts
  $ python setup.py test -s tests.DocsTests.test_docs
"""
from unipath import Path

ROOTDIR = Path(__file__).parent.parent

SETUP_INFO = {}

# load SETUP_INFO:
fn = ROOTDIR.child('lino_noi', 'setup_info.py')
exec(compile(open(fn, "rb").read(), fn, 'exec'))

from lino.utils.pythontest import TestCase

import os
os.environ['DJANGO_SETTINGS_MODULE'] = "lino_noi.settings.test"


class BaseTestCase(TestCase):
    project_root = ROOTDIR
    django_settings_module = 'lino_noi.settings.test'


class PackagesTests(BaseTestCase):

    def test_packages(self):
        self.run_packages_test(SETUP_INFO['packages'])


class SpecsTests(BaseTestCase):

    def test_export_excel(self):
        self.run_simple_doctests('docs/specs/export_excel.rst')

    def test_memo(self):
        self.run_simple_doctests('docs/specs/memo.rst')

    def test_care(self):
        self.run_simple_doctests('docs/specs/care.rst')

    def test_care_de(self):
        self.run_simple_doctests('docs/specs/care_de.rst')

    def test_std(self):
        self.run_simple_doctests('docs/specs/std.rst')

    def test_smtpd(self):
        self.run_simple_doctests('docs/specs/smtpd.rst')

    def test_ddh(self):
        self.run_simple_doctests('docs/specs/ddh.rst')

    def test_hosts(self):
        self.run_simple_doctests('docs/specs/hosts.rst')

    def test_tickets(self):
        self.run_simple_doctests('docs/specs/tickets.rst')

    def test_votes(self):
        self.run_simple_doctests('docs/specs/votes.rst')

    def test_topics(self):
        self.run_simple_doctests('docs/specs/topics.rst')

    def test_projects(self):
        self.run_simple_doctests('docs/specs/projects.rst')

    def test_faculties(self):
        self.run_simple_doctests('docs/specs/faculties.rst')

    def test_public(self):
        self.run_simple_doctests('docs/specs/public.rst')

    def test_bs3(self):
        self.run_simple_doctests('docs/specs/bs3.rst')

    def test_clocking(self):
        self.run_simple_doctests('docs/specs/clocking.rst')

    def test_general(self):
        self.run_simple_doctests('docs/specs/general.rst')

    def test_as_pdf(self):
        self.run_simple_doctests('docs/specs/as_pdf.rst')

    def test_db(self):
        self.run_simple_doctests('docs/specs/db.rst')


class ProjectsTests(BaseTestCase):
    """Run tests on the demo projects.
    """

    def test_team(self):
        self.run_django_manage_test('lino_noi/projects/team')

    def test_teamadm(self):
        self.run_django_manage_test('lino_noi/projects/bs3')

    def test_care(self):
        self.run_django_manage_test('lino_noi/projects/care')


