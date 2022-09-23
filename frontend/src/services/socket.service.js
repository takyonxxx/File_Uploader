import store from "@/store";

const storeBridge = (message) => {
  let finalStatus = message.finalStatus || "";
  let details = message.details || {};
  let text = message.text || "";
  let percentage = parseFloat(details.progress_bar_percentage || "NaN") || 0;
  let error = details.error || "";
  let fileName = details.filename || "";
  let repository_name = details.file_repo || "";
  let count_status =
    details.current_file && details.total_files
      ? `[${details.current_file}/${details.total_files}]`
      : "";
  let scanStatus = {
    percentage,
    repository_name,
    fileName,
    text,
    count_status,
    error,
    finalStatus,
  };
  store.commit("setScanStatus", scanStatus);
};

export { storeBridge };
