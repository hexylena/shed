angular.module('appFilters', [])

.filter('nospace', function () {
  return function (value) {
    return (!value) ? '' : value.replace(/ /g, '');
  };
})

.filter('InstallableTypeToText', function () {
  return function (value, variant) {
      console.log(value);
    var data = {
        'datatype': ['Datatype', 'Datatypes'],
        'package': ['Package', 'Packages'],
        'tool': ['Tool', 'Tools'],
        'gie': ['Galaxy Interactive Environment', 'Galaxy Interactive Environments'],
        'viz': ['Visualization', 'Visualizations'],
        'suite': ['Suite', 'Suites'],
    }
    var variant_idx = 0;
    if(variant === "plural"){
        variant_idx = 1;
    }
    return data[value][variant_idx]
  };
})
