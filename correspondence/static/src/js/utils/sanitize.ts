import { Values } from "../types";

export function sanitize(values: Values): Values {
  Object.keys(values).forEach((key) => {
    const value = values[key];

    if (value === "") {
      values[key] = null;
    }
  });

  return values;
}

export default sanitize;
