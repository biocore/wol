"use strict";

/**
 * tells javasript what function to call for mouse/keyboard events
 */
function initCallbacks(){
  const SHFT_KEY = 16;
  const DELAY = 500;
  window.onTreeSurface = false;
  window.timer = setTimeout(nodeHover, 100, 0,0);
  var event  = new Event('node_hover');
  $(".tree-surface").on('node_hover', nodeHover);
  $(".tree-surface").on("mousedown", mouseHandler);
  $(document).on("mouseup", mouseHandler);
  $(document).on("mousemove", mouseHandler);
  $(".tree-surface")[0].onwheel = mouseHandler;
  $(".tree-surface").hover(function() {window.onTreeSurface = true;}, 
      function(){window.onTreeSurface=false;})
  $(window).on("resize", resizeCanvas);

  $(".tree-surface")[0].ondblclick = mouseHandler;

  $(document).keydown(function(e) {
    shftPress = (e.which === SHFT_KEY) ? true : false;
  });
  $(document).keyup(function() {
    if(shftPress) {
      shftPress = false;
    //   let square = $(".square");
    //   let offset = square.offset();
    //   drawingData.lastMouseX = offset.left, drawingData.lastMouseY = offset.top;
    //   let width = square.width(), height = square.height();
    //   let topCorner = toTreeCoords(drawingData.lastMouseX, drawingData.lastMouseY);
    //   let bottomCorner = toTreeCoords(drawingData.lastMouseX + width, drawingData.lastMouseY + height);
    //   let edgeMetadata;
    //   $.getJSON(urls.selectTreeURL, {x1: topCorner[0], y1: topCorner[1],
    //             x2: bottomCorner[0], y2: bottomCorner[1]}, function(data) {
    //     edgeMetadata = data;
    //   }).done(function() {
    //     if(edgeMetadata.length === 0) {
    //       $(".selected-tree-menu").css({top: drawingData.lastMouseY, left: drawingData.lastMouseX, visibility: "hidden"});
    //       return;
    //     }
    //     drawingData.selectTree = extractInfo(edgeMetadata, field.edgeFields);
    //     updateGridData(edgeMetadata);
    //     fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    //     $(".selected-tree-menu").css({top: drawingData.lastMouseY, left: drawingData.lastMouseX, visibility: "visible"});
    //     requestAnimationFrame(loop);
    //   });
    }
  });
}

function nodeHover(x,y) {
  let id;
  let clsXTC, clsYTC, clsID;
  let close = 1000;
  let tmp;
  let xDist, yDist, treeX, treeY, nScreenX, nScreenY, treeSpace, screenSpace;
  let canvas = $(".tree-surface")[0];
  for(id in window.treeData) {
      treeX = window.treeData[id].x;
      treeY = window.treeData[id].y;
      // calculate the screen coordinate of the label
      treeSpace = vec4.fromValues(treeX, treeY, 0, 1);
      screenSpace = vec4.create();
      vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
      screenSpace[0] /= screenSpace[3];
      screenSpace[1] /= screenSpace[3];
      nScreenX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
      nScreenY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;
      xDist = x - nScreenX;
      yDist = y - nScreenY;

      tmp = xDist*xDist + yDist*yDist;
    if(Math.abs(tmp) < close) {
        close = Math.abs(tmp);
        clsXTC = treeX;
        clsYTC = treeY;
        clsID = id;
    }
  }
  if(close <= 50) {
    drawingData.hoveredNode = [clsXTC, clsYTC, 0, 1, 0];
    $("#hover-div").html(
      "<b>Genome ID:</b> " + clsID + "<br>"  +
      "<b>Kingdom: </b>" + metadata[clsID]["kingdom"] + "<br>" +
      "<b>Phylum: </b>" + metadata[clsID]["phylum"] + "<br>" +
      "<b>Class: </b>" + metadata[clsID]["class"] + "<br>" +
      "<b>Order: </b>" + metadata[clsID]["order"] + "<br>" +
      "<b>Family: </b>" + metadata[clsID]["family"] + "<br>" +
      "<b>Genus: </b>" +metadata[clsID]["genus"] + "<br>" +
      "<b>Species: </b>" + metadata[clsID]["species"] + "<br>"
    );
    // calculate the screen coordinate of the label
      let treeSpace = vec4.fromValues(clsXTC, clsYTC, 0, 1);
      let screenSpace = vec4.create();
      vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
      screenSpace[0] /= screenSpace[3];
      screenSpace[1] /= screenSpace[3];
      let pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
      let pixelY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;

      // make the div
      let div = $("#hover-div");

      div.css({left: Math.floor(pixelX) + "px",
               top: Math.floor(pixelY) + "px",
               display: "block"});
  } else {
    // make the div
      let div = $("#hover-div");

      div.css({display: "none"});
  }

  fillBufferData(shaderProgram.hoverNodeBuffer, drawingData.hoveredNode);
  requestAnimationFrame(loop);
}

