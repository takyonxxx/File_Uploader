<template>
  <v-row justify="center" align="center">
    <v-col cols="12" md="3" xl="3">
      <v-card elevation="5" outlined shaped>
        <v-row justify="center" class="mt-6">
          <v-col class="text-center">
            <v-img
              height="100"
              contain
              :src="require(`@/assets/logo.png`)"
            ></v-img>
            <div class="text-h4 mt-2">REGISTER</div>
          </v-col>
        </v-row>

        <ValidationObserver ref="bForm">
          <v-form @submit.prevent="register">
            <v-card-text>
              <b-input
                v-model="credentials.name"
                label="Name"
                rules="required"
                prepend-inner-icon="mdi-account"
                autocomplete="username20"
              >
              </b-input>
              <b-input
                v-model="credentials.email"
                label="Email"
                rules="required|email"
                prepend-inner-icon="mdi-email-outline"
                autocomplete="username30"
              >
              </b-input>
              <b-input
                v-model="credentials.password"
                :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                label="Password"
                rules="required|min:3"
                :type="show ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-outline"
                @click:append="show = !show"
                autocomplete="new-password"
              >
              </b-input>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" type="submit" block :loading="loading">
                Register
              </v-btn>
            </v-card-actions>
            <v-card-actions>
              <v-btn link color="warning" text to="/login">
                Already Member?
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-form>
        </ValidationObserver>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import bInput from "@/components/form/bInput";
export default {
  name: "Register",
  components: { bInput },
  data: () => ({
    credentials: {},
    loading: false,
    show: false,
  }),
  methods: {
    register() {
      this.$refs.bForm.validate().then((success) => {
        if (!success) {
          return;
        }
        this.loading = true;
        this.axios
          .post("auth/register", this.credentials)
          .then(({ data }) => {
            this.$toast.setMessage(data.message);
            this.$router.push("/login");
          })
          .catch(({ response }) => {
            console.log(response.data);
            this.$toast.setMessage(response.data.data[0].msg, 1);
          })
          .finally(() => {
            this.loading = false;
          });
      });
    },
  },
};
</script>

<style scoped></style>
