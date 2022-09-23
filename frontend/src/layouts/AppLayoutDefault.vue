<template>
  <v-app>
    <v-main>
      <!-- Provides the application the proper gutter -->
      <v-container fluid class="fill-height blue-grey lighten-5">
        <v-fade-transition mode="out-in">
          <router-view> </router-view>
        </v-fade-transition>
      </v-container>
    </v-main>
    <dm-toast></dm-toast>
  </v-app>
</template>

<script>
import DmToast from "@/components/common/bToast";
export default {
  name: "AppLayoutDefault",
  components: { DmToast },
};
</script>

<style scoped></style>
