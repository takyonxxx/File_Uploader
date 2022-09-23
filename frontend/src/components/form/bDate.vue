<template>
  <v-menu
    ref="menu"
    v-model="menu"
    transition="scale-transition"
    offset-y
    min-width="auto"
  >
    <template v-slot:activator="{ on }">
      <ValidationProvider
        :vid="$attrs.vid"
        :name="$attrs.vName"
        :mode="$attrs.mode || 'eager'"
        :rules="rules"
        v-slot="{ errors, valid, dirty }"
      >
        <v-text-field
          v-model="computedDateFormatted"
          :error-messages="errors"
          :success="valid && dirty"
          prepend-inner-icon="mdi-calendar"
          v-bind="$attrs"
          v-on="on"
        ></v-text-field>
      </ValidationProvider>
    </template>

    <v-date-picker
      v-model="innerValue"
      no-title
      scrollable
      :min="min"
      :max="max"
      v-bind="$attrs"
    >
    </v-date-picker>
  </v-menu>
</template>

<script>
import { ValidationProvider } from "vee-validate";

export default {
  name: "bDate",
  components: {
    ValidationProvider,
  },
  props: {
    rules: {
      type: [Object, String],
      default: "",
    },
    // must be included in props
    value: {
      type: null,
    },
    min: {
      type: null,
    },
    max: {
      type: null,
    },
  },
  data: () => ({
    innerValue: "",
    menu: false,
  }),
  watch: {
    // Handles internal model changes.
    innerValue(newVal) {
      this.$emit("input", newVal);
    },
    // Handles external model changes.
    value(newVal) {
      this.innerValue = newVal;
    },
  },
  computed: {
    computedDateFormatted() {
      return this.formatDate(this.innerValue);
    },
  },
  methods: {
    formatDate(date) {
      if (!date) return null;

      if (Array.isArray(this.innerValue)) {
        return this.innerValue.join(" ~ ");
      } else {
        const [year, month, day] = date.split("-");
        return `${day}/${month}/${year}`;
      }
    },
  },
  created() {
    if (this.value) {
      this.innerValue = this.$luxon.fromISO(this.value).toFormat("yyyy-LL-dd");
    }
  },
};
</script>
