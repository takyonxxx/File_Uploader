<template>
  <ValidationProvider
    :name="$attrs.label"
    :vid="$attrs.vid"
    :rules="rules"
    v-slot="{ errors }"
  >
    <v-combobox
      v-model="innerValue"
      :error-messages="errors"
      v-bind="$attrs"
      v-on="$listeners"
    >
      <template v-slot:selection="{ attrs, item, parent, selected, index }">
        <v-chip v-if="index < 4" small>
          <span>{{ item }}</span>
          <v-icon small @click="parent.selectItem(item)">
            mdi-close
          </v-icon>
        </v-chip>
        <span v-if="index > 3" class="grey--text caption">
          (+{{ innerValue.length - 4 }} others)
        </span>
      </template>
    </v-combobox>
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
