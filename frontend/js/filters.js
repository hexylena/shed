angular.module('appFilters', [])

.filter('nospace', function () {
  return function (value) {
    return (!value) ? '' : value.replace(/ /g, '');
  };
})

.filter('InstallableTypeToText', function () {
  return function (value) {
      console.log(value);
    var data = {
        'datatype': 'Datatypes',
        'package': 'Package',
        'tool': 'Tool',
        'gie': 'Galaxy Interactive Environment',
        'viz': 'Visualization',
        'suite': 'Suite',
    }
    return data[value]
  };
})
