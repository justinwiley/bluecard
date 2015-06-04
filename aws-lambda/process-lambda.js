// dependencies
var async = require('async');
var AWS = require('aws-sdk');
var util = require('util');
var rest = require('restler');
var s3 = new AWS.S3();
var mysql = require('mysql');
var iniparser = require('iniparser');
var config = iniparser.parseSync('config/config.cnf');
var s3 = new AWS.S3();
var connection = mysql.createConnection({
  host: config['mysql']['host'],
  user: config['mysql']['user'],
  password: config['mysql']['password'],
  database: config['mysql']['database']
});

// execute given rest method
function do_rest(method, url, data, callback) {
  var opts = {
    headers: {
      'Captricity-API-Token': config['captricity']['apitoken']
    },
    timeout: 10000
  };
  // attach data payload, setting multipart as appropriate
  if (data) {
    opts['data'] = data;
    if (data['uploaded_file']) opts['multipart'] = true;
  }

  rest[method](url, opts).on('complete', function(results, response) {
    console.log(' - %s request returned %s status', method, response.statusCode);
    if (response.statusCode == 200) {
      // if success, pass along results of next function
      // in waterfall
      callback(undefined, results);
    } else {
      // if unsuccessful, results will contain error information
      callback(results);
    }
  }).on('error', callback).on('timeout', callback);
}

// returns valid captricity url given batch id or underfined
function captricity_url(batch_id) {
  var batch_id = batch_id || '';
  var url = 'https://shreddr.captricity.com/api/v1/batch/' + batch_id;
  console.log(' - infered url: %s', url);
  return url
}

// simple logging function
function print_header(header) {
  console.log("\n---- %s ----\n", header);
}

// Amazon Lambda event handler
// Amazon passes an event (s3 upload in this case, passes it on as context)
// - Exit if invalid
// - Otherwise pull down the object, pass on to Captricity, store the result

exports.handler = function(event, context) {
  // Read options from the event.
  console.log("Reading options from event:\n", util.inspect(event, {
    depth: 5
  }));
  var bucket = event.Records[0].s3.bucket.name;
  // Object key may have spaces or unicode non-ASCII characters.
  var key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, " "));

  // Infer the image type.
  var typeMatch = key.match(/\.([^.]*)$/);
  if (!typeMatch) {
    console.error('unable to infer image type for key ' + key);
    return;
  }
  var imageType = typeMatch[1];
  if (imageType != "jpg" && imageType != "jpeg" && imageType != "png") {
    console.log('skipping non-image ' + key);
    return;
  }

  // used by waterfall, expects either an error, or null and a string of arguments
  // if an error is present, display it, raise exception
  function async_callback(err_or_status) {
    if (err_or_status) {
      console.error('Unable to process image %s/%s due to an error: %j', bucket, key, err_or_status);
      connection.end();
      context.done();
    } else if (err_or_status == 'process_complete') {
      console.log(' - all processing steps successfully finished');
      connection.end();
      context.done();
    } else {
      console.log(' - processing step finished');
    }
  }

  async.waterfall([
    // create Captricity batch
    function create_batch(callback) {
      print_header('create batch');
      console.log('creating Captricity batch')
      var form = {
        name: 'import-batch'
      };
      do_rest('post', captricity_url(), form, callback);
    },
    // assign a document to the batch
    function assign_document(results, callback) {
      print_header('assign document');
      var batch_id = results['id'];
      console.log('assigning document to batch ' + batch_id);
      var document_id = '94926'; // 'License' document
      var form = {
        documents: document_id
      };
      var url = captricity_url(batch_id);
      do_rest('put', url, form, callback);
    },
    // download s3 image, store in buffer
    function download_s3_image(results, callback) {
      print_header('download s3 image');
      var batch_id = results['id'];
      console.log('downloading image from s3');

      s3.getObject({
        Bucket: bucket,
        Key: key
      }, function(err, data) {
        if (err) callback(err); // an error occurred
        else callback(undefined, batch_id, data); // successful response
      });
    },
    // attach s3 image to batch
    function attach_image(batch_id, data, callback) {
      print_header('attach image');
      console.log('attaching %s %s size %s', key, data.ContentType);
      form = {
        'file_name': key,
        'uploaded_file': rest.data(key, data.ContentType, data.Body)
      };
      do_rest('post', captricity_url(batch_id + '/batch-file/'), form, callback);
    },
    // check Capricity errors
    function schedule_job(results, callback) {
      print_header('schedule job');
      console.log('attach results: %j', results);
      var batch_id = results['batch']['id'];
      console.log('scheduling batch %s', batch_id);
      do_rest('post', captricity_url(batch_id + '/submit'), undefined, callback);
    },
    // add the batch id and status of the job to the associated Document in MySQL
    function update_database(results, callback) {
      print_header('update db');
      console.log('schedule results: %j', results);
      // escape query params
      var batch_id = connection.escape(results['id']);
      var job_id = connection.escape(results['related_job_id']);
      var status = connection.escape(results['status']);
      var update_key = connection.escape('/imports/' + key);

      var sql = "UPDATE idimport_document SET ";
      sql = sql + " batch_id=" + batch_id;
      sql = sql + " AND job_id=" + job_id;
      sql = sql + " AND status=" + status;
      sql = sql + " WHERE image=" + update_key;

      console.log("setting status for %s to %s, sql:\n%s", key, status, sql);

      connection.connect();
      connection.query(sql, function(err, result) {
        if (err) {
          callback(err);
        } else {
          console.log('updated ' + result.affectedRows + ' rows');
          callback(undefined);
        }
      });
    },
    function finish(callback) {
      callback('process_complete');
    }
  ], async_callback);
}