import { DateTime } from "luxon";
import cloneDeep from "lodash/cloneDeep";

export const helpers = {
  data: () => ({
    loading: true,
    scanRunning: false,
    fileConnectorRunning: false,
    statusMessage: "",
    connectorTypes: {
      fileConnectorRunning: "• File",
    },
  }),

  methods: {
    getRunningScanDetails(connectorType) {
      let apiurl = "getCacheControllerById/";
      this.axios
        .post(apiurl, { key: connectorType })
        .then(({ data }) => {
          if (Object.keys(this.connectorTypes).includes(connectorType)) {
            this[connectorType] = data.status;
            let message = data.status
              ? this.connectorTypes[connectorType] +
                " repository is currently being scanned.<br>"
              : "";
            this.statusMessage = this.statusMessage + message;
          }
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    getScanProgress() {
      let apiurl = "getCacheControllerById/";
      this.axios
        .post(apiurl, { key: "scan_running" })
        .then(({ data }) => {
          if (data.scan_running) {
            this.scanRunning = true;
            let message = "Please wait for the scanning to finish first.";
            this.getRunningScanDetails("fileConnectorRunning");
            this.statusMessage = this.statusMessage + message;
            this.showMessage(this.statusMessage, 4);
            this.statusMessage = "";
            setTimeout(this.getScanProgress, 5000);
          } else {
            this.scanRunning = false;
          }
        })
        .catch((e) => {
          this.handleError(e);
        });
    },
    formatDateTime(dateTime, format) {
      return this.$luxon
        .fromISO(dateTime)
        .toFormat(format ? format : "dd/LL/yyyy HH:mm");
    },
    createdDate(date) {
      const d = this.$luxon.fromISO(date);
      if (DateTime.now().hasSame(d, "year")) {
        if (DateTime.now().hasSame(d, "day")) {
          return d.toFormat("HH:mm");
        } else {
          return d.toFormat("d LLL");
        }
      } else return d.toFormat("d LLL yyyy");
    },
    formatSize(Num = 0, dec = 2) {
      if (Num === null) {
        return;
      }
      if (Num < 1000) return Num + " Bytes";
      Num = ("0".repeat(((Num += "").length * 2) % 3) + Num).match(/.{3}/g);
      return (
        Number(Num[0]) +
        "." +
        Num[1].substring(0, dec) +
        " " +
        "  kMGTPEZY"[Num.length] +
        "B"
      );
    },
    shorten(str, count) {
      if (str.length > count + 3) return str.substr(0, count) + "...";
      else return str;
    },
    showMessage(msg, type) {
      if (type !== undefined) {
        this.$toast.setMessage(msg, type);
      } else {
        this.$toast.setMessage(msg, 2);
      }
    },
    handleError(error) {
      let status = null;
      this.loading = false;
      let msg;
      let r;
      if (error.data) {
        r = error.data;
      } else if (error.response) {
        status = error.response.status;
        if (error.response.data) {
          r = error.response.data;
        }
      } else {
        r = error;
      }

      if (r.hasOwnProperty("non_field_errors")) {
        msg = r.non_field_errors[0];
      } else if (r.hasOwnProperty("detail")) {
        msg = r.detail;
      } else {
        if (typeof r === "object") {
          const item = Object.entries(r)[0];
          // console.log(item);
          msg = `"${item[0]}" : ${item[1][0]}`;
        } else {
          msg = r;
        }
      }

      this.showMessage(msg, 1);
    },
    deepCopy(obj) {
      return cloneDeep(obj);
    },
    defined(obj) {
      return !(obj === undefined || obj === null);
    },
  },
};
