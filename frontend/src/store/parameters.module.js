const state = {
  grammarParams: {
    encodingTypes: [
      { id: 1, name: "UTF-8" },
      { id: 2, name: "UTF-9" },
    ],
    types: [
      { id: 1, name: "Pattern" },
      { id: 2, name: "Data File" },
      { id: 3, name: "Other" },
    ],
  },
};

const getters = {
  getGrammarParams() {
    return state.grammarParams;
  },
};

const actions = {};

const mutations = {};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
};
