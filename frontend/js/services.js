var app = angular.module('MyApp');

app.factory('Account', function($http) {
    return {
        getProfile: function() {
            return $http.get($rootScope._backendUrl + '/me');
        },
        updateProfile: function(profileData) {
            return $http.put($rootScope._backendUrl + '/me', profileData);
        }
    };
});


app.factory('Toolshed', function($http, $rootScope, $resource) {
    return {
        getUser: function(userId) {
            return $resource(
                $rootScope._backendUrl + '/users/:userId', {},
                {
                    query: {
                        method: 'GET',
                        params: {
                            userId: userId
                        }
                    }
                }
            );
        },
        getUsers: function(page_idx) {
            if(page_idx === undefined){
                page_idx = 0
            }
            return $resource(
                $rootScope._backendUrl + '/users.json?page=:pageIndex', {},
                {
                    query: {
                        method: 'GET',
                        params: {
                            pageIndex: page_idx + 1
                        }
                    }
                }
            );
        },
        getGroup: function(groupId) {
            return $resource(
                $rootScope._backendUrl + '/groups/:groupId', {},
                {
                    query: {
                        method: 'GET',
                        params: {
                            groupId: groupId
                        }
                    }
                }
            );
        },
        getGroups: function(page_idx) {
            if(page_idx === undefined){
                page_idx = 0
            }
            return $resource(
                $rootScope._backendUrl + '/groups.json?page=:pageIndex', {},
                {
                    query: {
                        method: 'GET',
                        params: {
                            pageIndex: page_idx + 1
                        }
                    }
                }
            );
        },
        //createGroup: function(group){
            //return $http.post($rootScope._backendUrl + '/group', group);
        //},
        getInstallables: function(installableType, page_idx) {
            installable_types = {
                'package': 0,
                'tool': 1,
                'datatype': 2,
                'suite': 3,
                'viz': 4,
                'gie': 5,
            }
            if(page_idx === undefined){
                page_idx = 0
            }
            return $resource($rootScope._backendUrl + '/installables.json?repository_type=:repositoryTypeId&page=:pageIndex', {}, {
                query: {method: 'GET', params:{repositoryTypeId: installable_types[installableType], pageIndex: page_idx + 1}}
            });
        },
        getInstallable: function(installableId) {
            return $resource($rootScope._backendUrl + '/installables/:installableId.json', {}, {
                query: {method: 'GET', params:{installableId: installableId}}
            });
        },
        getRevision: function(revisionId){
            return $resource($rootScope._backendUrl + '/revisions/:revisionId.json', {}, {
                query: {method: 'GET', params:{revisionId: revisionId}}
            });
        }
        //searchInstallables: function(query_string){
            //// TODO: split on multiple spaces
            //// TODO: query revisions, not parent packages
            ////var parts = query_string.split(' ');
            ////var filters = [
                ////{name: "name", op: "ilike"}
            ////]
            //return $http.get($rootScope._backendUrl + '/installable?q={"filters":[{"name":"name","op":"ilike","val":"%25' + query_string + '%25"}]}');
        //},
        //createInstallable: function(installable){
            //return $http.post($rootScope._backendUrl + '/installable', installable);
        //},
        //updateInstallable: function(installable){
            //return $http.patch($rootScope._backendUrl + '/installable/' + installable.id, installable);
        //},
        //createSuite: function(suite){
            //return $http.post($rootScope._backendUrl + '/installable', installable);
        //},
    }
});
