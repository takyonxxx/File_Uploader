import debounce from "lodash/debounce";
export const crudMixin = {
  data: () => ({
    options: {},
    items: [],
    currentItem: {},
    editedIndex: -1,
    searchText: "",
    searchDate: [],
    menu: false,
    total: null,
    loading: true,
    dialog: false,
    dialogKey: 0,
  }),
  watch: {
    options: {
      handler() {
        this.fetchItems();
      },
    },
    searchText: {
      handler(val) {
        if ((val && val.length > 2) || val.length === 0) {
          this.onSearch();
        }
      },
    },
  },
  methods: {
    addItem() {
      this.currentItem = { ...this.defaultItem } || {};
      this.editedIndex = -1;
      this.dialogKey++;
      this.dialog = true;
    },
    editItem(item) {
      this.currentItem = { ...item };
      this.editedIndex = this.items.indexOf(item);
      this.dialogKey++;
      this.dialog = true;
    },
    closeDialog() {
      this.dialog = false;
      this.editedIndex = -1;
    },
    onSearch: debounce(function () {
      this.options.page = 1;
      this.fetchItems();
    }, 500),
    onDate() {
      if (this.searchDate !== null && this.searchDate.length === 1) {
        this.searchDate.push(this.searchDate[0]);
      }
      this.$refs.menu.save(this.searchDate);
      this.onSearch();
    },
    onClear() {
      this.searchDate = [];
      this.onSearch();
    },
    deleteRecord(method, id) {
      this.axios
        .post("delete" + method + "/", { id: id })
        .then(({ data }) => {
          this.showMessage("Deleted Successfully");
          this.fetchItems();
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    async confirmDelete(method, id, name) {
      if (
        await this.$refs.confirm.open(
          "Are you sure you want to <b>delete</b> " + name
        )
      ) {
        this.deleteRecord(method, id);
      }
    },
  },
};
