var CanvasRenderer = (function() {
  var canvas, ctx, currentImage, detections, scale, offsetX, offsetY;
  var highlightIndex = -1;

  var CLASS_COLORS = {
    'missing_hole': '#FF0000',
    'mouse_bite': '#FFA500',
    'open_circuit': '#FFFF00',
    'short': '#00FF00',
    'spur': '#FF8C00',
    'spurious_copper': '#B400FF',
    'default': '#5856D6'
  };

  function getColor(className) {
    return CLASS_COLORS[className] || CLASS_COLORS['default'];
  }

  function init() {
    canvas = document.getElementById('detectCanvas');
    ctx = canvas.getContext('2d');
    setupInteraction();
    window.addEventListener('resize', function() {
      draw();
    });
  }

  function setupInteraction() {
    var isDragging = false;
    var lastX, lastY;
    var transform = { x: 0, y: 0, zoom: 1 };

    canvas.addEventListener('wheel', function(e) {
      e.preventDefault();
      var delta = e.deltaY > 0 ? 0.9 : 1.1;
      transform.zoom = Math.max(0.5, Math.min(5, transform.zoom * delta));
      draw();
    }, { passive: false });

    canvas.addEventListener('mousedown', function(e) {
      if (e.button === 0) {
        isDragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
        canvas.style.cursor = 'grabbing';
      }
    });

    window.addEventListener('mousemove', function(e) {
      if (isDragging) {
        transform.x += e.clientX - lastX;
        transform.y += e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        draw();
      }
    });

    window.addEventListener('mouseup', function() {
      isDragging = false;
      canvas.style.cursor = 'default';
    });

    canvas._transform = transform;
  }

  var drawPending = false;

  function draw() {
    if (!currentImage) return;

    var containerW = canvas.parentElement.clientWidth;
    var containerH = canvas.parentElement.clientHeight;

    if (containerW === 0 || containerH === 0) {
      if (!drawPending) {
        drawPending = true;
        requestAnimationFrame(function() {
          drawPending = false;
          draw();
        });
      }
      return;
    }

    var transform = canvas._transform || { x: 0, y: 0, zoom: 1 };

    canvas.width = containerW;
    canvas.height = containerH;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    var imgAspect = currentImage.width / currentImage.height;
    var canvasAspect = canvas.width / canvas.height;
    var drawW, drawH;

    if (imgAspect > canvasAspect) {
      drawW = canvas.width * 0.9;
      drawH = drawW / imgAspect;
    } else {
      drawH = canvas.height * 0.9;
      drawW = drawH * imgAspect;
    }

    scale = drawW / currentImage.width;
    offsetX = (canvas.width - drawW) / 2;
    offsetY = (canvas.height - drawH) / 2;

    ctx.save();
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.zoom, transform.zoom);
    ctx.translate(-transform.x, -transform.y);

    ctx.drawImage(currentImage, offsetX, offsetY, drawW, drawH);

    if (detections && detections.length > 0) {
      detections.forEach(function(det, i) {
        var bbox = det.bbox;
        var x = offsetX + bbox.x * scale;
        var y = offsetY + bbox.y * scale;
        var w = bbox.width * scale;
        var h = bbox.height * scale;
        var color = getColor(det.class);
        var isHighlight = (i === highlightIndex);

        ctx.strokeStyle = color;
        ctx.lineWidth = isHighlight ? 3 : 2;
        ctx.strokeRect(x, y, w, h);

        if (isHighlight) {
          ctx.fillStyle = color.replace(')', ',0.15)').replace('rgb', 'rgba');
          if (color.charAt(0) === '#') {
            var r = parseInt(color.slice(1,3),16);
            var g = parseInt(color.slice(3,5),16);
            var b = parseInt(color.slice(5,7),16);
            ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',0.15)';
          }
          ctx.fillRect(x, y, w, h);
        }

        var label = det.class + ' ' + (det.confidence * 100).toFixed(1) + '%';
        ctx.font = (isHighlight ? 'bold 13px' : '12px') + ' -apple-system, sans-serif';
        var textW = ctx.measureText(label).width + 10;
        ctx.fillStyle = color;
        ctx.fillRect(x, y - 20, textW, 20);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, x + 5, y - 5);
      });
    }

    ctx.restore();
  }

  function setImage(src) {
    return new Promise(function(resolve) {
      var img = new Image();
      img.onload = function() {
        currentImage = img;
        detections = [];
        highlightIndex = -1;
        if (canvas._transform) {
          canvas._transform = { x: 0, y: 0, zoom: 1 };
        }
        draw();
        resolve();
      };
      img.src = src;
    });
  }

  function setDetections(dets) {
    detections = dets;
    highlightIndex = -1;
    draw();
  }

  function setHighlight(index) {
    highlightIndex = index;
    draw();
  }

  function clearHighlight() {
    highlightIndex = -1;
    draw();
  }

  function clear() {
    currentImage = null;
    detections = [];
    highlightIndex = -1;
    if (canvas) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  function resetView() {
    if (canvas._transform) {
      canvas._transform = { x: 0, y: 0, zoom: 1 };
      draw();
    }
  }

  return {
    init: init,
    setImage: setImage,
    setDetections: setDetections,
    setHighlight: setHighlight,
    clearHighlight: clearHighlight,
    clear: clear,
    resetView: resetView,
    getColor: getColor
  };
})();
