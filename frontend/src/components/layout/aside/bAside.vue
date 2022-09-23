<template>
  <v-navigation-drawer
      class="grey lighten-3"
      app
      permanent
      :mini-variant="menu"
      mini-variant-width="72"
  >
    <div class="blue">
      <v-card-text class="text-center">
        <img
            height="60"
            width="180"
            :src="require(`@/assets/logo.png`)"
            alt="DEMO"
        />
      </v-card-text>
    </div>

    <v-list dense nav>
      <template v-for="item in menuItems">
        <v-list-item
            :key="item.title"
            v-if="item.url"
            link
            dense
            :to="item.url ? item.url : null"
            :disabled="!item.url"
            :title="item.title"
            @click.native="increaseCounter(item.url)"
        >
          <v-list-item-icon class="mr-3">
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <!--        <v-list-group v-else :key="item.title" group="/settings/*">-->
        <v-list-group
            v-else
            :key="item.title"
            :group="`/${item.title.toLowerCase()}/*`"
        >
          <template v-slot:activator>
            <v-list-item-icon class="mr-3">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{
                item.title.replace("-", " ")
              }}
            </v-list-item-title>
          </template>
          <v-list-item
              v-for="subItem in item.subItems"
              :key="subItem.title"
              link
              :title="subItem.title"
              :to="subItem.url"
          >
            <v-list-item-icon class="mx-3">
              <v-icon>{{ subItem.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ subItem.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import {mapState} from "vuex";
import store from "@/store";

export default {
  name: "bAside",
  data: () => ({
    menuItems: [
      {
        title: "Scan Repository",
        icon: "mdi-cube-scan",
        url: "/scan",
      },
      {
        title: "Repositories",
        icon: "mdi-source-repository-multiple",
        url: "/repositories",
      },
    ],
  }),
  computed: {
    ...mapState({
      menu: "menu",
    }),
  },
  methods: {
    increaseCounter(url) {
      store.commit("setPageCounter");
    },
  },
};
</script>
