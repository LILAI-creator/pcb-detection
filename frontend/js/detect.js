var Detector = (function() {
  var state = 'idle';

  function init() {
    UploadManager.init({
      onFileSelected: handleFileSelected
    });
    CanvasRenderer.init();

    document.getElementById('btnResetView').addEventListener('click', function() {
      CanvasRenderer.resetView();
    });

    document.getElementById('btnExportImage').addEventListener('click', exportResult);
    document.getElementById('btnExportJSON').addEventListener('click', exportJSON);
  }

  var lastResult = null;

  function handleFileSelected(file) {
    state = 'detecting';
    updateUI();
    UploadManager.setLoading(true);

    var reader = new FileReader();
    reader.onload = function(e) {
      showCanvas();
      CanvasRenderer.setImage(e.target.result).then(function() {
        showDetectingOverlay();
        return API.detect(file);
      }).then(function(result) {
        lastResult = result;
        CanvasRenderer.setDetections(result.defects || []);
        renderDetectionList(result.defects || []);
        showResultMeta(result);
        hideDetectingOverlay();
        state = 'done';
        updateUI();
        Toast.show('检测完成，发现 ' + (result.defects ? result.defects.length : 0) + ' 个缺陷', 'success');
      }).catch(function(err) {
        Toast.show(err.message || '检测失败', 'error');
        hideDetectingOverlay();
        state = 'idle';
        updateUI();
      }).finally(function() {
        UploadManager.setLoading(false);
      });
    };
    reader.readAsDataURL(file);
  }

  function renderDetectionList(defects) {
    var listEl = document.getElementById('detectionList');
    var countEl = document.getElementById('defectCount');

    if (!defects || defects.length === 0) {
      listEl.innerHTML = '<div class="empty-state"><div class="icon">✓</div><div>未检测到缺陷</div></div>';
      countEl.textContent = '0';
      return;
    }

    countEl.textContent = defects.length;

    listEl.innerHTML = defects.map(function(d, i) {
      var color = CanvasRenderer.getColor(d.class);
      var className = d.class || 'unknown';
      var conf = (d.confidence * 100).toFixed(1) + '%';
      return '<div class="detection-item" data-index="' + i + '">' +
        '<div class="color-dot" style="background:' + color + '"></div>' +
        '<div class="info">' +
          '<div class="class-name">' + className + '</div>' +
          '<div class="confidence">置信度: ' + conf + '</div>' +
          '<div class="bbox-info">[' + d.bbox.x.toFixed(0) + ', ' + d.bbox.y.toFixed(0) + ', ' + d.bbox.width.toFixed(0) + ', ' + d.bbox.height.toFixed(0) + ']</div>' +
        '</div>' +
      '</div>';
    }).join('');

    listEl.querySelectorAll('.detection-item').forEach(function(item) {
      item.addEventListener('mouseenter', function() {
        CanvasRenderer.setHighlight(parseInt(item.dataset.index));
      });
      item.addEventListener('mouseleave', function() {
        CanvasRenderer.clearHighlight();
      });
    });
  }

  function showResultMeta(result) {
    var metaEl = document.getElementById('resultMeta');
    metaEl.classList.remove('hidden');
    document.getElementById('metaTime').textContent = new Date(result.timestamp).toLocaleString('zh-CN');
    document.getElementById('metaDefects').textContent = result.defects ? result.defects.length : 0;
  }

  function showDetectingOverlay() {
    var existing = document.getElementById('detectOverlay');
    if (existing) return;
    var overlay = document.createElement('div');
    overlay.id = 'detectOverlay';
    overlay.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.3);display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:20px;z-index:10';
    overlay.innerHTML = '<div class="spinner"></div><div style="margin-top:12px;color:#fff;font-size:14px;font-weight:500">正在检测...</div>';
    var container = document.querySelector('.canvas-container');
    container.style.position = 'relative';
    container.appendChild(overlay);
  }

  function hideDetectingOverlay() {
    var overlay = document.getElementById('detectOverlay');
    if (overlay) overlay.remove();
  }

  function showPlaceholder(type) {
    var placeholder = document.getElementById('canvasPlaceholder');
    var canvasContainer = document.querySelector('.canvas-container');
    if (type === 'loading') {
      placeholder.innerHTML = '<div class="spinner"></div><div style="margin-top:12px;color:var(--text-secondary)">正在检测...</div>';
      placeholder.classList.remove('hidden');
      canvasContainer.classList.add('hidden');
    } else if (type === 'error') {
      placeholder.innerHTML = '<div class="icon" style="font-size:40px;opacity:0.5">⚠</div><div style="color:var(--text-secondary)">检测失败，请重试</div>';
      placeholder.classList.remove('hidden');
      canvasContainer.classList.add('hidden');
    } else {
      placeholder.innerHTML = '<div class="icon" style="font-size:40px;opacity:0.5">📷</div><div style="color:var(--text-secondary)">上传PCB板图像开始检测</div>';
      placeholder.classList.remove('hidden');
      canvasContainer.classList.add('hidden');
    }
  }

  function showCanvas() {
    document.getElementById('canvasPlaceholder').classList.add('hidden');
    document.querySelector('.canvas-container').classList.remove('hidden');
  }

  function updateUI() {
    var resultActions = document.getElementById('resultActions');
    if (state === 'done') {
      resultActions.classList.remove('hidden');
      showCanvas();
    } else {
      resultActions.classList.add('hidden');
    }
  }

  function exportResult() {
    var canvas = document.getElementById('detectCanvas');
    var link = document.createElement('a');
    link.download = 'pcb_detection_result.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  }

  function exportJSON() {
    if (!lastResult) {
      Toast.show('没有可导出的检测结果', 'warning');
      return;
    }
    var json = JSON.stringify(lastResult, null, 2);
    var blob = new Blob([json], { type: 'application/json' });
    var link = document.createElement('a');
    link.download = 'pcb_detection_result.json';
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  }

  return { init: init };
})();

var Toast = (function() {
  var container;

  function init() {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  function show(message, type) {
    type = type || 'success';
    var toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function() {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      toast.style.transition = '0.3s ease';
      setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
  }

  return { init: init, show: show };
})();
