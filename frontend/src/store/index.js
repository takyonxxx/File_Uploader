import Vue from "vue";
import Vuex from "vuex";

import auth from "./auth.module";
import permissions from "./permissions.module";
import parameters from "./parameters.module";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    menu: false,
    message: {
      content: "",
      type: null,
    },
    pageCounter: 0,
    scanStatus: {
      percentage: 0,
      repository_name: "",
      file_name: "",
    },
  },
  getters: {
    getScanStatus(state) {
      return state.scanStatus;
    },
  },
  mutations: {
    toggleMenu(state) {
      state.menu = !state.menu;
    },
    setMessage(state, { content, type }) {
      state.message.content = content;
      state.message.type = type;
    },
    setPageCounter(state) {
      state.pageCounter++;
    },
    setScanStatus(state, payload) {
      // console.log(payload);
      state.scanStatus = payload;
    },
  },
  actions: {},
  modules: {
    auth,
    permissions,
    parameters,
  },
});
