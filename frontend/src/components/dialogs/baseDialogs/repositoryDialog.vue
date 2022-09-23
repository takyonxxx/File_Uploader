<template>
  <v-card>
    <v-toolbar dark>{{ formTitle }}</v-toolbar>
    <v-card-text class="mt-10">
      <ValidationObserver ref="bForm">
        <v-row>
          <v-col md="12">
            <h4 v-if="physicalRepo">New Physical Repository</h4>
            <b-select
              v-else
              v-model="item.connector"
              :items="connectors"
              item-text="name"
              item-value="id"
              rules="required"
              label="Connector"
              @change="setFields"
            ></b-select
          ></v-col>
        </v-row>
        <v-row v-if="item.connector">
          <v-col md="12">
            <b-input
              v-model="item.name"
              @keydown.space.prevent
              rules="required"
              label="Repository Name"
              hint="Repository name must be entered without spaces"
            ></b-input
          ></v-col>
          <v-col v-for="field in customFields" md="12" :key="field.id">
            <template v-if="field.type === 'password'">
              <b-input
                v-model="field.value"
                :rules="field.is_required ? 'required' : ''"
                :label="field.name"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-outline"
                @click:append="showPassword = !showPassword"
                autocomplete="off"
              ></b-input>
            </template>
            <template v-else-if="field.data_type === 'text'">
              <b-input
                v-model="field.value"
                :rules="field.is_required ? 'required' : ''"
                :label="field.name"
              ></b-input>
            </template>
          </v-col>

          <v-col md="12"
            ><b-date
              v-model="item.start_date"
              rules="required"
              label="Start Date"
            ></b-date
          ></v-col>
          <template v-if="!physicalRepo">
            <v-col md="6"
              ><b-select
                v-model="item.frequency"
                :items="periods"
                item-value="id"
                item-text="text"
                :rules="{ required: !physicalRepo }"
                label="Update Frequency"
              ></b-select
            ></v-col>
            <v-col md="3"
              ><v-checkbox
                v-model="item.is_full_index"
                label="Full Index"
              ></v-checkbox
            ></v-col>
          </template>
        </v-row>
      </ValidationObserver>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text plain color="error" @click="$emit('close')">Cancel</v-btn>
      <v-btn color="success" @click="save" v-if="item.connector">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import BInput from "@/components/form/bInput";
import BSelect from "@/components/form/bSelect";
import BDate from "@/components/form/bDate";
import { helpers } from "@/mixins/helpers";
export default {
  name: "repositoryDialog",
  components: { BDate, BSelect, BInput },
  mixins: [helpers],
  props: {
    currentItem: {
      type: Object,
    },
    editedIndex: {
      type: Number,
      default: -1,
    },
    physicalRepo: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    item: {},
    connectors: [],
    periods: [
      { id: 1, text: "Daily" },
      { id: 2, text: "Weekly" },
      { id: 3, text: "Monthly" },
    ],
    customFields: [],
    showPassword: false,
  }),
  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Repository" : "Edit Repository";
    },
  },
  methods: {
    getConnectors() {
      this.axios
        .post("getConnectors/")
        .then(({ data }) => {
          this.connectors = data.result.filter((c) => c.id !== 4 && c.id !== 5);
          if (this.item.id) {
            this.customFields = this.item.fields.map((v) => ({
              ...v.connection_property,
              value: v.value,
            }));
          }
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    save() {
      this.$refs.bForm.validate().then((success) => {
        if (success) {
          let repo = { ...this.item };
          repo.start_date = this.$luxon.fromISO(repo.start_date).toISO();
          repo.fields = [...this.customFields];

          this.axios
            .post(
              this.editedIndex === -1
                ? "createRepository/"
                : "updateRepository/",
              repo
            )
            .then(({ data }) => {
              this.showMessage("Saved Successfully");
              this.$emit("save", data.id);
            })
            .catch((e) => {
              this.handleError(e);
            });
        }
      });
    },
    setFields() {
      this.customFields = [
        ...this.connectors
          .find((v) => v.id === this.item.connector)
          .fields.map((v) => ({ ...v, value: "" })),
      ];
    },
  },
  created() {
    if (this.physicalRepo) {
      this.item = {
        name: "",
        connector: 4,
      };
    } else {
      this.item = { ...this.currentItem };
      this.getConnectors();
    }
  },
};
</script>
