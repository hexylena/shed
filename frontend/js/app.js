var app = angular.module('MyApp', [
    'ngResource',
    'ngMessages',
    'ngAnimate',
    'toastr',
    'ui.router',
    'appFilters',
    'ngMaterial',
    'xeditable',
    'ngFileUpload',
    'hc.marked',
    'ui.gravatar',
    'picardy.fontawesome',
    'angularMoment',
    'satellizer'
]);

app.run(['$rootScope', '$state', '$stateParams', 'editableOptions', 'editableThemes',
    function($rootScope, $state, $stateParams, editableThemes, editableOptions){
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;
        // TODO: api.toolshed.galaxyproject.org ?
        $rootScope.host = 'gx.hx42.org';
        $rootScope.port = '8000'
        $rootScope._backendUrl = 'http://' + $rootScope.host + ':' + $rootScope.port + '/api';

        //editableThemes['angular-material'] = {
            //formTpl:      '<form class="editable-wrap"></form>',
            //noformTpl:    '<span class="editable-wrap"></span>',
            //controlsTpl:  '<md-input-container class="editable-controls" ng-class="{\'md-input-invalid\': $error}"></md-input-container>',
            //inputTpl:     '',
            //errorTpl:     '<div ng-messages="{message: $error}"><div class="editable-error" ng-message="message">{{$error}}</div></div>',
            //buttonsTpl:   '<span class="editable-buttons"></span>',
            //submitTpl:    '<md-button type="submit" class="md-primary">save</md-button>',
            //cancelTpl:    '<md-button type="button" class="md-warn" ng-click="$form.$cancel()">cancel</md-button>'
        //};

        //editableOptions.theme = 'angular-material';
    }
])


app.config(function($stateProvider, $urlRouterProvider, $authProvider, toastrConfig, $httpProvider) {
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


      // Users
      .state('user_list',  {
          url: '/user',
          templateUrl: 'partials/user_list.html',
          controller: 'UserListCtrl',
      })
      .state('user_detail', {
          url: '/user/{userId:[0-9]+}',
          templateUrl: 'partials/user_detail.html',
          controller: 'UserDetailCtrl',
      })
      // Groups
      .state('group_list',  {
          url: '/group',
          templateUrl: 'partials/group_list.html',
          controller: 'GroupListCtrl',
      })
      .state('group_detail', {
          url: '/group/{groupId:[0-9]+}',
          templateUrl: 'partials/group_detail.html',
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
      // Tags
      .state('tag_list',  {
          url: '/tag',
          templateUrl: 'partials/tag_list.html',
          controller: 'TagListCtrl',
      })
      .state('tag_detail', {
          url: '/tag/{tagId:[0-9]+}',
          templateUrl: 'partials/tag_detail.html',
          controller: 'TagDetailCtrl',
      })


      .state('search', {
          url: '/search/:searchTerm',
          templateUrl: 'partials/search.html',
          controller: 'SearchCtrl',
      })


      // Repositories
      .state('installable_detail', {
          url: '/installable/{installableId:[0-9]+}',
          templateUrl: 'partials/installable_detail.html',
          controller: 'InstallableDetailController',
      })
      .state('installable_detail.revision_detail', {
          url: '/installable/{installableId:[0-9]+}/{revisionId:[0-9]+}',
          templateUrl: 'partials/revision_detail.html',
          controller: 'RevisionDetailController',
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
      .state('create_suite', {
          url: '/new_suite',
          templateUrl: 'partials/create_suite.html',
          controller: 'CreateSuiteCtrl',
          resolve: {
            loginRequired: loginRequired,
          },
      })


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
        url: '/auth/github',
        redirectUri: 'http://gx.hx42.org:8000/auth/github',
        clientId: '9ba85b7e5e5684e3fcd8',
    });
  });
