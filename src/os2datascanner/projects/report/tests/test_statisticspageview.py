import datetime
import dateutil.parser
from typing import List, Tuple

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from os2datascanner.utils.system_utilities import parse_isoformat_timestamp
from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource)
from os2datascanner.engine2.rules.regex import RegexRule, Sensitivity
from os2datascanner.engine2.pipeline import messages

from ..reportapp.management.commands import pipeline_collector
from ..reportapp.models.documentreport_model import DocumentReport
from ..reportapp.models.roles.leader_model import Leader
from ..reportapp.models.roles.dpo_model import DataProtectionOfficer
from ..reportapp.views.views import StatisticsPageView


"""Shared data"""
time0 = "2020-11-11T11:11:59+02:00"
time1 = "2020-10-28T14:21:27+01:00"
time2 = "2020-09-22T04:07:12+03:00"

scan_tag0 = messages.ScanTagFragment(
        time=parse_isoformat_timestamp(time0),
        scanner=messages.ScannerFragment(pk=14, name="Dummy test scanner"),
        user=None, organisation=None)

scan_tag1 = messages.ScanTagFragment(
        time=parse_isoformat_timestamp(time1),
        scanner=messages.ScannerFragment(pk=11, name="Dummy test scanner2"),
        user=None, organisation=None)

scan_tag2 = messages.ScanTagFragment(
        time=parse_isoformat_timestamp(time2),
        scanner=messages.ScannerFragment(pk=17, name="Dummy test scanner3"),
        user=None, organisation=None)

common_rule = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.PROBLEM
)

common_rule_2 = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.CRITICAL
)

common_rule_3 = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.WARNING
)

"""EGON DATA"""
egon_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@olsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='egon'),
    path='TDJHGFIHDIJHSKJGHKFUGIUHIUEHIIHE',
    mail_subject='Jeg har en plan',
    folder_name='Hundehoveder',
    entry_id=None
)

egon_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@olsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='egon'),
    path='DLFIGHDSLUJKGFHEWIUTGHSLJHFGBSVDKJFHG',
    mail_subject='TI STILLE SINDSSYGE KVINDEMENNESKE!',
    folder_name='Fnatmider',
    entry_id=None
)

egon_scan_spec = messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=egon_email_handle.source,
        rule=common_rule,
        configuration={},
        progress=None)

egon_positive_match = messages.MatchesMessage(
        scan_spec=egon_scan_spec._replace(scan_tag=scan_tag0),
        handle=egon_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

egon_positive_match_1 = messages.MatchesMessage(
        scan_spec=egon_scan_spec._replace(scan_tag=scan_tag1),
        handle=egon_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

egon_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=egon_email_handle,
    metadata={"email-account": "egon@olsen.com"}
)

egon_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag1,
    handle=egon_email_handle_1,
    metadata={"email-account": "egon@olsen.com"}
)


"""KJELD DATA"""
kjeld_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='kjeld'),
    path='TDJHGFIHDIJHSKJGHKFUGIUHIUEHIIHE',
    mail_subject='Er det farligt?',
    folder_name='Favorit',
    entry_id=None
)

kjeld_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='kjeld'),
    path='ASDGYSDFSDFSDFDSFDFSASD',
    mail_subject='Hvad skal jeg sige til Yvonne?',
    folder_name='Indbakke',
    entry_id=None
)

kjeld_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=kjeld_email_handle.source,
    rule=common_rule,
    configuration={},
    progress=None)

kjeld_positive_match = messages.MatchesMessage(
        scan_spec=kjeld_scan_spec._replace(scan_tag=scan_tag0),
        handle=kjeld_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])]
)

kjeld_positive_match_1 = messages.MatchesMessage(
        scan_spec=kjeld_scan_spec._replace(scan_tag=scan_tag2),
        handle=kjeld_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])]
)

kjeld_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=kjeld_email_handle,
    metadata={"email-account": "kjeld@jensen.com"}
)

kjeld_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag2,
    handle=kjeld_email_handle_1,
    metadata={"email-account": "kjeld@jensen.com"}
)

"""BENNY DATA"""
benny_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@frandsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='benny'),
    path='HJKFHSDJKFDFKSLASDGHJ',
    mail_subject="Du' smælderfed mand!",
    folder_name='Vigtigt',
    entry_id=None
)

benny_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@frandsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='benny'),
    path='HJKFHSDJKFDFKSLASDGHJ',
    mail_subject="Så så Kjeld, det var jo ikke sådan ment",
    folder_name='Spam',
    entry_id=None
)

