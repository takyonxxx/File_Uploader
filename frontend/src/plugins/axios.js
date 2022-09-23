import axios from "axios";
import { saveToken, getToken, getRefresh } from "@/services/jwt.service";
import router from "@/router";

let baseUrl = "/api/";
const $axios = axios.create({
  baseURL: baseUrl,
});

$axios.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers["Authorization"] = "Bearer " + token;
    }
    return config;
  },
  (error) => {
    Promise.reject(error);
  }
);

// $axios.interceptors.response.use(
//   (response) => {
//     return response;
//   },
//   function (error) {
//     const originalRequest = error.config;
//     if (
//       error.response.status === 401 &&
//       originalRequest.url === baseUrl + "auth/refresh-tokens/"
//     ) {
//       router.push("/login");
//       return Promise.reject(error);
//     }
//
//     if ([403,401].includes(error.response.status) && !originalRequest._retry) {
//       originalRequest._retry = true;
//       const refreshToken = getRefresh();
//       return $axios
//         .post("auth/refresh-tokens/", {
//           refreshToken: refreshToken,
//         })
//         .then((res) => {
//           if (res.status === 200) {
//             saveToken(res.data.access);
//             $axios.defaults.headers.common["Authorization"] =
//               "Bearer " + getToken();
//             return $axios(originalRequest);
//           }
//         });
//     }
//     return Promise.reject(error);
//   }
// );

export default $axios;
