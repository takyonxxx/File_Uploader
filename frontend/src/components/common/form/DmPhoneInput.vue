<template>
  <ValidationProvider
    :name="$attrs.label"
    :rules="rules"
    v-slot="{ errors, valid }"
  >
    <v-text-field-simplemask
      v-model="innerValue"
      v-bind="$attrs"
      v-on="$listeners"
      :properties="{
        prefix: '+',
        suffix: '',
        readonly: false,
        disabled: false,
        outlined: false,
        clearable: false,
        placeholder: '90',
        success: valid,
        errorMessages: errors
      }"
      :options="{
        inputMask: '(##) ### ### ## ##',
        outputMask: '############',
        empty: '(90)',
        applyAfter: false,
        alphanumeric: true,
        lowerCase: false,
        length: 12
      }"
      v-bind:focus="focus"
      @focus="focus = false"
    />
  </ValidationProvider>
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
    }
  },
  data: () => ({
    innerValue: ""
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
