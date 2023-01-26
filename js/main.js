// Load data asynchronously

var files = [
  "./out/S049howManyEggCartons.csv"
];
var promises = [];

files.forEach(function (url, i) {
    promises.push(d3.csv(url));
});

Promise.all(promises).then(function (values) {
  createCodeHistorySnapshots(values[0]);
});

$(document).ready(function () {

  $('#sidebarCollapse').on('click', function () {
      $('#sidebar').toggleClass('active');
  });

});
