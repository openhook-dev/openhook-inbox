const VERTEX = `#version 300 es
in vec2 position;
void main(){gl_Position=vec4(position,0.,1.);}`;

// Original procedural field: a shaded, folded ring with screen-space dithering.
const FRAGMENT = `#version 300 es
precision highp float;
uniform vec2 resolution;
uniform vec2 pointer;
uniform float time;
uniform vec3 ink;
out vec4 color;
float threshold(vec2 cell){
  const float matrix[16]=float[16](0.,8.,2.,10.,12.,4.,14.,6.,3.,11.,1.,9.,15.,7.,13.,5.);
  ivec2 p=ivec2(mod(cell,4.));
  return (matrix[p.y*4+p.x]+.5)/16.;
}
void main(){
  vec2 cell=floor(gl_FragCoord.xy/6.);
  vec2 uv=(cell*6.+3.-resolution*.5)/min(resolution.x,resolution.y);
  uv+=pointer*.06;
  float rotation=time*.08;
  uv=mat2(cos(rotation),-sin(rotation),sin(rotation),cos(rotation))*uv;
  float angle=atan(uv.y,uv.x);
  float fold=.04*sin(angle*3.+time*.32);
  float radius=length(uv*vec2(1.,1.15));
  float width=.10+.035*sin(angle*2.-time*.19);
  float distance=abs(radius-.29-fold)/width;
  float surface=sqrt(max(0.,1.-distance*distance));
  float light=.18+.5*surface+.26*sin(angle+time*.12);
  float edge=1.-smoothstep(.85,1.08,distance);
  float dotValue=step(threshold(cell),light*edge);
  color=vec4(ink,dotValue*.68);
}`;

export function createDitherRenderer(canvas) {
  const gl = canvas.getContext("webgl2", {
    alpha: true,
    antialias: false,
    powerPreference: "low-power",
  });
  if (!gl) return null;
  function shader(type, source) {
    const result = gl.createShader(type);
    gl.shaderSource(result, source);
    gl.compileShader(result);
    if (!gl.getShaderParameter(result, gl.COMPILE_STATUS))
      throw new Error("Dither shader could not compile");
    return result;
  }
  const program = gl.createProgram();
  gl.attachShader(program, shader(gl.VERTEX_SHADER, VERTEX));
  gl.attachShader(program, shader(gl.FRAGMENT_SHADER, FRAGMENT));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS))
    throw new Error("Dither shader could not link");
  gl.useProgram(program);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
    gl.STATIC_DRAW,
  );
  const position = gl.getAttribLocation(program, "position");
  gl.enableVertexAttribArray(position);
  gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
  const uniforms = Object.fromEntries(
    ["resolution", "pointer", "time", "ink"].map((name) => [
      name,
      gl.getUniformLocation(program, name),
    ]),
  );
  let target = [0, 0],
    current = [0, 0];
  canvas.closest("section").addEventListener(
    "pointermove",
    (event) => {
      const rect = canvas.getBoundingClientRect();
      target = [
        (event.clientX - rect.left) / rect.width - 0.5,
        (event.clientY - rect.top) / rect.height - 0.5,
      ];
    },
    { passive: true },
  );
  return {
    draw(time, ink) {
      const width = Math.min(1000, Math.round(canvas.clientWidth)),
        height = Math.min(1100, Math.round(canvas.clientHeight));
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
        gl.viewport(0, 0, width, height);
      }
      current = current.map(
        (value, index) => value + (target[index] - value) * 0.04,
      );
      gl.uniform2f(uniforms.resolution, width, height);
      gl.uniform2f(uniforms.pointer, ...current);
      gl.uniform1f(uniforms.time, time);
      const rgb = ink
        .match(/[\d.]+/g)
        ?.slice(0, 3)
        .map(Number) || [160, 160, 160];
      gl.uniform3f(uniforms.ink, ...rgb.map((value) => value / 255));
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    },
  };
}
