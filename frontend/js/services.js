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
        //getUser: function(userId) {
            //return $http.get($rootScope._backendUrl + '/user/' + userId);
        //},
        //getUsers: function(pageNumber) {
            //if(pageNumber === undefined){
                //pageNumber = 1;
            //}
            //return $http.get($rootScope._backendUrl + '/user?page=' + pageNumber);
        //},
        //getGroup: function(groupId) {
            //return $http.get($rootScope._backendUrl + '/group/' + groupId);
        //},
        //getGroups: function(pageNumber) {
            //if(pageNumber === undefined){
                //pageNumber = 1;
            //}
            //return $http.get($rootScope._backendUrl + '/group?page=' + pageNumber);
        //},
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
                page_idx = 1
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
        //getInstallables: function(type, pageNumber) {
            //if(pageNumber === undefined){
                //pageNumber = 1;
            //}
            //if(type === undefined){
                //type = "tools";
            //}

            //var filterString = '&q={"filters":[{"name":"repository_type","op":"eq","val": "' + type + '"}]}';
            //return $http.get($rootScope._backendUrl + '/installable?page=' + pageNumber + filterString);
        //},
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
