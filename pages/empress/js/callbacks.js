"use strict";

/**
 * tells javasript what function to call for mouse/keyboard events
 */
function initCallbacks(){
  const SHFT_KEY = 16;
  const DELAY = 500;
  window.onTreeSurface = false;
  window.timer = setTimeout(hover, 100, 0,0);
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

function hover(x,y) {
  if($("body").css("cursor") !== 'none') {
    nodeHover(x,y);
    triangleHover(x,y);
  }
}

function nodeHover(x,y) {
  let id;
  let clsXTC, clsYTC, clsID;
  let close = 1000;
  let tmp;
  let xDist, yDist, treeX, treeY, nScreenX, nScreenY, treeSpace, screenSpace;
  let canvas = $(".tree-surface")[0];
  for(id in tree.tree) {
      treeX = tree.tree[id].x;
      treeY = tree.tree[id].y;
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
  if(close <= 50 && (clsID === "N1" || tree.metadata[clsID]["branch_is_visible"])) {
    drawingData.hoveredNode = [clsXTC, clsYTC, 0, 1, 0];
    if(clsID !== "N1") {
      $("#node-hover-div").html(
        "<b>Genome ID:</b> " + clsID + "<br>"  +
        "<b>Kingdom: </b>" + tree.metadata[clsID]["kingdom"] + "<br>" +
        "<b>Phylum: </b>" + tree.metadata[clsID]["phylum"] + "<br>" +
        "<b>Class: </b>" + tree.metadata[clsID]["class"] + "<br>" +
        "<b>Order: </b>" + tree.metadata[clsID]["order"] + "<br>" +
        "<b>Family: </b>" + tree.metadata[clsID]["family"] + "<br>" +
        "<b>Genus: </b>" + tree.metadata[clsID]["genus"] + "<br>" +
        "<b>Species: </b>" + tree.metadata[clsID]["species"] + "<br>" +
        "<b>taxa: </b>" + tree.tree[clsID]["leafcount"] + "<br>" +
        "<b>download: "
      );
      if(tree.tree[clsID]["link"] !== "") {
        $("#node-hover-div").append("<a href=" + tree.tree[clsID]["link"] + ">link</a><br>");
      }
    } else {
      $("#node-hover-div").html(
        "<b>Genome ID:</b> " + clsID + "<br>"  +
        "<b>Kingdom: </b>" + "null" + "<br>" +
        "<b>Phylum: </b>" + "null" +"<br>" +
        "<b>Class: </b>" + "null" + "<br>" +
        "<b>Order: </b>" + "null" + "<br>" +
        "<b>Family: </b>" + "null" + "<br>" +
        "<b>Genus: </b>" +"null" + "<br>" +
        "<b>Species: </b>" + "null" + "<br>" +
        "<b>taxa: </b>" + tree.tree[clsID]["leafcount"] + "<br>"
      );
    }
      // calculate the screen coordinate of the label
      let treeSpace = vec4.fromValues(clsXTC, clsYTC, 0, 1);
      let screenSpace = vec4.create();
      vec4.transformMat4(screenSpace, treeSpace, shaderProgram.mvpMat);
      screenSpace[0] /= screenSpace[3];
      screenSpace[1] /= screenSpace[3];
      let pixelX = (screenSpace[0] * 0.5 + 0.5) * canvas.offsetWidth;
      let pixelY = (screenSpace[1] * -0.5 + 0.5)* canvas.offsetHeight;

      // make the div
      let div = $("#node-hover-div");

      div.css({left: Math.floor(pixelX) + "px",
               top: Math.floor(pixelY) + "px",
               display: "block"});
  } else {
    // make the div
      let div = $("#node-hover-div");

      div.css({display: "none"});
  }

  fillBufferData(shaderProgram.hoverNodeBuffer, drawingData.hoveredNode);
  requestAnimationFrame(loop);
}

function triangleHover(x, y) {
  let treeCoords = toTreeCoords(x, y);
  let triRoot = tree.triangleAt(treeCoords[0], treeCoords[1]);
  let taxLevel = $("#collapse-level").val();
  let div = $("#tri-hover-div");
  if(triRoot != null) {
    div.html("<b>" + tree.metadata[triRoot.id][taxLevel] + "</b><br>" +
             "<b>Descendants: </b>" + tree.tree[triRoot.id]["leafcount"] + "<br>" );
    div.css({left: x + "px",
             top: y + "px",
             display: "block"});
    drawingData.highTri = triRoot.tri;
    fillBufferData(shaderProgram.highTriBuffer, drawingData.highTri);
  }
  else {
    drawingData.highTri = [];
    div.css({display: "none"});
  }
  requestAnimationFrame(loop);
}

function autoCollapseTree() {
  let selectElm = $("#collapse-level");
  if($("#collapse-cb").is(":checked")) {
    selectElm.attr("disabled", false);
    let taxLevel = selectElm.val();
    let edgeData = tree.collapse(taxLevel);
    drawingData.numBranches = edgeData.length;
    drawingData.triangles = tree.triData;
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  } else {
    selectElm.attr("disabled", true);
    let edgeData = tree.uncollapse();
    drawingData.numBranches = edgeData.length;
    drawingData.triangles = tree.triData;
    fillBufferData(shaderProgram.treeVertBuffer, edgeData);
    fillBufferData(shaderProgram.triangleBuffer, drawingData.triangles);
  }

  clearLabels("tip-label-container");
  clearLabels("node-label-container");
  retriveTaxonNodes('t');
  retriveTaxonNodes('n');
  requestAnimationFrame(loop);
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

function retriveTaxonNodes(triggerBy) {
  let taxLevel;
  let node;
  let selectElm;
  if(triggerBy === 't' && $("#tips").is(":checked")) {
    clearLabels("tip-label-container");
    selectElm = $("#tips-find-level");
    selectElm.attr("disabled", false)
    taxLevel = selectElm.val();
    tipLabels = tree.getTaxonLabels(taxLevel, "true");
  }
  else if(!$("#tips").is(":checked")) {
    $("#tips-find-level").attr('disabled',true);
    tipLabels = [];
    clearLabels("tip-label-container");
  }

  if(triggerBy === 'n' && $("#internal-nodes").is(":checked")) {
    selectElm = $("#nodes-find-level");
    selectElm.attr("disabled", false);
    taxLevel = selectElm.val();
    nodeLabels = tree.getTaxonLabels(taxLevel, "false");
  }
  else if(!$("#internal-nodes").is(":checked")) {
    $("#nodes-find-level").attr("disabled", true);
    nodeLabels = [];
  }
  requestAnimationFrame(drawLabels);
}

function clearLabels(container) {
   let divContainerElement = document.getElementById(container);
    while(divContainerElement.firstChild) {
      divContainerElement.removeChild(divContainerElement.firstChild);
    }
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

