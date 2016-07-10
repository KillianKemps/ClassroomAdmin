// Avoid conflict with Jinja template
Vue.config.delimiters = ['${', '}'];

new Vue({
  el: '#app',
  data: {
    isLoading: false,
    coursesArray: []
  },
  methods: {
    add: function (event) {
      console.log('Adding course...' , event.target.dataset.index - 1);
      this.coursesArray.push(event.target.dataset.index - 1);
    },
    create: function (event) {
      console.log('Sending request...');
      this.isLoading = true;

      // Creating form data for sending courses
      var formData = new FormData();
      formData.append('courses', this.coursesArray);
      this.coursesArray = [];

      this.$http.post('/create', formData)
      .then(function(response) {
        console.log('Request ok:', response);
          // success callback
        this.isLoading = false;
      }, function(response) {
        console.log('Got an error:', response);
          // error callback
        this.isLoading = false;
      });
    }
  }
})
