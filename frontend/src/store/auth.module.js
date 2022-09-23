import JwtService from "@/services/jwt.service";
import axios from "@/plugins/axios";
import router from "@/router";
import flatten from "lodash/flatten";

const state = {
  token: null,
  isAuthenticated: null,
  user: {},
};

const getters = {
  permissions(state) {
    return [
      ...new Set(
        flatten(state.user.roles.map((v) => v.permissions.map((z) => z.slug)))
      ),
    ];
  },
  currentUser(state) {
    return state.user;
  },
  isAuthenticated(state) {
    return state.isAuthenticated;
  },
};

const mutations = {
  setAuth(state, payload) {
    state.isAuthenticated = true;
    state.user = { ...payload };
  },
  purgeAuth(state, status = 0) {
    if (router.history.current.name !== "login") {
      router.push({ name: "login", params: { status: status } }).then(() => {
        state.isAuthenticated = false;
        state.user = {};
        JwtService.destroyToken();
      });
    }
  },
};

export default {
  namespaced: true,
  state,
  mutations,
  getters,
};
