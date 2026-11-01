from scripts.business_report import report
from openhook.settings import Settings
from openhook.store import Store
from openhook.sessions import Sessions


def test_read_only_report_does_not_turn_anonymous_activity_into_users(tmp_path):
    settings=Settings(database=str(tmp_path/'report.db'))
    channels=Sessions(Store(settings))
    owner=channels.create('Owner','Internal QA')
    channels.send(owner['participant_token'],'Synthetic test','test')
    before=(tmp_path/'report.db').read_bytes()
    result=report(settings.database)
    assert result['retained_channels']==1 and result['retained_channel_messages']==1
    assert result['customer_revenue'] is None
    assert 'Not distinct users' in result['channel_activity_note']
    assert 'Owner' not in str(result) and 'Synthetic test' not in str(result)
    assert (tmp_path/'report.db').read_bytes()==before
