export function hexToRGBA(hex: string | null, alpha = 1) {
  if (!hex) {
    return `rgba(0,0,0,${alpha})`;
  }

  let r = 0;
  let g = 0;
  let b = 0;

  if (hex.length === 4) {
    r = Number(`0x${hex[1]}${hex[1]}`);
    g = Number(`0x${hex[2]}${hex[2]}`);
    b = Number(`0x${hex[3]}${hex[3]}`);
  } else if (hex.length === 7) {
    r = Number(`0x${hex[1]}${hex[2]}`);
    g = Number(`0x${hex[3]}${hex[4]}`);
    b = Number(`0x${hex[5]}${hex[6]}`);
  }

  return `rgba(${r},${g},${b},${alpha})`;
}
