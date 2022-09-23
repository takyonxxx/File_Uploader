<template>
  <ValidationProvider
    :vid="$attrs.vid"
    :name="$attrs.vName"
    :mode="$attrs.mode || 'eager'"
    :rules="rules"
    v-slot="{ errors, valid, dirty }"
  >
    <v-text-field
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
    </v-text-field>
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
    // must be included in props
    value: {
      type: null,
    },
    vMask: {
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
