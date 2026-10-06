import { createRoot } from "react-dom/client";
import { Box, Flight, Plate, Press, Signal, path } from "react-isokit";

const SOURCE = { x: 0, y: 0, z: 22, w: 112, d: 65, h: 26 };
const AGENT = { x: 240, y: 0, z: 22, w: 112, d: 65, h: 26 };
const FLOOR = { x: 80, y: 106, z: 0, w: 192, d: 134, h: 12 };
const STORE = { ...FLOOR, z: 40, h: 16 };
const CAPTURE = { ...FLOOR, z: 88, h: 12 };
const ENVELOPE = { x: 32, y: 16, z: 55, w: 52, d: 28, h: 4 };
const RECEIPT = { x: 136, y: 139, z: 107, w: 72, d: 40, h: 4 };
const INCOMING = [
  [56, 65, 48],
  [56, 94, 48],
  [104, 130, 100],
  [165, 165, 100],
];
const OUTGOING = [
  [244, 130, 56],
  [306, 95, 56],
  [306, 65, 48],
];
const SOURCES = { http: "GITHUB", email: "EMAIL", dns: "DNS QUERY" };

function Slots({ received = false }) {
  return (
    <>
      {Array.from({ length: 24 }, (_, index) => (
        <rect
          key={index}
          x={23 + (index % 8) * 19}
          y={25 + Math.floor(index / 8) * 21}
          width={12}
          height={12}
          className={received && index < 8 ? "scene-slot filled" : "scene-slot"}
          style={{ transitionDelay: `${index * 25}ms` }}
        />
      ))}
    </>
  );
}

function WorkflowScene({ protocol, step, paused, onSelect }) {
  const received = step >= 4;
  const continued = step >= 6;
  const state = continued
    ? "continue"
    : received
      ? "stored"
      : step >= 2
        ? "incoming"
        : "waiting";
  return (
    <>
      <Plate
        label="Animated preview: an event arrives, Openhook stores it, and your agent reads it. Select a layer to explore the steps."
        fit={[SOURCE, AGENT, { ...FLOOR, h: 140 }]}
        aspect={1.68}
        pad={0.07}
        className="workflow-plate"
        data-state={state}
        data-paused={paused}
      >
        <path className="ik-detail ik-dash" d={path(INCOMING)} />
        <path className="ik-detail ik-dash" d={path(OUTGOING)} />
        <Box
          {...SOURCE}
          r={4}
          className="scene-source"
          top={
            <>
              <text className="ik-label scene-label" x={14} y={27}>
                {SOURCES[protocol]}
              </text>
              <text className="ik-label scene-small" x={14} y={46}>
                {step >= 2 ? "EVENT SENT" : "READY"}
              </text>
            </>
          }
        />
        <Box
          {...AGENT}
          r={4}
          className="scene-agent"
          top={
            <>
              <text className="ik-label scene-label" x={14} y={27}>
                YOUR AGENT
              </text>
              <text className="ik-label scene-small" x={14} y={46}>
                {continued ? "CONTINUE ↗" : "WAITING…"}
              </text>
            </>
          }
        />
        <Press
          label="Explore the agent step"
          onPress={() => onSelect(6)}
          sound={false}
          className="scene-base"
        >
          <g>
            <Box
              {...FLOOR}
              r={5}
              top={
                <text className="ik-label scene-small" x={22} y={116}>
                  03 / READ & CONTINUE
                </text>
              }
            />
          </g>
        </Press>
        <g className="scene-store-motion">
          <Press
            label="Explore the stored event"
            onPress={() => onSelect(4)}
            sound={false}
            className="scene-store"
          >
            <g>
              <Box
                {...STORE}
                r={5}
                top={<Slots received={received} />}
                front={
                  <text className="ik-label scene-small" x={15} y={12}>
                    02 / INBOX
                  </text>
                }
              />
            </g>
          </Press>
        </g>
        <g className="scene-capture-motion">
          <Press
            label="Explore the incoming event"
            onPress={() => onSelect(2)}
            sound={false}
            className="scene-capture"
          >
            <g>
              <Box
                {...CAPTURE}
                r={5}
                top={
                  <>
                    <path
                      className="ik-detail"
                      d="M24 24H168V84H24Z M24 45H168"
                    />
                    <text className="ik-label scene-label" x={34} y={39}>
                      OPENHOOK
                    </text>
                    <text className="ik-label scene-small" x={34} y={63}>
                      {received ? "EVENT RECEIVED" : "LISTENING…"}
                    </text>
                    <circle
                      className="scene-indicator"
                      cx={155}
                      cy={34}
                      r={2}
                    />
                    <text className="ik-label scene-small" x={24} y={116}>
                      01 / CATCH THE EVENT
                    </text>
                  </>
                }
              />
            </g>
          </Press>
        </g>
        {step >= 2 &&
          !received &&
          (paused ? (
            <Box
              {...ENVELOPE}
              r={2}
              className="scene-envelope"
              top={
                <path className="ik-detail" d="M7 6H45V22H7Z M7 6 26 17 45 6" />
              }
            />
          ) : (
            <Flight
              key={protocol}
              from={[32, 16, 55]}
              to={[136, 139, 107]}
              duration={1500}
              lift={40}
            >
              <Box
                {...ENVELOPE}
                r={2}
                className="scene-envelope"
                top={
                  <path
                    className="ik-detail"
                    d="M7 6H45V22H7Z M7 6 26 17 45 6"
                  />
                }
              />
            </Flight>
          ))}
        {received && (
          <g className="scene-receipt">
            <Box
              {...RECEIPT}
              r={2}
              className="scene-envelope"
              top={
                <>
                  <path className="ik-detail" d="M10 12H40M10 18H57M10 24H46" />
                  <text className="ik-label scene-small" x={50} y={32}>
                    ✓
                  </text>
                </>
              }
            />
          </g>
        )}
        {!paused && step === 2 && (
          <Signal
            key={`${protocol}-incoming`}
            points={INCOMING}
            duration={800}
          />
        )}
        {!paused && step === 6 && (
          <Signal
            key={`${protocol}-outgoing`}
            points={OUTGOING}
            duration={900}
          />
        )}
      </Plate>
      <div className="scene-steps" aria-label="Explore the event flow">
        {[
          [2, "EVENT SENT"],
          [4, "IN YOUR INBOX"],
          [6, "AGENT CONTINUES"],
        ].map(([value, label], index) => (
          <button
            key={value}
            onClick={() => onSelect(value)}
            aria-pressed={
              (index === 0 && state === "incoming") ||
              (index === 1 && state === "stored") ||
              (index === 2 && state === "continue")
            }
          >
            <span>0{index + 1}</span>
            {label}
          </button>
        ))}
      </div>
    </>
  );
}

export function mountWorkflow(element, onSelect) {
  const root = createRoot(element);
  return {
    update(protocol, step, paused) {
      root.render(
        <WorkflowScene
          protocol={protocol}
          step={step}
          paused={paused}
          onSelect={onSelect}
        />,
      );
    },
  };
}
