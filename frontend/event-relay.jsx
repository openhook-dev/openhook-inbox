import { useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Box, Plate, Press, Signal, path } from "react-isokit";
import "react-isokit/styles.css";

const BASE = { x: 0, y: 0, z: 0, w: 210, d: 146, h: 16 };
const SCREEN = { x: 14, y: 12, z: 16, w: 168, d: 46, h: 84 };
const KEY = { x: 60, y: 86, z: 16, w: 92, d: 43, h: 12 };
const PORT = { x: 186, y: 20, z: 16, w: 13, d: 24, h: 26 };
const ROUTE = [
  [106, 107, 29],
  [166, 107, 29],
  [170, 58, 70],
  [90, 58, 70],
];

async function call(action, values = {}) {
  const response = await fetch("/api/call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...values }),
  });
  const result = await response.json();
  if (!response.ok || !result.success)
    throw new Error(result.message || "Could not reach the inbox. Try again.");
  return result.data;
}

function EventRelay() {
  const inbox = useRef(null);
  const [count, setCount] = useState(0);
  const [phase, setPhase] = useState("ready");
  const [event, setEvent] = useState(null);
  const [message, setMessage] = useState("press send · receive a real webhook");
  const [opened, setOpened] = useState(false);

  async function send() {
    if (phase === "sending") return;
    setPhase("sending");
    setMessage("sending · native HTTP callback");
    try {
      if (!inbox.current) inbox.current = await call("create");
      const response = await fetch(inbox.current.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: "landing.callback",
          sequence: count + 1,
          from: "Openhook event relay",
        }),
      });
      if (!response.ok) {
        if (response.status === 404) {
          inbox.current = null;
          setEvent(null);
        }
        throw new Error("The callback could not be captured. Try again.");
      }
      const result = await call("get", {
        token: inbox.current.token,
        request_id: response.headers.get("x-openhook-event"),
      });
      setEvent(result.request);
      setCount(count + 1);
      setPhase("captured");
      setMessage(
        `captured · HTTP ${response.status} · event ${String(count + 1).padStart(2, "0")}`,
      );
    } catch (error) {
      setPhase("error");
      setMessage(error.message);
    }
  }

  function openInspector() {
    try {
      const saved = JSON.parse(
        localStorage.getItem("openhook-inboxes") || "[]",
      );
      const bookmarks = Array.isArray(saved) ? saved : [];
      if (!bookmarks.some((item) => item.token === inbox.current.token))
        bookmarks.unshift({
          ...inbox.current,
          name: "Landing relay",
        });
      localStorage.setItem("openhook-inboxes", JSON.stringify(bookmarks));
      setOpened(true);
      location.assign("/app");
    } catch {
      setMessage(
        "Browser storage is unavailable. Keep this page open to inspect the event.",
      );
    }
  }

  const readout = phase === "sending" ? "sending · wait for capture" : message;
  return (
    <div className="native-relay">
      <Plate
        fig="FIG 01"
        name="OPENHOOK / EVENT RELAY"
        hint="PRESS THE SEND KEY"
        readout={readout}
        aspect={1.7}
        pad={0.09}
        fit={[
          BASE,
          { ...SCREEN, z: 0, h: SCREEN.z + SCREEN.h },
          { ...PORT, z: 0, h: PORT.z + PORT.h },
          [106, 107, 45],
        ]}
        className="relay-plate"
        data-phase={phase}
        label="Openhook event relay. Press Send to create an inbox, capture a real HTTP webhook, and inspect the stored event."
      >
        <Box
          {...BASE}
          r={8}
          top={
            <>
              {Array.from({ length: 7 }, (_, i) => (
                <path
                  key={i}
                  className="ik-detail"
                  d={`M${22 + i * 5} 100v24`}
                />
              ))}
              <text className="ik-label" x={156} y={125}>
                OH / 01
              </text>
            </>
          }
        />
        <Box
          {...PORT}
          r={3}
          side={
            <rect
              className="ik-well"
              x={4}
              y={6}
              width={16}
              height={11}
              rx={2}
            />
          }
        />
        <Box
          {...SCREEN}
          r={7}
          front={
            <>
              <rect
                className="ik-screen"
                x={10}
                y={12}
                width={147}
                height={58}
                rx={4}
              />
              <text className="ik-screen-text relay-small" x={20} y={29}>
                INBOX / LANDING RELAY
              </text>
              <text className="ik-screen-text relay-status" x={20} y={49}>
                {phase === "captured"
                  ? "EVENT STORED"
                  : phase === "sending"
                    ? "RECEIVING…"
                    : phase === "error"
                      ? "TRY AGAIN"
                      : "WAITING"}
              </text>
              <text className="ik-screen-text relay-small" x={20} y={62}>
                HTTP · {String(count).padStart(2, "0")} CAPTURED
              </text>
              <circle className="relay-light" cx={150} cy={29} r={2} />
              <path className="ik-detail" d="M15 77H153" />
            </>
          }
          top={
            <>
              {Array.from({ length: 10 }, (_, i) => (
                <path
                  key={i}
                  className="ik-detail"
                  d={`M${24 + i * 12} 12v20`}
                />
              ))}
            </>
          }
        />
        <path className="ik-detail ik-dash" d={path(ROUTE)} />
        <Press
          label="Send a real HTTP webhook"
          onPress={send}
          disabled={phase === "sending"}
          sound={false}
          className="relay-send"
        >
          <g>
            <Box
              {...KEY}
              r={6}
              top={
                <>
                  <text className="ik-label relay-key-label" x={19} y={26}>
                    SEND ↗
                  </text>
                  <path className="ik-detail" d="M20 32H70" />
                </>
              }
            />
          </g>
        </Press>
        {phase === "sending" && (
          <Signal key={count} points={ROUTE} duration={600} />
        )}
      </Plate>
      <div className="relay-result" aria-live="polite">
        <div>
          <span className="bracket-label">
            [ {event ? "REAL EVENT CAPTURED" : "TRY THE WHOLE LOOP"} ]
          </span>
          <h3>
            {event
              ? "The reply is in your inbox."
              : "One press. A real callback."}
          </h3>
          <p>
            {event
              ? "These are the original bytes received by this Openhook deployment. Open the inspector to see its headers, timestamp, and source address."
              : "This key calls the running Openhook service. It creates a public endpoint, sends an HTTP event, and reads the result from its native store."}
          </p>
          {event && (
            <button
              className="button"
              onClick={openInspector}
              disabled={opened}
            >
              OPEN THIS INBOX ↗
            </button>
          )}
        </div>
        <pre>
          {event
            ? event.content
            : '{\n  "event": "landing.callback",\n  "sequence": 1,\n  "from": "Openhook event relay"\n}'}
        </pre>
      </div>
    </div>
  );
}

export function mountRelay(element) {
  createRoot(element).render(<EventRelay />);
}

export { mountWorkflow } from "./workflow-scene.jsx";
