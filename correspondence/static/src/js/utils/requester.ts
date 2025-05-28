import axios, { AxiosHeaders, AxiosResponse } from "axios";

axios.defaults.withCredentials = true;

type AxiosResponsePromise = Promise<AxiosResponse<any, any>>

export type Requester = {
  post: (path: string, data: any) => AxiosResponsePromise;
  patch: (path: string, data: any) => AxiosResponsePromise;
  get: (path: string) => AxiosResponsePromise;
};

const requester = (url: string, headers?: AxiosHeaders): Requester => {
  const post = (path: string, data: any): AxiosResponsePromise =>
    axios({
      method: "post",
      url: `${url}${path}`,
      headers: headers,
      data: data,
    });

  const patch = (path: string, data: any): AxiosResponsePromise =>
    axios({
      method: "patch",
      url: `${url}${path}`,
      headers: headers,
      data: data,
    });

  const get = (path: string): AxiosResponsePromise =>
    axios({
      method: "get",
      url: `${url}${path}`,
      headers: headers,
    });

  return {
    post: post,
    get: get,
    patch: patch,
  };
};

export default requester;
