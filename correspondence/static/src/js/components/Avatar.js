import React from "react";
import initials from "initials";
import contrast from "contrast";

const defaultColors = [
  "#2ecc71", // emerald
  "#3498db", // peter river
  "#8e44ad", // wisteria
  "#e67e22", // carrot
  "#e74c3c", // alizarin
  "#1abc9c", // turquoise
  "#2c3e50" // midnight blue
];

const sumChars = str => {
  let sum = 0;
  for (let i = 0; i < str.length; i++) {
    sum += str.charCodeAt(i);
  }

  return sum;
};

const Avatar = props => {
  const {
    name,
    size = "3rem",
    borderRadius = "0.5rem",
    colors = defaultColors
  } = props;

  const innerStyle = {
    lineHeight: size,
    textAlign: "center",
    borderRadius: borderRadius,
    fontWeight: "bold"
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
};

export default Avatar;
