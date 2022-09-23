<template>
  <v-row>
    <v-col>
      <v-data-table
        :items="items"
        :headers="headers"
        :options.sync="options"
        :server-items-length="total"
        :search="searchText"
        :loading="loading"
        :footer-props="{
          itemsPerPageOptions: [10, 25, 50, 100],
        }"
      >
        <template v-slot:top>
          <v-toolbar dense flat>
            <v-btn @click="addItem" small color="success"
              ><v-icon left>mdi-plus</v-icon> New
            </v-btn>
            <v-spacer> </v-spacer>
            <v-col md="3">
              <v-text-field
                v-model="searchText"
                label="Search"
                append-icon="mdi-magnify"
                single-line
                hide-details
              ></v-text-field>
            </v-col>
          </v-toolbar>
        </template>
        <template v-slot:item.connector="{ item }">
          {{
            connectors.find((v) => v.id === item.connector)
              ? connectors.find((v) => v.id === item.connector).name
              : ""
          }}
        </template>
        <template v-slot:item.frequency="{ item }">
          {{
            periods.find((v) => v.id === item.frequency)
              ? periods.find((v) => v.id === item.frequency).text
              : ""
          }}
        </template>
        <template v-slot:item.is_full_index="{ item }">
          <v-icon :color="item.is_full_index ? 'success' : 'error'">{{
            item.is_full_index ? "mdi-check" : "mdi-close"
          }}</v-icon>
        </template>
        <template v-slot:item.start_date="{ item }">
          {{ formatDateTime(item.start_date, "dd/LL/yyyy") }}
        </template>
        <template v-slot:item.risk_score="{ item }">
          {{ item.risk_score }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="teal lighten-1"
            @click="editItem(item)"
            title="Edit"
          >
            <v-icon> mdi-pencil-outline </v-icon>
          </v-btn>
          <v-btn
            icon
            color="error lighten-1"
            @click="confirmDelete(item)"
            title="Delete"
          >
            <v-icon> mdi-delete-outline </v-icon>
          </v-btn>
        </template>
      </v-data-table>
      <confirm-dialog ref="confirm"></confirm-dialog>
      <v-dialog v-model="dialog" width="600" :key="dialogKey" persistent>
        <repository-dialog
          :current-item="currentItem"
          :edited-index="editedIndex"
          @close="closeDialog"
          @save="repositorySaved"
        ></repository-dialog>
      </v-dialog>
    </v-col>
  </v-row>
</template>

<script>
import { crudMixin } from "@/mixins/crudMixin";
import { helpers } from "@/mixins/helpers";

import ConfirmDialog from "@/components/dialogs/bConfirmDialog";
import RepositoryDialog from "@/components/dialogs/baseDialogs/repositoryDialog";
export default {
  name: "Repositories",
  components: { RepositoryDialog, ConfirmDialog },
  mixins: [crudMixin, helpers],
  data: () => ({
    headers: [
      { text: "Repository Name", value: "name" },
      { text: "Connector", value: "connector" },
      { text: "Frequency", value: "frequency" },
      { text: "Full Index", value: "is_full_index" },
      { text: "Start Date", value: "start_date" },
      { text: "Risk Score", value: "risk_score" },
      { text: "Actions", value: "actions", sortable: false },
    ],
    connectors: [
      { id: 1, name: "File System" },
      { id: 2, name: "Exchange Server" },
      { id: 3, name: "Database Server" },
    ],
    periods: [
      { id: 1, text: "Daily" },
      { id: 2, text: "Weekly" },
      { id: 3, text: "Monthly" },
    ],
  }),
  computed: {},
  methods: {
    getConnectors() {
      this.axios
        .post("getConnectors/")
        .then(({ data }) => {
          this.connectors = data.result;
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    fetchItems() {
      this.axios
        .post("getRepositorys/", { ...this.options, search: this.searchText })
        .then(({ data }) => {
          this.items = data.result;
          this.total = data.total;
        })
        .catch((e) => {
          this.handleError(e);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    repositorySaved() {
      this.dialog = false;
      this.fetchItems();
    },
    deleteItem(id) {
      this.axios
        .post("deleteRepository/", { id: id })
        .then(({ data }) => {
          this.showMessage("Deleted Successfully");
          this.fetchItems();
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    async confirmDelete(item) {
      if (
        await this.$refs.confirm.open(
          ` Are you sure you want to <b>delete</b> ${item.name} .
                    <br>Deleting will <b>remove all segments and the data</b> related to segments.
                    You <b>must run calculate</b> segments again!`
        )
      ) {
        this.deleteItem(item.id);
      }
    },
  },
  created() {
    this.getConnectors();
  },
};
</script>
