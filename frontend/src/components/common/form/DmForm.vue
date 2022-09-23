<template>
  <ValidationObserver
    ref="dmForm"
    v-slot="{ invalid, validated, handleSubmit, validate }"
  >
    <v-form>
      <VTextFieldWithValidation
        rules="required|max:10"
        v-model="name"
        :counter="10"
        label="Name"
      />

      <VTextFieldWithValidation
        rules="required|email"
        v-model="email"
        label="E-mail"
      />

      <VSelectWithValidation
        rules="required"
        :items="items"
        v-model="select"
        label="Select"
      />

      <!-- Do this one yourself! -->
      <ValidationProvider
        rules="required"
        name="checkbox"
        v-slot="{ errors, valid }"
      >
        <v-checkbox
          v-model="checkbox"
          :error-messages="errors"
          :success="valid"
          value="1"
          label="Option"
          type="checkbox"
          required
        ></v-checkbox>
      </ValidationProvider>
    </v-form>

    <v-card-actions>
      <v-btn @click="clear">Clear</v-btn>
      <v-spacer></v-spacer>
      <v-btn @click="validate">Validate</v-btn>
      <v-btn
        color="primary"
        @click="handleSubmit(submit)"
        :disabled="invalid || !validated"
        >Sign Up</v-btn
      >
    </v-card-actions>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, ValidationProvider } from "vee-validate";
import VTextFieldWithValidation from "./inputs/VTextFieldWithValidation";
import VSelectWithValidation from "./inputs/VSelectWithValidation";

export default {
  data: () => ({
    items: ["", "Foo", "Bar"],
    name: "",
    email: "",
    select: "",
    checkbox: ""
  }),
  components: {
    ValidationObserver,
    ValidationProvider,
    VTextFieldWithValidation,
    VSelectWithValidation
  },
  methods: {
    async clear() {
      this.name = this.email = this.select = this.checkbox = "";
      requestAnimationFrame(() => {
        this.$refs.obs.reset();
      });
    },
    async submit() {
      console.log("Submitting!");
    }
  }
};
</script>
