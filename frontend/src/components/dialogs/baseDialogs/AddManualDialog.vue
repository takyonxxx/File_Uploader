<template>
  <v-card>
    <v-dialog v-model="dialog" width="600" :key="dialogKey" persistent>
      <add-grammar
        @closeDialog="closeDialog"
        :editedIndex="editedIndex"
        :undiscovered="true"
        :currentItem="currentItem"
        @save="grammarSaved"
      ></add-grammar>
    </v-dialog>
    <v-toolbar dark>Add Undiscovered Personal Data</v-toolbar>
    <v-card-text class="mt-10">
      <p class="h5">
        Undiscovered Data will be matched with
        <strong>Undiscovered File</strong>
      </p>
      <ValidationObserver ref="bForm">
        <v-row>
          <v-col md="12">
            <b-select
              outlined
              v-model="typeId"
              :items="grammars"
              item-text="name"
              item-value="id"
              rules="required"
              label="Select Grammar"
            >
              <template v-slot:item="{ item }">
                <div>
                  {{ item.name }}

                  <span class="text-subtitle-2 grey--text">
                    - ({{ item.data_type.category.name }})
                  </span>
                </div>
              </template>
              <template v-slot:selection="{ item }">
                <div>
                  {{ item.name }}

                  <span class="text-subtitle-2 grey--text">
                    - ({{ item.data_type.category.name }})
                  </span>
                </div>
              </template>
              <template v-slot:append-item>
                <v-list-item>
                  <v-btn outlined color="primary" block @click="addItem"
                    ><v-icon left>mdi-plus</v-icon> New Grammar</v-btn
                  >
                </v-list-item>
              </template>
            </b-select></v-col
          >
        </v-row>
      </ValidationObserver>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text plain color="error" @click="$emit('close')">Cancel</v-btn>
      <v-btn color="success" @click="save" v-if="typeId"
        ><v-icon>mdi-check</v-icon> Save</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import BSelect from "@/components/form/bSelect";
import AddGrammar from "./AddGrammar";
import { helpers } from "@/mixins/helpers";

export default {
  components: { AddGrammar, BSelect },
  mixins: [helpers],
  data: () => ({
    grammars: [],
    typeId: null,
    documentId: null,
    currentItem: {},
    editedIndex: -1,
    dialog: false,
    dialogKey: 0,
  }),
  computed: {},
  methods: {
    grammarSaved(id) {
      this.dialog = false;
      this.getGrammarTypes(id);
    },
    addItem() {
      (this.currentItem = {
        enabled: true,
        regex: null,
      }),
        (this.editedIndex = -1);
      this.dialogKey++;
      this.dialog = true;
    },
    setFields() {},
    getGrammarTypes(id) {
      this.axios
        .post("getGrammars/")
        .then(({ data }) => {
          this.grammars = data.result;
          if (id) {
            this.typeId = id;
          }
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    save() {
      this.$refs.bForm.validate().then((success) => {
        if (success) {
          this.axios
            .post("addProcessData/", { type: this.typeId })
            .then(({ data }) => {
              this.showMessage("Saved Successfully");
              this.$emit("save", data.document_id);
            })
            .catch((e) => {
              this.handleError(e);
            });
        }
      });
    },

    closeDialog() {
      this.dialog = false;
      this.editedIndex = -1;
    },
  },
  created() {
    this.getGrammarTypes();
  },
};
</script>
