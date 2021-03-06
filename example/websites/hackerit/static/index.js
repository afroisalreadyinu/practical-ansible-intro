angular.module('hackerit', [])
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
    $http.get("/link/").then(function(response) {
        self.links = response.data.links;
    });

    self.new_link = function() {
      $http({
        url: "/link/",
        method: "POST",
        data: JSON.stringify(self.new_link_data),
        headers: {'Content-Type': 'application/json'}
      }).then(function(response) {
        $http.get("/link/").then(function(response) {
          self.links = response.data.links;
        });
      });
    };

    self.upvote = function(link) {
      $http({
        url: "/vote/",
        method: "POST",
        data: JSON.stringify({link_id:link.link_id, upvote:true, downvote:false}),
        headers: {'Content-Type': 'application/json'}
      }).then(function(response) {
        link.upvoted = response.data.upvoted;
        link.downvoted = response.data.downvoted;
        link.points = response.data.points;
      });
    };

    self.downvote = function(link) {
      $http({
        url: "/vote/",
        method: "POST",
        data: JSON.stringify({link_id:link.link_id, downvote:true, upvote: false}),
        headers: {'Content-Type': 'application/json'}
      }).then(function(response) {
        link.upvoted = response.data.upvoted;
        link.downvoted = response.data.downvoted;
        link.points = response.data.points;
      });
    };
  }]);
