<template>
  <div id="app">
    <h1>Fullstack Project - Frontend</h1>
    <nav>
      <router-link to="/">UI</router-link> |
    </nav>
    <router-view />
  </div>
</template>


<script>
export default {
  name: "App",
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 60px;
}

nav {
  margin: 20px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
