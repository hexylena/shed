var app = angular.module('MyApp');

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
        Group: function(groupId){
            return $resource(
                $rootScope._backendUrl + '/groups/:groupId',
                {
                    groupId: '@groupId',
                    // This is automatically inserted as a query parameters
                    // because it isn't specified in the template.
                    page: '@page',
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
        Installable: function(installableId, page, repositoryType){
            return $resource(
                $rootScope._backendUrl + '/installables/:installableId',
                {
                    installableId: '@installableId',
                    // This is automatically inserted as a query parameter when
                    // present, because it isn't specified in the template.
                    page: '@page',
                    repositoryType: '@repositoryType',
                },
                {
                    query: {
                        method: 'GET',
                        params: {
                            page: page,
                            repositoryType: repositoryType
                        }
                    },
                    save: {
                        method: 'POST',
                    },
                    /*
                    get: {
                        method: 'GET',
                        params: {
                            installableId: installableId
                        }
                    },
                    update:{
                        method: 'PUT',
                        params: {
                            installableId: installableId
                        }
                    }
                    */
                }
            )
        },
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
