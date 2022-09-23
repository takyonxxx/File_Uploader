<template>
  <v-menu v-model="menu" offset-y right>
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        left
        text
        plain
        large
        v-bind="attrs"
        v-on="on"
        class="text-lowercase"
      >
        <v-icon left>mdi-account</v-icon>
        {{ user.first_name + " " + user.last_name }}
      </v-btn>
    </template>
    <v-card>
      <v-list actionable>
        <v-list-item color="primary">
          <v-list-item-avatar>
            <v-icon> mdi-account-circle </v-icon>
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title>
              {{ user.first_name + " " + user.last_name }}</v-list-item-title
            >
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <v-card-actions>
        <v-btn block color="error" small @click="logOut">Logout</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  name: "bUserMenu",
  data: () => ({
    menu: false,
  }),
  computed: {
    user() {
      return this.$store.state.auth.user;
    },
  },
  methods: {
    logOut() {
      this.$store.commit("auth/purgeAuth");
    },
  },
};
</script>

<style scoped></style>
