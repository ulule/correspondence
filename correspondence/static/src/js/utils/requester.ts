import axios, { AxiosHeaders, AxiosResponse } from "axios";

axios.defaults.withCredentials = true;

export type Requester = {
  post: (path: string, data: any) => Promise<AxiosResponse<any, any>>;
  patch: (path: string, data: any) => Promise<AxiosResponse<any, any>>;
  get: (path: string) => Promise<AxiosResponse<any, any>>;
};

const requester = (url: string, headers?: AxiosHeaders): Requester => {
  const post = (path: string, data: any): Promise<AxiosResponse<any, any>> =>
    axios({
      method: "post",
      url: `${url}${path}`,
      headers: headers,
      data: data,
    });

  const patch = (path: string, data: any): Promise<AxiosResponse<any, any>> =>
    axios({
      method: "patch",
      url: `${url}${path}`,
      headers: headers,
      data: data,
    });

  const get = (path: string): Promise<AxiosResponse<any, any>> =>
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
