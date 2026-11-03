"""Publication must not turn stored messages or leaked keys into success proof."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from examples.claude_codex_exchange import processing_evidence, public_events, reject_capabilities, verify_exchange


RECEIPT = Path(__file__).resolve().parent.parent / 'web/assets/claude-codex-exchange-20261101.json'


def test_publication_uses_an_allowlist_and_rejects_capabilities():
    event = {'kind': 'message', 'sequence': 1, 'sender_name': 'Codex', 'text': 'Ready locally.',
             'created_at': '2026-11-01T20:42:45Z', 'participant_token': 'ohp_PRIVATE',
             'sender_id': 'private-id', 'unexpected_private_field': 'do not publish'}
    assert set(public_events([event])[0]) == {'sequence', 'sender_name', 'text', 'created_at'}
    for field in ('text', 'sender_name'):
        for secret in ('ohp_PRIVATE', 'https://openhook.dev/channels#invite=ohi_PRIVATE'):
            leaked = {**event, field: secret}
            with pytest.raises(ValueError, match='Capability detected'):
                public_events([leaked])


def test_captured_receipt_requires_both_peer_reads_and_sends():
    receipt = json.loads(RECEIPT.read_text())
    reject_capabilities(receipt)
    assert receipt['channel_deleted'] is True
    verify_exchange(receipt['messages'], receipt['processing_evidence'], receipt['exit_codes'])
    for name in ('claude', 'codex'):
        missing_read = deepcopy(receipt['processing_evidence'])
        missing_read[name]['peer_sequences_read'] = []
        with pytest.raises(RuntimeError, match='did not demonstrably read'):
            verify_exchange(receipt['messages'], missing_read, receipt['exit_codes'])
        blocked_send = deepcopy(receipt['processing_evidence'])
        for call in blocked_send[name]['tool_calls']:
            if call['tool'] == 'send_agent_message':
                call['success'] = False
        with pytest.raises(RuntimeError, match='did not successfully send'):
            verify_exchange(receipt['messages'], blocked_send, receipt['exit_codes'])


@pytest.mark.parametrize('error_field', ['isError', 'is_error'])
def test_completed_mcp_errors_do_not_count_as_reads_or_success(tmp_path, error_field):
    (tmp_path / 'claude.jsonl').write_text('')
    batch = {'events': [{'kind': 'message', 'sequence': 3, 'is_self': False}]}
    row = {'type': 'item.completed', 'item': {'type': 'mcp_tool_call', 'tool': 'read_agent_messages',
           'status': 'completed', 'result': {error_field: True, 'content': [{'type': 'text', 'text': json.dumps(batch)}]}}}
    (tmp_path / 'codex.jsonl').write_text(json.dumps(row))
    evidence = processing_evidence(tmp_path)['codex']
    assert evidence['tool_calls'] == [{'tool': 'read_agent_messages', 'success': False}]
    assert evidence['peer_sequences_read'] == []


def test_claude_extracts_all_results_and_string_content(tmp_path):
    rows = [
        {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'send', 'name': 'mcp__openhook__send_agent_message'},
            {'type': 'tool_use', 'id': 'read', 'name': 'mcp__openhook__read_agent_messages'}]}},
        {'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 'send', 'content': 'failure', 'is_error': True},
            {'type': 'tool_result', 'tool_use_id': 'read', 'content': json.dumps({'events': [
                {'kind': 'message', 'sequence': 3, 'is_self': False},
                {'kind': 'message', 'sequence': 4, 'is_self': True}]})}]}},
        {'type': 'result', 'result': 'The peer answered.'},
    ]
    (tmp_path / 'claude.jsonl').write_text('\n'.join(json.dumps(row) for row in rows))
    (tmp_path / 'codex.jsonl').write_text('')
    evidence = processing_evidence(tmp_path)['claude']
    assert evidence['peer_sequences_read'] == [3]
    assert [call['success'] for call in evidence['tool_calls']] == [False, True]
