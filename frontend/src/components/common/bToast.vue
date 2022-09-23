<template>
  <div>
    <v-dialog v-model="show" v-if="htmlError" fullscreen>
      <v-toolbar flat dark color="warning">
        <v-toolbar-title>Warning</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="show = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>

      <div class="p-5" v-html="message"></div>
    </v-dialog>
    <v-snackbar
      v-else
      v-model="show"
      :top="type !== 1"
      :centered="type === 4 || type === 5"
      :color="handleColor"
      :timeout="type === 2 ? 1500 : 2500"
      @
      min-width="50px"
    >
      <div class="d-flex justify-space-between align-center">
        <template v-if="type === 4">
          <v-progress-circular indeterminate class="mr-3"></v-progress-circular>
          <div v-html="message"></div>
        </template>
        <template v-else>
          <v-icon class="mr-2">mdi-{{ handleIcon }}</v-icon>
          <div v-html="message"></div>
        </template>
      </div>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  name: "DmToast",
  data() {
    return {
      show: false,
      message: "",
      type: "",
    };
  },
  computed: {
    htmlError() {
      if (this.message !== undefined) {
        return this.message.substr(0, 9) === `<!DOCTYPE`;
      } else {
        return false;
      }
    },
    handleColor() {
      switch (this.type) {
        case 0:
          return "info";
        case 1:
          return "error";
        case 2:
          return "success";
        case 3:
          return "warning";
        case 4:
          return "cyan";
        case 5:
          return "warning";
        default:
          return "info";
      }
    },
    handleIcon() {
      switch (this.type) {
        case 0:
          return "information";
        case 1:
          return "alert";
        case 2:
          return "check-circle-outline";
        case 3:
          return "alert";
        case 4:
          return "information";
        case 5:
          return "information";
        default:
          return "information";
      }
    },
  },

  created() {
    this.$store.subscribe((mutation, state) => {
      if (mutation.type === "setMessage") {
        this.message = state.message.content;
        this.type = state.message.type;
        this.show = true;
      }
    });
  },
};
</script>
<style>
::v-deep .v-snack__wrapper {
  min-width: 100px;
}
</style>
