<template>
  <v-row>
    <v-col md="12">
      <v-data-table
          class="items-table-container"
          :headers="headers"
          :items="items"
          v-model="selectedItems"
          show-select
          item-key="id"
          :options.sync="options"
          :server-items-length="total"
          :search="searchText"
          :loading="loading"
          :items-per-page="500"
          :footer-props="{
          itemsPerPageOptions: [10, 25, 50, 100, 500, 1000, 10000],
        }"
      >
        <template v-slot:top>
          <v-toolbar dense flat>
            <v-row>
              <div class="text-center">
                <v-dialog v-model="dialog">
                  <v-card
                      class="blue-grey lighten-5"
                      outlined
                      v-if="fileDetails !== null"
                  >
                    <v-toolbar flat color="blue-grey lighten-1" dark>
                      <v-icon left>mdi-file-outline</v-icon>
                      File Details - {{ selectedFileName }}</v-toolbar
                    >
                    <v-card-text
                        class="text-block"
                        style="overflow-wrap: anywhere"
                        v-html="formatText(fileDetails)"
                    ></v-card-text>
                    <v-card-actions>
                      <v-btn color="primary" block @click="dialog = false">Close Content</v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
              </div>
              <v-col cols="2">
                <v-btn
                    @click="confirmScan()"
                    color="primary"
                    elevation="0"
                    :loading="scanning"
                    :disabled="scanning"
                >
                  <v-icon class="mr-3">mdi-text-search-variant</v-icon>

                  Scan Repositories
                </v-btn>
              </v-col>
              <v-col cols="auto">
                <v-btn
                    @click="confirmDelete()"
                    class="error mr-5"
                    elevation="0"
                    v-if="selectedItems.length > 0"
                >
                  <v-icon>mdi-delete</v-icon>
                  Delete Files
                </v-btn>
                <template>
                  <v-btn
                      @click="confirmAbortOperations()"
                      class="ml-3 success"
                      v-if="scanning"
                      :disabled="scanning === false"
                  >
                    <v-icon>mdi-close-circle-outline</v-icon>
                    Abort Operations
                  </v-btn>
                </template>
              </v-col>
              <confirm-dialog ref="confirm"></confirm-dialog>
              <v-col v-if="scanning">
                <v-container>
                  <v-row>
                    <v-col cols="4" align-self="center">
                      <v-progress-linear
                          rounded
                          :value="getScanStatus.percentage"
                          height="6"
                          class="ma-0"
                      ></v-progress-linear>
                    </v-col>
                    <v-col class="text-subtitle-2">
                      {{ getScanStatus.count_status }} {{ getScanStatus.text }}
                    </v-col>
                  </v-row>
                </v-container>
              </v-col>
              <template v-else>
                <v-spacer></v-spacer>
                <v-col md="3">
                  <v-text-field
                      v-model="searchText"
                      label="Search"
                      append-icon="mdi-magnify"
                      single-line
                      hide-details
                  ></v-text-field>
                </v-col>
              </template>
            </v-row>
          </v-toolbar>
        </template>

        <template v-slot:item.name="{ item }">
          <v-icon large color="blue-grey">{{
              ext[
                  item.name.substring(item.name.lastIndexOf(".") + 1).toLowerCase()
                  ]
            }}
          </v-icon>
          {{ item.name }}
        </template>
        <template v-slot:item.path="{ item }">
          {{ getPath(item) }}
        </template>
        <template v-slot:item.source="{ item }">
          <v-icon color="warning">{{ sourceIcons[item.source] }}</v-icon>
        </template>
        <template v-slot:item.size="{ item }">
          {{ formatSize(item.size) }}
        </template>
        <template v-slot:item.created="{ item }">
          {{ createdDate(item.created) }}
        </template>
        <template v-slot:item.id="{ item }">
          <v-btn class="mx-2" icon @click="() =>  fetchFileData(item.id, item.name)">
            <v-icon dark>mdi-cloud-upload</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-col>
    <v-col>
      <v-snackbar
          v-model="snackbar"
          :timeout="-1"
          :multi-line="true"
          vertical
          class="d-flex justify-content-center"
      >
        <p v-for="(variable, i) in infoMessage" :key="i">
          {{ variable }}
        </p>
        <template v-slot:action="{ attrs }">
          <v-btn color="blue" text v-bind="attrs" @click="snackbar = false">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-col>
  </v-row>
</template>

<script>
import {crudMixin} from "@/mixins/crudMixin";
import {helpers} from "@/mixins/helpers";
import DmCheckBox from "../components/common/form/DmCheckBox";
import ConfirmDialog from "@/components/dialogs/bConfirmDialog";
import {mapGetters, mapMutations} from "vuex";


