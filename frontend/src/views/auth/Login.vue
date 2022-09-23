<template>
  <v-row justify="center" align="center">
    <v-col cols="12" md="3" xl="3">
      <v-card outlined>
        <v-card-text class="blue darken-2">
          <v-row justify="center">
            <v-col xl="5" class="text-center">
              <v-img
                height="72"
                width="180"
                :src="require('@/assets/logo.png')"
                contain
              ></v-img>
            </v-col>
            <v-col xl="7">
              <v-row>
                <v-col offset-xl="2" xl="10">
                  <div></div>
                  <div
                    class="text-h6 white--text font-weight-light"
                    title="Artificial Intelligence"
                  >
                    <span class="text-h4 amber--text"> DEMO </span>
                    PROJECT
                  </div>
                 </v-col
                >
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>

        <ValidationObserver ref="bForm">
          <v-form @submit.prevent="login" class="py-5 px-3">
            <v-card-text>
              <b-input
                v-model="credentials.email"
                label="Email"
                rules="required"
                prepend-inner-icon="mdi-email-outline"
                autocomplete="username"
              >
              </b-input>
              <b-input
                v-model="credentials.password"
                :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                label="Password"
                rules="required"
                :type="show ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-outline"
                @click:append="show = !show"
                autocomplete="current-password"
              >
              </b-input>
            </v-card-text>
            <v-card-actions>
              <v-btn
                class="primary"
                large
                outlined
                dark
                type="submit"
                block
                :loading="loading"
              >
                Login
              </v-btn>
            </v-card-actions>
            <!--            <v-card-actions>
              <v-btn link color="warning" text to="/forgot-password">
                Forgot Password?
              </v-btn>
              <v-spacer></v-spacer>
              &lt;!&ndash;              <v-btn link color="info" text to="/register">
                Not A Member?
              </v-btn>&ndash;&gt;
            </v-card-actions>-->
          </v-form>
        </ValidationObserver>
      </v-card>
      <dm-toast></dm-toast>
      <div class="text-center pt-4">
        <small>{{ new Date().getFullYear() }} — <strong>DEMO Company</strong></small>
      </div>
    </v-col>
  </v-row>
</template>

<script>
import bInput from "@/components/form/bInput";
import { saveToken } from "@/services/jwt.service";
import DmToast from "../../components/common/bToast";
import { helpers } from "@/mixins/helpers";
import { socket } from "@/plugins/webSocket";

export default {
  name: "Login",
  components: { DmToast, bInput },
  mixins: [helpers],
  data: () => ({
    credentials: {},
    loading: false,
    show: false,
  }),
  methods: {
    login() {
      this.$refs.bForm.validate().then((success) => {
        if (!success) {
          return;
        }
        this.loading = true;
        this.axios
          .post("login/", this.credentials)
          .then(({ data }) => {
            saveToken(data.access);
            this.axios.post("currentUser/").then(({ data }) => {
              this.$store.commit("auth/setAuth", data);
              this.$toast.setMessage("Successfully Logged In", 2);
              socket.reconnect();
              this.$router.push("/scan");
            });
          })
          .catch((e) => {
            // this.$toast.setMessage("Error", 1);
            this.showMessage("Incorrect E-mail or password", 1);
            this.handleError(e);
          })
          .finally(() => {
            this.loading = false;
          });
      });
    },
  },
  mounted() {
    const status = parseInt(this.$route.params.status);
    if ([401, 403].includes(status)) {
      this.showMessage("Session Time Out", 1);
      // this.$route.params.status = "0";
    }
  },
};
</script>
