import axios from "axios";

axios.default.withCredentials = true;

const requester = (url, headers) => {
  const post = (path, data) =>
    axios({
      method: "post",
      url: `${url}${path}`,
      headers: headers,
      data: data
    });

  const patch = (path, data) =>
    axios({
      method: "patch",
      url: `${url}${path}`,
      headers: headers,
      data: data
    });

  const get = path =>
    axios({
      method: "get",
      url: `${url}${path}`,
      headers: headers
    });

  return {
    post: post,
    get: get,
    patch: patch
  };
};

export default requester;
