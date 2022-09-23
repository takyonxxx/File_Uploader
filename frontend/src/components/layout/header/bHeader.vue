<template>
  <v-app-bar app dark color="blue darken-1" flat>
    <v-app-bar-nav-icon
      @click="$store.commit('toggleMenu')"
    ></v-app-bar-nav-icon>
    <v-spacer />
    <b-user-menu></b-user-menu>
  </v-app-bar>
</template>

<script>
import BUserMenu from "@/components/layout/header/bUserMenu";
export default {
  name: "bHeader",
  components: { BUserMenu },
};
</script>
