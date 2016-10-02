// Avoid conflict with Jinja template
Vue.config.delimiters = ['${', '}'];

new Vue({
  el: '#app',
  data: {
    isLoading: false,
    isLoadingEmails: false,
    checkboxes: document.querySelectorAll('input[class=course]'),
    coursesArray: [],
    requestSucceeded: false,
    requestFailed: false,
    emailRequestSucceeded: false,
    emailRequestFailed: false,
    errorMessage: '',
    emailErrorMessage: ''
  },
  methods: {
    setAllCheckboxes: function(event) {
      console.log('Changing all..');
      for (i = 0; i < this.checkboxes.length; i++) {
        this.checkboxes[i].checked = event.target.checked;
        this.add({target: this.checkboxes[i]});
      }
    },
    add: function (event) {
      if (event.target.checked) {
        console.log('Adding course...' , event.target.dataset.index - 1);
        this.coursesArray.push(event.target.dataset.index - 1);
      }
      else {
        console.log('Removing course...' , event.target.dataset.index - 1);
        this.coursesArray.splice(this.coursesArray.indexOf(event.target.dataset.index - 1), 1);
      }
    },
    create: function (event) {
      if (this.coursesArray.length > 0) {
        console.log('Sending request...');
        this.requestFailed = false;
        this.requestSucceeded = false;
        this.isLoading = true;

        // Creating form data for sending courses
        var formData = new FormData();
        formData.append('courses', this.coursesArray);
        this.coursesArray = [];

        this.$http.post('/create', formData)
        .then(function(response) {
          console.log('Request ok:', response);
          // success callback
          if (response.status === 202) {
            this.poll();
          }
          else {
            this.isLoading = false;
            this.requestSucceeded = true;
          }
        }, function(response) {
          console.log('Got an error:', response);
          // error callback
          this.errorMessage = response.data;
          this.requestFailed = true;
          this.isLoading = false;
        });
      }
    },
    send: function (event) {
      if (this.coursesArray.length > 0) {
        console.log('Requesting to send email(s)...');
        this.emailrequestFailed = false;
        this.emailrequestSucceeded = false;
        this.isLoadingEmails = true;

        // Creating form data for sending courses
        var formData = new FormData();
        formData.append('courses', this.coursesArray);
        this.coursesArray = [];

        this.$http.post('/manually-send-email', formData)
        .then(function(response) {
          console.log('Request ok:', response);
          // success callback
          if (response.status === 202) {
            this.pollEmails();
          }
          else {
            this.isLoadingEmails = false;
            this.emailRequestSucceeded = true;
          }
        }, function(response) {
          console.log('Got an error:', response);
          // error callback
          this.emailErrorMessage = response.data;
          this.emailrequestFailed = true;
          this.isLoadingEmails = false;
        });
      }
    },
    poll: function (event) {
      var textarea = document.createElement('textarea');
      function unescapeHTML(html) {
          textarea.innerHTML = html;
          return textarea.textContent;
      }

      this.$http.get('/poll', {timeout: 5000})
      .then(function(response) {
        console.log('Poll request ok:', response);
        // success callback
        if (response.status === 202) {
          window.setTimeout(this.poll, 5000);
        }
        else {
          this.isLoading = false;
          this.requestSucceeded = true;
        }
      }, function(response) {
        console.log('Poll: Got an error:', response);
        // error callback
        this.errorMessage = unescapeHTML(response.data);
        this.requestFailed = true;
        this.isLoading = false;
      });
    },
    pollEmails: function (event) {
      var textarea = document.createElement('textarea');
      function unescapeHTML(html) {
          textarea.innerHTML = html;
          return textarea.textContent;
      }

      this.$http.get('/poll-emails', {timeout: 5000})
      .then(function(response) {
        console.log('Poll emails request ok:', response);
        // success callback
        if (response.status === 202) {
          window.setTimeout(this.pollEmails, 5000);
        }
        else {
          this.isLoadingEmails = false;
          this.emailRequestSucceeded = true;
        }
      }, function(response) {
        console.log('Poll-emails: Got an error:', response);
        // error callback
        this.emailErrorMessage = unescapeHTML(response.data);
        this.emailRequestFailed = true;
        this.isLoadingEmails = false;
      });
    }
  }
})
