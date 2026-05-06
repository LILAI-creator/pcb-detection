var UploadManager = (function() {
  var ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/bmp'];
  var MAX_SIZE = 20 * 1024 * 1024;
  var zoneEl, fileInput, onFileSelected;

  function init(options) {
    onFileSelected = options.onFileSelected || function() {};
    zoneEl = document.getElementById('uploadZone');
    fileInput = document.getElementById('fileInput');

    zoneEl.addEventListener('click', function() {
      fileInput.click();
    });

    fileInput.addEventListener('change', function(e) {
      if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
        fileInput.value = '';
      }
    });

    zoneEl.addEventListener('dragover', function(e) {
      e.preventDefault();
      zoneEl.classList.add('dragover');
    });

    zoneEl.addEventListener('dragleave', function(e) {
      e.preventDefault();
      zoneEl.classList.remove('dragover');
    });

    zoneEl.addEventListener('drop', function(e) {
      e.preventDefault();
      zoneEl.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
      }
    });
  }

  function handleFile(file) {
    if (ACCEPTED_TYPES.indexOf(file.type) === -1) {
      Toast.show('不支持的文件格式，请上传 JPG/PNG/BMP 图像', 'error');
      return;
    }
    if (file.size > MAX_SIZE) {
      Toast.show('文件大小超过 20MB 限制', 'error');
      return;
    }
    onFileSelected(file);
  }

  function setLoading(loading) {
    if (loading) {
      zoneEl.style.pointerEvents = 'none';
      zoneEl.style.opacity = '0.6';
    } else {
      zoneEl.style.pointerEvents = '';
      zoneEl.style.opacity = '';
    }
  }

  return { init: init, setLoading: setLoading };
})();
