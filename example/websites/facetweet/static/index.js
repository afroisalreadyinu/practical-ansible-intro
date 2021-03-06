angular.module('facetweet', [])
  .controller(
    'RootCtrl', ["$http", "$window", function($http, $window) {
      var self = this;
      self.logged_in = $window.user_email != null;

      self.signup = function() {
        $http({
          url: "/signup/",
          method: "POST",
          data: JSON.stringify(self.signup_data),
          headers: {'Content-Type': 'application/json'}
        }).then(function(response) {
          self.logged_in = true;
          $window.user_email = response.email;
        });
      };

      self.signin = function() {
        $http({
          url: "/login/",
          method: "POST",
          data: JSON.stringify(self.signin_data),
          headers: {'Content-Type': 'application/json'}
        }).then(function(response) {
          self.logged_in = true;
          $window.user_email = response.email;
        });
      };

    }])
  .controller('MainCtrl', ["$http", function($http) {
    var self = this;
    $http.get("/posts/").then(function(response) {
      self.posts = response.data.posts;
    });
    $http.get("/friends/").then(function(response) {
      self.friends = response.data.friends;
    });
    self.new_post = function() {
      $http({
        url: "/post/",
        method: "POST",
        data: JSON.stringify({"text":self.new_post_text}),
        headers: {'Content-Type': 'application/json'}
      }).then(function(response) {
        self.new_post_text = "";
        $http.get("/posts/").then(function(response) {
          self.posts = response.data.posts;
        });
      });
    };

    self.befriend = function() {
      $http({
        url: "/befriend/",
        method: "POST",
        data: JSON.stringify({"email": self.new_friend_email}),
        headers: {'Content-Type': 'application/json'}
      }).then(function(response) {
        self.new_friend_email = "";
        $http.get("/friends/").then(function(response) {
          self.friends = response.data.friends;
        });
        $http.get("/posts/").then(function(response) {
          self.posts = response.data.posts;
        });
      });
    };
  }]);
