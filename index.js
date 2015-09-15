var http   = require("http"),
    zlib   = require("zlib"),
    https  = require("https"),
    config = require("./config"),
    urlFix = require("./lib/urlFix"),
    stats  = require("./stats");


function empty(obj) { 
  // check if array or object by calling Object.prototype.toString.apply blah
  return Object.keys(obj).length === 0; 
}

function extend() {
  var source      = arguments[1],
      destination = arguments[0],
      sKeys       = Object.keys(source),
      counter, 
      currentKey,
      sKey;

  for(var x in sKeys) {
    sKey = source[sKeys[x]];
    destination[sKeys[x]] = sKey;
  }
};

function responseEventsHandler(responseHandler) {
  var data = "";
  responseHandler
    .on("data", function(chunk) {  
      data += chunk.toString();
    })                             
    .on("end", function() {        
      stats.stat(data);
    })
    .on("error", function(err) {
      console.log(err);
    });
}

function callback(response) {
  var data     = "",
      resEncod = response.headers['content-encoding'];
  if (resEncod === "gzip") {
    var gzip = zlib.createGunzip();
    response.pipe(gzip);
    data = responseEventsHandler(gzip);
  } else {
    data = responseEventsHandler(response);
  }
};

function grab(options) {
  extend(options, config.headers);
  if (options.protocol === "https:") {
    https.request(options, callback).end();
  } else {
    http.request(options, callback).end();
  }
};

grab(urlFix.format(process.argv[2]));