function autoCollapseTree() {
  console.log('Auto Collapse Tree')
  let collapsLevel = $("#collapse-level").val();
  const cm = $("#color-options-collapse").val();
  const attribute = $("#collapse-options").val();
  $.getJSON(urls.autoCollapseURL, {attribute: attribute, collapse_level: collapsLevel, cm : cm}, function(data){
    console.log("Auto Collapse Tree data return")
    let edgeData = extractInfo(data, field.edgeFields);
    drawingData.numBranches = edgeData.length
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}

function selectedTreeCollapse() {
  $(".selected-tree-menu").css({visibility: "hidden"})
  $.getJSON(urls.collapseSTreeURL, {}, function(data) {
    let edgeData = extractInfo(data, field.edgeFields);
    drawingData.numBranches = edgeData.length
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    drawingData.selectTree = [];
    fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}


function clearSelectedTreeCollapse(event) {
  let treeCoords = toTreeCoords(event.clientX, event.clientY);
  $.getJSON(urls.uncollapseSTreeURL, {x1: treeCoords[0], y1: treeCoords[1]}, function(data) {
    let edgeData = extractInfo(data, field.edgeFields);
    drawingData.numBranches = edgeData.length
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    drawingData.selectTree = [];
    fillBufferData(shaderProgram.selectBuffer, drawingData.selectTree);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}

/**
 * resizes the drawing canvas to fix the screen
 *
 * @param {Object} resize event used to dynamically resize the html document.
 */
function resizeCanvas(event) {
  setCanvasSize(gl.canvas);
  setPerspective();
  requestAnimationFrame(loop);
}

/**
 * Event called when user presses the select-data button. This method is responsible
 * for coordinating the highlight tip feature.
 */
function userHighlightSelect() {
  const attr = $("#highlight-options").val();
  const cm = $("#color-options").val();

  let edgeData = extractInfo(JSON.parse(highlight.edges), field.edgeFields);
  drawingData.numBranches = edgeData.length
  fillBufferData(shaderProgram.treeVertBuffer, edgeData);
  requestAnimationFrame(loop);
}

function userCladeColor(){
  console.log('ColorClades')
  const attribute = $('#clade-options').val();
  const taxLevel = $("#tax-level").val();
  const cm = $("#color-options-tax").val();
  $.getJSON(urls.newCladeColor, {attribute: attribute, tax_level: taxLevel, cm: cm}, function(data){
      console.log('loadColorClades');
      loadColorClades(data);
  })
}

function retriveTaxonNodes() {
  let TAXLEVEL;
  let node;
  if($("#tips").is(":checked")) {
    TAXLEVEL = $("#tips-find-level").val();
    tipLabels = [];
    for(node in metadata) {
      if(metadata[node][TAXLEVEL] != null && treeData[node]["is_tip"] === "true") {
        tipLabels.push([metadata[node]["x"],
                         metadata[node]["y"],
                         metadata[node][TAXLEVEL],
                         node]);
      }
    }
  }
  else {
    clearLabels("tip");
  }

  if($("#internal-nodes").is(":checked")) {
    TAXLEVEL = $("#nodes-find-level").val();
    nodeLabels = [];
    for(node in metadata) {
      if(metadata[node][TAXLEVEL] != null && treeData[node]["is_tip"] === "false") {
        nodeLabels.push([metadata[node]["x"],
                         metadata[node]["y"],
                         metadata[node][TAXLEVEL],
                         treeData[node]["leafcount"],
                         node]);
      }
    }
    nodeLabels.sort(function (dataRow1, dataRow2) {
      if(dataRow1[3] < dataRow2[3] ) {
        return 1;
      }
      return -1;
    });
  }
  else {
    clearLabels("node");
  }
  requestAnimationFrame(drawLabels);
}

function clearLabels(label) {
  if(label === "tip") {
    tipLabels = {};
  }
  else{
    nodeLabels = {};
  }
  requestAnimationFrame(drawLabels);
}

/**
 * Changes the metadata shown in SlickGrid to match the highlighted feature that
 * was selected.
 *
 * @param {Object} The button that corresponds to the highlighted feature.
 */
function selectTable(obj) {
  const item = attrItem[obj.parentElement.id];
  let l = '', u = '', e = '';
  if(item.operator === " > " ) {
    l = item.compVal;
  } else if(item.operator === " < ") {
    u = item.compVal;
  } else {
    e = item.compVal;
  }
  $.getJSON(urls.tableChangeURL, {attribute: item.attr, lower: l, equal: e,
            upper: u}, function(data){
    updateGridData(data);
  });
}

/**
 *
 */
function extractLabels(labs, labId) {
  let tempLabels = {};
  for(let i in labs) {
    let label = labs[i];
    let l = {
      x : label["x"],
      y : label["y"],
      label : label[labId]
    };
    tempLabels[i] = l;
  }
  let numLabels = Object.keys(tempLabels).length;
  labels = new Array(numLabels);
  for(let i = 0; i < numLabels; ++i) {
    labels[i] = [tempLabels[i].x, tempLabels[i].y, tempLabels[i].label];
  }
  requestAnimationFrame(loop);
}

function fillBufferData(buffer, data) {
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
}

function newTree() {
  const attr = $("#highlight-options").val();
  const l = $("#lower-bound").val();
  const u = $("#upper-bound").val();
  const e = $("#category").val();
  $.getJSON(urls.subTreeURL, {attribute: attr, lower: l, equal: e,
            upper: u}, function(data){
    loadTree(data);
  }).done(function() {
    $.getJSON(urls.cladeURL, {}, function(data) {
      loadColorClades(data);
    });
  });
}

function getOldTree(event) {
  $.getJSON(urls.oldTreeURL, {}, function(data){
    if(data.length == 0) {
      return;
    }
    loadTree(data);
  }).done(function() {
    $.getJSON(urls.cladeURL, {}, function(data) {
      loadColorClades(data);
    });
  });
}

function autoCollapse() {
  let tps = $('#tip-slider').val();
  let thrshld = $('#threshold-slider').val();
  $.getJSON(urls.autoCollapse, {tips: tps, threshold: thrshld}, function(data) {
    loadTree(data);
    $.getJSON(urls.trianglesURL, {}, function(data) {
      drawingData.triangles = extractInfo(data, field.triangleFields);
      fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
    }).done(function() {
      requestAnimationFrame(loop);
    });
  });
}
