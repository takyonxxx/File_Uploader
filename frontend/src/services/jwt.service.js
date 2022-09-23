export const getToken = () => {
  return localStorage.getItem("access");
};
export const getRefresh = () => {
  return localStorage.getItem("refresh");
};

export const saveToken = (token) => {
  localStorage.setItem("access", token);
};

export const saveRefresh = (token) => {
  localStorage.setItem("refresh", token);
};

export const destroyToken = () => {
  localStorage.removeItem("access");
};

export default { getToken, getRefresh, saveToken, saveRefresh, destroyToken };
