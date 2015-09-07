var app = angular.module('MyApp');

app.factory('Account', function($http) {
    return {
        getProfile: function() {
            return $http.get('/api/me');
        },
        updateProfile: function(profileData) {
            return $http.put('/api/me', profileData);
        }
    };
});

app.factory('Toolshed', function($http) {
    return {
        getInstallable: function(installableId) {
            return $http.get('/api/installable/' + installableId);
        },
        getInstallables: function(pageNumber) {
            if(pageNumber === undefined){
                pageNumber = 1;
            }
            return $http.get('/api/installable?page=' + pageNumber);
        },
        getUser: function(userId) {
            return $http.get('/api/user/' + userId);
        },
        getUsers: function(pageNumber) {
            if(pageNumber === undefined){
                pageNumber = 1;
            }
            return $http.get('/api/user?page=' + pageNumber);
        },
        getGroup: function(groupId) {
            return $http.get('/api/group/' + groupId);
        },
        getGroups: function(pageNumber) {
            if(pageNumber === undefined){
                pageNumber = 1;
            }
            return $http.get('/api/group?page=' + pageNumber);
        },
        createGroup: function(group){
            return $http.post('/api/group', group);
        },
        getInstallable: function(installableId) {
            return $http.get('/api/installable/' + installableId);
        },
        getInstallables: function(type, pageNumber) {
            if(pageNumber === undefined){
                pageNumber = 1;
            }
            if(type === undefined){
                type = "tools";
            }

            var filterString = '&q={"filters":[{"name":"repository_type","op":"eq","val": "' + type + '"}]}';
            return $http.get('/api/installable?page=' + pageNumber + filterString);
        },
        createInstallable: function(installable){
            return $http.post('/api/installable', installable);
        }
    }
});
