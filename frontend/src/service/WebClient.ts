/**
 * request 网络请求工具
 * 更详细的 api 文档: https://github.com/umijs/umi-request
 */
import { extend, ResponseError } from "umi-request";
import { Authority } from "./Authority";

const errorHandler = (error: ResponseError) => {
  if (error.response.status === 401) {
    Authority.clean();
    window.location.href = window.location.origin + "/login";
    return;
  }
  return Promise.reject(error);
};

const request = extend({
  errorHandler,
});

request.interceptors.request.use((url, options) => {
  const urlPrefix = process.env.NEXT_PUBLIC_ENV_URL_PREFIX;
  const fullUrl = process.env.NEXT_PUBLIC_ENV_URL_PREFIX
    ? `${urlPrefix}${url}`
    : url;
  const token = Authority.get();
  return {
    url: fullUrl,
    options: {
      ...options,
      headers: {
        ...options.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    },
  };
});

export default request;
