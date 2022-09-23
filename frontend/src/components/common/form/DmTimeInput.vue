<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    :return-value.sync="innerValue"
    offset-y
    min-width="auto"
  >
    <template v-slot:activator="{ on }">
      <ValidationProvider
        :vid="$attrs.vid"
        :name="$attrs.vName"
        :mode="$attrs.mode || 'eager'"
        :rules="rules"
        v-slot="{ errors, valid }"
      >
        <v-text-field
          v-model="innerValue"
          :error-messages="errors"
          :success="valid"
          readonly
          v-bind="$attrs"
          v-on="on"
        ></v-text-field>
      </ValidationProvider>
    </template>

    <v-time-picker
      v-if="menu"
      v-model="innerValue"
      format="24hr"
      no-title
      scrollable
      @click:minute="$refs.menu.save(innerValue)"
    >
    </v-time-picker>
  </v-menu>
</template>

<script>
import { ValidationProvider } from "vee-validate";

export default {
  components: {
    ValidationProvider
  },
  props: {
    rules: {
      type: [Object, String],
      default: ""
    },
    // must be included in props
    value: {
      type: null
    },
    vMask: {
      type: null
    }
  },
  data: () => ({
    innerValue: "",
    menu: false
  }),
  watch: {
    // Handles internal model changes.
    innerValue(newVal) {
      this.$emit("input", newVal);
    },
    // Handles external model changes.
    value(newVal) {
      this.innerValue = newVal;
    }
  },
  created() {
    if (this.value) {
      this.innerValue = this.value;
    }
  }
};
</script>
