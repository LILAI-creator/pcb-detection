var API = (function() {
  var BASE_URL = '';

  function setBaseUrl(url) {
    BASE_URL = url.replace(/\/$/, '');
  }

  function request(method, path, options) {
    options = options || {};
    var url = BASE_URL + path;
    var config = {
      method: method,
      headers: {}
    };

    if (options.body && !(options.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
      config.body = JSON.stringify(options.body);
    } else if (options.body) {
      config.body = options.body;
    }

    if (options.headers) {
      Object.keys(options.headers).forEach(function(key) {
        config.headers[key] = options.headers[key];
      });
    }

    return fetch(url, config)
      .then(function(res) {
        if (!res.ok) {
          return res.json().then(function(err) {
            throw { status: res.status, message: err.detail || err.message || '请求失败' };
          }).catch(function(e) {
            if (e.status) throw e;
            throw { status: res.status, message: '请求失败 (' + res.status + ')' };
          });
        }
        return res.json();
      });
  }

  function detect(imageFile) {
    var formData = new FormData();
    formData.append('file', imageFile);
    return request('POST', '/api/detect', { body: formData });
  }

  function getHistory(params) {
    params = params || {};
    var query = [];
    if (params.page) query.push('page=' + params.page);
    if (params.pageSize) query.push('page_size=' + params.pageSize);
    if (params.defectClass) query.push('defect_class=' + encodeURIComponent(params.defectClass));
    if (params.startDate) query.push('start_date=' + params.startDate);
    if (params.endDate) query.push('end_date=' + params.endDate);
    var path = '/api/history' + (query.length ? '?' + query.join('&') : '');
    return request('GET', path);
  }

  function getHistoryDetail(id) {
    return request('GET', '/api/history/' + id);
  }

  function getStats() {
    return request('GET', '/api/stats');
  }

  function getStatsTrend(params) {
    params = params || {};
    var query = [];
    if (params.days) query.push('days=' + params.days);
    var path = '/api/stats/trend' + (query.length ? '?' + query.join('&') : '');
    return request('GET', path);
  }

  function getDefectClasses() {
    return request('GET', '/api/defect-classes');
  }

  function getResultImage(imageUrl) {
    return BASE_URL + imageUrl;
  }

  return {
    setBaseUrl: setBaseUrl,
    detect: detect,
    getHistory: getHistory,
    getHistoryDetail: getHistoryDetail,
    getStats: getStats,
    getStatsTrend: getStatsTrend,
    getDefectClasses: getDefectClasses,
    getResultImage: getResultImage
  };
})();
