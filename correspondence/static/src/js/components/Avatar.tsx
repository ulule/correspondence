import * as React from "react";
import initials from "initials";

function hexToRgb(hex: string): number[] {
  if (hex.charAt && hex.charAt(0) === "#") {
    hex = removeHash(hex);
  }

  if (hex.length === 3) {
    hex = expand(hex);
  }

  const bigint = parseInt(hex, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return [r, g, b];
}

function removeHash(hex: string): string {
  const arr = hex.split("");
  arr.shift();
  return arr.join("");
}

function expand(hex: string): string {
  return hex
    .split("")
    .reduce(function (accum, value) {
      return accum.concat([value, value]);
    }, [])
    .join("");
}

function contrast(hex: string): string {
  const rgb = hexToRgb(hex);
  const o = Math.round((rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000);

  return o <= 180 ? "dark" : "light";
}

const defaultColors = [
  "#2ecc71", // emerald
  "#3498db", // peter river
  "#8e44ad", // wisteria
  "#e67e22", // carrot
  "#e74c3c", // alizarin
  "#1abc9c", // turquoise
  "#2c3e50", // midnight blue
];

function sumChars(str: string): number {
  let sum = 0;
  for (let i = 0; i < str.length; i++) {
    sum += str.charCodeAt(i);
  }

  return sum;
}

type AvatarProps = {
  name: string;
  size?: string;
  borderRadius?: string;
  colors?: string[];
};

export default function Avatar({
  name,
  size = "3rem",
  borderRadius = "0.5rem",
  colors = defaultColors,
}: AvatarProps): React.ReactElement {
  const innerStyle = {
    lineHeight: size,
    textAlign: "center" as "center",
    borderRadius: borderRadius,
    fontWeight: "bold",
    color: "",
    backgroundColor: "",
  };

  const abbr = initials(name);

  const i = sumChars(name) % colors.length;

  const bgColor = colors[i];

  if (contrast(bgColor) === "light") {
    innerStyle.color = "#000";
  } else {
    innerStyle.color = "#fff";
  }

  innerStyle.backgroundColor = bgColor;

  return (
    <div aria-label={name} className="letter-avatar">
      <div style={innerStyle} className="letter-avatar__inner">
        {abbr}
      </div>
    </div>
  );
}
