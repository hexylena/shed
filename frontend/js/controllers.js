var app = angular.module('MyApp');

app.controller('HomeCtrl', function($scope) {
});

app.controller('LoginCtrl', function($scope, $location, $auth, toastr) {
    $scope.login = function() {
        $auth.login($scope.user).then(function() {
            toastr.success('You have successfully signed in');
            $location.path('/');
        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
        });
    };
    $scope.authenticate = function(provider) {
        $auth.authenticate(provider).then(function() {
            toastr.success('You have successfully signed in with ' + provider);
            $location.path('/');
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
        {value: 1, label: 'Tool'},
        {value: 0, label: 'Packge (Repository Dependency)'},
        {value: 2, label: 'Datatype'},
        {value: 4, label: 'Visualization'},
        {value: 5, label: 'Galaxy Interactive Environment'},
    ];
    $scope.installable = {
        name: "",
        repository_type: 'tool',
        remote_repository_url: "",
        homepage_url: "",
        description: "",
        synopsis: "",
    };

    $scope.submit = function(){
        Toolshed.Installable().save($scope.installable, function(response){
            toastr.success(response.data.message, response.status);
            console.log(response)
        }, function(response){
            toastr.error(response.statusText, response.status);
            console.log(response);
        });

        //Toolshed.createInstallable($scope.installable).then(function(response) {
            //var created_object = response.data;
            //var redirect_location = '/installable/' + created_object.id;
            //console.log(redirect_location);
            //$location.path(redirect_location);
            //toastr.success("Created repository", "Success!");
            //$scope.canSubmit = true;
        //})
        //.catch(function(response) {
            //$scope.canSubmit = true;
        //});
    }

});

app.controller('CreateSuiteCtrl', function($scope, $location, $auth, toastr, Toolshed) {
    $scope.clearSuite = {
        name: "",
        repository_type: 'suite',
        description: "",
        synopsis: "",
        repositories: [],
    };

    // Clone the empty installable
    $scope.suite = JSON.parse(JSON.stringify($scope.clearSuite));

    $scope.querySearch = function(searchText) {
        if(searchText.length > 3){
            console.log(searchText);
            Toolshed.searchInstallables(searchText).then(function(response){
                console.log(response.data);
            }).catch(function(response) {
                toastr.error(response.data.message, response.status);
            });

            return [
                {name: 'bob', version: '1.0.0'}
            ]
        }
    }

    $scope.submit = function(){
        Toolshed.createSuite($scope.suite).then(function(response) {
            var redirect_location = '/installables/' + created_object.id;
            console.log(redirect_location);
            toastr.success("Created Suite", "Success!");
        })
        .catch(function(response) {
            toastr.error(response.data.message, response.status);
        });
    }

});

app.controller('InstallableListController', function($scope, $location, $auth, Toolshed, toastr){
    $scope.installable_type = $location.path().split('/')[2];
    $scope.installable_numeric_type = {
        'package': 0,
        'tool': 1,
        'datatype': 2,
        'suite': 3,
        'viz': 4,
        'gie': 5,
    }[$scope.installable_type]

    $scope.page = 0;
    $scope.pageCount = 1;

    $scope.cachedPages = {};


    $scope.fetchData = function(type, page){
        if(page in $scope.cachedPages){
            return;
        }

        Toolshed.Installable().query({
            page: page + 1,
            repository_type: type,
        }).$promise.then(function(response){
            $scope.cachedPages[$scope.page] = response.results;
            $scope.numResults = response.count;
            $scope.pageCount = Math.ceil(response.count / 20);
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
            $scope.fetchData($scope.installable_numeric_type, new_value);
        }
    );

    // Don't know if this is needed. It doesn't seem to be but ... ? Don't want people to see just an empty page.
    //$scope.fetchData($scope.installable_type, $scope.page);
});

app.controller('InstallableDetailController', function($scope, $location, $auth, Toolshed, toastr, $stateParams, $mdDialog, Upload){
    $scope.page = 1;

    $scope.saveForm = function(){
        // Persist updates to the backend
        var installable = Toolshed.Installable().update({
            installableId:$stateParams.installableId
        }, $scope.installable);
    }

    Toolshed.Installable().get({
        installableId: $stateParams.installableId
    }).$promise.then(function(response){
        $scope.installable = response;

        if($scope.installable.revision_set.length > 0){
            $scope.selectedRevision = $scope.installable.revision_set[$scope.installable.revision_set.length - 1].id
        }
    });

    $scope.newRevision = function(ev){
        $mdDialog.show({
            controller: DialogController,
            templateUrl: '/partials/dialog1.tmpl.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            clickOutsideToClose:true
        })
        .then(
            function(answer) {
                Upload.upload({
                    // Special URL for a special purpose
                    url: '/api/create_revision',
                    fields: {
                        'sig': answer.sig,
                        'installable_id': $scope.installable.id,
                        'commit': answer.message,
                    },
                    file: answer.file,
                }).progress(function (evt) {
                    var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                    console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
                }).success(function (data, status, headers, config) {
                    toastr.success(data, "Success");
                    $scope.freshen();
                }).error(function (data, status, headers, config) {
                    toastr.error(data, status);
                })
            },
            function() {
            }
        );
    };

    $scope.$watch(
        "selectedRevision",
        function(new_value) {
            if($scope.installable !== undefined && $scope.installable.revision_set !== undefined){
                for(var rev_idx in $scope.installable.revision_set){
                    if($scope.installable.revision_set[rev_idx].id == new_value){
                        $scope.selectedRevisionData = $scope.installable.revision_set[rev_idx];
                        $scope.revisionDownloadUrl = '/uploads/' + $scope.installable.name + '-' + $scope.selectedRevisionData.version + '.tar.gz';
                        break
                    }
                }
            }
        }
    );
});

function DialogController($scope, $mdDialog) {
    $scope.hide = function() {
        $mdDialog.hide();
    };
    $scope.cancel = function() {
        $mdDialog.cancel();
    };
    $scope.answer = function(answer) {
        $mdDialog.hide(answer);
    };
}

app.controller('NavbarCtrl', function($scope, $auth, $mdSidenav) {
    $scope.isAuthenticated = function() {
        return $auth.isAuthenticated();
    };

    if($auth.getPayload() !== undefined){
        $scope.username = $auth.getPayload().username;
        $scope.userid = $auth.getPayload().user_id;
    }

    $scope.toggleSidenav = function(menuId) {
        $mdSidenav(menuId).toggle();
    };

});

app.controller('UserListCtrl', function($scope, Toolshed) {
    // TODO: Pagination
    $scope.users = Toolshed.User().query({pageIndex: 0});
})

app.controller('UserDetailCtrl', function($scope, Toolshed, $stateParams) {
    $scope.user = Toolshed.User().get({userId: $stateParams.userId});
})

app.controller('TagListCtrl', function($scope, Toolshed) {
    Toolshed.Tag().query({page: 1}).$promise.then(function(response){
        $scope.tags = response.results;
        $scope.numResults = response.count;
        $scope.pageCount = Math.ceil(response.count / 20);
    });

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
})

app.controller('TagDetailCtrl', function($scope, Toolshed, $stateParams) {
    $scope.tag = Toolshed.Tag().get({tagId: $stateParams.tagId});
})

app.controller('SearchCtrl', function($scope, $timeout, $state, Toolshed, $stateParams) {
    $scope.searchTerm = $stateParams.searchTerm

    // http://stackoverflow.com/questions/15304562/how-to-put-a-delay-on-angularjs-instant-search
    var filterTextTimeout;
    $scope.searching = true;

    $scope.$watch(
        "searchTerm",
        function(new_value) {

            if(new_value.length < 4){
                return;
            }

            // If there's an existing timeout, cancel it.
            if (filterTextTimeout) {
                $timeout.cancel(filterTextTimeout);
            }
            filterTextTimeout = $timeout(function() {
                // Update URL bar so searches can easily be shared
                $state.go('search', {searchTerm: new_value}, {notify: false});
                // Update our term
                $scope.searchTerm = new_value;
                // Mark as searching so we can spin
                $scope.searching = true;
                // Run the search
                tss = Toolshed.Installable().query({search: new_value})
                // Promise to update a scoped object
                tss.$promise.then(function(results){
                    $scope.results = results
                    $scope.searching = false;
                })
            }, 1000); // delay 250 ms
        }
    );

})

app.controller('GroupListCtrl', function($scope, Toolshed, toastr) {
    // TODO: Pagination
    Toolshed.Group().query({page: 1}).$promise.then(function(response) {
        $scope.groups = response.results;
        $scope.numResults = response.count;
        $scope.pageCount = Math.ceil(response.count / 20);
    })
})

app.controller('GroupDetailCtrl', function($scope, Toolshed, $stateParams, toastr) {
    $scope.group = Toolshed.Group().get({groupId: $stateParams.groupId})

    $scope.searchUsers = function(query) {
        // TODO: delay search
        if(!query){
            return [];
        }
        // TODO: get contact searhc working at all.
        Toolshed.User().query({query: query}).$promise.then(function(response){
            console.log(response.results);
            return response.results
        });
    }

    $scope.saveForm = function(){
        // Persist updates to the backend

        // We create a separate user_set which will JUST contain IDs
        // This is an artefact of how the backend behaves.
        $scope.group.user_set = [];
        // Foreach person in our dereferenced set of users, push their IDs into
        // user_set
        angular.forEach($scope.group.user_set_deref, function(obj){
            $scope.group.user_set.push(obj.id)
        });
        // user_set is then used to update the group membership.
        var group = Toolshed.Group().update({
            groupId:$stateParams.groupId
        }, $scope.group);
    }
})

app.controller('GroupCreateCtrl', function($scope, Toolshed, $stateParams, toastr, $location) {
    $scope.group = {
        name: "",
        description: "",
        website: "",
        gpg_pubkey_id: "",
    }

    $scope.submit = function(){
        console.log("Submitting group")
        console.log($scope.group);

        Toolshed.Group().save($scope.group).$promise.then(
            function(response) {
                console.log(response);
                var redirect_location = '/group/' + response.data.id;
                console.log(redirect_location);
                $location.path(redirect_location);
                toastr.success("Created Group " + response.data.name, "Success!");
            }
        )
    }
})
