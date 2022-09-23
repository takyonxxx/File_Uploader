import store from "@/store";
import { getToken } from "@/services/jwt.service";
import ReconnectingWebSocket from "reconnecting-websocket";
import { storeBridge } from "@/services/socket.service";

let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let path = window.location.host;

let room_code = null;

function set_room_code(new_code) {
  room_code = new_code;
}
let urlProvider = async () => {
  const token = await getToken();
  return ws_scheme + "://" + path + "/ws/notifications" + "/?token=" + token;
};

const socket = new ReconnectingWebSocket(urlProvider, [], {
  startClosed: true,
  minReconnectionDelay: 1000 + Math.random() * 500,
  maxRetries: 5,
});

socket.addEventListener("open", () => {
  // store.commit("socket/SET_CONNECTION_STATUS", true);
  console.log("open");
});
socket.addEventListener("message", (message) => {
  storeBridge(JSON.parse(message.data));
  let details = JSON.parse(message.data).details || {};
  if (details.hasOwnProperty("error")) {
    // TODO: show user an error if websocket returns error as a progress
    console.log(details.error);
  }
});
socket.addEventListener("close", (message) => {
  //store.commit("socket/SET_CONNECTION_STATUS", false);
  console.log(message);
});
socket.addEventListener("error", (error) => {
  console.log(error);
});

export { socket, set_room_code };
