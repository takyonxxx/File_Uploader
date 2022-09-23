<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    :style="{ zIndex: options.zIndex }"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-toolbar :color="options.color" flat dark>{{
        options.title
      }}</v-toolbar>

      <v-card-text v-show="!!message" class="msg py-10" v-html="message">
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="pt-3">
        <v-spacer></v-spacer>
        <v-btn
          v-if="!options.noConfirm"
          color="grey"
          text
          class="body-2 font-weight-bold"
          @click.native="cancel"
          >Cancel
        </v-btn>
        <v-btn
          color="primary"
          class="body-2 font-weight-bold"
          outlined
          @click.native="agree"
          >OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  name: "ConfirmDialog",
  data() {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      message: null,
      options: {
        color: "red darken-3",
        width: 500,
        zIndex: 200,
        noConfirm: false,
        title: "Confirm",
      },
    };
  },
  methods: {
    open(message, options) {
      this.dialog = true;
      this.message = message;
      this.options = Object.assign(this.options, options);
      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    agree() {
      this.resolve(true);
      this.dialog = false;
    },
    cancel() {
      this.resolve(false);
      this.dialog = false;
    },
  },
};
</script>
