import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {channelTools} from '../web/assets/webmcp.js';

const source = readFileSync('web/assets/webmcp.js', 'utf8').replaceAll('export function ', 'function ');
function browser({supported = true, secure = true, register} = {}) {
  const tools = new Map(), handlers = {}, registrations = [], warnings = [];
  const context = {
    AbortController, console: {warn: value => warnings.push(value)},
    location: {origin: 'https://example.test'},
    window: {isSecureContext: secure, addEventListener: (name, handler) => { handlers[name] = handler; }},
    document: supported ? {modelContext: {registerTool: register || ((tool, options) => {
      tools.set(tool.name, tool); registrations.push({tool, options});
      options.signal.addEventListener('abort', () => tools.delete(tool.name), {once: true});
    })}} : {},
  };
  runInNewContext(source, context);
  return {...context, tools, handlers, registrations, warnings};
}
const names = tools => tools.map(t => t.name);
const actions = Object.fromEntries(['create', 'join', 'info', 'read', 'send', 'invite'].map(name => [name, () => ({action: name})]));

test('unsupported and insecure browsers do not register tools or change normal browsing', () => {
  for (const options of [{supported: false}, {secure: false}]) {
    const page = browser(options);
    const update = page.registerWebMCP(() => { throw new Error('must not be evaluated'); });
    update();
    assert.equal(page.registrations.length, 0);
    assert.equal(Object.keys(page.handlers).length, 0);
  }
});

test('tools follow membership and permissions without offering key replacement or deletion', () => {
  assert.deepEqual(names(channelTools({connected: false}, actions)), ['get_openhook_setup', 'create_agent_channel', 'join_agent_channel']);
  const info = {role: 'owner', permission: 'write', archived: false};
  const active = names(channelTools({connected: true, info}, actions));
  assert.deepEqual(active, ['get_openhook_setup', 'get_agent_channel', 'read_agent_messages', 'send_agent_message', 'invite_agent_channel']);
  const readonly = channelTools({connected: true, info: {...info, role: 'guest', permission: 'read'}}, actions);
  assert.deepEqual(names(readonly), ['get_openhook_setup', 'get_agent_channel', 'read_agent_messages']);
  assert.deepEqual(names(channelTools({connected: true, info: {...info, archived: true}}, actions)), names(readonly));
  assert.deepEqual(names(channelTools({connected: true, info, accessEnded: true}, actions)), ['get_openhook_setup', 'get_agent_channel']);
});

test('schemas are bounded, reject extra fields and never request a private member key', () => {
  const tools = [...channelTools({connected: false}, actions), ...channelTools({connected: true,
    info: {role: 'owner', permission: 'write'}}, actions)];
  for (const tool of tools) {
    assert.equal(tool.inputSchema.additionalProperties, false);
    assert.ok(!JSON.stringify(tool.inputSchema).includes('participant_token'));
    if (!tool.annotations.readOnlyHint) assert.equal(tool.annotations.consequentialHint, true);
    if (tool.name !== 'get_openhook_setup') assert.equal(tool.annotations.untrustedContentHint, true);
  }
  const send = tools.find(t => t.name === 'send_agent_message');
  assert.deepEqual(send.inputSchema.required, ['text', 'message_id']);
  assert.equal(send.inputSchema.properties.message_id.maxLength, 80);
  assert.equal(send.inputSchema.properties.text.maxLength, 16384);
});

test('scope and participant text cannot poison registered tool metadata', () => {
  const state = {connected: true, info: {role: 'owner', permission: 'write', scope: 'INJECTED_TEXT', title: 'INJECTED_TEXT', participants: [{name: 'INJECTED_TEXT'}]}};
  assert.ok(!JSON.stringify(channelTools(state, actions)).includes('INJECTED_TEXT'));
});

test('registration uses same-origin defaults, updates safely and resumes after page restoration', () => {
  const page = browser();
  let definitions = [{name: 'first', execute: () => ({ok: true})}];
  const update = page.registerWebMCP(() => definitions);
  assert.equal(page.registrations.length, 1);
  assert.deepEqual(Object.keys(page.registrations[0].options), ['signal']);
  update(); assert.equal(page.registrations.length, 1);
  definitions = [{name: 'second', execute: () => ({ok: true})}]; update();
  assert.equal(page.registrations[0].options.signal.aborted, true);
  assert.deepEqual([...page.tools.keys()], ['second']);
  page.handlers.pagehide(); assert.equal(page.tools.size, 0);
  update(); assert.equal(page.tools.size, 0); // A finishing request must not re-register an exited page.
  page.handlers.pageshow(); assert.deepEqual([...page.tools.keys()], ['second']);
});

test('execution forwards cancellation and returns useful cancellation without leaking thrown secrets', async () => {
  const page = browser(); let calls = 0, received;
  page.registerWebMCP(() => [{name: 'read', execute: (_, options) => { calls++; received = options.signal; return {ok: true}; }},
    {name: 'broken', execute: () => { throw new Error('ohp_PRIVATE_KEY'); }}]);
  const controller = new AbortController();
  assert.equal((await page.tools.get('read').execute({}, {signal: controller.signal})).ok, true);
  assert.equal(received, controller.signal);
  controller.abort();
  assert.match((await page.tools.get('read').execute({}, {signal: controller.signal})).error, /cancelled/);
  assert.equal(calls, 1);
  const failure = await page.tools.get('broken').execute({});
  assert.match(failure.error, /Check the channel page/);
  assert.ok(!JSON.stringify(failure).includes('PRIVATE_KEY'));
});

test('registration failures leave the normal page usable and reveal no exception details', async () => {
  for (const register of [() => { throw new Error('private'); }, () => Promise.reject(new Error('private'))]) {
    const page = browser({register});
    page.registerWebMCP(() => [{name: 'read', execute: () => {}}]);
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(page.warnings.length, 1);
    assert.ok(!page.warnings[0].includes('private'));
  }
});

test('setup links use the current deployment without leaking invitation or member state', async () => {
  const page = browser();
  const result = await page.setupTool().execute();
  assert.equal(result.skill_url, 'https://example.test/skill.md');
  assert.equal(result.channels_url, 'https://example.test/channels');
  assert.ok(!JSON.stringify(result).includes('ohp_'));
});
