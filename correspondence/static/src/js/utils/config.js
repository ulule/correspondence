class Config {
  set(key, data) {
    if (typeof key === "string") {
      this[key] = data;
    }

    if (Object.prototype.toString.call(key) === "[object Object]") {
      Object.assign(this, key);
    }
  }

  get(key) {
    return this[key] || "";
  }
}

export default new Config();
