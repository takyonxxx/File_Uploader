<template>
  <v-app>
    <b-aside></b-aside>
    <b-header></b-header>
    <v-main class="grey lighten-4">
      <v-container fluid class="pa-5">
        <v-card outlined>
          <v-card-text>
            <v-slide-x-transition mode="out-in">
              <router-view :key="pageCounter"></router-view>
            </v-slide-x-transition>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
    <v-footer app class="grey lighten-2 d-flex justify-center">
      {{ new Date().getFullYear() }} — <strong>DEMO PROJECT</strong>
    </v-footer>
    <dm-toast></dm-toast>
  </v-app>
</template>

<script>
import BAside from "@/components/layout/aside/bAside";
import BHeader from "@/components/layout/header/bHeader";
import DmToast from "@/components/common/bToast";

export default {
  name: "AppLayoutMain",
  components: { DmToast, BHeader, BAside },
  computed: {
    pageCounter() {
      return this.$store.state.pageCounter;
    },
  },
};
</script>