benny_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=benny_email_handle.source,
    rule=common_rule,
    configuration={},
    progress=None)

benny_positive_match = messages.MatchesMessage(
        scan_spec=benny_scan_spec._replace(scan_tag=scan_tag0),
        handle=benny_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

benny_positive_match_1 = messages.MatchesMessage(
        scan_spec=benny_scan_spec._replace(scan_tag=scan_tag1),
        handle=benny_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_3,
                matches=[{"dummy": "match object"}])]
)

benny_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=benny_email_handle,
    metadata={"email-account": "benny@jensen.com"}
)

benny_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag1,
    handle=benny_email_handle_1,
    metadata={"email-account": "benny@jensen.com"}
)

"""YVONNE DATA"""
yvonne_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='yvonne'),
    path='SDFYSDFUYSDFIUASDM;AMSD',
    mail_subject='Los fiskos, los salatos, los kotelettos, los vinos blancos og Los Coca Colos',
    folder_name='Spanien',
    entry_id=None
)

yvonne_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=yvonne_email_handle.source,
    rule=common_rule,
    configuration={},
    progress=None)

yvonne_positive_match = messages.MatchesMessage(
        scan_spec=yvonne_scan_spec._replace(scan_tag=scan_tag0),
        handle=yvonne_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

yvonne_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=yvonne_email_handle,
    metadata={"email-account": "yvonne@jensen.com"}
)


class StatisticsPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.generate_kjeld_data()
        cls.generate_egon_data()
        cls.generate_yvonne_data()
        cls.generate_benny_data()

    @classmethod
    def generate_kjeld_data(cls):
        cls.generate_match(kjeld_positive_match)
        cls.generate_metadata(kjeld_metadata)

        cls.generate_match(kjeld_positive_match_1)
        cls.generate_metadata(kjeld_metadata_1)

    @classmethod
    def generate_egon_data(cls):
        cls.generate_match(egon_positive_match)
        cls.generate_metadata(egon_metadata)

        cls.generate_match(egon_positive_match_1)
        cls.generate_metadata(egon_metadata_1)

    @classmethod
    def generate_yvonne_data(cls):
        cls.generate_match(yvonne_positive_match)
        cls.generate_metadata(yvonne_metadata)

    @classmethod
    def generate_benny_data(cls):
        cls.generate_match(benny_positive_match)
        cls.generate_metadata(benny_metadata)

        cls.generate_match(benny_positive_match_1)
        cls.generate_metadata(benny_metadata_1)

    @classmethod
    def generate_match(cls, match):
        prev, new = pipeline_collector.get_reports_for(
            match.handle.to_json_object(),
            match.scan_spec.scan_tag)
        pipeline_collector.handle_match_message(
            prev, new, match.to_json_object())

    @classmethod
    def generate_metadata(cls, metadata):
        prev, new = pipeline_collector.get_reports_for(
            metadata.handle.to_json_object(),
            metadata.scan_tag)
        pipeline_collector.handle_metadata_message(
            new, metadata.to_json_object())

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.kjeld = User.objects.create_user(
            first_name='Kjeld', username='kjeld', 
            email='kjeld@jensen.com', password='top_secret')
        self.egon = User.objects.create_user(
            first_name='Egon', username='egon',
            email='egon@olsen.com', password='top_secret')
        self.yvonne = User.objects.create_user(
            first_name='Yvonne', username='yvonne', 
            email='yvonne@jensen.com', password='top_secret') 
        self.benny = User.objects.create_user(
            first_name='Benny', username='benny', 
            email='benny@frandsen.com', password='top_secret') 

    # Tests are done as Kjeld
    # count_handled_matches()
    def test_statisticspage_count_unhandled_matches_no_role(self):
        view = self.get_statisticspage_object()
        self.assertListEqual(view.count_unhandled_matches(), 
                            [('benny@jensen.com', 2),
                            ('egon@olsen.com', 2),
                            ('kjeld@jensen.com', 2),
                            ('yvonne@jensen.com', 1)])

    def test_statisticspage_count_unhandled_matches_as_leader(self):
        leader = Leader.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        self.assertListEqual(view.count_unhandled_matches(), 
                            [('benny@jensen.com', 2),
                            ('egon@olsen.com', 2),
                            ('kjeld@jensen.com', 2),
                            ('yvonne@jensen.com', 1)])
        leader.delete()

    # count_all_matches_grouped_by_sensitivity()
    def test_statisticspage_count_all_matches_grouped_by_sensitivity_as_leader(self):
        leader = Leader.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        sens_list, total = view.count_all_matches_grouped_by_sensitivity()
        self.assertListEqual(sens_list, 
                            [['Kritisk', 4], ['Problem', 2], 
                            ['Advarsel', 1], ['Notifikation', 0]])
        self.assertEquals(total, 7)
        leader.delete()

    def test_statisticspage_count_all_matches_grouped_by_sensitivity_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        sens_list, total = view.count_all_matches_grouped_by_sensitivity()
        self.assertListEqual(sens_list, 
                            [['Kritisk', 4], ['Problem', 2], 
                            ['Advarsel', 1], ['Notifikation', 0]])
        self.assertEquals(total, 7)
        dpo.delete()

    # count_by_source_types
    def test_statisticspage_count_by_source_types_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        self.assertListEqual(view.count_by_source_types(),
                             [['Andet', 0], ['Webscan', 0],
                              ['Filscan', 0], ['Mailscan', 7]])
        dpo.delete()

    # count_handled_matches_grouped_by_sensitivity()
    def test_statisticspage_count_handled_matches_grouped_by_sensitivity_as_leader(self):
        leader = Leader.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        sens_list, total = view.count_handled_matches_grouped_by_sensitivity()
        self.assertListEqual(sens_list,
                            [['Kritisk', 0], ['Problem', 0], 
                            ['Advarsel', 0], ['Notifikation', 0]])
        self.assertEquals(total, 0)
        leader.delete()

    def test_statisticspage_count_handled_matches_grouped_by_sensitivity_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        sens_list, total = view.count_handled_matches_grouped_by_sensitivity()
        self.assertListEqual(sens_list,
                            [['Kritisk', 0], ['Problem', 0], 
                            ['Advarsel', 0], ['Notifikation', 0]])
        dpo.delete()

    # created_timestamp
    def test_statisticspage_created_timestamp_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        created_timestamp = [m.created_timestamp.date() for m in view.matches][:2]

        self.assertEquals(created_timestamp,
                          [timezone.now().date(), timezone.now().date()])
        dpo.delete()

    # count_new_matches_by_month()
    def test_statisticspage_count_new_matches_by_month_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        test_date = dateutil.parser.parse("2020-11-28T14:21:59+05:00")

        # Overrides timestamps static dates and saves the old ones
        original_timestamps = static_timestamps()

        self.assertListEqual(view.count_new_matches_by_month(test_date),
                             [['Dec', 0], ['Jan', 0], ['Feb', 0],
                              ['Mar', 0], ['Apr', 0], ['May', 0],
                              ['Jun', 0], ['Jul', 0], ['Aug', 0],
                              ['Sep', 1], ['Oct', 2], ['Nov', 4]])

        # Reset to old values
        reset_timestamps(original_timestamps)
        dpo.delete()

    def test_statisticspage_count_new_matches_by_month_old_matches_as_dpo(self):
        dpo = DataProtectionOfficer.objects.create(user=self.kjeld)
        view = self.get_statisticspage_object()
        test_date = dateutil.parser.parse("2021-09-28T14:21:59+05:00")

        # Overrides timestamps static dates and saves the old ones
        original_timestamps = static_timestamps()

        self.assertListEqual(view.count_new_matches_by_month(test_date),
                             [['Oct', 2], ['Nov', 4], ['Dec', 0],
                              ['Jan', 0], ['Feb', 0], ['Mar', 0],
                              ['Apr', 0], ['May', 0], ['Jun', 0],
                              ['Jul', 0], ['Aug', 0], ['Sep', 0]])

        # Reset to old values
        reset_timestamps(original_timestamps)
        dpo.delete()

    # StatisticsPageView()
    def get_statisticspage_object(self):
        request = self.factory.get('/statistics')
        request.user = self.kjeld
        view = StatisticsPageView()
        return view


# Helper functions
# Overrides timestamps to have static data
def static_timestamps() -> List[Tuple[int, datetime.datetime]]:
    original_timestamps = []
    for match in DocumentReport.objects.all():
        original_timestamps.append((match.pk, match.created_timestamp))
        match.created_timestamp = match.scan_time
        match.save()
    return original_timestamps


# Reset to old values
def reset_timestamps(arg: List[Tuple[int, datetime.datetime]]):
    for match in DocumentReport.objects.all():
        for a in arg:
            if a[0] == match.pk:
                match.created_timestamp = a[1]
        match.save()