export default {
  name: "ScanRepositories",
  components: {DmCheckBox, ConfirmDialog},
  mixins: [crudMixin, helpers],
  computed: {
    ...mapGetters({
      getScanStatus: "getScanStatus",
    }),
    selectedItemIds() {
      return this.selectedItems.map((s) => s.id);
    },
    scanComplete() {
      return this.getScanStatus.percentage === 100;
    },
    progressVisible() {
      return this.getScanStatus.percentage !== 0 || this.scanning;
    },
  },
  data: () => ({
    headers: [
      {text: "Repository", value: "repository.name"},
      {text: "Source", value: "source"},
      {text: "Path / Table", value: "path"},
      {text: "Title / Filename", value: "name"},
      {text: "Size", value: "size", align: "right", width: "120px"},
      {text: "Created", value: "created", width: "120px"},
      {text: "Content", value: "id", sortable: false},
    ],

    ext: {
      html: "mdi-language-html5",
      js: "mdi-nodejs",
      json: "mdi-code-json",
      md: "mdi-language-markdown",
      pdf: "mdi-file-pdf-box",
      png: "mdi-file-image",
      txt: "mdi-file-document-outline",
      xls: "mdi-file-excel-outline",
      docx: "mdi-file-word-outline",
    },
    selectedItems: [],
    sourceIcons: {
      FileConnector: "mdi-folder-outline",
    },
    fileDetails: null,
    scanning: false,
    infoMessage: [],
    snackbar: false,
    dialog: false,
  }),
  selectedFileName: "",
  methods: {
    ...mapMutations({
      setScanStatus: "setScanStatus",
    }),
    scrollToTop() {
      window.scrollTo(0, 0);
    },
    formatText(str) {
      return str.replace(/(\\r)*\\n/g, '<br>');
    },
    getPath(item) {
      if (item.source === "FileConnector") {
        return item.path.substring(0, item.path.lastIndexOf("/") + 1);
      }
      return item.path;
    },
    async confirmDelete(message) {
      if (
          await this.$refs.confirm.open(
              message
                  ? message
                  : ` <b>BE CAREFUL!</b>
                <br>You are deleting selected files!</b>`
          )
      ) {
        this.deleteItems();
      }
    },
    deleteItems() {
      this.loading = true;
      this.fileDetails = null
      this.axios
          .post("delete_files/", this.selectedItemIds)
          .then(({data}) => {
            this.fetchItems();
          })
          .catch((e) => {
            this.handleError(e);
          })
          .finally(() => {
            this.loading = false;
          });
    },
    async confirmAbortOperations(message) {
      this.abortOperations();
    },
    abortOperations() {
      this.loading = true;
      this.fileDetails = null
      this.axios
          .post("deleteProcessController/")
          .then(({data}) => {
            if (data.status) {
              this.fetchItems();
              this.scanning = false;
              this.setScanStatus(0);
            } else {
              this.handleError(
                  "Abortion operation cannot be completed. Please check system logs."
              );
            }
          })
          .catch((e) => {
            this.handleError(e);
          })
          .finally(() => {
            this.loading = false;
          });
    },
    async confirmScan(message) {
      this.fetchConnections();
    },
    fetchItems(continue_loading) {
      // this.getScanProgress();
      this.fileDetails = null
      this.axios
          .post("getDocuments/", {
            ...this.options,
            search: this.searchText,
            disable_manuel_data: true,
          })
          .then(({data}) => {
            this.items = data.result;
            this.total = data.total;
            this.selectedItems = [];
            if (
                !(
                    this.scanRunning
                )
            ) {
              this.scanning = false;
              this.setScanStatus(0);
            }
          })
          .catch((e) => {
            this.handleError(e);
          })
          .finally(() => {
            this.loading = continue_loading;
          });
    },
    fetchFileData(id, name) {
      this.selectedFileName = name;
      this.fileDetails = null
      this.dialog = true
      this.axios
          .post("get_document_content/", {id: id})
          .then(({data}) => {
            this.fileDetails = data.result;
            this.scrollToTop();
          })
          .catch((e) => {
            this.handleError(e);
          });
    },
    fetchConnections() {
      this.scanning = true;
      this.fileDetails = null
      this.axios
          .post("refresh_connections/", {
            ...this.options,
            search: this.searchText,
          })
          .then(({data}) => {
            if (data.status) {
              this.fetchItems()
            }
            this.items = data.result;
            this.total = data.total;
          })
          .catch((e) => {
            this.scanning = false;
            this.handleError(e);
          })
          .finally(() => {
            this.loading = false;
          });
    },
    socketTest() {
      this.loading = true;
      this.axios
          .post("socketTest/", {text: "Test deneme 1,2,3..."})
          .catch((e) => {
            this.handleError(e);
          })
          .finally(() => {
            this.loading = false;
          });
    },
  },
  created() {
    this.getScanProgress();
  },
  watch: {
    scanRunning(newVal) {
      this.scanRunning = newVal;
      if (this.scanRunning) {
        this.scanning = true;
        this.loading = true;
      }
    },
    scanComplete() {
      this.getScanProgress();
      if (this.scanComplete) {
        if (this.getScanStatus.error) {
          this.handleError(this.getScanStatus.error);
        }
        this.fetchItems();
        this.loading = false;
        if (this.getScanStatus.finalStatus !== "") {
          this.snackbar = true;
          this.infoMessage.push(this.getScanStatus.finalStatus);
        }
      }
    },
  },
};
</script>
