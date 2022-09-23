import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import VueJsonToCsv from "vue-json-to-csv";

import $axios from "@/plugins/axios";
import { DateTime } from "luxon";
import "@/plugins/vee-validate";
import { toast } from "@/mixins/toastMixin";
import { helpers } from "@/mixins/helpers";
import "@/assets/css/custom.css";
import { socket } from "@/plugins/webSocket";

Vue.prototype.axios = $axios;
Vue.prototype.$luxon = DateTime;
Vue.prototype.$toast = toast;
Vue.use(VueJsonToCsv);
Vue.prototype.$helpers = helpers;
Vue.prototype.$socket = socket;

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
