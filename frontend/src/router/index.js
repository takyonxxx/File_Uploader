import Vue from "vue";
import VueRouter from "vue-router";
import store from "@/store";
import $axios from "@/plugins/axios";
import isEmpty from "lodash/isEmpty";
import {socket} from "@/plugins/webSocket";

Vue.use(VueRouter);

const DEFAULT_TITLE = "DEMO PROJECT";

const routes = [
    {
        path: "/login",
        name: "login",
        meta: {
            title: "Login",
        },
        component: () => import("@/views/auth/Login.vue"),
    },
    {
        path: "/register",
        name: "register",
        meta: {
            title: "Register",
        },
        component: () => import("@/views/auth/Register.vue"),
    },
    {
        path: "/scan",
        name: "scan",
        meta: {
            title: "Scan Repositories",
            layout: "AppLayoutMain",
        },
        component: () => import("@/views/ScanRepositories.vue"),
    },
    {
        path: "/repositories",
        name: "repositories",
        meta: {
            title: "Repositories",
            layout: "AppLayoutMain",
            requiredPermission: "readRepository",
        },
        component: () => import("@/views/Repositories.vue"),
    },

];

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
});

router.beforeEach((to, from, next) => {
    // redirect to login page if not logged in and trying to access a restricted page
    const publicPages = ["/login", "/register"];
    const authRequired = !publicPages.includes(to.path);
    const loggedIn = localStorage.getItem("access");
    const noUser = isEmpty(store.state.auth.user);
    const isAuthenticated = store.state.auth.isAuthenticated;
    if (authRequired) {
        if (!loggedIn) {
            if (to.path !== "/login" && from.path !== "/login") {
                return next("/login");
            }
        }
        if (!isAuthenticated) {
            $axios
                .post("currentUser/")
                .then(({data}) => {
                    store.commit("auth/setAuth", data);
                    socket.reconnect();
                    return next();
                })
                .catch(() => {
                    store.commit("auth/purgeAuth");
                });
        }
        next();
    } else next();
});
router.afterEach((to) => {
    Vue.nextTick(() => {
        document.title = to.meta.title + " - DEMO" || DEFAULT_TITLE;
    });
});

export default router;
