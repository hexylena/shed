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
        User: function(userId, page_idx){
            return $resource(
                $rootScope._backendUrl + '/users/:userId',
                {
                    userId: '@userId',
                    // This is automatically inserted as a query parameters
                    // because it isn't specified in the template.
                    page: '@pageIndex',
                },
                {
                    query: {
                        method: 'GET',
                    },
                    get: {
                        method: 'GET',
                        params: {
                            userId: userId
                        }
                    }
                }
            )
        },
        Group: function(groupId, page_idx){
            return $resource(
                $rootScope._backendUrl + '/groups/:groupId',
                {
                    groupId: '@groupId',
                    // This is automatically inserted as a query parameters
                    // because it isn't specified in the template.
                    page: '@pageIndex',
                },
                {
                    query: {
                        method: 'GET',
                    },
                    get: {
                        method: 'GET',
                        params: {
                            groupId: groupId
                        }
                    },
                    update: {
                        method: 'PUT',
                        params: {
                            groupId: groupId
                        }
                    },
                    save: {
                        method: 'POST',
                    }
                }
            )
        },
        Search: function(query){
            return $resource(
                $rootScope._backendUrl + '/installables',
                {
                    search: '@query',
                },
                {
                    query: { method: 'GET'}
                }
            )
        },
        Tag: function(tagId, page_idx){
            return $resource(
                $rootScope._backendUrl + '/tags/:tagId',
                {
                    tagId: '@tagId',
                    // This is automatically inserted as a query parameter when
                    // present, because it isn't specified in the template.
                    page: '@page',
                },
                {
                    query: {
                        method: 'GET',
                    },
                    get: {
                        method: 'GET',
                        params: {
                            tagId: tagId
                        }
                    },
                    update: {
                        method: 'PUT',
                        params: {
                            tagId: tagId
                        }
                    },
                    save: {
                        method: 'POST',
                    }
                }
            )
        },
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
        },
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
            //return $resource($rootScope._backendUrl + '/installable', {}, {
                //submit: {method: 'POST', data}
                //query: {method: 'GET', params:{revisionId: revisionId}}
            //});
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
