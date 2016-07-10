// Avoid conflict with Jinja template
Vue.config.delimiters = ['${', '}'];

new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue.js!'
  },
  methods: {
    create: function (event) {
      this.$http.get('/create').then(function(response) {
        console.log('Request ok:', response);
          // success callback
      }, function(response) {
        console.log('Got an error:', response);
          // error callback
      });
    }
  }
})
