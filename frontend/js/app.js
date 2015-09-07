var app = angular.module('MyApp', [
    'ngResource',
    'ngMessages',
    'ngAnimate',
    'toastr',
    'ui.router',
    'appFilters',
    'ngMaterial',
    'satellizer'
]);

app.run(['$rootScope', '$state', '$stateParams',
    function($rootScope, $state, $stateParams){
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;
    }
])


app.config(function($stateProvider, $urlRouterProvider, $authProvider, toastrConfig) {
    angular.extend(toastrConfig, {
        'positionClass': 'toast-bottom-right',
    });

    $stateProvider
      .state('home', {
        url: '/',
        controller: 'HomeCtrl',
        templateUrl: 'partials/home.html'
      })
      .state('login', {
        url: '/login',
        templateUrl: 'partials/login.html',
        controller: 'LoginCtrl',
        resolve: {
          skipIfLoggedIn: skipIfLoggedIn
        }
      })
      .state('logout', {
        url: '/logout',
        template: null,
        controller: 'LogoutCtrl'
      })


      .state('user_list',  {
          url: '/user',
          templateUrl: 'partials/tool_authors.html',
          controller: 'UserListCtrl',
      })
      .state('user_detail', {
          url: '/user/:userId',
          templateUrl: 'partials/tool_author.html',
          controller: 'UserDetailCtrl',
      })
      .state('group_list',  {
          url: '/group',
          templateUrl: 'partials/groups.html',
          controller: 'GroupListCtrl',
      })
      .state('group_detail', {
          url: '/group/{groupId:[0-9]+}',
          templateUrl: 'partials/group.html',
          controller: 'GroupDetailCtrl',
      })
      .state('group_create', {
          url: '/group/new',
          templateUrl: 'partials/group_create.html',
          controller: 'GroupCreateCtrl',
          resolve: {
            loginRequired: loginRequired,
          },
      })


      .state('installable_detail', {
          url: '/installable/:installableId',
          templateUrl: 'partials/installable_detail.html',
          controller: 'InstallableDetailController',
      })
      .state('list_tools', {
          url: '/installables/tool',
          templateUrl: 'partials/installable_list.html',
          controller: 'InstallableListController',
      })
      .state('list_datatypes', {
          url: '/installables/datatype',
          templateUrl: 'partials/installable_list.html',
          controller: 'InstallableListController',
      })
      .state('list_packages', {
          url: '/installables/package',
          templateUrl: 'partials/installable_list.html',
          controller: 'InstallableListController',
      })
      .state('list_viz', {
          url: '/installables/viz',
          templateUrl: 'partials/installable_list.html',
          controller: 'InstallableListController',
      })
      .state('list_ie', {
          url: '/installables/gie',
          templateUrl: 'partials/installable_list.html',
          controller: 'InstallableListController',
      })

      .state('create_installable', {
          url: '/new',
          templateUrl: 'partials/create.html',
          controller: 'CreateCtrl',
          resolve: {
            loginRequired: loginRequired,
          },
      })



      .state('profile', {
        url: '/profile',
        templateUrl: 'partials/tool_author.html',
        controller: 'ProfileCtrl',
        resolve: {
          loginRequired: loginRequired
        }
      });

    $urlRouterProvider.otherwise('/');

    function skipIfLoggedIn($q, $auth) {
      var deferred = $q.defer();
      if ($auth.isAuthenticated()) {
        deferred.reject();
      } else {
        deferred.resolve();
      }
      return deferred.promise;
    }

    function loginRequired($q, $location, $auth) {
      var deferred = $q.defer();
      if ($auth.isAuthenticated()) {
        deferred.resolve();
      } else {
        $location.path('/login');
      }
      return deferred.promise;
    }

    $authProvider.github({
        clientId: '9ba85b7e5e5684e3fcd8',
    });
  });
