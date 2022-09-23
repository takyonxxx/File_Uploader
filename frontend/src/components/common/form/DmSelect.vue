<template>
  <ValidationProvider
    :name="$attrs.label"
    :rules="rules"
    :mode="$attrs.mode || 'eager'"
    v-slot="{ errors, valid, dirty }"
  >
    <v-select
      v-model="innerValue"
      :error-messages="errors"
      :success="valid && dirty"
      v-bind="$attrs"
      v-on="$listeners"
    >
      <!-- pass through scoped slots -->
      <template
        v-for="(_, scopedSlotName) in $scopedSlots"
        v-slot:[scopedSlotName]="slotData"
      >
        <slot :name="scopedSlotName" v-bind="slotData" />
      </template>

      <!-- pass through normal slots -->
      <template v-for="(_, slotName) in $slots" v-slot:[slotName]>
        <slot :name="slotName" />
      </template>
    </v-select>
  </ValidationProvider>
</template>

<script>
import { ValidationProvider } from "vee-validate";

export default {
  components: {
    ValidationProvider,
  },
  props: {
    rules: {
      type: [Object, String],
      default: "",
    },
    value: {
      type: null,
    },
  },
  data: () => ({
    innerValue: "",
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
  created() {
    if (this.value) {
      this.innerValue = this.value;
    }
  },
};
</script>
