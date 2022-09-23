import store from "@/store";

export const toast = {
  setMessage(content, type) {
    store.commit("setMessage", { content, type });
  },
};
