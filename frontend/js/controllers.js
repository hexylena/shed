var app = angular.module('MyApp');

app.controller('HomeCtrl', function($scope) {
});

app.controller('LoginCtrl', function($scope, $location, $auth, toastr) {
    $scope.login = function() {
        $auth.login($scope.user).then(function() {
            toastr.success('You have successfully signed in');
            $location.path('/queue');
        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
        });
    };
    $scope.authenticate = function(provider) {
        $auth.authenticate(provider).then(function() {
            toastr.success('You have successfully signed in with ' + provider);
            $location.path('/queue');
        })
        .catch(function(response) {
            toastr.error(response.data.message);
        });
    };
});

app.controller('LogoutCtrl', function($location, $auth, toastr) {
    if (!$auth.isAuthenticated()) { return; }

    $auth.logout().then(function() {
        toastr.info('You have been logged out');
        $location.path('/');
    });
});

app.controller('CreateCtrl', function($scope, $location, $auth, toastr, Toolshed) {
    $scope.repo_types = [
        {value: 'tool', label: 'Tool'},
        {value: 'package', label: 'Packge (Repository Dependency)'},
        {value: 'datatype', label: 'Datatype'},
        {value: 'viz', label: 'Visualization'},
        {value: 'gie', label: 'Galaxy Interactive Environment'},
    ];
    $scope.clearInstallable = {
        name: null,
        repository_type: 'tool',
        remote_repository_url: null,
        homepage_url: null,
        description: null,
        synopsis: null,
        //tags: [],
    };

    // Clone the empty installable
    $scope.installable = JSON.parse(JSON.stringify($scope.clearInstallable));
    $scope.canSubmit = true;

    $scope.submit = function(){
        $scope.canSubmit = false;

        Toolshed.createInstallable($scope.installable).then(function(response) {
            var created_object = response.data;
            var redirect_location = '/installables/' + created_object.id;
            console.log(redirect_location);
            //$location.path(redirect_location);
            toastr.success("Created repository", "Success!");
            $scope.canSubmit = true;
        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
            $scope.canSubmit = true;
        });
    }

});

app.controller('InstallableListController', function($scope, $location, $auth, Toolshed, toastr){
    $scope.installable_type = $location.path().split('/')[2];
    $scope.page = 0;
    $scope.pageCount = 1;

    $scope.cachedPages = {};

    $scope.fetchData = function(type, page){
        if(page in $scope.cachedPages){
            return;
        }
        Toolshed.getInstallables(type, page + 1).then(function(response) {
            $scope.cachedPages[$scope.page] = response.data.objects;
            $scope.numResults = response.data.num_results;
            $scope.pageCount = response.data.total_pages;

        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
        });
    }

    // http://stackoverflow.com/questions/11873570/angularjs-for-loop-with-numbers-ranges
    $scope.range = function(min, max, step){
        min = min || 0;
        max = max || 0;
        if(max < min){
            max = min;
        }
        step = step || 1;
        var input = [];
        for (var i = min; i <= max; i += step) input.push(i);
        return input;
    };

    $scope.$watch(
        "page",
        function(new_value) {
            $scope.fetchData($scope.installable_type, new_value);
        }
    );

    // Don't know if this is needed. It doesn't seem to be but ... ? Don't want people to see just an empty page.
    //$scope.fetchData($scope.installable_type, $scope.page);
});

app.controller('InstallableDetailController', function($scope, $location, $auth, Toolshed, toastr, $stateParams){
    $scope.page = 1;

    Toolshed.getInstallable($stateParams.installableId).then(function(response) {
        $scope.installable = response.data;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });

});



app.controller('NavbarCtrl', function($scope, $auth, $mdSidenav) {
    $scope.isAuthenticated = function() {
        return $auth.isAuthenticated();
    };

    if($auth.getPayload() !== undefined){
        $scope.username = $auth.getPayload().username;
    }

    $scope.toggleSidenav = function(menuId) {
        $mdSidenav(menuId).toggle();
    };

});

app.controller('UserListCtrl', function($scope, Toolshed) {
    Toolshed.getUsers().then(function(response) {
        $scope.users = response.data.objects;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });
})

app.controller('UserDetailCtrl', function($scope, Toolshed, $stateParams) {
    Toolshed.getUser($stateParams.userId).then(function(response) {
        $scope.user = response.data;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });
})

app.controller('GroupListCtrl', function($scope, Toolshed, toastr) {
    Toolshed.getGroups().then(function(response) {
        $scope.groups = response.data.objects;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });
})

app.controller('GroupDetailCtrl', function($scope, Toolshed, $stateParams, toastr) {
    Toolshed.getGroup($stateParams.groupId).then(function(response) {
        $scope.group = response.data;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });
})

app.controller('GroupCreateCtrl', function($scope, Toolshed, $stateParams, toastr, $location) {
    $scope.group = {
        display_name: null,
        description: null,
        website: null,
        gpg_pubkey_id: null,
    }

    $scope.submit = function(){
        console.log("Submitting group")
        console.log($scope.group);
        Toolshed.createGroup($scope.group).then(function(response) {
            var redirect_location = '/group/' + response.data.id;
            console.log(redirect_location);
            $location.path(redirect_location);
            toastr.success("Created Group " + response.data.display_name, "Success!");
        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
        });
    }


})

app.controller('ProfileCtrl', function($scope, $auth, toastr, Toolshed) {
    console.log($auth.getPayload());
    if($auth.getPayload() !== undefined){
        $scope.userId = $auth.getPayload().user_id;
    }

    Toolshed.getUser($scope.userId).then(function(response) {
        $scope.user = response.data;
    })
    .catch(function(response) {
        toastr.error(response.data.message, response.status);
    });
});

app.controller('SignupCtrl', function($scope, $location, $auth, toastr) {
    $scope.signup = function() {
        $auth.signup($scope.user).then(function() {
            $location.path('/queue');
            toastr.info('You have successfully created a new account');
        })
        .catch(function(response) {
            toastr.error(response.data.message);
        });
    };
});
