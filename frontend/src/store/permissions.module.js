const state = {
  permissions: [
    {
      id: 1,
      name: "Users",
      slug: "users",
      children: [
        { id: 2, name: "Get Users", slug: "getUsers" },
        { id: 3, name: "Get User", slug: "getUser" },
        { id: 4, name: "Create User", slug: "createUser" },
        { id: 5, name: "Edit User", slug: "editUser" },
        { id: 6, name: "Delete User", slug: "deleteUser" },
      ],
    },
  ],
};

const getters = {
  getPermissionByName: (state) => (name) => {
    return state.permissions.filter((v) => v.slug === name);
  },
};

const actions = {};

const mutations = {};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
};
