/**
 * Kollective Log Analyzer browser - main JavaScript
 * JBW 2015/12
 */


// ------ various utils --------

if (!String.prototype.format) {
  String.prototype.format = String.prototype.f = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}
