/** One continuous line wound into a rosette, the way the fine lines on a banknote are drawn.
 *  Three hypotrochoids; each is a single closed path so it can be drawn in one stroke on load. */
export function Guilloche() {
  const curve = (R: number, r: number, d: number, turns: number, scale: number) => {
    const steps = 720;
    let path = "";
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI * 2 * turns;
      const x = ((R - r) * Math.cos(t) + d * Math.cos(((R - r) / r) * t)) * scale;
      const y = ((R - r) * Math.sin(t) - d * Math.sin(((R - r) / r) * t)) * scale;
      path += `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return path + "Z";
  };
  return (
    <svg className="guilloche" viewBox="-310 -310 620 620" aria-hidden>
      <path pathLength={1} d={curve(96, 36, 58, 3, 2.35)} />
      <path pathLength={1} d={curve(105, 30, 34, 2, 2.6)} />
      <path pathLength={1} d={curve(84, 49, 70, 7, 2.3)} />
    </svg>
  );
}
